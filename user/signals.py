from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import CustomUser


@receiver(m2m_changed, sender=CustomUser.groups.through)
def check_staff(sender, instance, **kwargs):
    action = kwargs.pop("action", None)
    if action in ["post_add", "post_remove"]:
        instance.check_groups_staff()
