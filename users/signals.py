from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    group = apps.get_model('auth', 'Group')

    default_groups = ['Admins', 'Users', 'Moderators']

    for group_name in default_groups:
        group.objects.get_or_create(name=group_name)
