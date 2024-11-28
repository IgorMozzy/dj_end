import unittest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import Group

UserModel = get_user_model()


class UserApiTests(APITestCase):

    def setUp(self):
        # Создаем обычного пользователя
        self.user = UserModel.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Создаем администратора
        self.admin_user = UserModel.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )

        # Создаем группу и добавляем пользователя в нее
        self.group = Group.objects.create(name='TestGroup')
        self.user.groups.add(self.group)

        # Настраиваем клиент для пользователя
        self.user_client = APIClient()
        user_refresh = RefreshToken.for_user(self.user)
        self.user_token = str(user_refresh.access_token)
        self.user_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        # Настраиваем клиент для администратора
        self.admin_client = APIClient()
        admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(admin_refresh.access_token)
        self.admin_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)

        # URL-ы для API
        self.user_list_url = reverse('user-list')
        self.user_detail_url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.admin_detail_url = reverse('user-detail', kwargs={'pk': self.admin_user.pk})
        self.group_list_url = reverse('group-list')
        self.group_detail_url = reverse('group-detail', kwargs={'pk': self.group.pk})

    def test_create_user(self):
        # Тестирование создания пользователя любым пользователем (публичный доступ)
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }

        response = self.client.post(self.user_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserModel.objects.count(), 3)
        self.assertEqual(UserModel.objects.get(username='newuser').email, 'newuser@example.com')

    def test_get_user_list_user(self):
        # Обычный пользователь пытается получить список пользователей
        response = self.user_client.get(self.user_list_url)

        # Ожидаем 403, так как только администраторы могут просматривать список пользователей
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_list_admin(self):
        # Администратор пытается получить список пользователей
        response = self.admin_client.get(self.user_list_url)

        # Ожидаем 200 OK, так как администратор имеет доступ
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_detail_user(self):
        # Обычный пользователь получает свои детали
        response = self.user_client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_get_user_detail_admin(self):
        # Администратор получает детали другого пользователя
        response = self.admin_client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_user_self(self):
        # Обычный пользователь обновляет свои данные
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'password': 'newpassword456'
        }

        response = self.user_client.put(self.user_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = UserModel.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertTrue(updated_user.check_password('newpassword456'))

    def test_update_admin_other_user(self):
        # Администратор пытается обновить другого пользователя
        data = {
            'username': 'adminupdateduser',
            'email': 'adminupdated@example.com',
            'password': 'adminpassword456'
        }

        response = self.admin_client.put(self.user_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_other_user(self):
        # Пользователь пытается обновить другого пользователя
        data = {
            'username': 'adminupdateduser',
            'email': 'adminupdated@example.com',
            'password': 'adminpassword456'
        }

        response = self.user_client.put(self.admin_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_user(self):
        # Обычный пользователь делает частичное обновление своих данных
        data = {
            'email': 'partialupdate@example.com'
        }

        response = self.user_client.patch(self.user_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = UserModel.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, 'partialupdate@example.com')

    def test_delete_user_self(self):
        # Обычный пользователь пытается удалить себя
        response = self.user_client.delete(self.user_detail_url)

        # Пользователь не может сам себя удалить, должно вернуть 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_admin(self):
        # Администратор удаляет обычного пользователя
        response = self.admin_client.delete(self.user_detail_url)

        # Администратор может удалить пользователя
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserModel.objects.filter(pk=self.user.pk).count(), 0)

    # Тесты для управления группами
    def test_get_group_list_as_admin(self):
        response = self.admin_client.get(self.group_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group_names = [group['name'] for group in response.data]
        self.assertIn('TestGroup', group_names)
        self.assertIn('Admins', group_names)

    def test_get_group_list_as_user(self):
        response = self.user_client.get(self.group_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в данных ответа содержится группа с именем 'TestGroup'
        group_names = [group['name'] for group in response.data]
        self.assertIn('TestGroup', group_names)
        self.assertNotIn('Admins', group_names)

    def test_create_group_as_admin(self):
        data = {
            'name': 'NewGroup'
        }
        response = self.admin_client.post(self.group_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.filter(name='NewGroup').count(), 1)

    def test_create_group_as_user(self):
        data = {
            'name': 'UserGroup'
        }
        response = self.user_client.post(self.group_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_group_as_admin(self):
        data = {
            'name': 'UpdatedGroupName'
        }
        response = self.admin_client.patch(self.group_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_group = Group.objects.get(pk=self.group.pk)
        self.assertEqual(updated_group.name, 'UpdatedGroupName')

    def test_update_group_as_user(self):
        data = {
            'name': 'UserCannotUpdate'
        }
        response = self.user_client.patch(self.group_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_group_as_admin(self):
        response = self.admin_client.delete(self.group_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Group.objects.filter(pk=self.group.pk).count(), 0)

    def test_delete_group_as_user(self):
        response = self.user_client.delete(self.group_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


if __name__ == '__main__':
    unittest.main()
