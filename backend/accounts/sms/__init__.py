from django.utils.module_loading import import_string
from django.conf import settings
from accounts.sms.base import BaseSMSBackend

def get_sms_backend() -> BaseSMSBackend:
    """
    Dynamically loads and instantiates the configured SMS provider class.
    """
    backend_class = getattr(settings, 'SMS_BACKEND', 'accounts.sms.console.ConsoleSMSBackend')
    cls = import_string(backend_class)
    return cls()
