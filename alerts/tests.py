import json
import random
import string

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from alerts.models import Beneficiary
from users.managers import UserManager
from users.models import User


class TestBeneficiaryCreation(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.register_root_url = reverse("users:register-admin")
        self.beneficiaries_url = reverse("alerts:beneficiary-list")

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

        self.register_another_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user1@email.com",
            "organization_name": "CEIoT",
            "password": random_password,
            "password2": random_password,
        }

        self.register_beneficiary_data = {
            "name": "John",
            "surname": "Smith",
            "telephone": "1154047987",
            "company": "CLA",
            "description": "Prueba de beneficiario",
            "enabled": True,
        }

        self.update_beneficiary_data = {
            "description": "Cambio de texto de beneficiario",
            "enabled": False,
        }

        self.register_beneficiary_data_type = {
            "name": "John",
            "surname": "Smith",
            "telephone": "1154047987",
            "company": "CLA",
            "type_id": 5,
            "description": "Prueba de beneficiario",
            "enabled": True,
        }

        self.register_another_beneficiary_data = {
            "name": "John",
            "surname": "Smith",
            "telephone": "1154047988",
            "company": "CLA",
            "description": "Prueba de beneficiario",
            "enabled": True,
        }

        return super().setUp()

    def test_beneficiary_creation(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            user.organization.name, self.register_root_user_data["organization_name"]
        )
        self.assertEqual(user.role, "ADM")

        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.beneficiaries_url, self.register_beneficiary_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_beneficiary_creation_duplicated(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            user.organization.name, self.register_root_user_data["organization_name"]
        )
        self.assertEqual(user.role, "ADM")

        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.beneficiaries_url, self.register_beneficiary_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.beneficiaries_url, self.register_beneficiary_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_beneficiary_filter(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        root_user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            root_user.organization.name,
            self.register_root_user_data["organization_name"],
        )
        self.assertEqual(root_user.role, "ADM")

        self.client.force_authenticate(user=root_user)
        response = self.client.post(
            self.beneficiaries_url, self.register_beneficiary_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.register_root_url, self.register_another_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_another_root_user_data["email"])
        self.assertEqual(
            user.organization.name,
            self.register_another_root_user_data["organization_name"],
        )
        self.assertEqual(user.role, "ADM")

        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.beneficiaries_url,
            self.register_another_beneficiary_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=root_user)
        response = self.client.get(self.beneficiaries_url, format="json")
        list = json.loads(response.content)
        self.assertEqual(len(list), 1)

    def test_beneficiary_create_type(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        root_user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            root_user.organization.name,
            self.register_root_user_data["organization_name"],
        )
        self.assertEqual(root_user.role, "ADM")

        self.client.force_authenticate(user=root_user)
        response = self.client.post(
            self.beneficiaries_url, self.register_beneficiary_data_type, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_beneficiary_update_and_disable(self):
        response = self.client.post(
            self.register_root_url, self.register_root_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.register_root_user_data["email"])
        self.assertEqual(
            user.organization.name, self.register_root_user_data["organization_name"]
        )
        self.assertEqual(user.role, "ADM")

        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.beneficiaries_url, self.register_beneficiary_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        beneficiary = json.loads(response.content)

        beneficiaries_update_url = reverse(
            "alerts:beneficiary-detail", kwargs={"pk": beneficiary["id"]}
        )

        response = self.client.patch(
            beneficiaries_update_url, self.update_beneficiary_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        beneficiary = Beneficiary.objects.get(id=beneficiary["id"])
        self.assertEqual(
            beneficiary.description, self.update_beneficiary_data["description"]
        )
        self.assertEqual(beneficiary.enabled, False)
