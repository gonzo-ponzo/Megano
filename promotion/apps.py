from django.apps import AppConfig


class PromotionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "promotion"

    def ready(self):
        from . import signals  # noqa: F401

        return super().ready()
