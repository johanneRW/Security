import os

PRODUCTION = True if os.environ["PRODUCTION"] == "true" else False

MAPBOX_TOKEN = os.environ["MAPBOX_TOKEN"]

COOKIE_SECRET = os.environ["COOKIE_SECRET"]
COOKIE_SECURE = True if os.environ["COOKIE_SECURE"] == "true" else False

DEFAULT_EMAIL = os.environ["DEFAULT_EMAIL"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

DATABASE_URL = os.environ["DATABASE_URL"]

IMAGE_FOLDER = os.environ["IMAGE_FOLDER"]

HOST_NAME = os.environ["HOST_NAME"]

ITEMS_PER_PAGE = 2

MAX_FILE_SIZE = 5 * 1024 * 1024  # Maksimal filstørrelse i bytes (5 MB)

ALLOWED_IMAGE_FORMATS = ["JPEG", "PNG", "GIF", "WEBP"]

