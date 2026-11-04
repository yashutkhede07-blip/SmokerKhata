import pytest
from accounts.models import User
from shops.models import Shop, ShopMember, Role
from accounts.authentication import generate_tokens_for_user

@pytest.mark.django_db
def test_shop_creation_and_member_invitation(client):
    owner = User.objects.create(phone='9876543230')
    tokens = generate_tokens_for_user(owner)
    auth_header = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}

    # Create Shop
    create_resp = client.post(
        '/api/shops/',
        {'name': 'Chai & Snacks Corner', 'prefix': 'CSC01'},
        format='json',
        **auth_header
    )
    assert create_resp.status_code == 201
    shop_id = create_resp.json()['id']

    # Invite Cashier
    cashier_phone = '9876543231'
    invite_resp = client.post(
        f'/api/shops/{shop_id}/members/invite/',
        {
            'phone': cashier_phone,
            'role': Role.CASHIER,
            'can_view_reports': False,
            'can_edit_past_bills': False
        },
        format='json',
        **auth_header
    )
    assert invite_resp.status_code in [200, 201]

    # Verify Cashier role in shop
    member = ShopMember.objects.filter(shop_id=shop_id, user__phone=cashier_phone).first()
    assert member is not None
    assert member.role == Role.CASHIER
    assert member.can_view_reports is False
