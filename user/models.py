from phonenumber_field.modelfields import PhoneNumberField
from timestamps.models import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, is_active=True, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError(_("Емейл должен быть указан."))
        if not password:
            raise ValueError(_("Должен быть указан пароль"))
        user_obj = self.model(
            email=self.normalize_email(email),
        )
        user_obj.is_active = is_active
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомизированная модель пользователя"""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(max_length=125, unique=True, verbose_name=_("электронная почта"))
    first_name = models.CharField(max_length=30, verbose_name=_("имя"))
    last_name = models.CharField(max_length=150, verbose_name=_("фамилия"))
    middle_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_("отчество"))
    phone = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name=_("телефон")
    )
    avatar = models.ImageField(blank=True, upload_to="avatar/%Y/%m/%d", verbose_name=_("фото"))

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def get_fio(self):
        return " ".join(list(filter(lambda item: item is not None,
                                    [self.last_name, self.first_name, self.middle_name])))

    def save(self, *args, **kwargs):
        if self.pk:
            this_record = CustomUser.objects.get(pk=self.pk)
            if this_record.avatar and (this_record.avatar != self.avatar):
                this_record.avatar.delete(save=False)
        super(CustomUser, self).save(*args, **kwargs)

    def check_groups_staff(self):
        """если пользователя добавили хотя бы в одну группу, где есть какие-то права, пускаем пользователя в админку"""
        if self.pk and not self.is_superuser:
            groups = self.groups
            if groups.count() == 0:
                self.is_staff = False
            else:
                self.is_staff = False
                for group in groups.all():
                    if group.permissions.count() > 0:
                        self.is_staff = True
                        break
            self.save()

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
