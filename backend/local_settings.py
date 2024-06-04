import os

ENVIRONMENT = "development"
DEBUG = True

ALLOWED_HOSTS = ["localhost", "*"]

CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

TWILIO_ACCOUNT_SID = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
TWILIO_AUTH_TOKEN = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
DJANGO_TWILIO_FORGERY_PROTECTION = False

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
