from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parents[2]
APPS_DIR = BASE_DIR / "apps"
IN_K8S = Path("/var/run/secrets/kubernetes.io/serviceaccount").exists()

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "unsafe-dev-secret"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
    CSRF_TRUSTED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
    POSTGRES_HOST=(str, "localhost"),
    POSTGRES_PORT=(int, 5432),
    POSTGRES_DB=(str, "konglomerat"),
    POSTGRES_USER=(str, "postgres"),
    POSTGRES_PASSWORD=(str, ""),
    DB_CONN_MAX_AGE=(int, 60),
    ACCESS_TOKEN_MINUTES=(int, 10),
    REFRESH_TOKEN_DAYS=(int, 7),
    JWT_COOKIE_SECURE=(bool, False),
    JWT_COOKIE_SAMESITE=(str, "Lax"),
    SECURE_SSL_REDIRECT=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
    APP_FORCE_HTTPS=(bool, False),
    SECURE_HSTS_SECONDS=(int, 0),
    SECURE_HSTS_INCLUDE_SUBDOMAINS=(bool, False),
    SECURE_HSTS_PRELOAD=(bool, False),
    REDIS_URL=(str, "redis://localhost:6379/0"),
    USE_S3=(bool, False),
    USE_S3_FOR_STATIC=(bool, False),
    AWS_S3_VERIFY=(bool, True),
    AWS_QUERYSTRING_AUTH=(bool, True),
    AWS_S3_USE_SSL=(bool, True),
)

if not IN_K8S:
    environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

DJANGO_APPS = [
    "daphne",
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "channels",
    "corsheaders",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.users.apps.UsersConfig",
    "apps.companies.apps.CompaniesConfig",
    "apps.catalog.apps.CatalogConfig",
    "apps.content.apps.ContentConfig",
    "apps.commerce.apps.CommerceConfig",
    "apps.support.apps.SupportConfig",
    "apps.innovation.apps.InnovationConfig",
    "apps.communications.apps.CommunicationsConfig",
    "apps.operations.apps.OperationsConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.ai.apps.AiConfig",
]

USE_S3 = env("USE_S3")
if USE_S3:
    THIRD_PARTY_APPS.append("storages")

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"
APP_FORCE_HTTPS = env("APP_FORCE_HTTPS")
REDIS_URL = env("REDIS_URL")

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        "CONN_MAX_AGE": env("DB_CONN_MAX_AGE"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env("ACCESS_TOKEN_MINUTES")),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env("REFRESH_TOKEN_DAYS")),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": SECRET_KEY,
}

JWT_REFRESH_COOKIE_NAME = "kong_refresh"
JWT_COOKIE_SECURE = env("JWT_COOKIE_SECURE")
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Konglomerat API",
    "DESCRIPTION": "Django REST API for Konglomerat platform migration.",
    "VERSION": "0.1.0",
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

if USE_S3:
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="")
    AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default="") or None
    AWS_S3_VERIFY = env("AWS_S3_VERIFY")
    AWS_QUERYSTRING_AUTH = env("AWS_QUERYSTRING_AUTH")
    AWS_S3_USE_SSL = env("AWS_S3_USE_SSL")
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    required = {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "AWS_STORAGE_BUCKET_NAME": AWS_STORAGE_BUCKET_NAME,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise ImproperlyConfigured(f"USE_S3 is enabled but missing env vars: {', '.join(missing)}")

    STORAGES["default"] = {  #type: ignore
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "location": "media",
            "region_name": AWS_S3_REGION_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "verify": AWS_S3_VERIFY,
        },
    }

    if env("USE_S3_FOR_STATIC"):
        AWS_STATIC_BUCKET_NAME = env.str("AWS_STATIC_BUCKET_NAME", default="")
        if not AWS_STATIC_BUCKET_NAME:
            raise ImproperlyConfigured("USE_S3_FOR_STATIC is enabled but AWS_STATIC_BUCKET_NAME is empty")
        STORAGES["staticfiles"] = {    #type: ignore
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STATIC_BUCKET_NAME,
                "location": "static",
                "region_name": AWS_S3_REGION_NAME,
                "endpoint_url": AWS_S3_ENDPOINT_URL,
                "verify": AWS_S3_VERIFY,
            },
        }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

