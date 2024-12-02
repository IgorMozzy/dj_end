from django.contrib import admin
from .models import Movie, Genre, Review, Rating, UserMovieList, MovieImage


# Inline for additional movie images
class MovieImageInline(admin.TabularInline):  # Use admin.StackedInline for vertical display
    model = MovieImage
    extra = 1
    fields = ['image']
    max_num = 10


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'is_highlight', 'duration']
    list_filter = ['release_date', 'is_highlight', 'genres']
    search_fields = ['title', 'description']
    inlines = [MovieImageInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['movie', 'user', 'created_at', 'updated_at', 'updated_by']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['movie__title', 'user__username', 'text']
    autocomplete_fields = ['movie', 'user', 'updated_by']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['movie', 'user', 'value']
    list_filter = ['value', 'user', 'movie']
    search_fields = ['movie__title', 'user__username']
    autocomplete_fields = ['movie', 'user']


@admin.register(UserMovieList)
class UserMovieListAdmin(admin.ModelAdmin):
    list_display = ['user', 'name']
    list_filter = ['user']
    search_fields = ['name', 'user__username']
    autocomplete_fields = ['user', 'movies']

    # Inline movies in user movie list (optional)
    filter_horizontal = ['movies']
