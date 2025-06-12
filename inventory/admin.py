from django.contrib import admin
from .models import (
    Product, Category, Customer, Employee, Sale,
    SaleDetail, Supplier, PurchaseOrder, PartTimeWorkLog
)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'purchasing_price', 'selling_price', 'stock']
    list_filter = ['category']
    search_fields = ['name']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(SaleDetail)
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_type', 'role', 'shift', 'monthly_salary', 'hourly_wage', 'join_date']
    list_filter = ['employee_type', 'shift', 'role']
    search_fields = ['name', 'email', 'phone', 'designation']

@admin.register(PartTimeWorkLog)
class PartTimeWorkLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'hours_worked', 'daily_payment']
    list_filter = ['date']
    search_fields = ['employee__name']
