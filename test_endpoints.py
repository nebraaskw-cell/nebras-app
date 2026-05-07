"""Test endpoints directly via Django test client."""
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client

client = Client(SERVER_NAME='127.0.0.1')

endpoints = [
    "/api/v1/health/",
    "/api/v1/sessions/sessions/",
    "/api/v1/attendance/records/",
    "/api/v1/circles/enrollments/",
    "/api/v1/notifications/",
    "/api/v1/notifications/unread-count/",
]

for path in endpoints:
    resp = client.get(path)
    print(f"{path} -> {resp.status_code}")
