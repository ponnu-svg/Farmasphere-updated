from django import forms
from .models import *

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message']

class FarmerProductForm(forms.ModelForm):
    class Meta:
        model = FarmerProduct
        fields = ['product_name', 'quantity', 'price', 'description']

class MerchantRequestForm(forms.ModelForm):
    class Meta:
        model = MerchantRequest
        fields = ['product_name', 'quantity', 'price', 'description', 'latitude', 'longitude']
