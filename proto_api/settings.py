import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv
import pymysql

# Load .env
load_dotenv()

# MySQL adapter (if you ever spin up a MySQL URL locally)
pymysql.install_as_MySQLdb()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "replace-me-in-prod")
DEBUG = os.getenv("DEBUG", "False") == "True"

# Hosts
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
ALLOWED_HOSTS = [
    "proto-api-kg9r.onrender.com",
    "localhost",
    "127.0.0.1",
]
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Apps
INSTALLED_APPS = [
    # CORS must come first
    "corsheaders",

    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your domains
    "Domains.Auth",
    "Domains.ManageData",
    "Domains.Onboard",
    "Domains",

    # Utilities
    "django_extensions",
    "explorer",
]

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",             # ← must be at top
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS configuration
CORS_ALLOWED_ORIGINS = [
    "https://proto-ux.netlify.app",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# URL & WSGI
ROOT_URLCONF = "proto_api.urls"
WSGI_APPLICATION = "proto_api.wsgi.application"

# Templates (required for admin & any template rendering)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
    )
}

# Custom user
AUTH_USER_MODEL = "Auth.User"

# Django Explorer (if you actually use it)
EXPLORER_CONNECTIONS = {"default": "default"}
EXPLORER_ALLOW_MUTATIONS = True
EXPLORER_SQL_BLACKLIST = []

# DRF
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "USER_ID_FIELD": "id",
}

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default PK field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# PageSpeed (if someone still calls it)
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")


# Caching & Logging
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "brief": {"format": "%(levelname)s %(name)s | %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "brief"},
    },
    "loggers": {
        "ux_eval": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
