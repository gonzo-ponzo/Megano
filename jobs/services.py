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
from django.core.mail import EmailMessage


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
                    return (None, f"invalid logo - {v}; ratio ({ratio}) must be in [0.95,1.05]")
            except Exception as e:
                return (None, f"invalid logo - {v}; error message - {e}")
            return (File(open(logo_path, 'rb'), name=v), "")
        return v

    @validator("shop_photos")
    def check_correct_photos(cls, v, values):
        if v and "email" in values.keys():
            res = []
            for file_name in v:
                logo_path = os.path.join(settings.IMPORT_INCOME, values["email"], file_name)
                try:
                    check_image = Image.open(logo_path)
                    ratio = check_image.width / check_image.height
                    if ratio > 1.05 or ratio < 0.95:
                        res.append((None, f"invalid photo - {file_name}; ratio ({ratio}) must be in [0.95,1.05]"))
                    else:
                        res.append((File(open(logo_path, 'rb'), name=file_name), ""))
                except Exception as e:
                    res.append((None, f"invalid photo - {file_name}; error message - {e}"))
            v = res
        return v


class OfferInfo(BaseModel):
    product_id: int
    amount: int
    price: Decimal

    @validator("price")
    def check_correct_price(cls, v):
        if (v < 0) or (int(v*100) < v*100):
            raise ValueError(f"invalid price - {v}; must be positive, 2 decimal points")
        return v

    @validator("product_id")
    def check_correct_product(cls, v):
        if v <= 0:
            raise ValueError(f"invalid product_id - {v}")
        return v

    @validator("amount")
    def check_correct_amount(cls, v):
        if v <= 0:
            raise ValueError(f"invalid product value - {v}")
        return v


class ShopModel(BaseModel):
    shop: ShopBaseInfo
    offers: list[OfferInfo] | None = None


def try_start_import(file_names, email_admin):
    process, _ = Process.objects.get_or_create(name="shop_import")
    if process.is_run:
        return False, "Предыдущий импорт ещё не выполнен. Пожалуйста, дождитесь его окончания"
    process.is_run = True
    process.save()
    shop_import.delay(file_names, "shop_import", email_admin)
    return True, "Импорт запущен"


def one_shop_import(file_name):  # noqa C901
    try:
        data = ShopModel.parse_file(file_name)
    except ValidationError as e:
        return False, f"ERROR: {e.json}"
    except Exception as e:
        return False, f"ERROR {type(e)}: {e}"

    shop_data = data.shop
    email = shop_data.email
    shop = Shop.objects.filter(email=email).first()

    fields = {"name", "description", "phone", "address"}  # "image" отдельно
    fields_requred = fields | {"user_mail"}

    user = None
    if shop_data.user_mail:
        user = get_user_model().objects.filter(email=shop_data.user_mail).first()

    message_list = []
    has_warnings = False

    if shop:  # редактирование информации о магазине
        if Shop.objects.filter(phone=shop_data.phone).exclude(pk=shop.pk).first():
            return False, f"ERROR: Phone {shop_data.phone} is already used"
        for key in fields:
            if key in shop_data.__fields_set__:
                setattr(shop, key, shop_data.__dict__.get(key))
        if shop_data.user_mail:
            if user:
                shop.user = user
            else:
                return False, f"ERROR: User with email {shop_data.user_mail} not found"
        if shop_data.image:
            if shop_data.image[0]:
                shop.image = shop_data.image[0]
            else:
                message_list.append(shop_data.image[1])
        shop.save()
        message_list.append(f"Shop {shop.name}, id={shop.pk} edited")
    else:  # добавление нового магазина
        need_fields = fields_requred - shop_data.__fields_set__
        if len(need_fields) > 0:
            return False, f"ERROR: Required fields: {need_fields}"
        if Shop.objects.filter(phone=shop_data.phone).first():
            return False, f"ERROR: Phone {shop_data.phone} is already used"
        if not user:
            return False, f"ERROR: User with email {shop_data.user_mail} not found"
        shop = Shop.objects.create(email=email, user=user, **{key: shop_data.__dict__.get(key) for key in fields})
        if shop_data.image:
            if shop_data.image[0]:
                shop.image = shop_data.image[0]
            else:
                message_list.append(shop_data.image[1])
        else:
            message_list.append("logo missed")
        shop.save()
        message_list.append(f"Shop {shop.name}, id={shop.pk} created")

    if shop_data.shop_photos:
        for f, e in shop_data.shop_photos:
            if f:
                ShopImage.objects.create(image=f, shop=shop)
                message_list.append(f"Photo {f} added")
            else:
                message_list.append(f"WARNING: {e}")
                has_warnings = True

    if data.offers:
        for offer_data in data.offers:
            product = Product.objects.filter(pk=offer_data.product_id).first()
            if product:
                offer, created = Offer.objects.update_or_create(shop=shop, product=product,
                                                                defaults={"price": offer_data.price,
                                                                          "amount": offer_data.amount})
                if created:
                    message_list.append(f"Offer ({product}, {offer_data.amount}, {offer_data.price}) created")
                else:
                    message_list.append(f"Offer ({product}, {offer_data.amount}, {offer_data.price}) updated")
            else:
                message_list.append(f"WARNING: Product with product_id={offer_data.product_id} not found")
                has_warnings = True

    return not has_warnings, message_list


def send_mail_from_site(subject, message, recipient_list, attach=None):
    email = EmailMessage(subject=subject, body=message, from_email=settings.EMAIL_HOST_USER,
                         to=recipient_list)
    if attach:
        email.attach_file(attach)
    email.send()
