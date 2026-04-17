import os
from datetime import timedelta
from pathlib import Path
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(name, default=False):
    v = os.environ.get(name)
    return default if v is None else v.lower() in {'1', 'true', 'yes', 'on'}


def _int(name, default):
    v = os.environ.get(name)
    return default if v is None else int(v)


SECRET_KEY   = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-before-production')
DEBUG        = _bool('DEBUG', True)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    # Internal
    'apps.accounts',
    'apps.events',
    'apps.tickets',
    'apps.payments',
    'apps.organizer',
    'apps.notifications',
    'apps.admin_panel',
    'apps.core',
    'apps.kyc',
    'apps.support',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF     = 'planova.urls'
WSGI_APPLICATION = 'planova.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME',     'hotelmate_db'),
        'USER':     os.environ.get('DB_USER',     'hotelmate'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '123456'),
        'HOST':     os.environ.get('DB_HOST',     'localhost'),
        'PORT':     os.environ.get('DB_PORT',     '5432'),
        'OPTIONS':  {'connect_timeout': 10},
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

STATIC_URL   = '/static/'
STATIC_ROOT  = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL    = '/media/'
MEDIA_ROOT   = BASE_DIR / 'media'

# ─── Security ───────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE    = _bool('SESSION_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_HTTPONLY  = True
CSRF_COOKIE_SECURE       = _bool('CSRF_COOKIE_SECURE',    not DEBUG)
CSRF_COOKIE_HTTPONLY     = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY      = 'same-origin'
X_FRAME_OPTIONS             = 'DENY'

if not DEBUG:
    SECURE_HSTS_SECONDS             = _int('SECURE_HSTS_SECONDS', 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = _bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD             = _bool('SECURE_HSTS_PRELOAD', True)
    SECURE_SSL_REDIRECT             = _bool('SECURE_SSL_REDIRECT', True)

# ─── CORS (secure by default) ────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS   = [
    os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
] if not DEBUG else []

# ─── DRF ────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS':      'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS':   [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

# ─── JWT ────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':     timedelta(minutes=_int('JWT_ACCESS_TOKEN_MINUTES', 15)),
    'REFRESH_TOKEN_LIFETIME':    timedelta(days=_int('JWT_REFRESH_TOKEN_DAYS', 7)),
    'ROTATE_REFRESH_TOKENS':     _bool('JWT_ROTATE_REFRESH_TOKENS', True),
    'BLACKLIST_AFTER_ROTATION':  _bool('JWT_BLACKLIST_AFTER_ROTATION', True),
    'UPDATE_LAST_LOGIN':         _bool('JWT_UPDATE_LAST_LOGIN', True),
    'ALGORITHM':                 os.environ.get('JWT_ALGORITHM', 'HS256'),
    'SIGNING_KEY':               os.environ.get('JWT_SIGNING_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES':         ('Bearer',),
    'AUTH_TOKEN_CLASSES':        ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_OBTAIN_SERIALIZER':   'apps.accounts.serializers.LoginSerializer',
    'TOKEN_REFRESH_SERIALIZER':  'apps.accounts.serializers.RefreshTokenSerializer',
}

# ─── Swagger / OpenAPI ──────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE':       'HotelMate API',
    'DESCRIPTION': 'Complete API for HotelMate — Event Ticketing Platform (v2.0)',
    'VERSION':     '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True, 'displayOperationId': False, 'persistAuthorization': True,
    },
    'TAGS': [
        {'name': 'System',      'description': 'Health check, newsletter'},
        {'name': 'Authentication', 'description': 'Register, login, logout, 2FA, email verification, password reset'},
        {'name': 'Events',      'description': 'Event catalog, categories, favorites, reviews, status workflow'},
        {'name': 'Organizer',   'description': 'Organizer profile and full dashboard'},
        {'name': 'Tickets',     'description': 'Ticket types, purchasing, QR codes, check-in'},
        {'name': 'Payments',    'description': 'Stripe checkout, wallet, transactions, withdrawals, refunds'},
        {'name': 'Notifications','description': 'In-app and email notifications'},
        {'name': 'KYC',         'description': 'Identity verification documents'},
        {'name': 'Support',     'description': 'Support tickets and messaging'},
        {'name': 'Admin Panel', 'description': 'Administration, moderation, analytics, reports'},
    ],
    'ENUM_NAME_OVERRIDES': {
        'UserRoleEnum':          'apps.accounts.models.User.Role',
        'EventStatusEnum':       'apps.events.models.Event.Status',
        'EventTypeEnum':         'apps.events.models.Event.EventType',
        'PaymentStatusEnum':     'apps.payments.models.Payment.Status',
        'PaymentProviderEnum':   'apps.payments.models.Payment.Provider',
        'TicketStatusEnum':      'apps.tickets.models.Ticket.Status',
        'NotificationTypeEnum':  'apps.notifications.models.Notification.Type',
    },
}

# ─── Stripe ─────────────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY     = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY     = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
STRIPE_CURRENCY       = os.environ.get('STRIPE_CURRENCY', 'eur')

# ─── SendGrid ────────────────────────────────────────────────────────────────
DEFAULT_FROM_EMAIL   = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@hotelmate.com')
SENDGRID_API_KEY     = os.environ.get('SENDGRID_API_KEY', '')
SENDGRID_TIMEOUT     = _int('SENDGRID_TIMEOUT', 10)
SENDGRID_FROM_EMAIL  = os.environ.get('SENDGRID_FROM_EMAIL', DEFAULT_FROM_EMAIL)

# ─── Twilio ──────────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')

# ─── Celery ──────────────────────────────────────────────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL    = REDIS_URL
CELERY_RESULT_BACKEND= REDIS_URL
CELERY_TIMEZONE      = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'send-upcoming-event-reminders': {
        'task':     'apps.notifications.tasks.queue_event_reminder_emails',
        'schedule': crontab(minute=0),
    },
}

# ─── Cache ───────────────────────────────────────────────────────────────────
if REDIS_URL and not DEBUG:
    CACHES = {'default': {
        'BACKEND':  'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }}
else:
    CACHES = {'default': {
        'BACKEND':  'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hotelmate-dev-cache',
    }}

# ─── Business logic ──────────────────────────────────────────────────────────
PLATFORM_COMMISSION = float(os.environ.get('PLATFORM_COMMISSION', '0.90'))
