from rest_framework import serializers
from shops.models import Shop, ShopMember, Role
from accounts.models import User
from accounts.serializers import clean_phone_number

class ShopMemberSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = ShopMember
        fields = ('id', 'user', 'user_phone', 'user_name', 'role', 'can_edit_past_bills', 'can_view_reports', 'created_at')
        read_only_fields = ('id', 'created_at')

class ShopSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Shop
        fields = ('id', 'name', 'prefix', 'address', 'currency', 'created_at', 'members_count')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        user = self.context['request'].user
        shop = Shop.objects.create(owner=user, **validated_data)
        ShopMember.objects.create(shop=shop, user=user, role=Role.OWNER)
        return shop

class InviteMemberSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    role = serializers.ChoiceField(choices=[Role.MANAGER, Role.CASHIER])
    can_edit_past_bills = serializers.BooleanField(default=False)
    can_view_reports = serializers.BooleanField(default=False)

    def validate_phone(self, value):
        return clean_phone_number(value)
