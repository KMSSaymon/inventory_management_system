from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'inventory_category'  # Specify the exact table name in the database

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, default='000-000-0000')  # Added default value
    email = models.EmailField(default='unknown@example.com')  
    address = models.TextField(default='Unknown')

    class Meta:
        db_table = 'inventory_supplier'  # Specify the exact table name in the database

    def __str__(self):
        return self.name


class Product(models.Model):
    
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchasing_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    selling_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    image = models.ImageField(upload_to='product_images/',null=True,blank=True) 
    stock = models.PositiveIntegerField(default=0) 

    class Meta:
        db_table = 'inventory_product'

    def __str__(self):
        return self.name



class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('part_time', 'Part-time'),
    ]

    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('salesman', 'Salesman'),
        ('staff', 'Staff'),
    ]

    SHIFT_CHOICES = [
        ('none', 'No Shift'),
        ('shift_1', '9:00 AM - 5:00 PM'),
        ('shift_2', '5:00 PM - 12:00 AM'),
    ]

    name = models.CharField(max_length=100, default='Unknown')
    phone = models.CharField(max_length=20, default='N/A')
    email = models.EmailField(unique=True, default='example@example.com')
    address = models.TextField(default='Not provided')

    designation = models.CharField(max_length=100, default='Staff')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE_CHOICES, default='permanent')
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, default='none')

    username = models.CharField(max_length=50, unique=True, default='defaultuser')
    password = models.CharField(max_length=100, default='123456')

    # Salary Details
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_wage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    join_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_employee'

    def __str__(self):
        return f"{self.name} ({self.role}, {self.employee_type})"


class PartTimeWorkLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, limit_choices_to={'employee_type': 'part_time'})
    date = models.DateField(auto_now_add=True)
    hours_worked = models.PositiveIntegerField()

    def daily_payment(self):
        if self.hours_worked >= 4:
            return self.hours_worked * self.employee.hourly_wage
        return 0

    daily_payment.short_description = 'Daily Payment'

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.hours_worked} hrs"




class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'inventory_customer'  # Keep the table name consistent

    def __str__(self):
        return f"{self.name} ({self.phone})"



class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_purchase'  # Specify the exact table name in the database

    def __str__(self):
        return f"{self.customer.name} - {self.product.name}"
    
class Sale(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale #{self.id} - {self.customer.name}"


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Unit price at time of sale

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Sale #{self.sale.id})"
    
class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'inventory_purchase_order'

    def __str__(self):
        return f"PO #{self.id} - {self.supplier.name}"


class PurchaseOrderDetail(models.Model):
    order = models.ForeignKey('PurchaseOrder', on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'inventory_purchase_order_detail'

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (PO #{self.order.id})"


class CustomerOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} ordered {self.product.name} ({self.quantity})"
    

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Manager/Owner'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return self.username



