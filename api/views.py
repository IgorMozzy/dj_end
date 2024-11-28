import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.renderers import JSONRenderer

from api.serializers import UserSerializer, GroupSerializer

UserModel = get_user_model()

logger = logging.getLogger('API_log')


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        logger.info(f"Checking if user {request.user.username} is the owner of the object.")
        return obj == request.user


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow if the user is the owner of the object or an administrator
        logger.info(f"Checking if user {request.user.username} is the owner or an admin.")
        return request.user.is_staff or obj == request.user


# View for listing users and creating a new user
class UserList(generics.ListCreateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [JSONRenderer]

    def get_permissions(self):
        if self.request.method == 'POST':
            # Allow anyone to create a user
            return [AllowAny()]
        else:
            # Only administrators can see the list of users
            return [IsAdminUser()]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"User {user.username} created successfully.")


# View for retrieving, updating, and deleting a user
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [JSONRenderer]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            # Only administrators can delete users
            logger.info(f"Delete request for user by {self.request.user.username}.")
            return [IsAdminUser()]
        elif self.request.method in ['PUT', 'PATCH', 'GET']:
            # Admin or owner can update their information and view details
            logger.info(f"Request to {self.request.method} user {self.kwargs['pk']} by {self.request.user.username}.")
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        else:
            # Default to denying access
            return [IsAuthenticated()]

    def delete(self, request, *args, **kwargs):
        # Administrator deletes a user
        user = self.get_object()
        logger.info(f"User {user.username} is being deleted by admin {request.user.username}.")
        super().delete(request, *args, **kwargs)
        return JsonResponse({'message': 'Deleted'}, status=200)


# View for listing groups and creating a new group
class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    renderer_classes = [JSONRenderer]

    def get_permissions(self):
        if self.request.method == 'POST':
            # Only administrators can create new groups
            logger.info(f"Group creation request received by {self.request.user.username}.")
            return [IsAdminUser()]
        elif self.request.method == 'GET':
            # Administrators see all groups, users see only their groups
            logger.info(f"Group list request by {self.request.user.username}.")
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # Administrators see all groups, users see only their groups
        user = self.request.user
        if user.is_staff:
            logger.info(f"Admin {user.username} requesting all groups.")
            return Group.objects.all()
        else:
            logger.info(f"User {user.username} requesting their groups.")
            return user.groups.all()

    def perform_create(self, serializer):
        group = serializer.save()
        logger.info(f"Group {group.name} created successfully by {self.request.user.username}.")


# View for working with a specific group
class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    renderer_classes = [JSONRenderer]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only administrators can modify or delete groups
            logger.info(f"Request to {self.request.method} group {self.kwargs['pk']} by {self.request.user.username}.")
            return [IsAdminUser()]
        elif self.request.method == 'GET':
            # Administrators can see all groups, users can see only their groups
            logger.info(f"Group detail request by {self.request.user.username}.")
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        # Administrators see all groups, users see only their groups
        user = self.request.user
        if user.is_staff:
            logger.info(f"Admin {user.username} requesting group details.")
            return Group.objects.all()
        else:
            logger.info(f"User {user.username} requesting details for their groups.")
            return user.groups.all()

    def perform_update(self, serializer):
        group = serializer.save()
        logger.info(f"Group {group.name} updated successfully by {self.request.user.username}.")

    def perform_destroy(self, instance):
        logger.info(f"Group {instance.name} is being deleted by admin {self.request.user.username}.")
        instance.delete()
