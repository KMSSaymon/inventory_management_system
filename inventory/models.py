from django.db import models

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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # ✅ ADD THIS

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
    email = models.EmailField()
    address = models.TextField()

    class Meta:
        db_table = 'inventory_customer'  # Specify the exact table name in the database

    def __str__(self):
        return self.name


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_purchase'  # Specify the exact table name in the database

    def __str__(self):
        return f"{self.customer.name} - {self.product.name}"
