from .settings import *  # noqa: F401,F403


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

MEDIA_ROOT = BASE_DIR / 'test_media'

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SENDGRID_API_KEY = 'test-sendgrid-key'
SENDGRID_FROM_EMAIL = 'test@example.com'
DEFAULT_FROM_EMAIL = 'test@example.com'

STRIPE_SECRET_KEY = 'sk_test_fake'
STRIPE_WEBHOOK_SECRET = 'whsec_test_fake'
JWT_SIGNING_KEY = 'test-jwt-signing-key-with-sufficient-length'
SIMPLE_JWT['SIGNING_KEY'] = JWT_SIGNING_KEY
