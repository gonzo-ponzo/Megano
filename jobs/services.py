from pydantic import BaseModel, EmailStr, ValidationError, validator
from phonenumber_field.phonenumber import PhoneNumber

from .models import Process
from .tasks import shop_import
from shop.models import Shop
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail


class ShopBaseInfo(BaseModel):
    email: EmailStr
    name: str | None = None
    description: str | None = None
    phone: str | None = None
    address: str | None = None
    logo_image: str | None = None
    user_mail: EmailStr | None = None
    # TODO + список фотографий магазина

    @validator("phone")
    def check_correct_phone(cls, v):
        try:
            return PhoneNumber.from_string(v)
        except Exception as e:
            raise ValueError(f"invalid PhoneNumber - {v}; error message - {e}")


class ShopModel(BaseModel):
    shop: ShopBaseInfo
    # TODO + раздел с офферами
    # TODO + раздел с акциями


def try_start_import(file_names):
    process, _ = Process.objects.get_or_create(name="shop_import")
    if process.is_run:
        return False
    process.is_run = True
    process.save()
    shop_import.delay(file_names, "shop_import")
    return True


def one_shop_import(file_name):
    try:
        data = ShopModel.parse_file(file_name)
    except ValidationError as e:
        return False, e.json

    shop_data = data.shop
    email = shop_data.email
    shop = Shop.objects.filter(email=email).first()

    fields = {"name", "description", "phone", "address"}
    fields_requred = fields | {"user_mail"}

    user = None
    if shop_data.user_mail:
        user = get_user_model().objects.filter(email=shop_data.user_mail).first()

    if shop:
        for key in fields:
            if key in shop_data.__fields_set__:
                setattr(shop, key, shop_data.__dict__.get(key))
        if user:
            shop.user = user
        shop.save()
        return True, "TODO logo and shop-pictures"  # TODO
    else:
        need_fields = fields_requred - shop_data.__fields_set__
        if len(need_fields) > 0:
            return False, f"Required fields: {need_fields}"
        if not user:
            return False, f"User with email {shop_data.user_mail} not found"
        shop = Shop.objects.create(email=email, user=user, **{key: shop_data.__dict__.get(key) for key in fields})
        return True, "TODO logo and shop-pictures"  # TODO
    return True, "All correct, supposed"


def send_mail_from_site(subject, message, recipient_list):
    # TODO отправку делать через механизм очереди, или на крайний случай обернуть в try
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list)
