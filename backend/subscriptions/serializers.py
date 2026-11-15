from rest_framework import serializers
from subscriptions.models import Plan, Subscription, FeatureFlag


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = ['id', 'name', 'is_enabled']


class PlanSerializer(serializers.ModelSerializer):
    feature_flags = FeatureFlagSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'interval', 'price_paise', 'limits', 'is_active', 'feature_flags']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    is_write_allowed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'shop', 'plan', 'status', 'trial_start', 'trial_end',
            'current_period_start', 'current_period_end', 'grace_end',
            'is_write_allowed'
        ]
