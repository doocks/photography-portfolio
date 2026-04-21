import os
from pathlib import Path
import secrets
import dj_database_url  # Install: pip install dj-database-url

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# PRODUCTION SETTINGS - CRITICAL CHANGES
# ============================================================

# ❌ CHANGE THIS - NEVER use DEBUG=True in production
DEBUG = False  # ← MUST BE FALSE!

# ❌ CHANGE THIS - Use your actual domain
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'localhost',  # For testing only
    '127.0.0.1',
]

# ❌ CHANGE THIS - Use environment variable for SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # Generate a fallback (but use environment variable in production!)
    SECRET_KEY = secrets.token_urlsafe(50)

# ============================================================
# INSTALLED APPS (Same)
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gallery',
]

# ============================================================
# MIDDLEWARE - ADDED Security middleware for production
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← ADD THIS for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'photography.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'gallery.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'photography.wsgi.application'

# ============================================================
# DATABASE - SWITCH TO PostgreSQL for production
# ============================================================
# Use environment variable for database URL
# Example: DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'photography_db'),
        'USER': os.environ.get('DB_USER', 'photography_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# If using DATABASE_URL environment variable (recommended):
# import dj_database_url
# DATABASES['default'] = dj_database_url.config(default=os.environ.get('DATABASE_URL'))

# ============================================================
# PASSWORD VALIDATION - ENABLE for production
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC & MEDIA FILES - PRODUCTION CONFIG
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# EMAIL - USE REAL SMTP in production
# ============================================================
# For production, use real email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@yourdomain.com')

# ============================================================
# HTTPS / SSL SECURITY - CRITICAL for production
# ============================================================
# Enable these when you have SSL certificate installed
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# ============================================================
# LOGGING - Production logging to file
# ============================================================
# Create logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gallery': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}