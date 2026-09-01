"""
Cargo Management System - Base Settings
"""

import os
from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOW_ALL_ORIGINS=(bool, False),
    LEAFLET_TILE_URL=(
        str,
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    ),
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"), overwrite=False)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-cargo-ms-dev-key-change-in-production")

DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

SITE_ID = 1

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_filters",
    "corsheaders",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "channels",
    "storages",
]

CUSTOM_APPS = [
    "core",
    "accounts",
    "branches",
    "customers",
    "cargo",
    "packages",
    "warehouse",
    "transportation",
    "gps_tracking",
    "delivery",
    "billing",
    "payments",
    "documents",
    "notifications",
    "claims",
    "reports",
    "audit",
    "dashboard",
    "api",
    "ai_intelligence",
    "cross_border",
    "iot_sensors",
    "access_channels",
    "self_service",
    "fleet_intelligence",
    "risk_management",
    "saas_config",
    "webhooks_integration",
    "health_check",
    "public_tracking",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "core.middleware.SuppressViteClientRequestsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.AuditMiddleware",
]

ROOT_URLCONF = "cargo_ms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
        },
    },
]

WSGI_APPLICATION = "cargo_ms.wsgi.application"
ASGI_APPLICATION = "cargo_ms.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="mysql://root:@127.0.0.1:3306/cargo_db",
    ),
}

DATABASES["default"]["ENGINE"] = "django.db.backends.mysql"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Password reset token expiry
# ---------------------------------------------------------------------------

PASSWORD_RESET_TIMEOUT_DAYS = 3

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("sw", "Swahili"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Africa/Dar_es_Salaam"

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------------
# Media files
# ---------------------------------------------------------------------------

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Cache (dev default: locmem)
# ---------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cargo-ms-locmem",
    }
}

# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# ---------------------------------------------------------------------------
# DRF Spectacular (OpenAPI / Swagger)
# ---------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "Cargo Management System API",
    "DESCRIPTION": "API for the Cargo Management System — shipments, tracking, billing, and more.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/",
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_RESPONSE": True,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "DisplayOperationId": True,
    },
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
    },
    "TAGS": [
        {"name": "accounts", "description": "User management & authentication"},
        {"name": "branches", "description": "Branch operations"},
        {"name": "customers", "description": "Customer records"},
        {"name": "cargo", "description": "Cargo & shipment management"},
        {"name": "packages", "description": "Package tracking"},
        {"name": "warehouse", "description": "Warehouse management"},
        {"name": "transportation", "description": "Transport routes & scheduling"},
        {"name": "gps_tracking", "description": "Real-time GPS tracking"},
        {"name": "delivery", "description": "Delivery management"},
        {"name": "billing", "description": "Billing & invoicing"},
        {"name": "payments", "description": "Payment processing"},
        {"name": "documents", "description": "Document management"},
        {"name": "notifications", "description": "Notifications & alerts"},
        {"name": "claims", "description": "Claims management"},
        {"name": "reports", "description": "Reports & analytics"},
        {"name": "audit", "description": "Audit trail"},
        {"name": "dashboard", "description": "Dashboard data"},
        {"name": "ai_intelligence", "description": "AI-powered insights"},
        {"name": "cross_border", "description": "Cross-border logistics"},
        {"name": "iot_sensors", "description": "IoT sensor data"},
        {"name": "access_channels", "description": "Access channel management"},
        {"name": "self_service", "description": "Self-service portal"},
        {"name": "fleet_intelligence", "description": "Fleet analytics & intelligence"},
        {"name": "risk_management", "description": "Risk assessment & mitigation"},
        {"name": "saas_config", "description": "SaaS configuration"},
        {"name": "webhooks_integration", "description": "Webhooks & third-party integrations"},
    ],
}

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=30)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": env("JWT_ISSUER", default="cargo-ms"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_SLIDING_LIFETIME_MINUTES", default=60)),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=env.int("JWT_SLIDING_REFRESH_LIFETIME_DAYS", default=7)),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
}

# ---------------------------------------------------------------------------
# Channels (dev default: in-memory)
# ---------------------------------------------------------------------------

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ---------------------------------------------------------------------------
# WhiteNoise
# ---------------------------------------------------------------------------

WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@cargo-ms.co.tz")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "cargo_ms": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# Leaflet / Maps
# ---------------------------------------------------------------------------

LEAFLET_TILE_URL = env(
    "LEAFLET_TILE_URL",
    default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
)

# ---------------------------------------------------------------------------
# Core app config
# ---------------------------------------------------------------------------

CORE_DEFAULT_CURRENCY = env("CORE_DEFAULT_CURRENCY", default="TZS")
CORE_COMPANY_NAME = env("CORE_COMPANY_NAME", default="Cargo Management System")
CORE_SUPPORT_EMAIL = env("CORE_SUPPORT_EMAIL", default="support@cargo-ms.co.tz")
CORE_TRACKING_URL_BASE = env("CORE_TRACKING_URL_BASE", default="https://track.cargo-ms.co.tz")

# ---------------------------------------------------------------------------
# Accounts app config
# ---------------------------------------------------------------------------

ACCOUNTS_INVITATION_EXPIRY_DAYS = env.int("ACCOUNTS_INVITATION_EXPIRY_DAYS", default=7)
ACCOUNTS_DEFAULT_ROLE = env("ACCOUNTS_DEFAULT_ROLE", default="operator")
ACCOUNTS_ENABLE_2FA = env.bool("ACCOUNTS_ENABLE_2FA", default=False)

# ---------------------------------------------------------------------------
# Branches app config
# ---------------------------------------------------------------------------

BRANCHES_GEOFENCE_DEFAULT_RADIUS = env.int("BRANCHES_GEOFENCE_DEFAULT_RADIUS", default=500)

# ---------------------------------------------------------------------------
# Customers app config
# ---------------------------------------------------------------------------

CUSTOMERS_ENABLE_LOYALTY = env.bool("CUSTOMERS_ENABLE_LOYALTY", default=True)
CUSTOMERS_LOYALTY_POINTS_PER_TZS = env.float("CUSTOMERS_LOYALTY_POINTS_PER_TZS", default=0.001)

# ---------------------------------------------------------------------------
# Cargo app config
# ---------------------------------------------------------------------------

CARGO_MAX_WEIGHT_KG = env.float("CARGO_MAX_WEIGHT_KG", default=5000.0)
CARGO_DEFAULT_CURRENCY = env("CARGO_DEFAULT_CURRENCY", default="TZS")
CARGO_ENABLE_AUTO_PRICING = env.bool("CARGO_ENABLE_AUTO_PRICING", default=True)

# ---------------------------------------------------------------------------
# Packages app config
# ---------------------------------------------------------------------------

PACKAGES_BARCODE_PREFIX = env("PACKAGES_BARCODE_PREFIX", default="CMS")
PACKAGES_ENABLE_QR = env.bool("PACKAGES_ENABLE_QR", default=True)

# ---------------------------------------------------------------------------
# Warehouse app config
# ---------------------------------------------------------------------------

WAREHOUSE_LOW_STOCK_THRESHOLD = env.int("WAREHOUSE_LOW_STOCK_THRESHOLD", default=10)
WAREHOUSE_ENABLE_ZONE_MANAGEMENT = env.bool("WAREHOUSE_ENABLE_ZONE_MANAGEMENT", default=True)

# ---------------------------------------------------------------------------
# Transportation app config
# ---------------------------------------------------------------------------

TRANSPORTATION_FUEL_EFFICIENCY_L_per_100KM = env.float("TRANSPORTATION_FUEL_EFFICIENCY_L_per_100KM", default=35.0)
TRANSPORTATION_DEFAULT_SPEED_KMH = env.int("TRANSPORTATION_DEFAULT_SPEED_KMH", default=80)

# ---------------------------------------------------------------------------
# GPS Tracking app config
# ---------------------------------------------------------------------------

GPS_TRACKING_POLL_INTERVAL_SECONDS = env.int("GPS_TRACKING_POLL_INTERVAL_SECONDS", default=10)
GPS_TRACKING_HISTORY_RETENTION_DAYS = env.int("GPS_TRACKING_HISTORY_RETENTION_DAYS", default=90)

