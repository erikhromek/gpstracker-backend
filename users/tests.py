import json
import random
import string

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.managers import UserManager
from users.models import User


class TestUserRegistration(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.register_root_url = reverse("users:register-admin")
        self.register_url = reverse("users:register-user")
        self.users_url = reverse("users:list")

        random_password = "".join(
            random.choice(string.ascii_letters) for i in range(10)
        )
        random_password2 = "".join(
            random.choice(string.ascii_letters) for i in range(10)
        )

        self.register_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user@email.com",
            "organization_name": "CEIoT",
            "password": random_password,
            "password2": random_password,
        }

        self.register_another_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user@email1.com",
            "organization_name": "CEIoT2",
            "password": random_password,
            "password2": random_password,
        }

        self.register_incorrect_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user@email.com",
            "password": random_password,
            "password2": random_password,
        }

        self.register_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user1@email.com",
            "password": random_password,
            "password2": random_password,
        }

        self.register_another_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user2@email.com",
            "password": random_password,
            "password2": random_password,
        }

        self.register_root_user_data_with_empty_password = {
            "name": "John",
            "email": "test_user@email.com",
            "surname": "Smith",
            "organization_name": "CEIoT",
            "password": "",
        }

        self.register_user_data_with_incorrect_password = {
            "name": "John",
            "email": "test_user@email.com",
            "surname": "Smith",
            "organization_name": "CEIoT",
            "password": random_password,
            "password2": random_password2,
        }

        return super().setUp()

    def test_root_user_creation(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            user.organization.name, self.register_root_user_data["organization_name"]
        )
        self.assertEqual(user.role, "ADM")

    def test_user_creation(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(user.role, "ADM")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.register_url, self.register_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_user_data["email"])
        self.assertEqual(user.role, "OPS")

    def test_user_empty_password_creation(self):
        response = self.client.post(
            self.register_root_url,
            self.register_root_user_data_with_empty_password,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incorrect_root_user_creation(self):
        response = self.client.post(
            self.register_root_url,
            self.register_incorrect_root_user_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_incorrect_user_creation(self):
        response = self.client.post(
            self.register_url, self.register_user_data, format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_incorrect_root_and_user_creation(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(user.role, "ADM")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.register_url, self.register_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_user_data["email"])
        self.assertEqual(user.role, "OPS")

        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.register_url, self.register_user_data, format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_same_organization(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_root = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(user_root.role, "ADM")
        self.client.force_authenticate(user=user_root)

        response = self.client.post(
            self.register_url, self.register_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_user_data["email"])
        self.assertEqual(user.role, "OPS")

        response = self.client.post(
            self.register_root_url, self.register_another_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=user_root)

        response = self.client.get(self.users_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        list = json.loads(response.content)
        self.assertEqual(len(list), 2)


class TestUserLogin(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.register_root_url = reverse("users:register-admin")
        self.register_url = reverse("users:register-user")
        self.login_url = reverse("users:login")
        self.details_url = reverse("users:details")

        random_password = "".join(
            random.choice(string.ascii_letters) for i in range(10)
        )

        self.register_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user@email.com",
            "organization_name": "CEIoT",
            "password": random_password,
            "password2": random_password,
        }

        self.register_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user1@email.com",
            "password": random_password,
            "password2": random_password,
        }

        self.register_another_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user2@email.com",
            "password": random_password,
            "password2": random_password,
        }

        self.login_user_data = {
            "email": "test_user@email.com",
            "password": random_password,
        }

        return super().setUp()

    def test_root_user_login(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            user.organization.name, self.register_root_user_data["organization_name"]
        )
        self.assertEqual(user.role, "ADM")

        login_data = {
            "username": self.register_root_user_data["email"],
            "password": self.register_root_user_data["password"],
        }

        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_root_user_login(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            user.organization.name, self.register_root_user_data["organization_name"]
        )
        self.assertEqual(user.role, "ADM")

        login_data = {
            "username": self.register_root_user_data["email"],
            "password": "FAKE_PASSWORD",
        }

        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(user.role, "ADM")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.register_url, self.register_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_user_data["email"])
        self.assertEqual(user.role, "OPS")

        login_data = {
            "username": self.register_user_data["email"],
            "password": self.register_user_data["password"],
        }

        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_details(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(user.role, "ADM")
        self.client.force_authenticate(user=user)

        response = self.client.get(self.details_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content["id"], user.id)


class TestUserUpdate(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.register_root_url = reverse("users:register-admin")
        self.register_url = reverse("users:register-user")
        self.login_url = reverse("users:login")
        random_password = "".join(
            random.choice(string.ascii_letters) for i in range(10)
        )

        self.register_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user@email.com",
            "organization_name": "CEIoT",
            "password": random_password,
            "password2": random_password,
        }

        self.update_user_data = {
            "name": "Josh",
            "surname": "Richards",
        }

    def test_user_update(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(user.role, "ADM")
        self.client.force_authenticate(user=user)

        self.update_url = reverse("users:update", kwargs={"pk": user.id})

        response = self.client.patch(
            self.update_url, self.update_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content["name"], self.update_user_data["name"])
        self.assertEqual(content["surname"], self.update_user_data["surname"])
