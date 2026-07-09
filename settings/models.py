from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating
    'create_date_time' and 'update_date_time' fields.
    """
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProfileSettings(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_settings",
    )
    bio = models.TextField(blank=True, default="")

    class Meta:
        db_table = "profile_settings"
        verbose_name = "Profile Settings"
        verbose_name_plural = "Profile Settings"

    def __str__(self):
        return f"ProfileSettings(user_id={self.user_id})"


class SettingsNotification(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    email = models.BooleanField(default=True)
    push = models.BooleanField(default=True)
    marketing = models.BooleanField(default=False)

    class Meta:
        db_table = "settings_notification"
        verbose_name = "Notification Settings"
        verbose_name_plural = "Notification Settings"

    def __str__(self):
        return f"SettingsNotification(user_id={self.user_id})"


class SettingsPrivacy(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="privacy_settings",
    )
    auth_2f = models.BooleanField(default=False)
    data_sharing = models.BooleanField(default=False)
    activity_status = models.BooleanField(default=True)

    class Meta:
        db_table = "settings_privacy"
        verbose_name = "Privacy Settings"
        verbose_name_plural = "Privacy Settings"

    def __str__(self):
        return f"SettingsPrivacy(user_id={self.user_id})"


class AccountLanguage(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_language",
    )
    lang = models.CharField(max_length=10) 

    class Meta:
        db_table = "account_language"
        verbose_name = "Account Language"
        verbose_name_plural = "Account Languages"

    def __str__(self):
        return f"AccountLanguage(user_id={self.user_id}, lang={self.lang})"


class AccountCurrency(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_currency",
    )
    currency = models.CharField(max_length=10)  

    class Meta:
        db_table = "account_currency"
        verbose_name = "Account Currency"
        verbose_name_plural = "Account Currencies"

    def __str__(self):
        return f"AccountCurrency(user_id={self.user_id}, currency={self.currency})"


class AccountTimeZone(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_time_zone",
    )
    time_zone = models.CharField(max_length=64)  # e.g. "Asia/Dhaka"

    class Meta:
        db_table = "account_time_zone"
        verbose_name = "Account Time Zone"
        verbose_name_plural = "Account Time Zones"

    def __str__(self):
        return f"AccountTimeZone(user_id={self.user_id}, time_zone={self.time_zone})"


class Security2FA(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_2fa",
    )
    authenticator_app = models.BooleanField(default=False)
    OTP = models.BooleanField(default=False)
    B_T = models.BooleanField(default=False)  # NOTE: confirm what B_T represents (e.g. Backup Tokens?)

    class Meta:
        db_table = "security_2fa"
        verbose_name = "2FA Security Settings"
        verbose_name_plural = "2FA Security Settings"

    def __str__(self):
        return f"Security2FA(user_id={self.user_id})"