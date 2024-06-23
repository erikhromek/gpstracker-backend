import json
import random
import string
from urllib.parse import urlencode

from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from alerts.models import Alert, Beneficiary
from backend import settings
from backend.routing import websocket_urlpatterns
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

    def test_beneficiary_update_and_delete(self):
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
        beneficiary = json.loads(response.content)
        self.assertEqual(
            beneficiary["description"], self.update_beneficiary_data["description"]
        )

        response = self.client.delete(beneficiaries_update_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        beneficiary = Beneficiary.objects.get(id=beneficiary["id"])
        self.assertEqual(beneficiary.enabled, False)


class TestTypesCreation(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.register_root_url = reverse("users:register-admin")
        self.register_beneficiary_type_url = reverse("alerts:beneficiary-type-list")
        self.register_alert_type_url = reverse("alerts:alert-type-list")

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

        self.register_beneficiary_type_data = {"code": "SER", "description": "Sereno"}

        self.register_alert_type_data = {
            "code": "TEST",
            "description": "Prueba de alerta",
        }

    def test_beneficiary_type_creation(self):
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
            self.register_beneficiary_type_url,
            self.register_beneficiary_type_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_alert_type_creation(self):
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
            self.register_alert_type_url, self.register_alert_type_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_alert_type_duplication(self):
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
            self.register_alert_type_url, self.register_alert_type_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.register_alert_type_url, self.register_alert_type_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestAlerts(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.register_root_url = reverse("users:register-admin")
        self.register_alert_url = reverse("alerts:alert-list")
        self.register_alert_type_url = reverse("alerts:alert-type-list")
        self.register_beneficiary_type_url = reverse("alerts:beneficiary-type-list")
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

        self.register_beneficiary_type_data = {"code": "SER", "description": "Sereno"}

        self.register_alert_data = {
            "latitude": "-34.757884",
            "longitude": "-58.2927029",
            "telephone": "1154047987",
        }

        self.update_alert_data = {"state": "A"}

        self.update_alert_data1 = {"observations": "Prueba de alerta"}

        self.update_alert_data2 = {"state": "N"}

        self.update_alert_data3 = {"state": "C"}

        self.register_beneficiary_data = {
            "name": "John",
            "surname": "Smith",
            "telephone": "1154047987",
            "company": "CLA",
            "description": "Prueba de beneficiario",
            "enabled": True,
        }

        self.register_alert_type_data = {
            "code": "TEST",
            "description": "Prueba de alerta",
        }

    def test_alert_creation(self):
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
            self.register_beneficiary_type_url,
            self.register_beneficiary_type_data,
            format="json",
        )
        type = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.register_beneficiary_data["type_id"] = type["id"]
        response = self.client.post(
            self.beneficiaries_url,
            self.register_beneficiary_data,
            format="json",
        )
        beneficiary = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(beneficiary["type_id"], type["id"])

        response = self.client.post(
            self.register_alert_url,
            self.register_alert_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_alert_update(self):
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
            self.register_beneficiary_type_url,
            self.register_beneficiary_type_data,
            format="json",
        )
        type = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.register_beneficiary_data["type_id"] = type["id"]
        response = self.client.post(
            self.beneficiaries_url,
            self.register_beneficiary_data,
            format="json",
        )
        beneficiary = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(beneficiary["type_id"], type["id"])

        response = self.client.post(
            self.register_alert_url,
            self.register_alert_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        alert = json.loads(response.content)

        update_alert_url = reverse("alerts:alert-detail", kwargs={"pk": alert["id"]})
        response = self.client.patch(
            update_alert_url,
            self.update_alert_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            update_alert_url,
            self.update_alert_data1,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            update_alert_url,
            self.update_alert_data2,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(
            update_alert_url,
            self.update_alert_data3,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.register_alert_type_url, self.register_alert_type_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        type = json.loads(response.content)

        response = self.client.patch(
            update_alert_url,
            {"type_id": type["id"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_alert_url = reverse("alerts:alert-detail", kwargs={"pk": alert["id"]})
        response = self.client.get(
            get_alert_url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        alert = json.loads(response.content)

        self.assertEqual(alert["state"], "C")
        self.assertIsNotNone(alert["datetime_closed"])
        self.assertIsNotNone(alert["type_id"])


class TestTwilioWebhook(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    def setUp(self):
        self.twilio_webhook_url = reverse("alerts:twilio-webhook")
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
        self.register_beneficiary_data = {
            "name": "John",
            "surname": "Smith",
            "telephone": "1154047987",
            "company": "CLA",
            "description": "Prueba de beneficiario",
            "enabled": True,
        }

        self.twilio_sms_data = {
            "From": 1154047987,
            "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "Body": "https://maps.google.com/?q=-34.75755778740859,-58.28999854451876",
            "NumMedia": 0,
        }

    def test_twilio_sms_webhook(self):
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

        settings.DEBUG = False
        response = self.client.post(
            self.twilio_webhook_url,
            urlencode(self.twilio_sms_data),
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        alerts = Alert.objects.all()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(
            alerts[0].beneficiary.telephone, self.register_beneficiary_data["telephone"]
        )


class TestAlertChannels(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_manager = UserManager()

    @classmethod
    def setUpTestData(cls):
        register_root_url = reverse("users:register-admin")
        random_password = "".join(
            random.choice(string.ascii_letters) for i in range(10)
        )

        register_root_user_data = {
            "name": "John",
            "surname": "Smith",
            "email": "test_user@email.com",
            "organization_name": "CEIoT",
            "password": random_password,
            "password2": random_password,
        }

        c = Client()

        c.post(register_root_url, register_root_user_data, format="json")

    def setUp(self):
        self.update_alert_data = {"state": "A"}
        self.register_alert_data = {
            "latitude": "-34.757884",
            "longitude": "-58.2927029",
            "telephone": "1154047987",
        }
        self.user = User.objects.all()[0]
        self.organization_id = self.user.organization.id
        return super().setUp()

    async def test_alert_consumer_connect(self):
        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns),
            f"/ws/alerts/organization-{self.organization_id}/",
        )
        communicator.scope["user"] = self.user
        connected, subprotocol = await communicator.connect()
        assert connected

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "1",
            {
                "type": "alert_message",
                "message": self.register_alert_data,
            },
        )

        response = await communicator.receive_from()
        assert json.loads(response) == self.register_alert_data
        # Close
        await communicator.disconnect()

        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns),
            f"/ws/alerts/organization-{self.organization_id + 1}/",
        )
        communicator.scope["user"] = self.user
        connected, subprotocol = await communicator.connect()
        assert not connected
        # Close
        await communicator.disconnect()
