import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """Provides a fresh unauthenticated DRF API client."""
    return APIClient()

@pytest.fixture
def db_access(db):
    """Convenience fixture ensuring database access for tests."""
    return db
