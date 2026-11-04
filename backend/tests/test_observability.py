import pytest
from smokerkhata.observability import scrub_text, before_send_scrub_pii

def test_scrub_text_indian_phone_numbers():
    assert scrub_text("User with phone 9876543210 failed login") == "User with phone [REDACTED_PHONE] failed login"
    assert scrub_text("+919876543210 error occurred") == "[REDACTED_PHONE] error occurred"
    assert scrub_text("Normal text without number") == "Normal text without number"

def test_before_send_scrub_pii():
    event = {
        'message': 'Failed OTP verification for 9876543210',
        'exception': {
            'values': [{'value': 'Invalid attempt on +919876543210'}]
        },
        'breadcrumbs': {
            'values': [{'message': 'Sent SMS to 9876543210'}]
        },
        'user': {
            'id': 'user-uuid-123',
            'username': '9876543210',
            'phone': '9876543210'
        }
    }

    cleaned = before_send_scrub_pii(event, None)
    assert '[REDACTED_PHONE]' in cleaned['message']
    assert '9876543210' not in cleaned['message']
    assert '[REDACTED_PHONE]' in cleaned['exception']['values'][0]['value']
    assert '[REDACTED_PHONE]' in cleaned['breadcrumbs']['values'][0]['message']
    assert cleaned['user']['username'] == '[REDACTED_PHONE]'
    assert cleaned['user']['phone'] == '[REDACTED_PHONE]'
    assert cleaned['user']['id'] == 'user-uuid-123'
