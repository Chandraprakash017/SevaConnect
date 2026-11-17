from types import SimpleNamespace
from unittest.mock import patch

from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.test import APIClient


class TechnicianLocationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.booking_id = ObjectId()
        self.technician_id = ObjectId()
        self.user_id = ObjectId()
        self.client.force_authenticate(user=SimpleNamespace(
            id=str(self.user_id),
            role="technician",
            is_authenticated=True,
        ))

    @patch("bookings.views.db")
    def test_assigned_technician_can_share_location_while_on_the_way(self, database):
        database.technicians.find_one.return_value = {"_id": self.technician_id}
        database.bookings.find_one.return_value = {
            "_id": self.booking_id,
            "technician_id": self.technician_id,
            "status": "on_way",
        }
        database.bookings.update_one.return_value = SimpleNamespace(matched_count=1)

        response = self.client.post(
            f"/api/bookings/{self.booking_id}/location/",
            {"latitude": 19.076, "longitude": 72.8777, "accuracy_m": 12},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["technician_location"]["latitude"], 19.076)
        update = database.bookings.update_one.call_args.args[1]["$set"]["technician_location"]
        self.assertEqual(update["longitude"], 72.8777)
        self.assertIn("updated_at", update)

    @patch("bookings.views.db")
    def test_invalid_coordinates_are_rejected(self, database):
        response = self.client.post(
            f"/api/bookings/{self.booking_id}/location/",
            {"latitude": 91, "longitude": 72},
            format="json",
        )

        self.assertEqual(response.status_code, 400, response.data)
        database.bookings.find_one.assert_not_called()
        database.bookings.update_one.assert_not_called()

    @patch("bookings.views.db")
    def test_location_is_rejected_outside_on_the_way_status(self, database):
        database.technicians.find_one.return_value = {"_id": self.technician_id}
        database.bookings.find_one.return_value = {
            "_id": self.booking_id,
            "technician_id": self.technician_id,
            "status": "inspection",
        }

        response = self.client.post(
            f"/api/bookings/{self.booking_id}/location/",
            {"latitude": 19.076, "longitude": 72.8777},
            format="json",
        )

        self.assertEqual(response.status_code, 409, response.data)
        database.bookings.update_one.assert_not_called()
