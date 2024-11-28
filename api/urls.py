from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import permissions
from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API Documentation for your Django Project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def admin_required(user):
    return user.is_staff


urlpatterns = [
    path('api/users/', views.UserList.as_view(), name='user-list'),
    path('api/users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('api/groups/', views.GroupList.as_view(), name='group-list'),
    path('api/groups/<int:pk>/', views.GroupDetail.as_view(), name='group-detail'),

    re_path(r'^swagger/$',
            login_required(user_passes_test(admin_required)(schema_view.with_ui('swagger', cache_timeout=0))),
            name='schema-swagger-ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
