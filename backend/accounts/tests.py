from unittest.mock import patch

from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.test import APIClient


class AdminLoginTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("accounts.views.generate_tokens_for_user", return_value={"access": "access", "refresh": "refresh"})
    @patch("accounts.views.bcrypt.checkpw", return_value=True)
    @patch("accounts.views.db")
    def test_admin_can_use_admin_login(self, database, check_password, generate_tokens):
        database.users.find_one.return_value = {
            "_id": ObjectId(),
            "name": "Site Admin",
            "email": "admin@example.com",
            "password_hash": "hashed-password",
            "role": "admin",
            "is_active": True,
        }

        response = self.client.post(
            "/api/auth/admin-login/",
            {"email": "ADMIN@example.com", "password": "secure-password"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )
        self.assertEqual(response.data["user"]["role"], "admin")
        generate_tokens.assert_called_once()

    @patch("accounts.views.generate_tokens_for_user")
    @patch("accounts.views.bcrypt.checkpw", return_value=True)
    @patch("accounts.views.db")
    def test_non_admin_cannot_use_admin_login(self, database, check_password, generate_tokens):
        database.users.find_one.return_value = {
            "_id": ObjectId(),
            "name": "Customer",
            "email": "customer@example.com",
            "password_hash": "hashed-password",
            "role": "customer",
            "is_active": True,
        }

        response = self.client.post(
            "/api/auth/admin-login/",
            {"email": "customer@example.com", "password": "secure-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 403, response.data)
        generate_tokens.assert_not_called()

    @patch("accounts.views.db")
    def test_public_registration_rejects_admin_role(self, database):
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Attacker",
                "email": "admin@example.com",
                "password": "secure-password",
                "phone": "9876543210",
                "role": "admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        database.users.find_one.assert_not_called()
