import os
from pathlib import Path
from django.utils import timezone
from accounts.sms.base import BaseSMSBackend

class FileSMSBackend(BaseSMSBackend):
    """
    CI / Headless SMS backend that logs OTP messages to a local file for automated test inspection.
    """
    def __init__(self, log_path=None):
        if log_path:
            self.log_path = Path(log_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
            log_dir = base_dir / 'logs'
            log_dir.mkdir(exist_ok=True)
            self.log_path = log_dir / 'otp.log'

    def send_otp(self, phone: str, code: str) -> bool:
        timestamp = timezone.now().isoformat()
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Phone: {phone} | Code: {code}\n")
        return True
