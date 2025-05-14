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

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
            'propagate': False,
        },
    },
}

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
    
    # Proto API itself
    "proto_api.apps.ProtoApiConfig",

    # Utilities
    "django_extensions",
    "explorer",
]

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",             # ← must be at the very top
    "django.middleware.security.SecurityMiddleware",     # Security middleware comes next
    "whitenoise.middleware.WhiteNoiseMiddleware",        # Then whitenoise
    "proto_api.middleware.SqlExplorerMiddleware",        # Custom middleware after Django's security
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = True  # Since you want to allow access from netlify, this might be easier to manage
CORS_ALLOWED_ORIGINS = [
    "https://proto-ux.netlify.app",
    "http://localhost:3000",
    "https://proto-api-kg9r.onrender.com/toolkit/web-metrics",
    "https://proto-api-kg9r.onrender.com/ask-ai/evaluate-ui",
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

# Ensure CORS headers are added to responses
CORS_EXPOSE_HEADERS = [
    "access-control-allow-origin",
    "access-control-allow-credentials",
]

# Add CORS preflight cache for better performance
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# URL & WSGI
ROOT_URLCONF = "proto_api.urls"
WSGI_APPLICATION = "proto_api.wsgi.application"

# Templates (required for admin & any template rendering)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "explorer" / "templates",  # Add SQL Explorer templates
        ],
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
        ssl_require=True,  # Enable SSL for database connections
        engine="django.db.backends.postgresql",  # Explicitly set the engine
    )
}

# Custom user
AUTH_USER_MODEL = "Auth.User"

# SQL Explorer configuration - minimal configuration
EXPLORER_CONNECTIONS = {"default": "default"}
EXPLORER_DEFAULT_CONNECTION = "default"
EXPLORER_ENABLE_TASKS = False   # Disable Celery dependency
EXPLORER_ASYNC_SCHEMA = False   # Disable async operations
EXPLORER_PERMISSION_VIEW = lambda u: True   # Make it accessible to anyone for now
EXPLORER_PERMISSION_CHANGE = lambda u: True   # Make it accessible to anyone for now

# Allow all SQL commands (remove blacklist)
EXPLORER_SQL_BLACKLIST = []  # Empty list means no restrictions

# Simplified explorer settings
EXPLORER_UNSAFE_QUERY_ALERT = True
EXPLORER_UNSAFE_RENDERING = False
EXPLORER_UNSAFE_QUERY_ALERT_MSG = "This query is potentially unsafe"
EXPLORER_UNSAFE_QUERY_ALERT_MSG_LEVEL = "warning"
EXPLORER_SCHEMA_CACHE_ENABLED = True

# DRF
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Remove non-existent directories
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
#     BASE_DIR / "explorer" / "static",  # Add SQL Explorer static files
# ]
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

# Celery Configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', None)
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', None)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
