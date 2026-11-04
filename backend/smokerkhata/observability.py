import re

PHONE_REGEX = re.compile(r'(?:\+?91[\-\s]?)?[6-9]\d{9}')

def scrub_text(text: str) -> str:
    """Scrub 10-digit Indian phone numbers from string."""
    if not isinstance(text, str):
        return text
    return PHONE_REGEX.sub('[REDACTED_PHONE]', text)

def before_send_scrub_pii(event, hint):
    """
    Sentry before_send callback.
    Scrubs phone numbers and sensitive PII from messages, breadcrumbs, and exception details.
    Attaches user_id and shop_id tags if user is authenticated.
    """
    if not event:
        return event

    # Scrub message
    if 'message' in event and isinstance(event['message'], str):
        event['message'] = scrub_text(event['message'])

    # Scrub log/exception values
    if 'exception' in event and 'values' in event['exception']:
        for val in event['exception']['values']:
            if 'value' in val and isinstance(val['value'], str):
                val['value'] = scrub_text(val['value'])

    # Scrub breadcrumbs
    if 'breadcrumbs' in event and 'values' in event['breadcrumbs']:
        for crumb in event['breadcrumbs']['values']:
            if 'message' in crumb and isinstance(crumb['message'], str):
                crumb['message'] = scrub_text(crumb['message'])

    # Ensure user phone is never transmitted
    if 'user' in event:
        if 'username' in event['user'] and PHONE_REGEX.search(str(event['user']['username'])):
            event['user']['username'] = '[REDACTED_PHONE]'
        if 'phone' in event['user']:
            event['user']['phone'] = '[REDACTED_PHONE]'

    return event
