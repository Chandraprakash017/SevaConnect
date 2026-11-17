"""Create an administrator account without exposing credentials in shell history."""

import getpass

import bcrypt
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from common.db import db


class Command(BaseCommand):
    help = "Create a SevaConnect administrator account."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email address for the new administrator")

    def handle(self, *args, **options):
        if db is None:
            raise CommandError("MongoDB is unavailable; administrator was not created.")

        email = options["email"].strip().lower()
        if not email or "@" not in email:
            raise CommandError("Enter a valid email address.")
        if db.users.find_one({"email": email}):
            raise CommandError(f"An account with {email} already exists.")

        name = input("Administrator name: ").strip()
        phone = input("Phone number: ").strip()
        password = getpass.getpass("Password (minimum 12 characters): ")
        confirmation = getpass.getpass("Confirm password: ")

        if not name or not phone:
            raise CommandError("Name and phone number are required.")
        if len(password) < 12:
            raise CommandError("Administrator passwords must be at least 12 characters.")
        if password != confirmation:
            raise CommandError("Passwords do not match.")

        db.users.insert_one({
            "name": name,
            "email": email,
            "password_hash": bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            "phone": phone,
            "role": "admin",
            "is_active": True,
            "created_at": timezone.now(),
        })
        self.stdout.write(self.style.SUCCESS(f"Administrator account created for {email}."))
