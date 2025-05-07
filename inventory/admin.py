from django.contrib import admin
from .models import Product, Category, Customer, Employee, Sale, SaleDetail

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'purchasing_price', 'selling_price', 'stock']
    list_filter = ['category']
    search_fields = ['name']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Sale)
admin.site.register(SaleDetail)

