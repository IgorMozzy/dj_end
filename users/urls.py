# URL Patterns
from django.urls import path
from django.contrib.auth import views as auth_views
from users.views import login_view, admin_user_list, user_detail, register

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('a/users/', admin_user_list, name='admin_user_list'),
    path('user/<int:pk>/', user_detail, name='user_detail'),
    path('register/', register, name='register'),
]
