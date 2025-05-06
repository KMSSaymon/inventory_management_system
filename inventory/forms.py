from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'category', 'supplier', 'quantity', 'purchasing_price', 'selling_price', 'image']
