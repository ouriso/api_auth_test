import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class UserAPITest(TestCase):
    def setUp(self):
        self.client_jerry = APIClient()
        self.client_tom = APIClient()
        self.client_anon = APIClient()

        self.dataset_read = {
            "username": "jack",
            "first_name": "Jack",
            "last_name": "Black",
            "is_active": False
        }
        self.dataset_write = self.dataset_read.copy()
        self.dataset_write['password'] = "asfaQQWd12"

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
            password='A12345a!',
            is_superuser=False
        )

        token_jerry, created = Token.objects.get_or_create(user=self.user_jerry)
        token_tom, created = Token.objects.get_or_create(user=self.user_tom)

        self.client_jerry.credentials(
            HTTP_AUTHORIZATION='Token ' + token_jerry.key
        )
        self.client_tom.credentials(
            HTTP_AUTHORIZATION='Token ' + token_tom.key
        )

    def test_get_list_not_auth(self):
        response = self.client_anon.get(
            reverse('users-list')
        )
        data = json.loads(response.content)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            ('Проверьте, что при GET-запросе по ссылке "/api/v1/users"'
             ' неавторизаванному пользователю возвращается код 200')
        )
        self.assertEqual(
            len(data), 2,
            ('Проверьте, что при GET-запросе по ссылке "/api/v1/users"'
             ' выводите всех юзеров')
        )
        self.check_user(self.user_jerry, data[0])
        self.check_user(self.user_tom, data[1])

    def test_get_list_auth(self):
        response = self.client_jerry.get(
            reverse('users-list')
        )
        data = json.loads(response.content)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            ('Проверьте, что при GET-запросе по ссылке "/api/v1/users"'
             ' авторизаванному пользователю возвращается код 200')
        )
        self.assertEqual(
            len(data), 2,
            ('Проверьте, что при GET-запросе по ссылке "/api/v1/users"'
             ' выводите всех юзеров')
        )
        self.check_user(self.user_jerry, data[0])
        self.check_user(self.user_tom, data[1])

    def test_get_user(self):
        response = self.client_jerry.get(
            reverse('users-detail', args=[1])
        )
        data = json.loads(response.content)
        self.check_user(self.user_jerry, data)

    def test_post_not_auth(self):
        response = self.client_anon.post(
            reverse('users-list'),
            data=self.dataset_write
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            ('Проверьте, что при POST-запросе неавторизованному пользователю'
             ' возвращается код 401')
        )
        self.assertEqual(
            User.objects.count(), 2,
            ('Проверьте, что новый пользователь не создается'
             ' при POST-запросе от неавторизованного пользователя')
        )

    def test_post_auth_wrong(self):
        response = self.client_jerry.post(
            reverse('users-list'),
            data={}
        )
        data = json.loads(response.content)
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            ('Проверьте, что при POST-запросе с неверными данными'
             'возвращается код 400')
        )
        self.assertEqual(
            data.get('username'), ["This field is required."],
            'Проверьте, что при POST-запросе поле "username" обязательно'
        )
        self.assertEqual(
            data.get('password'), ["This field is required."],
            'Проверьте, что при POST-запросе поле "password" обязательно'
        )
        self.assertEqual(
            data.get('is_active'), ["This field is required."],
            'Проверьте, что при POST-запросе поле "is_active" обязательно'
        )

    def test_post_auth_not_admin(self):
        response = self.client_tom.post(
            reverse('users-list'),
            data=self.dataset_write
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            'Проверьте, что при POST-запросе не админом возвращается код 403'
        )
        self.assertEqual(
            User.objects.count(), 2,
            ('Проверьте, что при POST-запросе от не админа'
             ' новый пользователь не создается')
        )

    def test_post_auth_admin(self):
        response = self.client_jerry.post(
            reverse('users-list'),
            data=self.dataset_write
        )
        data = json.loads(response.content)
        user = User.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_user(user, self.dataset_read)
        self.check_data(self.dataset_read, data)

    def test_patch_not_auth(self):
        response = self.client_anon.patch(
            reverse('users-detail', args=[1]),
            data=self.dataset_write
        )
        user = User.objects.get(id=1)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            ('Проверьте, что при PATCH-запросе неавторизованному пользователю'
             ' возвращается код 401')
        )
        with self.assertRaises(AssertionError):
            self.check_user(user, self.dataset_read)

    def test_patch_not_self(self):
        response = self.client_tom.patch(
            reverse('users-detail', args=[1]),
            data=self.dataset_write
        )
        user = User.objects.get(id=1)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            ('Проверьте, что при PATCH-запросе на изменение чужого аккаунта'
             ' возвращается код 403')
        )
        with self.assertRaises(AssertionError):
            self.check_user(user, self.dataset_read)

    def test_patch_self(self):
        response = self.client_jerry.patch(
            reverse('users-detail', args=[1]),
            data=self.dataset_write
        )
        user = User.objects.get(id=1)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            ('Проверьте, что при PATCH-запросе пользователю'
             ' возвращается код 200')
        )
        self.check_user(user, self.dataset_read)

    def test_delete_not_auth(self):
        response = self.client_anon.delete(
            reverse('users-detail', args=[1])
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            ('Проверьте, что при DELETE-запросе на удаление аккаунта'
             ' неавторизаванному пользователю возвращается код 401')
        )
        self.assertTrue(
            User.objects.filter(id=1).exists(),
            ('Проверьте, что при DELETE-запросе от неавторизаванного'
             ' пользователя удаление не происходит')
        )

    def test_delete_not_self(self):
        response = self.client_tom.delete(
            reverse('users-detail', args=[1])
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            ('Проверьте, что при DELETE-запросе на удаление чужого аккаунта'
             ' авторизованному пользователю возвращается код 403')
        )
        self.assertTrue(
            User.objects.filter(id=1).exists(),
            ('Проверьте, что при DELETE-запросе от авторизаванного'
             ' пользователя удаление чужого аккаунта не происходит')
        )

    def test_delete_admin(self):
        response = self.client_jerry.delete(
            reverse('users-detail', args=[2])
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            ('Проверьте, что при DELETE-запросе на удаление аккаунта'
             ' админу возвращается код 204')
        )
        self.assertFalse(
            User.objects.filter(id=2).exists(),
            ('Проверьте, что при DELETE-запросе от админа'
             ' удаление аккаунта происходит')
        )

    def test_delete_self(self):
        response = self.client_tom.delete(
            reverse('users-detail', args=[2])
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            ('Проверьте, что при DELETE-запросе на удаление'
             ' собственного аккаунта возвращается код 204')
        )
        self.assertFalse(
            User.objects.filter(id=2).exists(),
            ('Проверьте, что при DELETE-запросе удаление'
             ' собственного аккаунта происходит')
        )

    def check_user(self, user, data):
        for key, value in data.items():
            self.assertEqual(getattr(user, key), value, f'Поле {key} неверно')

    def check_data(self, dataset, json):
        for key, value in dataset.items():
            self.assertEqual(value, json.get(key), f'Поле {key} неверно')


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
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            ('Проверьте, что при запросе на получение токена с неверными'
             ' данными возвращается код 400')
        )
        self.assertIsNone(
            json.loads(response.content).get('token'),
            ('Проверьте, что при запросе на получение токена с неверными'
             ' данными не возвращаете поле token')
        )

    def test_get_token(self):
        response = self.client.post(
            reverse('token-auth'), {
                'username': self.username,
                'password': self.password
            }
        )
        token = json.loads(response.content).get('token')
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            ('Проверьте, что при запросе на получение токена с верными'
             ' данными возвращается код 200')
        )
        self.assertIsNotNone(
            json.loads(response.content).get('token'),
            ('Проверьте, что при запросе на получение токена с верными'
             ' данными возвращаете поле token')
        )
        self.assertEqual(
            token, self.token.key,
            'Проверьте, что генерируется правильный токен'
        )

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.delete(
            reverse('users-detail', args=[1])
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            'Проверьте, что генерируется правильный токен'
        )
