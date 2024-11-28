import json
import logging
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from .forms import UserLoginForm, UserRegistrationForm, UserForm, GroupForm
from .models import CustomUser

logger = logging.getLogger('user_activity')


def empty_home(request):
    return render(request, 'base.html')


def login_view(request):
    referer = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    next_url = '/' if 'login' in referer else referer
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User {user.username} logged in successfully.")
                # if user.is_staff:
                #     return redirect('admin_user_list')
                # else:
                #     return redirect('user_detail', pk=user.pk)
                return HttpResponseRedirect(next_url)
            else:
                logger.warning(f"Failed login attempt for username {username}.")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assign user to Users group
            default_group, created = Group.objects.get_or_create(name='Users')
            user.groups.add(default_group)
            messages.success(request, 'Registration successful. You can now log in.')
            logger.info(f"User {user.username} registered successfully and assigned to 'Users' group.")
            login(request, user)
            return redirect('user_detail', pk=user.pk)
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
            logger.warning(f"Failed registration attempt. Errors: {form.errors}")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def admin_user_list(request):
    if not request.user.is_staff:
        logger.warning(f"Unauthorized access attempt by user {request.user.username}")
        return HttpResponse('Unauthorized', status=401)

    users = CustomUser.objects.all()
    groups = Group.objects.all()
    user_form = UserForm()
    group_form = GroupForm()

    if request.method == 'POST':
        if 'create_user' in request.POST:
            logger.info(f"POST Data: {request.POST}")
            user_form = UserForm(request.POST)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.save()

                # Assign groups to the new user
                group_ids = request.POST.getlist('groups')
                for group_id in group_ids:
                    group = get_object_or_404(Group, pk=group_id)
                    user.groups.add(group)

                logger.info(f"User {user.username} created successfully.")
                return redirect('admin_user_list')
            else:
                logger.error(f"Failed to create user: {user_form.errors}")

        elif 'create_group' in request.POST:
            group_form = GroupForm(request.POST)
            if group_form.is_valid():
                group_form.save()
                logger.info("Group created successfully.")
                return redirect('admin_user_list')
            else:
                logger.error(f"Failed to create group: {group_form.errors}")

        elif request.headers.get('Content-Type') == 'application/json':
            # Handle AJAX requests for updating user statuses
            try:
                data = json.loads(request.body)
                user_id = data.get("user_id")
                field = data.get("field")
                value = data.get("value")

                user = get_object_or_404(CustomUser, pk=user_id)
                if field == "is_active":
                    user.is_active = value
                elif field == "is_staff":
                    user.is_staff = value
                user.save()

                logger.info(f"User {user.username} {field} updated to {value}.")
                return JsonResponse({"success": True})
            except Exception as e:
                logger.error(f"Error updating user status: {e}")
                return JsonResponse({"success": False, "error": str(e)})

        elif 'delete_user' in request.POST:
            user_id = request.POST['delete_user']
            try:
                user_to_delete = get_object_or_404(CustomUser, pk=user_id)
                username = user_to_delete.username
                user_to_delete.delete()
                logger.info(f"User {username} deleted successfully.")
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
            return redirect('admin_user_list')

    return render(request, 'admin_user_list.html', {
        'users': users,
        'groups': groups,
        'user_form': user_form,
        'group_form': group_form
    })


@login_required
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    # Check if the current user is allowed to modify this user's data
    if not request.user.is_staff and request.user.pk != user.pk:
        logger.warning(f"Unauthorized modification attempt by user {request.user.username} on user {user.username}")
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        if 'delete_user' in request.POST:
            if request.user.is_staff:
                user.delete()
                messages.success(request, 'User has been successfully deleted.')
                logger.info(f"User {user.username} deleted by admin {request.user.username}")
                return redirect('admin_user_list')
            else:
                messages.error(request, 'You do not have permission to delete this user.')
                logger.warning(f"User {request.user.username} tried to delete user {user.username} without permission")
                return redirect('user_detail', pk=pk)

        # Create form without processing the "password" field
        user_form = UserForm(request.POST, instance=user)

        if user_form.is_valid():
            # Save the rest of the user data without sending to the database yet
            user_data = user_form.save(commit=False)

            # Check for new password
            new_password = request.POST.get('password')
            if new_password:
                user_data.set_password(new_password)
                messages.success(request, 'Password has been successfully updated.')
                logger.info(f"User {user.username} updated their password.")
                login(request, user_data)
            else:
                messages.success(request, 'User details have been successfully updated.')
                logger.info(f"User {user.username} details updated successfully.")

            user_data.save()  # Save changes to the database

            # Update groups for admin
            if request.user.is_staff and 'groups' in request.POST:
                group_ids = request.POST.getlist('groups')
                user.groups.set(group_ids)  # Update groups directly through the standard groups field
                messages.success(request, 'User groups have been successfully updated.')
                logger.info(f"User {user.username} groups updated by admin {request.user.username}.")

            return redirect('user_detail', pk=pk)

    else:
        user_form = UserForm(instance=user)

    groups = Group.objects.all() if request.user.is_staff else user.groups.all()

    return render(request, 'user_detail.html', {
        'user': user,
        'user_form': user_form,
        'groups': groups,
        'is_admin': request.user.is_staff,
    })
