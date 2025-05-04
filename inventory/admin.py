from django.contrib import admin
from .models import Category, Supplier, Product, Employee, Customer, Purchase

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(Customer)
admin.site.register(Purchase)