# ---------------------------------------------------------------------------
# Delivery app config
# ---------------------------------------------------------------------------

DELIVERY_MAX_ATTEMPTS = env.int("DELIVERY_MAX_ATTEMPTS", default=3)
DELIVERY_RETRY_HOURS = env.int("DELIVERY_RETRY_HOURS", default=4)
DELIVERY_ENABLE_LIVE_TRACKING = env.bool("DELIVERY_ENABLE_LIVE_TRACKING", default=True)

# ---------------------------------------------------------------------------
# Billing app config
# ---------------------------------------------------------------------------

BILLING_INVOICE_PREFIX = env("BILLING_INVOICE_PREFIX", default="INV-")
BILLING_TAX_RATE_PERCENT = env.float("BILLING_TAX_RATE_PERCENT", default=18.0)
BILLING_CURRENCY = env("BILLING_CURRENCY", default="TZS")

# ---------------------------------------------------------------------------
# Payments app config
# ---------------------------------------------------------------------------

PAYMENTS_ENABLE_MPESA = env.bool("PAYMENTS_ENABLE_MPESA", default=True)
PAYMENTS_ENABLE_TIGOPESA = env.bool("PAYMENTS_ENABLE_TIGOPESA", default=True)
PAYMENTS_ENABLE_AZAMPESA = env.bool("PAYMENTS_ENABLE_AZAMPESA", default=True)
PAYMENTS_ENABLE_BANK_TRANSFER = env.bool("PAYMENTS_ENABLE_BANK_TRANSFER", default=True)
PAYMENTS_ENABLE_CASH = env.bool("PAYMENTS_ENABLE_CASH", default=True)
PAYMENTS_WEBHOOK_SECRET = env("PAYMENTS_WEBHOOK_SECRET", default="")

# ---------------------------------------------------------------------------
# Documents app config
# ---------------------------------------------------------------------------

DOCUMENTS_ALLOWED_EXTENSIONS = env.list(
    "DOCUMENTS_ALLOWED_EXTENSIONS",
    default=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
)
DOCUMENTS_MAX_UPLOAD_SIZE_MB = env.int("DOCUMENTS_MAX_UPLOAD_SIZE_MB", default=25)

# ---------------------------------------------------------------------------
# Notifications app config
# ---------------------------------------------------------------------------

NOTIFICATIONS_ENABLE_SMS = env.bool("NOTIFICATIONS_ENABLE_SMS", default=True)
NOTIFICATIONS_ENABLE_EMAIL = env.bool("NOTIFICATIONS_ENABLE_EMAIL", default=True)
NOTIFICATIONS_ENABLE_PUSH = env.bool("NOTIFICATIONS_ENABLE_PUSH", default=False)
NOTIFICATIONS_ENABLE_WHATSAPP = env.bool("NOTIFICATIONS_ENABLE_WHATSAPP", default=False)
NOTIFICATIONS_SMS_PROVIDER = env("NOTIFICATIONS_SMS_PROVIDER", default="africastalking")
NOTIFICATIONS_AFRICASTALKING_API_KEY = env("NOTIFICATIONS_AFRICASTALKING_API_KEY", default="")
NOTIFICATIONS_AFRICASTALKING_USERNAME = env("NOTIFICATIONS_AFRICASTALKING_USERNAME", default="sandbox")

# ---------------------------------------------------------------------------
# Claims app config
# ---------------------------------------------------------------------------

CLAIMS_DEFAULT_RESOLUTION_DAYS = env.int("CLAIMS_DEFAULT_RESOLUTION_DAYS", default=14)
CLAIMS_ENABLE_AUTO_ESCALATION = env.bool("CLAIMS_ENABLE_AUTO_ESCALATION", default=True)
CLAIMS_ESCALATION_DAYS = env.int("CLAIMS_ESCALATION_DAYS", default=7)

# ---------------------------------------------------------------------------
# Reports app config
# ---------------------------------------------------------------------------

REPORTS_CACHE_TIMEOUT_SECONDS = env.int("REPORTS_CACHE_TIMEOUT_SECONDS", default=300)
REPORTS_DEFAULT_PAGE_SIZE = env.int("REPORTS_DEFAULT_PAGE_SIZE", default=50)

