from django.urls import path

from .views import AllSettingsView

urlpatterns = [
    path("settings/", AllSettingsView.as_view(), name="all-settings"),
]