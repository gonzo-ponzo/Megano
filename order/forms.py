from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("delivery_type", "city", "address", "payment_type", "comment")
        widgets = {
            "delivery_type": forms.RadioSelect,
            "payment_type": forms.RadioSelect,
            "city": forms.TextInput(attrs={"class": "form-input", "data-validate": "require"}),
            "address": forms.Textarea(attrs={"class": "form-textarea", "data-validate": "require"}),
            "comment": forms.Textarea(attrs={"class": "form-textarea"}),
        }
