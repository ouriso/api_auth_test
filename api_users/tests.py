import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.username = 'jerry'
        self.password = 'A12345a!'

        self.user_jerry = User.objects.create_user(
            username=self.username,
            first_name='Jerry',
            last_name='Mouse',
            password=self.password,
            is_active=True
        )
        self.token, created = Token.objects.get_or_create(user=self.user_jerry)

    def test_get_token_wrong_data(self):
        response = self.client.post(
            reverse('token-auth'), {
                'username': self.username,
                'password': (self.password + 'x')
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Проверьте, что при запросе на получение токена с неверными данными возвращается код 400')
        self.assertIsNone(json.loads(response.content).get('token'), 'Проверьте, что при запросе на получение токена с неверными данными не возвращаете поле token')

    def test_get_token(self):
        response = self.client.post(
            reverse('token-auth'), {
                'username': self.username,
                'password': self.password
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Проверьте, что при запросе на получение токена с верными данными возвращается код 200')
        self.assertIsNotNone(json.loads(response.content).get('token'), 'Проверьте, что при запросе на получение токена с верными данными возвращаете поле token')
        self.assertEqual(json.loads(response.content).get('token'), self.token.key, 'Проверьте, что генерируется правильный токен')

    def test_auth_token(self):
        pass


class UserAPITest(TestCase):
    def setUp(self):
        self.client_jerry = APIClient()
        self.client_tom = APIClient()
        self.client_anon = APIClient()

        self.data = {
            "username": "jack",
            "first_name": "Jack",
            "last_name": "Black",
            "password": "asfaQQWd12",
            "is_active": "False"
        }

        self.user_jerry = User.objects.create_user(
            first_name='Jerry',
            last_name='Mouse',
            username='jerry',
            email='jerry@disney.com',
            password='A12345a!',
            is_superuser=True
        )
        self.user_tom = User.objects.create_user(
            first_name='Tom',
            last_name='Cat',
            username='tom',
            email='tom@disney.com',
            password='A12345a!'
        )

        token_jerry, created = Token.objects.get_or_create(user=self.user_jerry)
        token_tom, created = Token.objects.get_or_create(user=self.user_tom)

        self.client_jerry.credentials(HTTP_AUTHORIZATION='Token ' + token_jerry.key)
        self.client_tom.credentials(HTTP_AUTHORIZATION='Token ' + token_tom.key)

    def test_get_list_not_auth(self):
        response = self.client_anon.get(
            reverse('users-list')
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Проверьте, что при GET-запросе по ссылке "/api/v1/users" неавторизаванному пользователю возвращается код 200')
        self.assertEqual(len(data), 2, 'Проверьте, что при GET-запросе по ссылке "/api/v1/users" выводите всех юзеров')

    def test_get_list_auth(self):
        response = self.client_jerry.get(
            reverse('users-list')
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Проверьте, что при GET-запросе по ссылке "/api/v1/users" авторизаванному пользователю возвращается код 200')
        self.assertEqual(len(data), 2, 'Проверьте, что при GET-запросе по ссылке "/api/v1/users" выводите всех юзеров')

    def test_get_user(self):
        response = self.client_jerry.get(
            reverse('users-detail', args=[1])
        )
        data = json.loads(response.content)
        self.check_data(self.user_jerry, data)

    def test_post_not_auth(self):
        response = self.client_anon.post(
            reverse('users-list')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Проверьте, что при POST-запросе неавторизованному пользователю возвращается код 403')

    def test_post_auth(self):
        response = self.client_jerry.post(
            reverse('users-list'),
            data=self.data
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(3 , data.get('id'), 'Проверьте, что сериалайзер возвращает поле "id"')
        self.assertEqual(self.data.get('username'), data.get('username'), 'Проверьте, что сериалайзер возвращает поле "username"')
        self.assertEqual(self.data.get('first_name'), data.get('first_name'), 'Проверьте, что сериалайзер возвращает поле "first_name"')
        self.assertEqual(self.data.get('last_name'), data.get('last_name'), 'Проверьте, что сериалайзер возвращает поле "last_name"')
        self.assertFalse(data.get('is_active'), 'Проверьте, что сериалайзер возвращает поле "is_active"')
        self.assertEqual(self.data.get('last_login'), data.get('last_login'), 'Проверьте, что сериалайзер возвращает поле "last_login"')
        self.assertFalse(data.get('is_superuser'), 'Проверьте, что сериалайзер возвращает поле "is_superuser"')

    def test_patch_not_auth(self):
        pass

    def test_patch_not_self(self):
        pass

    def test_patch_self(self):
        pass

    def test_delete_not_auth(self):
        pass

    def test_delete_not_self(self):
        pass

    def test_delete_admin(self):
        pass

    def test_delete_self(self):
        pass

    def check_data(self, user, response):
        self.assertEqual(len(response), 7)
        self.assertEqual(user.id, response.get('id'), 'Проверьте, что сериалайзер возвращает поле "id"')
        self.assertEqual(user.username, response.get('username'), 'Проверьте, что сериалайзер возвращает поле "username"')
        self.assertEqual(user.first_name, response.get('first_name'), 'Проверьте, что сериалайзер возвращает поле "first_name"')
        self.assertEqual(user.last_name, response.get('last_name'), 'Проверьте, что сериалайзер возвращает поле "last_name"')
        self.assertEqual(user.is_active, response.get('is_active'), 'Проверьте, что сериалайзер возвращает поле "is_active"')
        self.assertEqual(user.last_login, response.get('last_login'), 'Проверьте, что сериалайзер возвращает поле "last_login"')
        self.assertEqual(user.is_superuser, response.get('is_superuser'), 'Проверьте, что сериалайзер возвращает поле "is_superuser"')