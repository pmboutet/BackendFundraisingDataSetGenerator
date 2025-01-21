from .base import *

DEBUG = True

ALLOWED_HOSTS = ['test-app.herokuapp.com']

# Test database configuration
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# CORS settings for test environment
CORS_ALLOWED_ORIGINS = [
    'https://test-frontend-domain.com',
    'http://localhost:3000',
]
CORS_ALLOW_CREDENTIALS = True

# Less strict security settings for test environment
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# More verbose logging for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
