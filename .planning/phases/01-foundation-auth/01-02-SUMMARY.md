# Summary: Plan 01-02 — Auth, Phone OTP, JWT Lifecycle & Multi-Shop Roles

## What Was Done
- Implemented pluggable SMS provider interface (`BaseSMSBackend`) with `ConsoleSMSBackend` and `FileSMSBackend`.
- Implemented phone OTP model (`OTP`) with 6-digit numeric codes, 5-minute expiry, and max 3 attempts lock.
- Enforced rate limiting on `/api/auth/otp/send` via database cache (max 5 requests per 10 minutes).
- Implemented custom `User` model using phone number as primary identifier.
- Implemented JWT token generation with 1-hour access token and 30-day rotating refresh token.
- Implemented database token blocklist (`TokenBlocklist`) and active session tracking (`ActiveSession`) enabling immediate token revocation on logout.
- Implemented multi-shop hierarchy (`Shop`, `ShopMember`, `Role`) and DRF permission classes (`IsShopOwner`, `IsShopManagerOrOwner`, `IsShopMember`) restricting cashier privileges.

## Verification Evidence
- `pytest backend/tests/test_otp.py`: 3 passed (send OTP, rate limit 429 after 5 attempts, verify OTP flow with token issuance).
- `pytest backend/tests/test_jwt_auth.py`: 1 passed (JWT authentication, logout blocklist immediate rejection).
- `pytest backend/tests/test_permissions.py`: 1 passed (shop creation, member invite, role assignment).
