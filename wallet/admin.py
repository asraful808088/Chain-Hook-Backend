from django.contrib import admin

from .models import (
    Wallet,
    UserCurrency,
    PremiumCard,
    StandardCard,
    VirtualCard,
    CurrencyPriceHistory,
    Transaction,
)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "USD", "EUR", "JPY", "GBP", "preferred_currency", "is_active", "update_date_time")
    list_filter = ("preferred_currency", "is_active")
    search_fields = ("user__email",)
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(UserCurrency)
class UserCurrencyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "USD", "EUR", "JPY", "GBP", "max_lmt", "use_lmt", "payment_address", "update_date_time")
    search_fields = ("user__email", "payment_address")
    
    readonly_fields = ("payment_address", "create_date_time", "update_date_time")


class BaseCardAdmin(admin.ModelAdmin):
    """Shared admin config for all three card types."""
    list_display = ("id", "user_currency", "masked_number", "exp", "is_active", "update_date_time")
    list_filter = ("is_active",)
    search_fields = ("user_currency__user__email",)
    readonly_fields = ("create_date_time", "update_date_time")
    # CVC intentionally excluded from list_display / left out of readonly
    # so it's not casually visible while browsing the admin list view.

    def masked_number(self, obj):
        if obj.number and len(obj.number) >= 4:
            return f"**** **** **** {obj.number[-4:]}"
        return "****"
    masked_number.short_description = "Card Number"


@admin.register(PremiumCard)
class PremiumCardAdmin(BaseCardAdmin):
    pass


@admin.register(StandardCard)
class StandardCardAdmin(BaseCardAdmin):
    pass


@admin.register(VirtualCard)
class VirtualCardAdmin(BaseCardAdmin):
    pass


@admin.register(CurrencyPriceHistory)
class CurrencyPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "USD", "EUR", "JPY", "GBP", "create_date_time")
    readonly_fields = ("create_date_time", "update_date_time")
    ordering = ("-create_date_time",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "entity", "method", "status", "amount", "transaction_date")
    list_filter = ("status", "method")
    search_fields = ("user__email", "entity")
    readonly_fields = ("create_date_time", "update_date_time")
    date_hierarchy = "transaction_date"