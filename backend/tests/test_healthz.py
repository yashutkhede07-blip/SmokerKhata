import pytest
from unittest.mock import patch
from django.db import OperationalError

@pytest.mark.django_db
def test_healthz_healthy(client):
    """GET /healthz returns 200 and status ok when DB is operational."""
    response = client.get('/healthz')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['database'] == 'connected'

@pytest.mark.django_db
def test_healthz_db_failure(client):
    """GET /healthz returns 503 and status error when DB raises an OperationalError."""
    with patch('django.db.connection.ensure_connection', side_effect=OperationalError("Database down")):
        response = client.get('/healthz')
        assert response.status_code == 503
        data = response.json()
        assert data['status'] == 'error'
        assert data['database'] == 'unreachable'
        # Crucial: verify no sensitive info leaked
        assert 'Database down' not in str(data)
