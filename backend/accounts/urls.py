from django.urls import path
from accounts.views import SendOTPView, VerifyOTPView, LogoutView, ActiveSessionsListView

app_name = 'accounts'

urlpatterns = [
    path('otp/send', SendOTPView.as_view(), name='otp_send'),
    path('otp/send/', SendOTPView.as_view(), name='otp_send_slash'),
    path('otp/verify', VerifyOTPView.as_view(), name='otp_verify'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp_verify_slash'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('logout/', LogoutView.as_view(), name='logout_slash'),
    path('sessions', ActiveSessionsListView.as_view(), name='sessions_list'),
    path('sessions/', ActiveSessionsListView.as_view(), name='sessions_list_slash'),
]
