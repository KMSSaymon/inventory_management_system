from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def home(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

        query = """
        SELECT p.id, p.name, p.brand, p.quantity,
               c.name AS category,
               s.name AS supplier
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
                'quantity': row[3], 'category': row[4], 'supplier': row[5]
            }
            for row in cursor.fetchall()
        ]

    return render(request, 'inventory/home.html', {
        'products': products,
        'categories': categories
    })


from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def add_product(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST['name']
        brand = request.POST['brand']
        quantity = request.POST['quantity']
        category_name = request.POST['category']  # Changed to category name
        supplier_name = request.POST['supplier_name']
        supplier_phone = request.POST['supplier_phone']
        supplier_email = request.POST['supplier_email']
        image = request.FILES.get('image')

        try:
            with connection.cursor() as cursor:
                # Check if category exists
                cursor.execute("SELECT id FROM inventory_category WHERE name = %s", [category_name])
                category_result = cursor.fetchone()

                # If category doesn't exist, insert it
                if not category_result:
                    cursor.execute(
                        "INSERT INTO inventory_category (name) VALUES (%s)", [category_name]
                    )
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    category_id = cursor.fetchone()[0]
                else:
                    category_id = category_result[0]

                # Check if supplier exists
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

                # Handle image saving
                image_name = None
                if image:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'product_images'))
                    image_name = fs.save(image.name, image)

                # Insert product with image path
                cursor.execute(
                    "INSERT INTO inventory_product (name, brand, quantity, category_id, supplier_id, price, image) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [name, brand, quantity, category_id, supplier_id, 0.00, f'product_images/{image_name}' if image_name else None]
                )

            return redirect('home')  # Redirect to home after successful insert

        except Exception as e:
            print(f"Error occurred: {e}")
            return redirect('home')

    # GET request - show form for adding a new product
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

    return render(request, 'inventory/add_product.html', {'categories': categories})
