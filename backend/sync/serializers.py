from rest_framework import serializers


class SyncOperationItemSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=255)
    entity_type = serializers.CharField(max_length=50)
    entity_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['CREATE', 'UPDATE', 'DELETE'])
    data = serializers.DictField(required=False, default=dict)
    timestamp = serializers.DateTimeField(required=False)


class SyncPushSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=50, required=False, default='COUNTER1')
    operations = SyncOperationItemSerializer(many=True)

    def validate_operations(self, value):
        if not value:
            raise serializers.ValidationError("At least one operation is required.")
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 operations per batch.")
        # Check for duplicate idempotency keys within the same batch
        keys = [op['idempotency_key'] for op in value]
        if len(keys) != len(set(keys)):
            raise serializers.ValidationError("Duplicate idempotency keys within the batch.")
        return value


class SyncJournalEntrySerializer(serializers.Serializer):
    sequence = serializers.IntegerField()
    entity_type = serializers.CharField()
    entity_id = serializers.UUIDField()
    action = serializers.CharField()
    payload = serializers.DictField()
    created_at = serializers.DateTimeField()
