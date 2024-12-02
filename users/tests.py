import json

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

CustomUser = get_user_model()


class UserDetailViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )

        self.client = Client()

    def test_user_detail_view_get_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('user_detail', kwargs={'pk': self.user.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail.html')

    def test_user_detail_view_get_unauthenticated(self):
        response = self.client.get(reverse('user_detail', kwargs={'pk': self.user.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/login/?next=/user/{self.user.pk}/")

    def test_user_detail_update_by_owner(self):
        self.client.login(username='testuser', password='testpassword123')

        data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': '',
        }

        response = self.client.post(reverse('user_detail', kwargs={'pk': self.user.pk}), data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_detail', kwargs={'pk': self.user.pk}))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'User details have been successfully updated.')

    def test_user_detail_update_by_admin(self):
        self.client.login(username='admin', password='adminpassword123')

        data = {
            'username': 'adminupdateduser',
            'email': 'adminupdateduser@example.com',
            'password': '',
        }

        response = self.client.post(reverse('user_detail', kwargs={'pk': self.user.pk}), data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'adminupdateduser')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_detail', kwargs={'pk': self.user.pk}))

    def test_user_detail_delete_by_admin(self):
        self.client.login(username='admin', password='adminpassword123')

        data = {
            'delete_user': str(self.user.pk)
        }

        response = self.client.post(reverse('user_detail', kwargs={'pk': self.user.pk}), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_user_list'))
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_register_view_post(self):
        register_url = reverse('register')

        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }

        response = self.client.post(register_url, data)
        self.assertEqual(response.status_code, 302)
        new_user = CustomUser.objects.get(username='newuser')
        self.assertEqual(new_user.groups.filter(name='Users').exists(), True)

    def test_admin_user_list_view_as_admin(self):
        self.client.login(username='admin', password='adminpassword123')
        response = self.client.get(reverse('admin_user_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin User List')

    def test_admin_user_list_view_as_non_admin(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('admin_user_list'))

        self.assertEqual(response.status_code, 401)

    def test_create_user_as_admin(self):
        self.client.login(username='admin', password='adminpassword123')
        data = {
            'create_user': '',
            'username': 'createduser',
            'email': 'createduser@example.com',
            'password': 'createdpassword123'
        }

        response = self.client.post(reverse('admin_user_list'), data)
        self.assertEqual(response.status_code, 302)
        created_user = CustomUser.objects.get(username='createduser')
        self.assertEqual(created_user.email, 'createduser@example.com')

    def test_delete_user_as_admin(self):
        self.client.login(username='admin', password='adminpassword123')
        data = {
            'delete_user': str(self.user.pk)
        }

        response = self.client.post(reverse('admin_user_list'), data)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(pk=self.user.pk)

    def test_ajax_update_user_status(self):
        self.client.login(username='admin', password='adminpassword123')

        data = {
            "user_id": self.user.pk,
            "field": "is_active",
            "value": False
        }

        response = self.client.post(
            reverse('admin_user_list'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.is_active)
        self.assertEqual(json.loads(response.content).get('success'), True)

    def test_register_invalid_password(self):
        register_url = reverse('register')

        data = {
            'username': 'invaliduser',
            'email': 'invalid@example.com',
            'password1': 'password123',
            'password2': 'differentpassword'
        }

        response = self.client.post(register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registration failed. Please correct the errors below.')
