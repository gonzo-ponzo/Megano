from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import UserRegistrationForm, UserLoginForm


class UserLoginView(LoginView):
    """Страница входа"""

    form_class = UserLoginForm
    template_name = "user/login.html"

    def get_success_url(self):
        next = self.request.GET.get('next')
        if next:
            return next
        return reverse("main-page")


class UserRegistrationView(View):
    """Страница регистрации"""

    def get(self, request, *args, **kwargs):
        context = {'form': UserRegistrationForm}
        return render(request, "user/register.html", context=context)

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST, request.FILES)
        form_data = form.data
        if form.is_valid():
            email = form_data.get("email")
            raw_password = form_data.get("password1")
            user = form.save()
            if request.FILES:
                avatar = request.FILES["avatar"]
                user.avatar = avatar
                user.save(update_fields=["avatar"])
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect(reverse("main-page"))
        else:
            context = {"form": form}
            return render(request, "user/register.html", context=context)


class LogoutView(LogoutView):
    next_page = reverse_lazy("main-page")


@login_required
def user_page(request):
    return render(request, 'user/account.html')


@login_required
def user_update(request):  # get/post
    return render(request, 'user/profile.html')


@login_required
def orders_history(request):
    return HttpResponse("Эта страница еще никем не сделана")


@login_required
def views_history(request):
    return HttpResponse("Эта страница еще никем не сделана")
