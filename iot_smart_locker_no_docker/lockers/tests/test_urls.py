import pytest
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_deposit():
    assert reverse("lockers:deposit") == "/lockers/deposit/"
    assert resolve("/lockers/deposit/").view_name == "lockers:deposit"
