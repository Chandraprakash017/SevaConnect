from types import SimpleNamespace
from unittest.mock import Mock, patch

from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.test import APIClient


class VerifyTechnicianTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            user=SimpleNamespace(is_authenticated=True, role="admin")
        )
        self.tech_id = str(ObjectId())

    @patch("technicians.views.db")
    def test_verification_requires_a_boolean(self, database):
        response = self.client.put(
            f"/api/technicians/{self.tech_id}/verify/",
            {"is_verified": "false"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        database.technicians.update_one.assert_not_called()

    @patch("technicians.views.db")
    def test_admin_can_verify_technician(self, database):
        database.technicians.update_one.return_value = Mock(matched_count=1)

        response = self.client.put(
            f"/api/technicians/{self.tech_id}/verify/",
            {"is_verified": True},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        database.technicians.update_one.assert_called_once_with(
            {"_id": ObjectId(self.tech_id)},
            {"$set": {"is_verified": True}},
        )
