from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection, transaction
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import ProductForm
import logging
import os
import traceback

from django.db.models import Q, Sum
from datetime import datetime

from .forms import EmployeeForm
from .models import Employee
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .models import Product, PurchaseOrder, PurchaseOrderDetail, Supplier, Category, CustomerOrder, Customer, Employee,Sell, SellItem
from .forms import PurchaseOrderDetailForm, SupplierForm, CustomUserCreationForm

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'inventory/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'inventory/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required(login_url='login')
def home(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

        query = """
        SELECT p.id, p.name, p.brand, p.quantity,
               c.name AS category,
               s.name AS supplier,
               p.image,
               p.selling_price AS price
        FROM inventory_product p
        JOIN inventory_category c ON p.category_id = c.id
        JOIN inventory_supplier s ON p.supplier_id = s.id
        WHERE 1=1
        """
        params = []

        if search:
            query += " AND p.name LIKE %s"
            params.append(f'%{search}%')

        if category_id:
            query += " AND c.id = %s"
            params.append(category_id)

        cursor.execute(query, params)
        products = [
            {
                'id': row[0], 'name': row[1], 'brand': row[2],
                'quantity': row[3], 'category': row[4],
                'supplier': row[5], 'image': row[6], 'price': row[7]
            }
            for row in cursor.fetchall()
        ]

    return render(request, 'inventory/home.html', {
        'products': products,
        'categories': categories
    })

def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        brand = request.POST['brand']
        quantity = request.POST['quantity']
        purchasing_price = request.POST['purchasing_price']
        selling_price = request.POST['selling_price']
        category_name = request.POST['category']
        supplier_name = request.POST['supplier_name']
        supplier_phone = request.POST['supplier_phone']
        supplier_email = request.POST['supplier_email']
        image = request.FILES.get('image')

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM inventory_category WHERE name = %s", [category_name])
                category_result = cursor.fetchone()

                if not category_result:
                    cursor.execute("INSERT INTO inventory_category (name) VALUES (%s)", [category_name])
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    category_id = cursor.fetchone()[0]
                else:
                    category_id = category_result[0]

                cursor.execute("SELECT id FROM inventory_supplier WHERE name = %s", [supplier_name])
                result = cursor.fetchone()

                if result:
                    supplier_id = result[0]
                else:
                    cursor.execute(
                        "INSERT INTO inventory_supplier (name, phone, email, address) VALUES (%s, %s, %s, %s)",
                        [supplier_name, supplier_phone, supplier_email, 'Unknown']
                    )
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    supplier_id = cursor.fetchone()[0]

                image_name = None
                if image:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'product_images'))
                    image_name = fs.save(image.name, image)

                cursor.execute(
                    """
                    INSERT INTO inventory_product
                    (name, brand, quantity, purchasing_price, selling_price, category_id, supplier_id, image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [name, brand, quantity, purchasing_price, selling_price,
                     category_id, supplier_id, f'product_images/{image_name}' if image_name else None]
                )

            return redirect('home')

        except Exception as e:
            print(f"Error occurred: {e}")
            return redirect('home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

        cursor.execute("SELECT DISTINCT brand FROM inventory_product")
        brands = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT name FROM inventory_supplier")
        suppliers = [row[0] for row in cursor.fetchall()]

    return render(request, 'inventory/add_product.html', {
        'categories': categories,
        'brands': brands,
        'suppliers': suppliers,
    })

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/edit_product.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/delete_product.html', {'product': product})

@login_required
def create_purchase_order(request):
    print("✅ Starting create_purchase_order view")
    print("User:", request.user, "Authenticated:", request.user.is_authenticated)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                print("✅ Inside transaction block")

                # 1️⃣ Supplier data
                supplier_name = request.POST.get('supplier_name')
                supplier_phone = request.POST.get('supplier_phone')
                supplier_email = request.POST.get('supplier_email')
                supplier_address = request.POST.get('supplier_address')
                print("✅ Supplier data collected")

                supplier = Supplier.objects.filter(
                    name=supplier_name,
                    phone=supplier_phone,
                    email=supplier_email,
                    address=supplier_address
                ).first()

                if not supplier:
                    supplier = Supplier.objects.create(
                        name=supplier_name,
                        phone=supplier_phone,
                        email=supplier_email,
                        address=supplier_address
                    )


                print(f"✅ Supplier object ready: {supplier.name}")

                if request.user.role not in ['manager', 'owner']:
                    print("❌ Unauthorized user role:", request.user.role)
                    messages.error(request, 'You do not have permission to create a purchase order.')
                    return redirect('home')

                # 2️⃣ Create Purchase Order
                purchase_order = PurchaseOrder.objects.create(
                    supplier=supplier,
                    ordered_by=request.user,
                    status='Pending'
                )
                print(f"✅ PurchaseOrder created: ID = {purchase_order.id}")

                # 3️⃣ Product data (store in detail only)
                product_name = request.POST.get('product_name')
                brand = request.POST.get('brand')
                category_name = request.POST.get('category')
                unit_size = request.POST.get('unit_size')
                quantity = int(request.POST.get('quantity'))
                purchasing_price = float(request.POST.get('purchasing_price'))
                selling_price = float(request.POST.get('selling_price', 0.0))
                image = request.FILES.get('image')

                category, _ = Category.objects.get_or_create(name=category_name)

                PurchaseOrderDetail.objects.create(
                    order=purchase_order,
                    product=None,
                    product_name=product_name,
                    quantity=quantity,
                    price_per_unit=purchasing_price,
                    brand=brand,
                    category_name=category.name,
                    unit_size=unit_size,
                    selling_price=selling_price,
                    image=image
                )

                print("✅ PurchaseOrderDetail created without affecting stock")

                messages.success(request, 'Purchase order created successfully!')
                return redirect('purchase_order_success', order_id=purchase_order.id)

        except Exception as e:
            print("❌ Error while creating purchase order:", e)
            traceback.print_exc()
            messages.error(request, f"Error occurred: {str(e)}")
            return redirect('create_purchase_order')

    # GET form render
    print("➡ Rendering GET form")
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    brands = Product.objects.values_list('brand', flat=True).distinct()
    categories = Category.objects.values_list('name', flat=True)

    return render(request, 'purchase/create.html', {
        'suppliers': suppliers,
        'products': products,
        'brands': brands,
        'categories': categories
    })


@login_required
def purchase_order_success(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    details = order.details.all()
    return render(request, 'purchase/purchase_order_success.html', {
        'order': order,
        'details': details
    })

@login_required
def profile_view(request):
    return render(request, 'inventory/profile.html', {'user': request.user})

def manager_only(user):
    return user.is_authenticated and user.role == 'manager'

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'inventory/employee_list.html', {'employees': employees})

@login_required
def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().order_by('-date')
    return render(request, 'purchase/order_list.html', {'orders': orders})

@require_POST
@csrf_protect
def create_supplier(request):
    logger.info("create_supplier called")
    form = SupplierForm(request.POST)
    if form.is_valid():
        supplier = form.save()
        logger.info(f"Supplier created: {supplier.name}")
        return JsonResponse({'success': True, 'supplier_id': supplier.id, 'supplier_name': supplier.name})
    else:
        logger.error(f"Form errors: {form.errors}")
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def mark_order_arrived(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)

    if order.status != 'Arrived':
        for detail in order.details.all():
            supplier = order.supplier
            quantity = detail.quantity
            price = detail.price_per_unit

            # Extract extra info from detail
            product_name = detail.product_name
            brand = detail.brand
            category_name = detail.category_name
            unit_size = detail.unit_size or "N/A"
            selling_price = detail.selling_price or 0.0
            image = detail.image

            # Get or create category
            category, _ = Category.objects.get_or_create(name=category_name)

            # Try to find existing product
            product = Product.objects.filter(
                name=product_name,
                brand=brand,
                category=category,
                supplier=supplier
            ).first()

            if product:
                product.quantity += quantity
                product.stock += quantity
                product.save()
            else:
                product = Product.objects.create(
                    name=product_name,
                    brand=brand,
                    category=category,
                    supplier=supplier,
                    quantity=quantity,
                    stock=quantity,
                    purchasing_price=price,
                    selling_price=selling_price,
                    unit_size=unit_size,
                    image=image
                )

            if not detail.product:
                detail.product = product
                detail.save()

        order.status = 'Arrived'
        order.save()

    return redirect('purchase_order_list')

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')  # change this if your product list view has a different name

    return render(request, 'inventory/delete_product.html', {'product': product})


def manager_or_owner(user):
    return user.is_authenticated and user.role in ['manager', 'owner']

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'inventory/employee_list.html', {'employees': employees})

@login_required
@user_passes_test(manager_or_owner)
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'inventory/employee_form.html', {'form': form, 'title': 'Add Employee'})

@login_required
@user_passes_test(manager_or_owner)
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'inventory/employee_form.html', {'form': form, 'title': 'Edit Employee'})

@login_required
@user_passes_test(manager_or_owner)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_list')
    return render(request, 'inventory/employee_confirm_delete.html', {'employee': employee})


@transaction.atomic
def create_sell(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')

        # 🔥 Check if customer already exists
        customer, created = Customer.objects.get_or_create(
            phone=customer_phone,
            defaults={'name': customer_name}
        )

        discount = float(request.POST.get('discount', 0))
        total_price = float(request.POST.get('total_price', 0))

        sell = Sell.objects.create(
            customer=customer,
            discount_amount=discount,
            total_price=total_price,
        )

        # Get all items
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        for i in range(len(product_ids)):
            product_id = product_ids[i]
            quantity = int(quantities[i])
            unit_price = float(unit_prices[i])

            product = Product.objects.get(id=product_id)
            SellItem.objects.create(
                sell=sell,
                product=product,
                quantity=quantity,
                price_per_unit=unit_price
            )

            # 🔁 Update stock
            product.stock -= quantity
            product.save()

        return redirect('invoice', sell_id=sell.id)
    
    # GET request
    products = Product.objects.all()
    return render(request, 'inventory/create_sell.html', {'products': products})



def sells_report(request):
    sells = Sell.objects.all().order_by('-sell_date')

    # Filters
    customer_query = request.GET.get('customer', '')
    product_query = request.GET.get('product', '')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if customer_query:
        sells = sells.filter(Q(customer__name__icontains=customer_query) | Q(customer__phone__icontains=customer_query))

    if product_query:
        sells = sells.filter(items__product__name__icontains=product_query).distinct()

    if date_from:
        sells = sells.filter(sell_date__date__gte=date_from)
    if date_to:
        sells = sells.filter(sell_date__date__lte=date_to)

    total_revenue = sells.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_discount = sells.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0

    return render(request, 'inventory/sells_report.html', {
        'sells': sells,
        'total_revenue': total_revenue,
        'total_discount': total_discount
    })

def invoice_view(request, sell_id):
    sell = Sell.objects.get(id=sell_id)
    return render(request, 'inventory/invoice.html', {'sell': sell})


def customer_list(request):
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'inventory/customer_list.html', {'customers': customers})




    

