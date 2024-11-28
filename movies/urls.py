from django.conf.urls.static import static
from django.urls import path\

from conf import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.movie_catalog, name='catalog'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/add_review/', views.add_review, name='add_review'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),

    # TODO: recheck necessity of these paths below
    path('movie/<int:movie_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('movie/<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
    path('movie/<int:movie_id>/review/', views.write_or_edit_review, name='write_review'),
    path('movie/<int:movie_id>/review/<int:review_id>/', views.write_or_edit_review, name='edit_review'),
    path('movie/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # TODO: Section is almost done, but not presented in UI
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/user/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('moderation/user/<int:user_id>/', views.user_profile_view, name='moderator_user_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
