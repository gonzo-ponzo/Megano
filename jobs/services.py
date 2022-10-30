from pydantic import BaseModel, EmailStr, ValidationError, validator
from phonenumber_field.phonenumber import PhoneNumber
from decimal import Decimal

from .models import Process
from .tasks import shop_import
from shop.models import Shop
from product.models import Product, Offer
#from promotion.models import PromotionOffer
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
    else:
        need_fields = fields_requred - shop_data.__fields_set__
        if len(need_fields) > 0:
            return False, f"Required fields: {need_fields}"
        if not user:
            return False, f"User with email {shop_data.user_mail} not found"
        shop = Shop.objects.create(email=email, user=user, **{key: shop_data.__dict__.get(key) for key in fields})
    error_list = []
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
    return True, "TODO logo and shop-pictures"  # TODO


def send_mail_from_site(subject, message, recipient_list):
    # TODO отправку делать через механизм очереди, или на крайний случай обернуть в try
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list)
