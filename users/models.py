from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, phone=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('The Username field must be set'))

        if email:
            email = self.normalize_email(email)
            # Check for email uniqueness only if the email is provided
            if CustomUser.objects.filter(email=email).exists():
                raise ValueError(_('A user with this email already exists'))

        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if extra_fields.get('is_staff') is not True:
            user_group, created = Group.objects.get_or_create(name='Users')
            user.groups.add(user_group)

        return user

    def create_superuser(self, username, email=None, phone=None,
                         password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        user = self.create_user(username, email, phone, password, **extra_fields)

        admin_group, created = Group.objects.get_or_create(name='Admins')
        user.groups.add(admin_group)

        return user


# Custom User Model
class CustomUser(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
