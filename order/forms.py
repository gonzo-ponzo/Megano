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


class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("payment_type",)
        labels = {"payment_type": ""}
        widgets = {"payment_type": forms.Select(attrs={"class": "form-select"})}


class PaymentForm(forms.Form):
    card_number = forms.CharField()
