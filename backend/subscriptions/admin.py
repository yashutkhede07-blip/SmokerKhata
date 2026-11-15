from django.contrib import admin, messages
from django.utils.html import format_html
from subscriptions.models import Plan, FeatureFlag, Subscription, SubscriptionEvent, SubscriptionStatus
from subscriptions.services import SubscriptionService


class FeatureFlagInline(admin.TabularInline):
    model = FeatureFlag
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'interval', 'price_display', 'is_active', 'created_at')
    list_filter = ('interval', 'is_active')
    inlines = [FeatureFlagInline]

    def price_display(self, obj):
        return f"₹{obj.price_paise / 100:.2f}"
    price_display.short_description = "Price (INR)"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('shop', 'plan', 'status_badge', 'trial_end', 'current_period_end', 'mrr_display')
    list_filter = ('status', 'plan')
    search_fields = ('shop__name', 'shop__prefix', 'razorpay_subscription_id')
    actions = ['extend_trial_7_days']

    def status_badge(self, obj):
        colors = {
            SubscriptionStatus.ACTIVE: 'green',
            SubscriptionStatus.TRIAL: 'blue',
            SubscriptionStatus.GRACE: 'orange',
            SubscriptionStatus.EXPIRED: 'red',
            SubscriptionStatus.CANCELLED: 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.status}</span>')
    status_badge.short_description = "Status"

    def mrr_display(self, obj):
        if obj.status == SubscriptionStatus.ACTIVE and obj.plan:
            if obj.plan.interval == 'YEARLY':
                mrr = (obj.plan.price_paise / 100) / 12
            elif obj.plan.interval == 'QUARTERLY':
                mrr = (obj.plan.price_paise / 100) / 3
            else:
                mrr = obj.plan.price_paise / 100
            return f"₹{mrr:.2f}"
        return "₹0.00"
    mrr_display.short_description = "MRR"

    def extend_trial_7_days(self, request, queryset):
        for sub in queryset:
            SubscriptionService.extend_trial(
                subscription=sub,
                extra_days=7,
                admin_user=request.user,
                reason="Admin manual 7-day trial extension"
            )
        self.message_user(request, f"Extended trial by 7 days for {queryset.count()} subscriptions.", messages.SUCCESS)
    extend_trial_7_days.short_description = "Extend trial by 7 days (logged to audit)"


@admin.register(SubscriptionEvent)
class SubscriptionEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'provider', 'processed', 'created_at', 'processed_at')
    list_filter = ('provider', 'processed')
    readonly_fields = ('event_id', 'provider', 'raw_payload', 'created_at', 'processed_at')
