from django.conf import settings
from common.models import UUIDModel, TimeStampedModel, SoftDeleteModel, ShopScopedModel

def test_production_security_settings():
    """Verify security configurations for production readiness."""
    assert hasattr(settings, 'SECRET_KEY')
    assert hasattr(settings, 'CACHES')
    assert settings.CACHES['default']['BACKEND'] == 'django.core.cache.backends.db.DatabaseCache'
    assert hasattr(settings, 'Q_CLUSTER')
    assert settings.Q_CLUSTER['orm'] == 'default'

def test_common_abstract_models_exist():
    """Verify that common models exist and have correct abstract meta."""
    assert UUIDModel._meta.abstract is True
    assert TimeStampedModel._meta.abstract is True
    assert SoftDeleteModel._meta.abstract is True
    assert ShopScopedModel._meta.abstract is True
