from django.shortcuts import render , get_object_or_404, redirect
from .models import Product
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .forms import ProductForm
from .forms import PurchaseOrderForm
from .models import Product, PurchaseOrder
import os

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

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
                    "INSERT INTO inventory_product (name, brand, quantity, category_id, supplier_id, price, image) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [name, brand, quantity, category_id, supplier_id, 0.00, f'product_images/{image_name}' if image_name else None]
                )

            return redirect('home')

        except Exception as e:
            print(f"Error occurred: {e}")
            return redirect('home')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

    return render(request, 'inventory/add_product.html', {'categories': categories})

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

def create_purchase_order(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            # Save the purchase order and get the instance
            order = form.save()

            # Redirect to the success page with the order's id
            return redirect('purchase_success', order_id=order.id)  # Passing the order_id here

    else:
        form = PurchaseOrderForm()

    return render(request, 'purchase/create.html', {'form': form})

def purchase_success(request, order_id):
    # Retrieve the PurchaseOrder object using the order_id
    order = PurchaseOrder.objects.get(id=order_id)

    # Render the success page and pass the order details
    return render(request, 'purchase/success.html', {'order': order})
