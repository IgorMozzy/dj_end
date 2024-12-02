import json
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from movies.models import Genre, Movie, Review, Rating, UserMovieList
from movies.models import MovieImage

User = get_user_model()


# tests for models
class GenreModelTest(TestCase):
    def test_create_genre(self):
        genre = Genre.objects.create(name="Action")
        self.assertEqual(str(genre), "Action")


class MovieModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Sci-Fi")

    def test_create_movie(self):
        movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller.",
            release_date=date(2010, 7, 16),
            duration=148,
        )
        movie.genres.add(self.genre)
        self.assertEqual(str(movie.title), "Inception")
        self.assertEqual(movie.average_rating(), 0)


class MovieImageModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller.",
            release_date=date(2010, 7, 16),
        )

    def test_create_movie_image(self):
        image = MovieImage.objects.create(movie=self.movie, image="images/extra/test.jpg")
        self.assertEqual(str(image), f"Extra image for {self.movie.title}")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller.",
            release_date=date(2010, 7, 16),
        )

    def test_create_review(self):
        review = Review.objects.create(movie=self.movie, user=self.user, text="Great movie!")
        self.assertEqual(review.text, "Great movie!")


class RatingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller.",
            release_date=date(2010, 7, 16),
        )

    def test_create_rating(self):
        rating = Rating.objects.create(movie=self.movie, user=self.user, value=5)
        self.assertEqual(rating.value, 5)


class UserMovieListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller.",
            release_date=date(2010, 7, 16),
        )

    def test_create_user_movie_list(self):
        user_list = UserMovieList.objects.create(user=self.user, name="Favorites")
        user_list.movies.add(self.movie)
        self.assertIn(self.movie, user_list.movies.all())


# urls tests
class EndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.genre = Genre.objects.create(name="Action")
        self.movie = Movie.objects.create(
            title="Inception",
            description="A mind-bending thriller.",
            release_date=date(2010, 7, 16),
            duration=148,
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie, user=self.user, text="Amazing movie!"
        )
        self.rating = Rating.objects.create(movie=self.movie, user=self.user, value=5)

    def test_movie_detail_view(self):
        response = self.client.get(reverse("movie_detail", args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")

    def test_add_review_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(reverse("add_review", args=[self.movie.id]), {"text": "Great movie!"})
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Review.objects.filter(movie=self.movie).count(), 2)

    def test_toggle_favorite_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("toggle_favorite", args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)

    def test_rate_movie_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("rate_movie", args=[self.movie.id]),
            data=json.dumps({"rating": 4}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "success")

    def test_user_profile_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
