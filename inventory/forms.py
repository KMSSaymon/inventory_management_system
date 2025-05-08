from django import forms
from .models import Product
from .models import PurchaseOrder
from .models import CustomerOrder
from .models import Customer

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'category', 'supplier', 'quantity', 'purchasing_price', 'selling_price', 'image']

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['product', 'supplier', 'quantity', 'price_per_unit']

# inventory/forms.py
class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = CustomerOrder
        fields = ['customer', 'product', 'quantity']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']
