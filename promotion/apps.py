from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PromotionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "promotion"
    verbose_name = _('акции')

    def ready(self):
        from . import signals  # noqa: F401

        return super().ready()
