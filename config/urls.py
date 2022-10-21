"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path(", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path(", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""
from django.contrib import admin
from django.urls import path, include
from user.views import UserLoginView, UserRegistrationView, LogoutView, \
                       user_page, UserUpdateView, orders_history, views_history, ViewsHistory
from product.views import MainPage
from payment.api import api_one_bill
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", MainPage.as_view(), name="main-page"),
    path('i18n/', include('django.conf.urls.i18n')),
    path("login/", UserLoginView.as_view(), name="login-page"),
    path("register/", UserRegistrationView.as_view(), name="registration-page"),
    path("product/", include("product.urls"), name="product"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user_page/", user_page, name="account"),
    path("user_page/update/", UserUpdateView.as_view(), name="profile"),
    path("orders_history/", orders_history, name="orders_history"),
    path("history/", ViewsHistory.as_view(), name="views_history"),
    path("catalog/", include("product.urls_catalog")),
    path("shop/", include("shop.urls"), name='shop'),
    path("order/", include(("order.urls", 'order'), namespace='order'),
         name='order'),
    path("promotion/", include("promotion.urls"), name='promotion'),
    path("payment/<int:order_number>", api_one_bill, name='one_payment'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