# ---------------------------------------------------------------------------
# Audit app config
# ---------------------------------------------------------------------------

AUDIT_LOG_RETENTION_DAYS = env.int("AUDIT_LOG_RETENTION_DAYS", default=365)
AUDIT_TRACK_USER_ACTIONS = env.bool("AUDIT_TRACK_USER_ACTIONS", default=True)
AUDIT_EXCLUDED_PATHS = env.list(
    "AUDIT_EXCLUDED_PATHS",
    default=["/api/schema/", "/admin/jsi18n/"],
)

# ---------------------------------------------------------------------------
# Dashboard app config
# ---------------------------------------------------------------------------

DASHBOARD_REFRESH_INTERVAL_SECONDS = env.int("DASHBOARD_REFRESH_INTERVAL_SECONDS", default=60)
DASHBOARD_CHART_DATA_POINTS = env.int("DASHBOARD_CHART_DATA_POINTS", default=12)

# ---------------------------------------------------------------------------
# AI Intelligence app config
# ---------------------------------------------------------------------------

AI_INTELLIGENCE_ENABLE_PREDICTIONS = env.bool("AI_INTELLIGENCE_ENABLE_PREDICTIONS", default=True)
AI_INTELLIGENCE_MODEL_PATH = env("AI_INTELLIGENCE_MODEL_PATH", default=str(BASE_DIR / "ai_models"))
AI_INTELLIGENCE_FORECAST_HORIZON_DAYS = env.int("AI_INTELLIGENCE_FORECAST_HORIZON_DAYS", default=30)

# ---------------------------------------------------------------------------
# Cross Border app config
# ---------------------------------------------------------------------------

CROSS_BORDER_DEFAULT_ORIGIN_COUNTRY = env("CROSS_BORDER_DEFAULT_ORIGIN_COUNTRY", default="TZ")
CROSS_BORDER_CUSTOMS_BROKER_API_KEY = env("CROSS_BORDER_CUSTOMS_BROKER_API_KEY", default="")
CROSS_BORDER_ENABLE_DUTY_CALCULATION = env.bool("CROSS_BORDER_ENABLE_DUTY_CALCULATION", default=True)

# ---------------------------------------------------------------------------
# IoT Sensors app config
# ---------------------------------------------------------------------------

IOT_SENSORS_DATA_RETENTION_DAYS = env.int("IOT_SENSORS_DATA_RETENTION_DAYS", default=180)
IOT_SENSORS_ENABLE_TEMPERATURE = env.bool("IOT_SENSORS_ENABLE_TEMPERATURE", default=True)
IOT_SENSORS_ENABLE_HUMIDITY = env.bool("IOT_SENSORS_ENABLE_HUMIDITY", default=True)
IOT_SENSORS_ENABLE_VIBRATION = env.bool("IOT_SENSORS_ENABLE_VIBRATION", default=False)
IOT_SENSORS_TEMPERATURE_ALERT_MIN = env.float("IOT_SENSORS_TEMPERATURE_ALERT_MIN", default=0.0)
IOT_SENSORS_TEMPERATURE_ALERT_MAX = env.float("IOT_SENSORS_TEMPERATURE_ALERT_MAX", default=40.0)

# ---------------------------------------------------------------------------
# Access Channels app config
# ---------------------------------------------------------------------------

ACCESS_CHANNELS_ENABLE_USSD = env.bool("ACCESS_CHANNELS_ENABLE_USSD", default=True)
ACCESS_CHANNELS_ENABLE_SMS_GATEWAY = env.bool("ACCESS_CHANNELS_ENABLE_SMS_GATEWAY", default=True)
ACCESS_CHANNELS_ENABLE_WEB_PORTAL = env.bool("ACCESS_CHANNELS_ENABLE_WEB_PORTAL", default=True)
ACCESS_CHANNELS_USSD_SHORT_CODE = env("ACCESS_CHANNELS_USSD_SHORT_CODE", default="*150*50#")

# ---------------------------------------------------------------------------
# Self Service app config
# ---------------------------------------------------------------------------

