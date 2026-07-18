import datetime
import os
from pathlib import Path
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = config('DEBUG', default=False, cast=bool)

# SECRET_KEY: a dev-only fallback is allowed in DEBUG, but production must set it
# explicitly (missing key raises at startup instead of silently using a public one).
if DEBUG:
    SECRET_KEY = config('SECRET_KEY', default="django-insecure-dev-only-key-do-not-use-in-production")
else:
    SECRET_KEY = config('SECRET_KEY')


CROSS_ORIGIN_DEVELOPMENT = config('CROSS_ORIGIN_DEVELOPMENT', default=False, cast=bool)

# Headers allowed on cross-origin requests (shared across environments).
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-client-type',
    'ngrok-skip-browser-warning',
]

# Origins trusted for CSRF (env-driven, with a sensible dev default).
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default=(
        'https://localhost,https://127.0.0.1,'
        'http://127.0.0.1:5173,http://localhost:5173,https://localhost:5173,'
        'https://*.ngrok-free.app,https://*.ngrok-free.dev'
    ),
    cast=Csv(),
)

CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    # Local development: allow any host/origin for convenience.
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Production: never use wildcards. Reflecting any origin while allowing
    # credentials lets any site make authenticated requests as a logged-in
    # user, so origins/hosts must come from an explicit allowlist.
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())


# Application definition

INSTALLED_APPS = [
    # unfold packages
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",

    # django packages
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # external packages
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "import_export",
    "corsheaders",
    # "channels",

    # internal apps
    "apps.seeders",
    "apps.user",
    "apps.system_setting",
    "apps.cms",

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.user.middleware.ClientTypeMiddleware",  # Hybrid auth middleware
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# Developer-only tooling — never load in production.
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += [
        "querycount.middleware.QueryCountMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

ROOT_URLCONF = "project.urls"

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

# ASGI_APPLICATION = 'project.asgi.application'
WSGI_APPLICATION = "project.wsgi.application"


# Channels configuration

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [(os.environ.get("REDIS_HOST", "127.0.0.1"), int(os.environ.get("REDIS_PORT", 6379)))],
#         },
#     },
# }

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]



# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Database configuration based on DEBUG mode
if DEBUG:
    # Development: Use SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Production: Use PostgreSQL with environment variables
    DATABASES = {
        "default": {
            "ENGINE": config('DATABASE_ENGINE', default='django.db.backends.postgresql'),
            "NAME": config('DATABASE_NAME', default='django_db'),
            "USER": config('DATABASE_USER', default='django_user'),
            "PASSWORD": config('DATABASE_PASSWORD', default='django_password'),
            "HOST": config('DATABASE_HOST', default='db'),
            "PORT": config('DATABASE_PORT', default='5432'),
        }
    }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# auth user model
AUTH_USER_MODEL = "user.User"


# Rest framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.user.authentication.HybridJWTAuthentication",  # Hybrid auth for Web + Mobile
    ),
    "EXCEPTION_HANDLER": "apps.utils.custom_exception.custom_exception_handler",
    # NOTE: rates are only enforced when the throttle classes are actually
    # registered. Without DEFAULT_THROTTLE_CLASSES the rates below are inert.
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/min",
        "user": "120/min",
        # Scoped rates for sensitive, unauthenticated endpoints.
        "otp": "5/min",
        "login": "10/min",
    },
}


# ============================================
# JWT Settings (Production-Ready)
# ============================================
SIMPLE_JWT = {
    # Token Lifetimes
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=60),  
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=7),  
}




# ============================================
# Cookie SameSite and Secure Configuration
# ============================================
if CROSS_ORIGIN_DEVELOPMENT and DEBUG:
    # Cross-origin dev (e.g. SPA on a different host): cookies must be
    # SameSite=None + Secure to be sent on cross-site XHR.
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Safe default: SameSite=Lax blocks cross-site cookie delivery (mitigates
    # CSRF). Override COOKIE_SAMESITE=None (with HTTPS) only for a genuinely
    # cross-origin deployment. Secure cookies are required outside DEBUG.
    _cookie_samesite = config('COOKIE_SAMESITE', default='Lax')
    SESSION_COOKIE_SAMESITE = _cookie_samesite
    CSRF_COOKIE_SAMESITE = _cookie_samesite
    SESSION_COOKIE_SECURE = config('COOKIE_SECURE', default=not DEBUG, cast=bool)
    CSRF_COOKIE_SECURE = config('COOKIE_SECURE', default=not DEBUG, cast=bool)


# ============================================
# Production TLS/HTTPS hardening
# Opt-in via env so the default (plain-HTTP) setup keeps working; turn these on
# once TLS is terminated in front of the app, otherwise you can get redirect loops.
# ============================================
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)  # e.g. 31536000 (1 year) once on HTTPS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
    # Enable when running behind a reverse proxy / load balancer that sets X-Forwarded-Proto.
    if config('USE_X_FORWARDED_PROTO', default=False, cast=bool):
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



# email settings (credentials must come from the environment — never commit them)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)  # Or 465 if using SSL
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)  # If you use port 587

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)



# internal ips for debug toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# social auth settings (empty default so the project boots without Google configured)
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_SECRET_KEY = config('GOOGLE_SECRET_KEY', default='')


# unfold settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from project import unfold_config
UNFOLD = unfold_config.get_unfold_settings()





# Stripe Settings (empty default so the project boots without Stripe configured)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')