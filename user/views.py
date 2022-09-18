from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth.views import LoginView

from .forms import UserRegistrationForm  # , UserLoginForm


class UserLoginView(LoginView):
    """Страница входа"""

    # form_class = UserLoginForm  # AuthenticationForm
    form_class = AuthenticationForm
    template_name = 'user/login.html'

    def get_success_url(self):
        return reverse("main-page")


class UserRegistrationView(View):
    """Страница регистрации"""

    def get(self, request, *args, **kwargs):
        context = {'form': UserRegistrationForm}
        return render(request, 'user/register.html', context=context)

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST, request.FILES)
        form_data = form.data
        if form.is_valid():
            email = form_data.get("email")
            raw_password = form_data.get("password1")
            user = form.save()
            if request.FILES:
                avatar = request.FILES['avatar']
                user.avatar = avatar
                user.save(update_fields=["avatar"])
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect(reverse('main-page'))
        else:
            context = {"form": form}
            return render(request, 'user/register.html', context=context)
