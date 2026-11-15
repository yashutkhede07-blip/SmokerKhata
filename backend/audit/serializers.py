from rest_framework import serializers
from audit.models import AuditLogEntry


class AuditLogEntrySerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = AuditLogEntry
        fields = [
            'id', 'shop', 'user', 'user_phone', 'model_name',
            'record_id', 'action', 'old_values', 'new_values',
            'notes', 'created_at'
        ]
        read_only_fields = fields
