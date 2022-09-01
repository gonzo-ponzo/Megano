from django.contrib import admin
from shop.models import Shop


class ShopsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Shop, ShopsAdmin)
