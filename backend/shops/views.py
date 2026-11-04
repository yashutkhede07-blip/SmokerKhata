from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from shops.models import Shop, ShopMember, Role
from shops.serializers import ShopSerializer, ShopMemberSerializer, InviteMemberSerializer
from accounts.models import User
from accounts.permissions import IsShopOwner, IsShopManagerOrOwner, IsShopMember

class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return shops where the user is either the owner or an active member
        return Shop.objects.filter(members__user=self.request.user).distinct()

    def get_permissions(self):
        if self.action in ['destroy', 'invite_member', 'remove_member']:
            return [permissions.IsAuthenticated(), IsShopOwner()]
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsShopManagerOrOwner()]
        return [permissions.IsAuthenticated(), IsShopMember()]

    @action(detail=True, methods=['post'], url_path='members/invite')
    def invite_member(self, request, pk=None):
        shop = self.get_object()
        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        role = serializer.validated_data['role']
        can_edit_past_bills = serializer.validated_data['can_edit_past_bills']
        can_view_reports = serializer.validated_data['can_view_reports']

        user, _ = User.objects.get_or_create(phone=phone)

        member, created = ShopMember.objects.update_or_create(
            shop=shop,
            user=user,
            defaults={
                'role': role,
                'can_edit_past_bills': can_edit_past_bills,
                'can_view_reports': can_view_reports
            }
        )

        return Response(ShopMemberSerializer(member).data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='members')
    def list_members(self, request, pk=None):
        shop = self.get_object()
        members = ShopMember.objects.filter(shop=shop)
        return Response(ShopMemberSerializer(members, many=True).data)

    @action(detail=True, methods=['post'], url_path='members/(?P<member_id>[^/.]+)/remove')
    def remove_member(self, request, pk=None, member_id=None):
        shop = self.get_object()
        member = get_object_or_404(ShopMember, id=member_id, shop=shop)
        if member.role == Role.OWNER and shop.owner == member.user:
            return Response({'error': 'Cannot remove the primary shop owner.'}, status=status.HTTP_400_BAD_REQUEST)
        member.delete()
        return Response({'message': 'Member removed.'}, status=status.HTTP_200_OK)
