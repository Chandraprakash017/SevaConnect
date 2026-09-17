"""
SevaConnect Django Settings
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key from environment
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-secret-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# All Django apps + our SevaConnect apps
INSTALLED_APPS = [
    # Django core — required by rest_framework_simplejwt
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Our apps
    'common',
    'accounts',
    'departments',
    'services',
    'bookings',
    'technicians',
    'payments',
    'reviews',
    'ai_assistant',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS must be first
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# We use MongoDB via pymongo directly - no Django ORM database needed
# Django needs a database config to run migrations for session/auth tables,
# but since we're not using those, we use a dummy in-memory sqlite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    # Use our custom MongoDB JWT authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'common.authentication.MongoJWTAuthentication',
    ),
    # Require authentication by default (can override per view)
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT token settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    # We use 'user_id' as the key in the token payload
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS settings - allow React frontend to talk to Django backend
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
]
CORS_ALLOW_CREDENTIALS = True

# MongoDB connection string from environment
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/sevaconnect')

# Google Gemini API key - NEVER expose this in the frontend
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Razorpay payment keys
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
