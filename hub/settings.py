"""
Django settings for hub.

Local development uses PostgreSQL username/password authentication.
Azure can use Microsoft Entra managed identity for PostgreSQL by setting
AZURE_POSTGRES_ENTRA=True.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

AZURE_ENTRA_AUTH = os.environ.get("AZURE_ENTRA_AUTH", "False").lower() == "true"
AZURE_POSTGRES_ENTRA = os.environ.get("AZURE_POSTGRES_ENTRA", "False").lower() == "true"


def _lista(nome, predefinito=""):
    """Variabile d'ambiente con valori separati da virgola -> lista."""
    return [x.strip() for x in os.environ.get(nome, predefinito).split(",") if x.strip()]


ALLOWED_HOSTS = _lista("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = _lista("DJANGO_CSRF_TRUSTED_ORIGINS")

# Azure App Service sets WEBSITE_HOSTNAME automatically.
if os.environ.get("WEBSITE_HOSTNAME"):
    hostname = os.environ["WEBSITE_HOSTNAME"]
    if hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(hostname)
    origin = "https://" + hostname
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "confronto",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "hub.wsgi.application"


# PostgreSQL.
# In Azure, hub.db_backend refreshes a Microsoft Entra token whenever Django
# opens a new DB connection. Locally, standard PostgreSQL password auth remains.
DATABASES = {
    "default": {
        "ENGINE": "hub.db_backend" if AZURE_POSTGRES_ENTRA else "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "hub"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "300")),
        "OPTIONS": {"sslmode": os.environ.get("DB_SSLMODE", "prefer")},
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}

# Used only for local development. In Azure, Easy Auth / Microsoft Entra
# authenticates users before requests reach Django.
LOGIN_URL = "/admin/login/"
