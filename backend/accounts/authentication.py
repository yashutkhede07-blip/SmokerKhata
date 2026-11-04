import jwt
import uuid
from datetime import datetime, timedelta, timezone as dt_timezone
from django.conf import settings
from rest_framework import authentication, exceptions
from accounts.models import User, TokenBlocklist

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'jwt-fallback-key')
JWT_ALGORITHM = 'HS256'

def generate_tokens_for_user(user: User, device_id: str = '', device_name: str = '') -> dict:
    """
    Generates a 1-hour access token and a 30-day rotating refresh token for the user.
    """
    now = datetime.now(dt_timezone.utc)
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())

    access_payload = {
        'token_type': 'access',
        'jti': access_jti,
        'user_id': str(user.id),
        'phone': user.phone,
        'device_id': device_id,
        'exp': int((now + timedelta(hours=1)).timestamp()),
        'iat': int(now.timestamp())
    }

    refresh_payload = {
        'token_type': 'refresh',
        'jti': refresh_jti,
        'user_id': str(user.id),
        'device_id': device_id,
        'exp': int((now + timedelta(days=30)).timestamp()),
        'iat': int(now.timestamp())
    }

    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        'access': access_token,
        'refresh': refresh_token,
        'access_expires_in': 3600,
        'refresh_expires_in': 86400 * 30,
        'access_jti': access_jti,
        'refresh_jti': refresh_jti
    }

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Token has expired.')
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed('Invalid token.')

class JWTAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class validating JWTs against signature, expiration, and database token blocklist.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        raw_token = parts[1]
        payload = decode_token(raw_token)

        if payload.get('token_type') != 'access':
            raise exceptions.AuthenticationFailed('Invalid token type.')

        jti = payload.get('jti')
        if jti and TokenBlocklist.objects.filter(jti=jti).exists():
            raise exceptions.AuthenticationFailed('Token has been revoked.')

        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found.')

        if not user.is_active or user.is_deleted:
            raise exceptions.AuthenticationFailed('User account is disabled.')

        # Attach active token jti to request for potential logout
        request.auth_jti = jti
        return (user, raw_token)
