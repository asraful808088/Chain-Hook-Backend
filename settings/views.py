from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ProfileSettings,
    SettingsNotification,
    SettingsPrivacy,
    AccountLanguage,
    AccountCurrency,
    AccountTimeZone,
    Security2FA,
)
from .serializers import (
    ProfileSettingsSerializer,
    SettingsNotificationSerializer,
    SettingsPrivacySerializer,
    AccountLanguageSerializer,
    AccountCurrencySerializer,
    AccountTimeZoneSerializer,
    Security2FASerializer,
)


class AllSettingsView(APIView):
    """
    GET /settings/

    Returns every settings section for the logged-in user in a single
    response. Any section the user hasn't created yet comes back as null
    instead of raising an error.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Each of these is a OneToOneField, so accessing the reverse
        # relation either returns the instance or raises the model's own
        # DoesNotExist exception if the user hasn't set it up yet.
        data = {}

        try:
            data["profile"] = ProfileSettingsSerializer(user.profile_settings).data
        except ProfileSettings.DoesNotExist:
            data["profile"] = None

        try:
            data["notifications"] = SettingsNotificationSerializer(user.notification_settings).data
        except SettingsNotification.DoesNotExist:
            data["notifications"] = None

        try:
            data["privacy"] = SettingsPrivacySerializer(user.privacy_settings).data
        except SettingsPrivacy.DoesNotExist:
            data["privacy"] = None

        try:
            data["language"] = AccountLanguageSerializer(user.account_language).data
        except AccountLanguage.DoesNotExist:
            data["language"] = None

        try:
            data["currency"] = AccountCurrencySerializer(user.account_currency).data
        except AccountCurrency.DoesNotExist:
            data["currency"] = None

        try:
            data["time_zone"] = AccountTimeZoneSerializer(user.account_time_zone).data
        except AccountTimeZone.DoesNotExist:
            data["time_zone"] = None

        try:
            data["security_2fa"] = Security2FASerializer(user.security_2fa).data
        except Security2FA.DoesNotExist:
            data["security_2fa"] = None

        return Response(data)

    # Maps the JSON key the client sends -> (model class, serializer class)
    SECTION_MAP = {
        "profile": (ProfileSettings, ProfileSettingsSerializer),
        "notifications": (SettingsNotification, SettingsNotificationSerializer),
        "privacy": (SettingsPrivacy, SettingsPrivacySerializer),
        "language": (AccountLanguage, AccountLanguageSerializer),
        "currency": (AccountCurrency, AccountCurrencySerializer),
        "time_zone": (AccountTimeZone, AccountTimeZoneSerializer),
        "security_2fa": (Security2FA, Security2FASerializer),
    }

    def patch(self, request):
        """
        PATCH /settings/

        Body can include any combination of section keys, e.g.:
        {
          "notifications": {"push": false},
          "privacy": {"auth_2f": true},
          "language": {"lang": "bn"}
        }

        Only the sections included in the body are touched. Each section
        is created for the user on first use (get_or_create), then
        partially updated with the fields you sent.
        """
        user = request.user
        result = {}
        errors = {}

        for key, payload in request.data.items():
            if key not in self.SECTION_MAP:
                errors[key] = f"Unknown settings section '{key}'."
                continue

            model_cls, serializer_cls = self.SECTION_MAP[key]
            instance, _ = model_cls.objects.get_or_create(user=user)
            serializer = serializer_cls(instance, data=payload, partial=True)

            if serializer.is_valid():
                serializer.save()
                result[key] = serializer.data
            else:
                errors[key] = serializer.errors

        if errors:
            return Response(
                {"updated": result, "errors": errors},
                status=400 if not result else 207,  
            )

        return Response(result)