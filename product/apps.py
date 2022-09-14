from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "product"

    def ready(self):
        from . import signals  # noqa: F401

        return super().ready()
