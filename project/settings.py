import datetime
import os
from pathlib import Path
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config('SECRET_KEY', default="django-insecure-_(4sk(m(!$$xxvz)-7!b7ibkz&2sotl0#=hv8+e*_^__qzgs18")

DEBUG = config('DEBUG', default=False, cast=bool)



CROSS_ORIGIN_DEVELOPMENT = config('CROSS_ORIGIN_DEVELOPMENT', default=False, cast=bool)

if DEBUG:
    ALLOWED_HOSTS = ['*']  
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
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
    CSRF_TRUSTED_ORIGINS = [
        'https://localhost',
        'https://127.0.0.1',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5173',
        'https://localhost:5173',
        'https://*.ngrok-free.app',
        'https://*.ngrok-free.dev', 
        "http://172.16.200.94:8000",
        "http://172.16.200.94:9000",
        
    ]

else:
    ALLOWED_HOSTS = ['*']  
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
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
    CSRF_TRUSTED_ORIGINS = [
        'https://localhost',
        'https://127.0.0.1',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5173',
        'https://localhost:5173',
        'https://*.ngrok-free.app',
        'https://*.ngrok-free.dev', 
        "http://172.16.200.94:8000",
        "http://172.16.200.94:9000",
        
    ]


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
    "debug_toolbar",
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

#master user

AUTHENTICATION_BACKENDS = [
    "apps.user.backends.MasterUserBackend",  
    "django.contrib.auth.backends.ModelBackend",
]
MASTER_USER_EMAIL = "rafi.cse.ahmed@gmail.com"



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
}


# ============================================
# JWT Settings (Production-Ready)
# ============================================
SIMPLE_JWT = {
    # Token Lifetimes
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=60),  # 1 hour
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=7),  # 7 days
    "REMEMBER_ME_REFRESH_LIFETIME": datetime.timedelta(days=30),  # 30 days for "Remember Me"
    
    # Token Rotation & Security
    "ROTATE_REFRESH_TOKENS": True,  # Generate new refresh token on refresh
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklist old refresh tokens
    "UPDATE_LAST_LOGIN": False,  # Don't update last_login on token refresh
    
    # Algorithm & Keys
    "ALGORITHM": "HS256",  # Use RS256 with public/private keys for better security in production
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    
    # Token Claims
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    
    # Token Validation
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    
    # Additional Security
    "JTI_CLAIM": "jti",  # Unique token identifier for blacklisting
}


# ============================================
# Hybrid Authentication Security Settings
# ============================================

# User-Agent Binding (prevents token theft across different devices/browsers)
ENABLE_USER_AGENT_BINDING = True  # Set to False if you have issues with mobile apps

# CSRF Protection for Cookie-based Auth (optional, adds extra security for web clients)
ENABLE_CSRF_FOR_COOKIES = False  # Enable in production if needed

# Cookie Settings
ACCESS_TOKEN_COOKIE_MAX_AGE = 3600  # 1 hour in seconds
REFRESH_TOKEN_COOKIE_MAX_AGE = 604800  # 7 days in seconds

# Cookie Domain - Set to None in development to allow all subdomains/IPs
# In production, set to your actual domain (e.g., '.yourdomain.com')
SESSION_COOKIE_DOMAIN = None  # None = defaults to current domain only

# Production Cookie Security (automatically enabled when DEBUG=False)
SESSION_COOKIE_HTTPONLY = True  # XSS protection
CSRF_COOKIE_HTTPONLY = True  # XSS protection

# ============================================
# Cookie SameSite and Secure Configuration
# ============================================
if CROSS_ORIGIN_DEVELOPMENT and DEBUG:

    SESSION_COOKIE_SAMESITE = 'None'  
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True    
    CSRF_COOKIE_SECURE = True

else:
    # SESSION_COOKIE_SAMESITE = 'Lax'   
    # CSRF_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE = True      
    # CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_SAMESITE = 'None'  
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True    
    CSRF_COOKIE_SECURE = True






# email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 587  # Or 465 if using SSL
EMAIL_USE_TLS = True  # If you use port 587

EMAIL_HOST_USER = 'hello@clever-cv.de'
EMAIL_HOST_PASSWORD = 'Poseidon2301!'
DEFAULT_FROM_EMAIL = 'hello@clever-cv.de'



# internal ips for debug toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# social auth settings

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = config('GOOGLE_SECRET_KEY')


# unfold settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from project import unfold_config
UNFOLD = unfold_config.get_unfold_settings()





# Stripe Settings

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET')