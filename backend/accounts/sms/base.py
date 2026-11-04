from abc import ABC, abstractmethod

class BaseSMSBackend(ABC):
    """
    Abstract interface for SMS OTP delivery providers.
    """

    @abstractmethod
    def send_otp(self, phone: str, code: str) -> bool:
        """
        Send an OTP code to a 10-digit Indian mobile number.
        Returns True on successful dispatch, False on failure.
        """
        pass
