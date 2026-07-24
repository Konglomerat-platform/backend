from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-secret-key-for-konglomerat-refactor-0000000000"
SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY  # noqa: F405
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MEDIA_ROOT = BASE_DIR / "test-media"  # noqa: F405
USE_S3 = False
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
# The suite must never reach the Gemini API: a developer with a key in .env
# would otherwise get non-deterministic assertions, network-dependent runs and
# real quota spend. Tests that exercise the model override this explicitly and
# patch the client.
GEMINI_API_KEY = ""
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",  # noqa: F405
    }
}
