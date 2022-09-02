from .base import *  # noqa: F403

DEBUG = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
        },
    },
    "handlers": {
        "debug-console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["require_debug_true"],
        },
    },
}

try:
    INTERNAL_IPS.append("127.0.0.1")  # noqa: F405
except Exception:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

# setting for debug_toolbar to use docker
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]

COUNT_ELEMENTS_BEST_OFFER_SHOP = 6