SELF_SERVICE_ENABLE_TRACKING = env.bool("SELF_SERVICE_ENABLE_TRACKING", default=True)
SELF_SERVICE_ENABLE_QUOTE_REQUEST = env.bool("SELF_SERVICE_ENABLE_QUOTE_REQUEST", default=True)
SELF_SERVICE_ENABLE_COMPLAINT = env.bool("SELF_SERVICE_ENABLE_COMPLAINT", default=True)
SELF_SERVICE_PORTAL_TITLE = env("SELF_SERVICE_PORTAL_TITLE", default="Cargo MS Self Service")

# ---------------------------------------------------------------------------
# Fleet Intelligence app config
# ---------------------------------------------------------------------------

FLEET_INTELLIGENCE_ENABLE_PREDICTIVE_MAINTENANCE = env.bool(
    "FLEET_INTELLIGENCE_ENABLE_PREDICTIVE_MAINTENANCE", default=True
)
FLEET_INTELLIGENCE_FUEL_ALERT_THRESHOLD_PERCENT = env.float(
    "FLEET_INTELLIGENCE_FUEL_ALERT_THRESHOLD_PERCENT", default=15.0
)
FLEET_INTELLIGENCE_TIRE_PRESSURE_MIN_PSI = env.float("FLEET_INTELLIGENCE_TIRE_PRESSURE_MIN_PSI", default=80.0)
FLEET_INTELLIGENCE_TIRE_PRESSURE_MAX_PSI = env.float("FLEET_INTELLIGENCE_TIRE_PRESSURE_MAX_PSI", default=120.0)

# ---------------------------------------------------------------------------
# Risk Management app config
# ---------------------------------------------------------------------------

RISK_MANAGEMENT_ENABLE_AUTO_SCORING = env.bool("RISK_MANAGEMENT_ENABLE_AUTO_SCORING", default=True)
RISK_MANAGEMENT_HIGH_RISK_THRESHOLD = env.float("RISK_MANAGEMENT_HIGH_RISK_THRESHOLD", default=0.7)
RISK_MANAGEMENT_REVIEW_INTERVAL_DAYS = env.int("RISK_MANAGEMENT_REVIEW_INTERVAL_DAYS", default=30)

# ---------------------------------------------------------------------------
# SaaS Config app config
# ---------------------------------------------------------------------------

SAAS_CONFIG_MULTI_TENANT = env.bool("SAAS_CONFIG_MULTI_TENANT", default=False)
SAAS_CONFIG_DEFAULT_TENANT = env("SAAS_CONFIG_DEFAULT_TENANT", default="default")
SAAS_CONFIG_PLAN_FEATURES = env.dict("SAAS_CONFIG_PLAN_FEATURES", default={})

# ---------------------------------------------------------------------------
# Webhooks Integration app config
# ---------------------------------------------------------------------------

WEBHOOKS_INTEGRATION_DEFAULT_TIMEOUT = env.int("WEBHOOKS_INTEGRATION_DEFAULT_TIMEOUT", default=10)
WEBHOOKS_INTEGRATION_MAX_RETRIES = env.int("WEBHOOKS_INTEGRATION_MAX_RETRIES", default=3)
WEBHOOKS_INTEGRATION_ENABLE_LOGGING = env.bool("WEBHOOKS_INTEGRATION_ENABLE_LOGGING", default=True)
WEBHOOKS_INTEGRATION_HMAC_SECRET = env("WEBHOOKS_INTEGRATION_HMAC_SECRET", default="")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 30
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 25
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_ROUTES = {
    "notifications.tasks.*": {"queue": "notifications"},
    "delivery.tasks.*": {"queue": "delivery"},
    "reports.tasks.*": {"queue": "reports"},
    "billing.tasks.*": {"queue": "billing"},
    "gps_tracking.tasks.*": {"queue": "gps"},
    "ai_intelligence.tasks.*": {"queue": "ai"},
    "iot_sensors.tasks.*": {"queue": "iot"},
    "webhooks_integration.tasks.*": {"queue": "webhooks"},
}

# ---------------------------------------------------------------------------
# Django Filter
# ---------------------------------------------------------------------------

FILTERS_DEFAULT_LOOKUP_EXPR = "exact"
