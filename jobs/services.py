import json

from .models import Process
from .tasks import shop_import
from shop.models import Shop
from django.contrib.auth import get_user_model


def try_start_import(file_names):
    process, _ = Process.objects.get_or_create(name="shop_import")
    if process.is_run:
        return False
    process.is_run = True
    process.save()
    shop_import.delay(file_names, "shop_import")
    return True

def one_shop_import(file_name):
    str_data = open(file_name, "r").read()
    if str_data.count('"email"') != 1:
        return False, "Incorrect shop's email"
    data = json.loads(str_data)
    #print(data)
    if "shop" not in data.keys():
        return False, "Incorrect part shop"
    shop_data = data["shop"]
    if "email" not in shop_data.keys():
        return False, "Not found shop email"
    email = shop_data["email"]
    shop = Shop.objects.filter(email=email).first()
    print(shop)
    # "image", "user" - отдельно
    fields = ["name", "description", "phone", "address"]
    if shop:
        for key in fields:
            if key in shop_data.keys():
                setattr(shop, key, shop_data[key])
        # еще лого, картинки магазина, продавец
        shop.save()
    else:
        need_fields = set(fields) - set(shop_data.keys())
        if len(need_fields) > 0:
            return False, f"Required fields: {need_fields}"
        user = get_user_model().objects.get(pk=1)  # TODO
        shop = Shop.objects.create(email=email, user=user, **{key:shop_data[key] for key in fields})
        # еще необязательные лого, картинки магазина, и обязательный продавец
    return True, "All correct, supposed"
