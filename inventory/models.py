from django.db import models
from django.contrib.auth.models import User

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
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # ✅ ADD THIS
    stock = models.PositiveIntegerField(default=0)  # ✅ This line must exist

    class Meta:
        db_table = 'inventory_product'

    def __str__(self):
        return self.name




class Employee(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'inventory_employee'  # Specify the exact table name in the database

    def __str__(self):
        return self.name


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
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} from {self.supplier}"
    
class CustomerOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} ordered {self.product.name} ({self.quantity})"


