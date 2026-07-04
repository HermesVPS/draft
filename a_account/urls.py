from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    CustomSignupView,
    CustomPasswordChangeView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetFromKeyView,
    CustomConfirmEmailView,
    CustomEmailVerificationSentView,
    CustomEmailView,
    UserNameChangeView,
    profile,
    delete_account,
)

app_name = "account"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", CustomSignupView.as_view(), name="signup"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path(
        "password/change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password/reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/key/<uidb36>-<key>/",
        CustomPasswordResetFromKeyView.as_view(),
        name="password_reset_from_key",
    ),
    path("confirm-email/", CustomEmailVerificationSentView.as_view(), name="email_verification_sent"),
    path("confirm-email/<key>/", CustomConfirmEmailView.as_view(), name="confirm_email"),
    path("email/", CustomEmailView.as_view(), name="email"),
    path("profile/", profile, name="profile"),
    path("name/change/", UserNameChangeView.as_view(), name="name_change"),
    path("delete/", delete_account, name="delete"),
]