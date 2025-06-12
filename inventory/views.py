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
import logging
import os

from .models import Product, PurchaseOrder, PurchaseOrderDetail, Supplier, Category, CustomerOrder, Customer, Employee
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
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Log the start of the transaction
                logger.info("Starting transaction for creating purchase order")

                # Handle Supplier
                supplier_name = request.POST.get('supplier_name')
                supplier_phone = request.POST.get('supplier_phone')
                supplier_email = request.POST.get('supplier_email')
                supplier_address = request.POST.get('supplier_address')

                supplier, created = Supplier.objects.get_or_create(
                    name=supplier_name,
                    defaults={
                        'phone': supplier_phone,
                        'email': supplier_email,
                        'address': supplier_address
                    }
                )

                # Log supplier creation or retrieval
                logger.info(f"Supplier: {supplier.name} {'created' if created else 'retrieved'}")

                # Create Purchase Order
                purchase_order = PurchaseOrder.objects.create(
                    supplier=supplier,
                    ordered_by=request.user
                )

                # Log purchase order creation
                logger.info(f"Purchase Order created with ID: {purchase_order.id}")

                # Handle Product
                product_name = request.POST.get('product_name')
                brand = request.POST.get('brand')
                category_name = request.POST.get('category')
                quantity = int(request.POST.get('quantity'))
                purchasing_price = float(request.POST.get('purchasing_price'))

                # Handle category
                category, _ = Category.objects.get_or_create(name=category_name)

                # Handle product
                product, product_created = Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        'brand': brand,
                        'category': category,
                        'supplier': supplier,
                        'quantity': quantity,
                        'purchasing_price': purchasing_price,
                        'stock': quantity
                    }
                )

                # Log product creation or retrieval
                logger.info(f"Product: {product.name} {'created' if product_created else 'retrieved'}")

                # If product already exists, update stock & price
                if not product_created:
                    product.quantity += quantity
                    product.stock += quantity
                    product.purchasing_price = purchasing_price
                    product.save()
                    logger.info(f"Product updated: {product.name}")

                # Create PurchaseOrderDetail
                purchase_order_detail = PurchaseOrderDetail.objects.create(
                    order=purchase_order,
                    product=product,
                    quantity=quantity,
                    price_per_unit=purchasing_price
                )

                # Log purchase order detail creation
                logger.info(f"Purchase Order Detail created with ID: {purchase_order_detail.id}")

                # Redirect to success page
                messages.success(request, 'Purchase order created successfully!')
                return redirect('purchase_order_success', order_id=purchase_order.id)

        except Exception as e:
            # Log the error
            logger.error(f"Error occurred: {str(e)}")
            messages.error(request, f'Error occurred: {str(e)}')
            # Redirect back to the form page with error message
            return redirect('create_purchase_order')

    # GET Request — render the form
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    brands = Product.objects.values_list('brand', flat=True).distinct()
    categories = Category.objects.values_list('id', 'name')

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
