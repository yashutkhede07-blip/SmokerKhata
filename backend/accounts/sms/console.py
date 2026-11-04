from accounts.sms.base import BaseSMSBackend
import sys

class ConsoleSMSBackend(BaseSMSBackend):
    """
    Development SMS backend that prints OTP codes to stdout.
    """
    def send_otp(self, phone: str, code: str) -> bool:
        sys.stdout.write(f"\n[DEV SMS] To: {phone} | OTP: {code} | Valid for 5 minutes\n")
        sys.stdout.flush()
        return True
