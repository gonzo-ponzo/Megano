from .models import Product, ProductImage, Offer, ProductProperty, Property, \
    Review
from shop.models import Shop
from user.models import CustomUser
from django.shortcuts import get_object_or_404
from django.db.models import Min, Sum, Avg


def get_main_pic(obj: Product):
    """
    Получение активного изображения продукта
    """
    try:
        main_pic = ProductImage.objects.all().filter(product_id=obj.id)[0].image
    except Exception:
        main_pic = None
    return main_pic


def get_secondary_pics(obj: Product):
    """
    Получение всех изображений продукта за исключением активного
    """
    try:
        pics = ProductImage.objects.all().filter(product_id=obj.id)[1:]
    except ProductImage.DoesNotExist:
        pics = None
    return pics


def get_prices(obj: Product):
    """
    Получение всех цен на продукт
    """
    try:
        prices = Offer.objects.all().filter(product_id=obj.id)
    except Offer.DoesNotExist:
        prices = None
    return prices


def get_min_price(obj: Product):
    """
    Получение минимальной цены продукта
    """
    try:
        min_price = min([offer.price for offer in get_prices(obj)])
    except Exception:
        return None
    return min_price


def get_top_price(obj: Product):
    """
    Получение максимальной цены продукта
    """
    try:
        max_price = max([offer.price for offer in get_prices(obj)])
    except Exception:
        if len(get_prices(obj)) == 1:
            return get_prices(obj)[0].price
        else:
            return None
    return max_price


def get_discount(obj: Product):
    """
    Получение скидки на продукт в процентах
    """
    try:
        if get_top_price(obj) == get_min_price(obj):
            return None
        discount = int(((get_top_price(obj) - get_min_price(obj)) /
                        get_top_price(obj)) * 100)
    except Exception:
        return None
    return discount


def get_description(obj: Product):
    """
    Получение описания продукта
    """
    try:
        description = get_object_or_404(Product, id=obj.id
                                        ).description
    except Product.DoesNotExist:
        description = None
    return description


def get_property_values(obj: Product):
    """
    Получение значений свойств продукта
    """
    try:
        property_values = ProductProperty.objects.all().filter(
            product_id=obj
        )
    except Property.DoesNotExist:
        property_values = None
    return property_values


def get_property_idx(obj: Product):
    """
    Получение значений id свойств продукта
    """
    property_idx = [value.property_id for value in
                    get_property_values(obj)]
    return property_idx


def get_property_names(obj: Product):
    """
    Получение наименований свойств продукта
    """
    try:
        property_names = [
            get_object_or_404(Property, id=idx).name
            for idx in get_property_idx(obj)
        ]
    except Property.DoesNotExist:
        property_names = None
    return property_names


def get_property_dict(obj: Product):
    """
    Получение словаря свойств-значений продукта
    """
    property_dict = zip(get_property_names(obj),
                        get_property_values(obj))
    return property_dict


def get_offer_list(obj: Product):
    """
    Получение словаря магазин-цена продукта
    """
    try:
        offers = Offer.objects.all().filter(product_id=obj)
    except Offer.DoesNotExist:
        offers = None
    offer_list = [(get_object_or_404(
        Shop, id=offer.shop_id
    ), offer.price, offer.amount) for offer in offers]
    return offer_list


def get_review(obj: Product):
    """
    Получение всех отзывов о продукте
    """
    try:
        reviews_list = Review.objects.all().filter(product_id=obj.id)
        reviews = [(review, get_object_or_404(CustomUser, id=review.user_id))
                   for review in reviews_list]
    except Review.DoesNotExist:
        reviews = None
    return reviews


def get_queryset_for_catalog():
    queryset = Product.objects.all()
    queryset = queryset.filter(offer__isnull=False)
    queryset = queryset.prefetch_related('productimage_set')
    queryset = queryset.select_related('category')
    # queryset = queryset.prefetch_related('shop')
    queryset = queryset.annotate(min_price=Min('offer__price'))
    queryset = queryset.annotate(rating=Avg('review__rating', default=0))
    queryset = queryset.annotate(order_count=Sum('offer__orderoffer__amount', default=0))
    queryset = queryset.order_by('pk')

    return queryset
