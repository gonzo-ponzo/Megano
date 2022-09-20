from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminCreationForm, UserAdminChangeForm

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """ """
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ["email", "is_staff"]
    list_filter = []

    fieldsets = ((None, {"fields": ("email", "password")}),
                 (_("Личные данные"), {"fields": ("first_name", "last_name", "middle_name", "phone", "avatar")}),
                 (_("Разрешения"), {"fields": ("is_active", "groups")}),
                 )

    add_fieldsets = (
                (None, {"fields": ("email", "password1", "password2")}),
                (_("Личные данные"), {"fields": ("first_name", "last_name", "middle_name", "phone", "avatar")}),
    )
    exclude = ()

    ordering = ["email"]
    search_fields = ["email"]