UNFOLD = {
    "SITE_TITLE": "Konglomerat Admin",
    "SITE_HEADER": "Konglomerat",
    "SITE_SUBHEADER": "Platform management",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Accounts & Companies"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Users"), "icon": "person", "link": reverse_lazy("admin:users_user_changelist")},
                    {"title": _("Companies"), "icon": "business", "link": reverse_lazy("admin:companies_company_changelist")},
                    {"title": _("Groups"), "icon": "security", "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
            {
                "title": _("Catalog & Commerce"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Products"), "icon": "inventory_2", "link": reverse_lazy("admin:catalog_product_changelist")},
                    {"title": _("Product Images"), "icon": "image", "link": reverse_lazy("admin:catalog_productimage_changelist")},
                    {"title": _("Orders"), "icon": "shopping_cart", "link": reverse_lazy("admin:commerce_order_changelist")},
                    {"title": _("Favorite Collections"), "icon": "favorite", "link": reverse_lazy("admin:commerce_favoritecollection_changelist")},
                    {"title": _("Favorite Items"), "icon": "bookmark", "link": reverse_lazy("admin:commerce_favoriteitem_changelist")},
                ],
            },
            {
                "title": _("Content & Innovation"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("News Articles"), "icon": "newspaper", "link": reverse_lazy("admin:content_newsarticle_changelist")},
                    {"title": _("News Images"), "icon": "collections", "link": reverse_lazy("admin:content_newsimage_changelist")},
                    {"title": _("R&D Submissions"), "icon": "science", "link": reverse_lazy("admin:innovation_rndsubmission_changelist")},
                ],
            },
            {
                "title": _("Support & Communications"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Complaints"), "icon": "support_agent", "link": reverse_lazy("admin:support_complaint_changelist")},
                    {"title": _("Complaint Attachments"), "icon": "attach_file", "link": reverse_lazy("admin:support_complaintattachment_changelist")},
                    {"title": _("Chat Threads"), "icon": "forum", "link": reverse_lazy("admin:communications_chatthread_changelist")},
                    {"title": _("Chat Messages"), "icon": "chat", "link": reverse_lazy("admin:communications_chatmessage_changelist")},
                    {"title": _("Message Receipts"), "icon": "mark_chat_read", "link": reverse_lazy("admin:communications_messagereceipt_changelist")},
                ],
            },
            {
                "title": _("Operations"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Conferences"), "icon": "event", "link": reverse_lazy("admin:operations_conference_changelist")},
                    {"title": _("Conference Attendance"), "icon": "groups", "link": reverse_lazy("admin:operations_conferenceattendance_changelist")},
                    {"title": _("Management Modules"), "icon": "dashboard_customize", "link": reverse_lazy("admin:operations_managementmodule_changelist")},
                    {"title": _("Reports"), "icon": "bar_chart", "link": reverse_lazy("admin:operations_report_changelist")},
                ],
            },
            {
                "title": _("Notifications & AI"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Notifications"), "icon": "notifications", "link": reverse_lazy("admin:notifications_notification_changelist")},
                    {"title": _("Notification Reads"), "icon": "done_all", "link": reverse_lazy("admin:notifications_notificationread_changelist")},
                    {"title": _("AI Usage"), "icon": "smart_toy", "link": reverse_lazy("admin:ai_aiusage_changelist")},
                    {"title": _("AI Interactions"), "icon": "psychology", "link": reverse_lazy("admin:ai_aiinteraction_changelist")},
                ],
            },
        ],
    },
}
