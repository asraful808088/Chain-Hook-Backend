from rest_framework import serializers

from .models import (
    ProfileSettings,
    SettingsNotification,
    SettingsPrivacy,
    AccountLanguage,
    AccountCurrency,
    AccountTimeZone,
    Security2FA,
)


class ProfileSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSettings
        fields = ["id", "bio", "create_date_time", "update_date_time"]


class SettingsNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsNotification
        fields = ["id", "email", "push", "marketing", "create_date_time", "update_date_time"]


class SettingsPrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsPrivacy
        fields = ["id", "auth_2f", "data_sharing", "activity_status", "create_date_time", "update_date_time"]


class AccountLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountLanguage
        fields = ["id", "lang", "create_date_time", "update_date_time"]


class AccountCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountCurrency
        fields = ["id", "currency", "create_date_time", "update_date_time"]


class AccountTimeZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountTimeZone
        fields = ["id", "time_zone", "create_date_time", "update_date_time"]


class Security2FASerializer(serializers.ModelSerializer):
    class Meta:
        model = Security2FA
        fields = ["id", "authenticator_app", "OTP", "B_T", "create_date_time", "update_date_time"]