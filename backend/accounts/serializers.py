import re
from rest_framework import serializers
from accounts.models import User, OTP, ActiveSession

INDIAN_PHONE_REGEX = re.compile(r'^[6-9]\d{9}$')

def clean_phone_number(phone: str) -> str:
    cleaned = re.sub(r'[\s\-\(\)\+]', '', str(phone).strip())
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not INDIAN_PHONE_REGEX.match(cleaned):
        raise serializers.ValidationError('Phone number must be a valid 10-digit Indian mobile number.')
    return cleaned

class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        return clean_phone_number(value)

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6, min_length=6)
    device_id = serializers.CharField(max_length=128, required=False, default='')
    device_name = serializers.CharField(max_length=128, required=False, default='')

    def validate_phone(self, value):
        return clean_phone_number(value)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'full_name', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

class ActiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveSession
        fields = ('id', 'device_id', 'device_name', 'ip_address', 'last_activity')
