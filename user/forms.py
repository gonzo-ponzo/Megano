from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserAdminCreationForm(UserCreationForm):
    """Форма создания пользователей через админку"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['placeholder'] = '+12125552368'

    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Подтвердите пароль"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def clean(self):
        """Проверка на совпадение введенных паролей"""
        cleaner_data = super().clean()
        password = cleaner_data.get("password1")
        password_2 = cleaner_data.get("password2")
        if password is not None and password != password_2:
            self.add_error("password2", _("Введенные пароли должны совпадать"))
        return cleaner_data

    def save(self, commit=True):
        """Сохранение паролей в формате хеша"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password1"))
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """Форма для изменения пользователя через админку"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['placeholder'] = '+7(926)111-11-11'

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "middle_name",
                  "phone", "avatar", "is_active", "groups"]


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": _(
            "Введенные данные некоректны. Попробуйте еще раз."
        ),
        "inactive": _("Пользователь неактивен."),
    }


class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].error_messages = {"unique": _("Пользователь с таким емейлом уже зарегистрирован")}
        self.fields["phone"].widget.attrs["placeholder"] = "+7(926)111-11-11"

    password1 = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Подтвердите пароль"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Для верификации введите такой же пароль как ранее."),
    )

    error_messages = {
        "password_mismatch": _("Пароли не совпадают"),
    }

    class Meta:
        model = User
        fields = ["email", "password1", "password2", "first_name", "last_name", "middle_name", "phone", "avatar"]
