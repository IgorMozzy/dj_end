from django.contrib import admin
from .models import Movie, Genre, Review, Rating, UserMovieList, MovieImage


admin.site.register(Review)
admin.site.register(Rating)
admin.site.register(UserMovieList)


class MovieImageInline(admin.TabularInline):  # Или admin.StackedInline для вертикального отображения
    model = MovieImage
    extra = 1  # Показывать одну пустую форму для добавления нового изображения
    fields = ['image']
    max_num = 10  # Максимум 10 изображений (опционально)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'is_highlight', 'duration']
    list_filter = ['release_date', 'is_highlight', 'genres']
    search_fields = ['title', 'description']
    inlines = [MovieImageInline]  # Добавление инлайнов


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
