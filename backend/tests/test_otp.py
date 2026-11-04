import pytest
from django.core.cache import cache
from accounts.models import OTP, User

@pytest.mark.django_db
def test_send_otp_success(client):
    cache.clear()
    response = client.post('/api/auth/otp/send', {'phone': '9876543210'}, format='json')
    assert response.status_code == 200
    assert response.json()['phone'] == '9876543210'

    otp = OTP.objects.filter(phone='9876543210').first()
    assert otp is not None
    assert len(otp.code) == 6
    assert not otp.is_expired

@pytest.mark.django_db
def test_send_otp_rate_limiting(client):
    cache.clear()
    phone = '9876543211'
    for _ in range(5):
        resp = client.post('/api/auth/otp/send', {'phone': phone}, format='json')
        assert resp.status_code == 200

    # 6th attempt should be rate-limited
    resp = client.post('/api/auth/otp/send', {'phone': phone}, format='json')
    assert resp.status_code == 429
    assert 'Too many OTP requests' in resp.json()['error']

@pytest.mark.django_db
def test_verify_otp_flow(client):
    cache.clear()
    phone = '9876543212'
    client.post('/api/auth/otp/send', {'phone': phone}, format='json')
    otp = OTP.objects.filter(phone=phone).latest('created_at')

    # Incorrect OTP
    bad_resp = client.post('/api/auth/otp/verify', {'phone': phone, 'code': '000000'}, format='json')
    assert bad_resp.status_code == 400
    assert bad_resp.json()['remaining_attempts'] == 2

    # Correct OTP
    good_resp = client.post('/api/auth/otp/verify', {'phone': phone, 'code': otp.code}, format='json')
    assert good_resp.status_code == 200
    data = good_resp.json()
    assert 'tokens' in data
    assert 'access' in data['tokens']
    assert 'refresh' in data['tokens']
    assert data['user']['phone'] == phone
