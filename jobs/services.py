import os
from pydantic import BaseModel, EmailStr, ValidationError, validator
from phonenumber_field.phonenumber import PhoneNumber
from decimal import Decimal
from PIL import Image
from django.core.files import File

from .models import Process
from .tasks import shop_import
from shop.models import Shop, ShopImage
from product.models import Product, Offer
# from promotion.models import PromotionOffer
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail


class ShopBaseInfo(BaseModel):
    email: EmailStr
    name: str | None = None
    description: str | None = None
    phone: str | None = None
    address: str | None = None
    image: str | None = None
    user_mail: EmailStr | None = None
    shop_photos: list[str] | None = None

    @validator("phone")
    def check_correct_phone(cls, v):
        try:
            return PhoneNumber.from_string(v)
        except Exception as e:
            raise ValueError(f"invalid PhoneNumber - {v}; error message - {e}")

    @validator("image")
    def check_correct_logo(cls, v, values):
        if v and "email" in values.keys():
            logo_path = os.path.join(settings.IMPORT_INCOME, values["email"], v)
            try:
                check_image = Image.open(logo_path)
                ratio = check_image.width / check_image.height
                if ratio > 1.05 or ratio < 0.95:
                    raise ValueError(f"ratio ({ratio}) must be in [0.95,1.05]")
            except Exception as e:
                raise ValueError(f"invalid LOGO - {v}; error message - {e}")
            return File(open(logo_path, 'rb'), name=v)
        return v

    @validator("shop_photos")
    def check_correct_photos(cls, v, values):
        if v and "email" in values.keys():
            res = []
            for file_name in v:  # TODO соотношение сторон проверять? в верстке картинки оквадачиваются
                logo_path = os.path.join(settings.IMPORT_INCOME, values["email"], file_name)
                try:
                    check_image = Image.open(logo_path)
                    res.append((File(open(logo_path, 'rb'), name=file_name), ""))
                except Exception as e:
                    res.append((None, f"invalid LOGO - {v}; error message - {e}"))
            v = res
        return v


class OfferInfo(BaseModel):
    product_id: int
    amount: int
    price: Decimal
    promotion: int | None = None  # TODO

    @validator("price")
    def check_correct_price(cls, v):
        if int(v*100) < v*100:
            raise ValueError(f"invalid price - {v}; must be 2 decimal points")
        return v


class ShopModel(BaseModel):
    shop: ShopBaseInfo
    offers: list[OfferInfo] | None = None


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

    fields = {"name", "description", "phone", "address", "image"}
    fields_requred = fields | {"user_mail"}

    user = None
    if shop_data.user_mail:
        user = get_user_model().objects.filter(email=shop_data.user_mail).first()

    if shop:  # редактирование информации о магазине
        if Shop.objects.filter(phone=shop_data.phone).exclude(pk=shop.pk).first():
            return False, f"Phone {shop_data.phone} is already used"
        for key in fields:
            if key in shop_data.__fields_set__:
                setattr(shop, key, shop_data.__dict__.get(key))
        if user:
            shop.user = user
        shop.save()
    else:  # добавление нового магазина
        need_fields = fields_requred - shop_data.__fields_set__
        if len(need_fields) > 0:
            return False, f"Required fields: {need_fields}"
        if Shop.objects.filter(phone=shop_data.phone).first():
            return False, f"Phone {shop_data.phone} is already used"
        if not user:
            return False, f"User with email {shop_data.user_mail} not found"
        shop = Shop.objects.create(email=email, user=user, **{key: shop_data.__dict__.get(key) for key in fields})

    error_list = []
    if shop_data.shop_photos:
        for f, e in shop_data.shop_photos:
            if f:
                ShopImage.objects.create(image=f, shop=shop)
            else:
                error_list.append(e)

    if data.offers:
        for offer_data in data.offers:
            product = Product.objects.filter(pk=offer_data.product_id).first()
            if product:
                offer = Offer.objects.filter(shop=shop, product=product).first()  # TODO update_or_create
                if offer:
                    offer.price = offer_data.price
                    offer.amount = offer_data.amount
                    offer.save()
                else:
                    Offer.objects.create(shop=shop, product=product, price=offer_data.price, amount=offer_data.amount)
            else:
                error_list.append(f"Product c offer_data.product_id={offer_data.product_id} not found")

    if len(error_list) > 0:
        return False, error_list
    return True, "TODO promo"  # TODO


def send_mail_from_site(subject, message, recipient_list):
    # TODO отправку делать через механизм очереди, или на крайний случай обернуть в try
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list)
