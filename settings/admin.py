from django.contrib import admin

from .models import (
    ProfileSettings,
    SettingsNotification,
    SettingsPrivacy,
    AccountLanguage,
    AccountCurrency,
    AccountTimeZone,
    Security2FA,
)


@admin.register(ProfileSettings)
class ProfileSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bio", "create_date_time", "update_date_time")
    search_fields = ("user__username", "user__email", "bio")
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(SettingsNotification)
class SettingsNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "email", "push", "marketing", "update_date_time")
    list_filter = ("email", "push", "marketing")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(SettingsPrivacy)
class SettingsPrivacyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "auth_2f", "data_sharing", "activity_status", "update_date_time")
    list_filter = ("auth_2f", "data_sharing", "activity_status")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(AccountLanguage)
class AccountLanguageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lang", "update_date_time")
    search_fields = ("user__username", "user__email", "lang")
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(AccountCurrency)
class AccountCurrencyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "currency", "update_date_time")
    search_fields = ("user__username", "user__email", "currency")
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(AccountTimeZone)
class AccountTimeZoneAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "time_zone", "update_date_time")
    search_fields = ("user__username", "user__email", "time_zone")
    readonly_fields = ("create_date_time", "update_date_time")


@admin.register(Security2FA)
class Security2FAAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "authenticator_app", "OTP", "B_T", "update_date_time")
    list_filter = ("authenticator_app", "OTP", "B_T")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("create_date_time", "update_date_time")