# Phase 7 Research: Subscriptions & Admin Panel

## Architecture & Integration Context

### 1. Requirements Matrix
- **SUBS-01**: 14-day free trial on signup with all features, zero upfront card/payment.
- **SUBS-02 & SUBS-03**: `Plan` model editable in Django admin (Monthly, Quarterly, Yearly), with limits:
  - Max staff members / cashiers
  - Max shops per owner
  - Backup retention days
  - Report / Excel export access
- **SUBS-04 & SUBS-05**: Razorpay Subscriptions integration (web):
  - Webhook endpoint verifying HMAC-SHA256 signature using `X-Razorpay-Signature`.
  - Store raw event payload in `SubscriptionEvent` DB table first.
  - Process idempotently (replaying event has zero duplicate billing periods).
- **SUBS-06**: Google Play Billing purchase verification via server-side verification logic / token handler.
- **SUBS-07 & SUBS-08**: Subscription status enforcement middleware / permission check:
  - Trial active → Full access
  - Subscription active → Full access
  - Expired + within 5 days → Grace period (Full access with banner)
  - Expired > 5 days → Read-only mode (Write endpoints return 403 Forbidden with `read_only_mode` message)
- **SUBS-09**: Never delete expired data; read & export endpoints accessible for 90 days.
- **SUBS-10**: Prorated plan upgrade / downgrade calculations.
- **ADMN-01**: Django Admin for Shop / Subscriptions displaying MRR, active status, churn risk.
- **ADMN-02**: Admin action to extend trial/subscription with mandatory reason logged to `AuditLogEntry`.
- **ADMN-03**: Feature flags per plan configurable in Django admin.

### 2. External API Coverage Gate
- Razorpay Subscriptions API & Webhook (`X-Razorpay-Signature`)
- Google Play Developer API (Android purchase token validation)
- Pluggable mock/test client interfaces so unit tests run deterministically offline without live network dependencies.
