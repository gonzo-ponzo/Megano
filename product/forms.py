from django import forms
from product.models import Product, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name",)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
