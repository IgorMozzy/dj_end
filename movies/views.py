from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Q, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now

from .forms import ReviewForm
from .models import Movie, Review, Rating, UserMovieList

User = get_user_model()


# TODO: move to permissions.py?
def is_moderator(user):
    return user.is_superuser or user.groups.filter(name='Moderators').exists()


# start page / handling
def home(request):
    highlighted_movies = Movie.objects.filter(is_highlight=True)[:8]
    # TODO: recheck for a better way to do it
    top_movies = (
        Movie.objects.annotate(average_rating=Avg('rating__value'))
        .order_by(F('average_rating').desc(nulls_last=True))[:250]
    )

    return render(request, 'home_1.html', {
        'highlighted_movies': highlighted_movies,
        'top_movies': top_movies
    })


def movie_catalog(request):
    search_query = request.GET.get('search', '').strip()
    sort_option = request.GET.get('sort', 'title')
    sort_order = request.GET.get('order', 'asc')

    movies = Movie.objects.annotate(average_rating=Avg('rating__value'))

    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(genres__name__icontains=search_query)
        ).distinct()

    # Сортировка
    if sort_option == 'rating':
        movies = movies.annotate(average_rating=Avg('rating__value'))
        # TODO: recheck for a better way to do it (also in home view)
        movies = movies.order_by(
            F('average_rating').desc(nulls_last=True) if sort_order == 'desc' else F('average_rating').asc(
                nulls_first=True)
        )
    elif sort_option == 'year':
        movies = movies.order_by('-release_date' if sort_order == 'desc' else 'release_date')
    else:
        movies = movies.order_by('-title' if sort_order == 'desc' else 'title')

    return render(request, 'catalog.html', {
        'movies': movies,
        'search_query': search_query,
        'sort_option': sort_option,
        'sort_order': sort_order,
    })


@login_required
def user_profile(request, user_id=None):
    if not user_id:
        profile_user = request.user
    else:
        if not (is_moderator(request.user) or request.user):
            return HttpResponse('Unauthorized', status=401)
        profile_user = get_object_or_404(User, id=user_id)

    reviews = profile_user.review_set.all()
    ratings = profile_user.rating_set.all()

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'reviews': reviews,
        'ratings': ratings,
    })


# Detailed page and its handling
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user

    is_favorite = False
    user_rating = None
    reviews = movie.reviews.all()

    if user.is_authenticated:
        # info for context
        favorite_list = UserMovieList.objects.filter(user=user, name="Favorites").first()
        if favorite_list and movie in favorite_list.movies.all():
            is_favorite = True

        user_rating_obj = Rating.objects.filter(user=request.user, movie=movie).first()
        user_rating = user_rating_obj.value if user_rating_obj else None

    return render(request, 'detail.html', {
        'movie': movie,
        'is_favorite': is_favorite,
        'user_rating': user_rating,  # or None
        'average_rating': movie.average_rating(),  # or None
        'reviews': reviews,
        'is_moderator': is_moderator(user),
    })


def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('movie_detail', movie_id=movie.id)
    else:
        form = ReviewForm()
    return render(request, 'movies/add_review.html', {'form': form, 'movie': movie})


def toggle_favorite(request, movie_id):
    # handling fav button
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user

    favorite_list, created = UserMovieList.objects.get_or_create(user=user, name="Favorites")

    if movie in favorite_list.movies.all():
        favorite_list.movies.remove(movie)
        return JsonResponse({'status': 'removed'})
    else:
        favorite_list.movies.add(movie)
        return JsonResponse({'status': 'added'})


def rate_movie(request, movie_id):
    # handling rate button
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        rating_value = data.get('rating')

        if rating_value and 1 <= int(rating_value) <= 5:
            movie = get_object_or_404(Movie, id=movie_id)
            Rating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'value': int(rating_value)}
            )
            return JsonResponse({'status': 'success', 'message': 'Rating submitted'})
        return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def write_or_edit_review(request, movie_id, review_id=None):
    movie = get_object_or_404(Movie, id=movie_id)

    if review_id:
        # If review_id is provided = moderator or admin editing a specific review
        if not is_moderator(request.user):
            return redirect('movie_detail', movie_id=movie.id)
        review = get_object_or_404(Review, id=review_id)
        created = True
    else:
        # or retrieve user's own review
        review = Review.objects.filter(user=request.user, movie=movie).first()
        created = False
        if not review and request.method == 'POST':
            review = Review(user=request.user, movie=movie)

    if request.method == 'POST':
        # handling for updating/creating review
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            if created:
                form.instance.updated_at = now()
                form.instance.updated_by = request.user
            form.save()
            return redirect('movie_detail', movie_id=movie.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'write_review.html', {
        'form': form,
        'movie': movie,
        'review': review,
        'created': created,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # checking permissions
    if (review.user != request.user and not request.user.is_superuser
            and not request.user.groups.filter(name="Moderators").exists()):
        return HttpResponse('Unauthorized', status=401)

    if request.method == "POST":
        review.delete()
        return redirect("movie_detail", movie_id=review.movie.id)

    return render(request, "confirm_delete.html", {"review": review})


# views for moderators
@user_passes_test(is_moderator)
def moderation_dashboard(request):
    if request.user.is_superuser:
        # full data for superusers
        users = User.objects.all()
        reviews = Review.objects.all().order_by('-created_at')
    else:
        # only show regular users and their reviews for moderators
        users = User.objects.filter(is_superuser=False).exclude(groups__name='Moderators')
        reviews = Review.objects.filter(user__is_superuser=False).exclude(user__groups__name='Moderators').order_by('-created_at')

    return render(request, 'moderation_dashboard.html', {'users': users, 'reviews': reviews})


@user_passes_test(is_moderator)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('moderation_dashboard')


@user_passes_test(is_moderator)
def user_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    reviews = Review.objects.filter(user=user)
    ratings = Rating.objects.filter(user=user)

    return render(request, 'moderator_user_profile.html', {
        'profile_user': user,
        'reviews': reviews,
        'ratings': ratings,
    })
