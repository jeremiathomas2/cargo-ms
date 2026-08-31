"""
Cargo Management System - Development Settings
"""

from cargo_ms.settings.base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Cache — local memory (no Redis required)
# ---------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cargo-ms-dev-locmem",
    }
}

# ---------------------------------------------------------------------------
# Channel layers — in-memory (no Redis required)
# ---------------------------------------------------------------------------

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ---------------------------------------------------------------------------
# Email — console backend for development
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Django Debug Toolbar (optional, installed separately)
# ---------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F821
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F821
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
    }
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Django Extensions (optional)
# ---------------------------------------------------------------------------

try:
    import django_extensions  # noqa: F401

    INSTALLED_APPS += ["django_extensions"]  # noqa: F821
except ImportError:
    pass

# ---------------------------------------------------------------------------
# CORS — allow all origins in development
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ---------------------------------------------------------------------------
# REST Framework — browsable API enabled in dev
# ---------------------------------------------------------------------------

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F821
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# ---------------------------------------------------------------------------
# Logging — verbose in development
# ---------------------------------------------------------------------------

LOGGING["root"]["level"] = "DEBUG"  # noqa: F821
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F821
LOGGING["loggers"]["cargo_ms"]["level"] = "DEBUG"  # noqa: F821
LOGGING["handlers"]["console"]["formatter"] = "simple"  # noqa: F821

# ---------------------------------------------------------------------------
# WhiteNoise — simplified for dev
# ---------------------------------------------------------------------------

WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False

# ---------------------------------------------------------------------------
# OTP — always allow bypass in development
# ---------------------------------------------------------------------------

ACCOUNTS_ENABLE_2FA = False  # noqa: F821
