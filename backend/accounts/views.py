import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import User, OTP, TokenBlocklist, ActiveSession
from accounts.serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer, ActiveSessionSerializer
from accounts.sms import get_sms_backend
from accounts.authentication import generate_tokens_for_user, decode_token

OTP_RATE_LIMIT_SECONDS = 600
OTP_RATE_LIMIT_MAX_ATTEMPTS = 5

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        # Enforce rate limit via database cache
        cache_key = f"otp_ratelimit_{phone}"
        attempt_count = cache.get(cache_key, 0)
        if attempt_count >= OTP_RATE_LIMIT_MAX_ATTEMPTS:
            return Response(
                {'error': 'Too many OTP requests. Please wait 10 minutes.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate 6-digit numeric OTP
        code = f"{secrets.randbelow(900000) + 100000:06d}"
        expires_at = timezone.now() + timedelta(minutes=5)

        OTP.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at
        )

        # Send via configured backend
        sms_backend = get_sms_backend()
        sms_backend.send_otp(phone, code)

        cache.set(cache_key, attempt_count + 1, timeout=OTP_RATE_LIMIT_SECONDS)

        return Response({
            'message': 'OTP sent successfully.',
            'phone': phone,
            'expires_in_seconds': 300
        }, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        device_id = serializer.validated_data.get('device_id', '')
        device_name = serializer.validated_data.get('device_name', '')

        # Look for latest active OTP record
        otp_record = OTP.objects.filter(phone=phone, is_verified=False).order_by('-created_at').first()

        if not otp_record or otp_record.is_expired:
            return Response({'error': 'OTP has expired or is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.is_locked:
            return Response({'error': 'Maximum attempts exceeded. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.code != code:
            otp_record.attempts_count += 1
            otp_record.save(update_fields=['attempts_count'])
            remaining = max(0, 3 - otp_record.attempts_count)
            return Response({
                'error': 'Incorrect OTP.',
                'remaining_attempts': remaining
            }, status=status.HTTP_400_BAD_REQUEST)

        # Success - mark verified
        otp_record.is_verified = True
        otp_record.save(update_fields=['is_verified'])

        # Get or create user
        user, _ = User.objects.get_or_create(phone=phone)

        # Issue JWT tokens
        tokens = generate_tokens_for_user(user, device_id=device_id, device_name=device_name)

        # Record ActiveSession
        ip = request.META.get('REMOTE_ADDR')
        ActiveSession.objects.create(
            user=user,
            device_id=device_id,
            device_name=device_name,
            jti=tokens['access_jti'],
            ip_address=ip
        )

        return Response({
            'tokens': tokens,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        jti = getattr(request, 'auth_jti', None)
        if jti:
            TokenBlocklist.objects.get_or_create(
                jti=jti,
                user=request.user,
                defaults={'expires_at': timezone.now() + timedelta(hours=1)}
            )
            ActiveSession.objects.filter(jti=jti).delete()

        # Invalidate refresh token if provided
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                payload = decode_token(refresh_token)
                ref_jti = payload.get('jti')
                if ref_jti:
                    TokenBlocklist.objects.get_or_create(
                        jti=ref_jti,
                        user=request.user,
                        defaults={'expires_at': timezone.now() + timedelta(days=30)}
                    )
            except Exception:
                pass

        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)

class ActiveSessionsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = ActiveSession.objects.filter(user=request.user).order_by('-last_activity')
        return Response(ActiveSessionSerializer(sessions, many=True).data)

    def delete(self, request):
        """Allows terminating all other active sessions."""
        current_jti = getattr(request, 'auth_jti', None)
        other_sessions = ActiveSession.objects.filter(user=request.user).exclude(jti=current_jti)
        for s in other_sessions:
            TokenBlocklist.objects.get_or_create(
                jti=s.jti,
                user=request.user,
                defaults={'expires_at': timezone.now() + timedelta(hours=1)}
            )
        other_sessions.delete()
        return Response({'message': 'Terminated all other active sessions.'})
