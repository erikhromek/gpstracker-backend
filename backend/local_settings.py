import os

ENVIRONMENT = "development"
DEBUG = True

ALLOWED_HOSTS = ["localhost", "*"]

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

TWILIO_AUTH_TOKEN = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

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
