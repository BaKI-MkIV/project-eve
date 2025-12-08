import os

ROOT_URLCONF = 'eve_backend.urls'
WSGI_APPLICATION = 'eve_backend.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'eve_main'),
        'USER': os.environ.get('DB_USER', 'freeman_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'hellotherefreeman'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'products',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # <- должно быть в начале
    'django.middleware.common.CommonMiddleware',
]

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOW_ALL_ORIGINS = True

# Для отладки можно добавить:
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'products.exceptions.custom_exception_handler'
}
