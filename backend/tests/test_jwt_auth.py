import pytest
from accounts.models import User, TokenBlocklist
from accounts.authentication import generate_tokens_for_user

@pytest.mark.django_db
def test_jwt_authentication_and_blocklist(client):
    user = User.objects.create(phone='9876543220')
    tokens = generate_tokens_for_user(user)
    access_token = tokens['access']

    # Authenticated request to list sessions
    response = client.get('/api/auth/sessions', HTTP_AUTHORIZATION=f'Bearer {access_token}')
    assert response.status_code == 200

    # Logout to blocklist token
    logout_resp = client.post(
        '/api/auth/logout',
        {'refresh': tokens['refresh']},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    assert logout_resp.status_code == 200

    # Token must now be rejected
    rejected_resp = client.get('/api/auth/sessions', HTTP_AUTHORIZATION=f'Bearer {access_token}')
    assert rejected_resp.status_code == 403 or rejected_resp.status_code == 401
