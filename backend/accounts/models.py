import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from common.models import UUIDModel, TimeStampedModel, SoftDeleteModel

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The phone number must be provided')
        phone = phone.strip()
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if password is None:
            raise ValueError('Superusers must have a password')
        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Custom user model indexed by 10-digit Indian phone number.
    """
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    full_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone} ({self.full_name or 'No Name'})"

class OTP(UUIDModel, TimeStampedModel):
    """
    Database-backed phone OTP store with attempt locking and expiration.
    """
    phone = models.CharField(max_length=15, db_index=True)
    code = models.CharField(max_length=6)
    attempts_count = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'created_at']),
        ]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_locked(self):
        return self.attempts_count >= 3

class TokenBlocklist(UUIDModel, TimeStampedModel):
    """
    Database blocklist for revoked JWT jti identifiers.
    """
    jti = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_tokens')
    expires_at = models.DateTimeField(db_index=True)

    def __str__(self):
        return f"Revoked jti:{self.jti} for {self.user.phone}"

class ActiveSession(UUIDModel, TimeStampedModel):
    """
    Tracks active devices and sessions for user/staff members.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_id = models.CharField(max_length=128, blank=True)
    device_name = models.CharField(max_length=128, blank=True)
    jti = models.CharField(max_length=64, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.user.phone} on {self.device_name or 'unknown'}"
