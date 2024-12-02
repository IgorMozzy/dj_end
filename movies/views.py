from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Q, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now

from .forms import ReviewForm
from .models import Movie, Review, Rating, UserMovieList, Genre

User = get_user_model()


# TODO: move to permissions.py?
def is_moderator(user):
    return user.is_superuser or user.groups.filter(name='Moderators').exists()


# start page
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
    all_genres = Genre.objects.all()

    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(genres__name__icontains=search_query)
        ).distinct()

    # Retrieve filter parameters
    rating_min = request.GET.get('rating_min')
    rating_max = request.GET.get('rating_max')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    selected_genres = request.GET.getlist('genres')
    print(selected_genres)
    # Apply filters
    if rating_min:
        movies = movies.filter(average_rating__gte=rating_min)
    if rating_max:
        movies = movies.filter(average_rating__lte=rating_max)
    if year_min:
        movies = movies.filter(release_date__year__gte=year_min)
    if year_max:
        movies = movies.filter(release_date__year__lte=year_max)
    if selected_genres:
        movies = movies.filter(genres__id__in=selected_genres).distinct()

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
        'all_genres': all_genres,
        'selected_genres': selected_genres,
    })


@login_required
def user_profile(request, user_id=None):
    if not user_id:
        profile_user = request.user
    else:
        if not (is_moderator(request.user) or request.user.is_superuser):
            return HttpResponse('Unauthorized', status=401)
        profile_user = get_object_or_404(User, id=user_id)

    reviews = profile_user.review_set.all().order_by('-created_at')
    ratings = profile_user.rating_set.all().order_by('-id')
    favorite_list = UserMovieList.objects.filter(user=profile_user, name="Favorites").first()
    favorites = favorite_list.movies.all() if favorite_list else []

    # Pagination
    review_paginator = Paginator(reviews, 5)  # Show 5 reviews per page
    rating_paginator = Paginator(ratings, 5)  # Show 5 ratings per page
    favorite_paginator = Paginator(favorites, 5)  # Show 5 favorites per page

    review_page = request.GET.get('review_page', 1)
    rating_page = request.GET.get('rating_page', 1)
    favorite_page = request.GET.get('favorite_page', 1)

    reviews_paginated = review_paginator.get_page(review_page)
    ratings_paginated = rating_paginator.get_page(rating_page)
    favorites_paginated = favorite_paginator.get_page(favorite_page)

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'reviews': reviews_paginated,
        'ratings': ratings_paginated,
        'favorites': favorites_paginated,
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
        created = False or review
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
    search_query = request.GET.get('search', '').strip()

    if request.user.is_superuser:
        # Full data for superusers
        users = User.objects.all()
        if search_query:
            users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))
        reviews = Review.objects.filter(user__in=users).order_by('-created_at')
    else:
        # Only show regular users and their reviews for moderators
        users = User.objects.filter(is_superuser=False).exclude(groups__name='Moderators')
        if search_query:
            users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))
        reviews = Review.objects.filter(
            user__in=users
        ).order_by('-created_at')

    # pagination
    user_paginator = Paginator(users, 10)
    review_paginator = Paginator(reviews, 10)  # Show 10 reviews per page

    user_page = request.GET.get('user_page', 1)
    review_page = request.GET.get('review_page', 1)

    paginated_users = user_paginator.get_page(user_page)
    paginated_reviews = review_paginator.get_page(review_page)

    return render(request, 'moderation_dashboard.html', {
        'users': paginated_users,
        'reviews': paginated_reviews,
        'search_query': search_query,
    })


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
