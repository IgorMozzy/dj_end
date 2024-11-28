from django.db import models

from conf import settings


User = settings.AUTH_USER_MODEL


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    is_highlight = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration in minutes")

    # TODO: maybe a common field (write it after save of Rating)
    #  with average rating would be better? Need to think
    def average_rating(self):
        ratings = self.rating.all()
        return ratings.aggregate(models.Avg('value'))['value__avg'] or 0

    # TODO: Recheck and implement to views and templates
    def review_count(self):
        return self.reviews.count()


class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='images/extra/')

    def __str__(self):
        return f"Extra image for {self.movie.title}"


class Review(models.Model):
    movie = models.ForeignKey(Movie, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name="updated_reviews", null=True, blank=True,
                                   on_delete=models.SET_NULL)


class Rating(models.Model):
    movie = models.ForeignKey(Movie, related_name='rating', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()


class UserMovieList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField(Movie, related_name='user_lists')
