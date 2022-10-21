from django.contrib.auth import authenticate, login, get_user
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from product.services import BrowsingHistory


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
    user = get_user(request)
    context = {
        'viewed_products': BrowsingHistory(user).get_history(3)
    }
    return render(request, 'user/account.html', context=context)


class UserUpdateView(View):
    """Страница редактирования личных данных"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {'form': UserUpdateForm(instance=request.user)}
        return render(request, "user/profile.html", context=context)

    def post(self, request, *args, **kwargs):
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        is_ok = False
        if form.is_valid():
            form_data = form.data
            user = request.user
            user.email = form_data.get("email")
            user.phone = form_data.get("phone")
            fio = form_data.get("fio").split()
            user.last_name = fio[0]
            user.first_name = fio[1]
            if len(fio) > 2:
                user.middle_name = " ".join(fio[2:])
            else:
                user.middle_name = ""
            password = form_data.get("password1")
            if len(password) > 0:
                user.set_password(password)
            if request.FILES:
                avatar = request.FILES["avatar"]
                user.avatar = avatar
            user.save()
            is_ok = True
        context = {"form": form, "is_ok": is_ok}
        return render(request, "user/profile.html", context=context)


@login_required
def orders_history(request):
    return HttpResponse("Эта страница еще никем не сделана")


@login_required
def views_history(request):
    return HttpResponse("Эта страница еще никем не сделана")


class ViewsHistory(LoginRequiredMixin, TemplateView):

    template_name = 'user/historyview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user(self.request)
        context['viewed_products'] = BrowsingHistory(user).get_history()
        return context
