from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("account:login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("account/", include("a_account.urls")),
    path("account/", include("allauth.account.urls")),
    path("dashboard/", include("a_dashboard.urls")),
    path("campaigns/", include("a_campaigns.urls")),
]
