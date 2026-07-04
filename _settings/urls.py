from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("a_account.urls")),
    path("", lambda request: redirect("account:login"), name="home"),
    path("account/", include("allauth.account.urls")),

]
