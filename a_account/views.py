from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now, timedelta
from django.views.generic.edit import UpdateView
from django_ratelimit.decorators import ratelimit

from a_account.models.profile_models import UserProfile
from a_account.models.tracking_models import SignupAttempt
from a_account.forms import UserNameChangeForm

from core.utils.fingerprint import generate_fingerprint
from core.utils.logging_util import logger

from allauth.account.views import (
    ConfirmEmailView,
    EmailVerificationSentView,
    EmailView,
    LogoutView,
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetFromKeyView,
    SignupView,
)


@login_required
def profile(request):
    """User profile view."""
    request.session["current_view"] = "account:profile"
    return render(request, "account/profile.html")


class CustomLogoutView(LogoutView):
    template_name = "logout.html"


class CustomLoginView(LoginView):
    template_name = "login.html"


@method_decorator(
    ratelimit(key="ip", rate="2/h", method="POST", block=True), name="dispatch"
)
class CustomSignupView(SignupView):
    template_name = "signup.html"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            logger.debug(f"🚨 Rate limited IP: {request.META.get('REMOTE_ADDR')}")
            return HttpResponseForbidden(
                "Too many signup attempts. Please try again later."
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request
        fingerprint = generate_fingerprint(request)
        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")

        recent_attempts = SignupAttempt.objects.filter(
            fingerprint=fingerprint, created_at__gte=now() - timedelta(hours=1)
        ).count()

        if recent_attempts >= 2:
            logger.debug(f"🚫 Too many attempts from fingerprint {fingerprint}")
            return HttpResponseForbidden(
                "Too many signups from this device. Try again later."
            )

        # Log this attempt
        SignupAttempt.objects.create(
            fingerprint=fingerprint, ip_address=ip, user_agent=ua
        )

        response = super().form_valid(form)
        user = self.user

        profile, created = UserProfile.objects.get_or_create(
            user=user, defaults={"credits": 10}
        )
        if created:
            logger.debug(
                f"✅ Created UserProfile with 10 free credits for {user.email}"
            )
        else:
            logger.debug(f"ℹ️ UserProfile already exists for {user.email}")

        return response


class CustomPasswordResetView(PasswordResetView):
    template_name = "password_reset.html"


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "password_change.html"


class CustomConfirmEmailView(ConfirmEmailView):
    template_name = "confirm_email.html"


class CustomEmailVerificationSentView(EmailVerificationSentView):
    template_name = "verification_sent.html"


class CustomEmailView(EmailView):
    template_name = "email.html"

    def post(self, request, *args, **kwargs):
        logger.debug("✅ POST received:")
        logger.debug("POST keys:", list(request.POST.keys()))
        logger.debug("POST data:", request.POST.dict())
        return super().post(request, *args, **kwargs)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "password_reset_done.html"


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = "password_reset_from_key.html"
    reset_url_token = "set-password"  # This is the correct attribute name

    def dispatch(self, request, uidb36, key, **kwargs):
        # Fix the uidb36 parameter by removing any hyphens
        if "-" in uidb36:
            parts = uidb36.split("-")
            uidb36 = parts[0]
            # If there was a hyphen in uidb36, prepend it to key
            key = "-".join(parts[1:]) + "-" + key

        logger.debug(f"FIXED DEBUG: uidb36={uidb36}, key={key}")
        return super().dispatch(
            request, uidb36, key, **kwargs
        )  # This is the correct attribute name


class UserNameChangeView(LoginRequiredMixin, UpdateView):
    """View for updating user's first name and last name."""

    form_class = UserNameChangeForm
    template_name = "name_change.html"
    success_url = reverse_lazy("account:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


@login_required
def delete_account(request):
    """View for deleting a user account."""
    if request.method == "POST":
        user = request.user
        # Log the deletion attempt
        logger.info(f"Account deletion requested for user: {user.email}")

        try:
            # Delete the user (this will cascade to related models like UserProfile)
            user.delete()
            logger.info(f"Account successfully deleted for user: {user.email}")

            # Redirect to home page after successful deletion
            return redirect("home")
        except Exception as e:
            logger.error(f"Error deleting account for {user.email}: {str(e)}")
            # If there's an error, redirect back to profile with an error message
            return redirect("account:profile")

    # If not a POST request, redirect to profile
    return redirect("account:profile")
