from django.core.validators import RegexValidator
from timestamps.models import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError(_("Емеил должен быть указан."))
        if not password:
            raise ValueError(_("Должен быть указан пароль"))
        user_obj = self.model(
            email=self.normalize_email(email),
        )
        user_obj.is_active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password):
        user = self.create_user(email=email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password, is_staff=True, is_admin=True)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомизированная модель пользователя"""

    ROLES = (("Admin", "Admin"), ("Buyer", "Buyer"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    phone_regex_validator = RegexValidator(
        regex=r"\d{3}-\d{3}-\d{2}-\d{2}", message=_("Номер телефона должен быть в формате  123-456-78-90")
    )

    email = models.EmailField(max_length=125, unique=True, verbose_name=_("емеил"))
    first_name = models.CharField(max_length=30, verbose_name=_("имя"))
    last_name = models.CharField(max_length=150, verbose_name=_("фамилия"))
    middle_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_("отчество"))
    phone = models.CharField(max_length=20, validators=[phone_regex_validator], verbose_name=_("телефон"))
    avatar = models.ImageField(blank=True, upload_to="avatar/%Y/%m/%d", verbose_name=_("фото"))
    role = models.CharField(choices=ROLES, default="Buyer", max_length=10, verbose_name=_("роль"))

    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    cart = models.JSONField(default={})

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
