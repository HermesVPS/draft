"""
Django settings for the Outlook Draft Campaign Manager (standalone).

Forked from a generic scaffold; branding renamed to "draft". Auth is
django-allauth (email-only login). Microsoft Graph (Entra) OAuth lives
server-side in the a_campaigns app.
"""

from pathlib import Path

import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=lambda v: [s.strip() for s in v.split(",") if s.strip()]
)

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "_app.apps.CoreConfig",
    "a_account",
    "a_dashboard",
    "a_campaigns",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "_settings.urls"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "_settings.wsgi.application"

# ---------------------------------------------------------------------------
# Database — Postgres when DATABASE_URL is set, else SQLite (dev)
# ---------------------------------------------------------------------------
DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Microsoft Graph (Entra) — server-side OAuth
# ---------------------------------------------------------------------------
MS_GRAPH_CLIENT_ID = config("MS_GRAPH_CLIENT_ID", default="")
MS_GRAPH_CLIENT_SECRET = config("MS_GRAPH_CLIENT_SECRET", default="")
MS_GRAPH_TENANT_ID = config("MS_GRAPH_TENANT_ID", default="")
MS_GRAPH_SCOPES = config(
    "MS_GRAPH_SCOPES",
    default="openid profile email User.Read Mail.ReadWrite Mail.ReadWrite.Shared",
).split()
MS_GRAPH_REDIRECT_PATH = "/microsoft/callback/"

# Fernet key for encrypting Microsoft refresh tokens at rest. Falls back to a
# key derived from SECRET_KEY so a fresh clone still runs (rotate in prod).
TOKEN_ENCRYPTION_KEY = config("TOKEN_ENCRYPTION_KEY", default="")

# ---------------------------------------------------------------------------
# Suppression / unsubscribe sync (shared mailbox)
# ---------------------------------------------------------------------------
SUPPRESSION_MAILBOX = config("SUPPRESSION_MAILBOX", default="support@proactivetraining.com.au")
SUPPRESSION_FOLDER = config("SUPPRESSION_FOLDER", default="UNSUBSCRIBE")

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
UV_LINK_MODE = config("UV_LINK_MODE", default="copy")
