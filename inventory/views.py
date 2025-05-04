from django.shortcuts import render, redirect
from django.db import connection

def home(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    with connection.cursor() as cursor:
        # Fetch categories
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

        # Build dynamic SQL for product search/filter
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


def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        brand = request.POST['brand']
        quantity = request.POST['quantity']
        category_id = request.POST['category']
        supplier_name = request.POST['supplier_name']
        supplier_contact = request.POST['supplier_contact']

        try:
            with connection.cursor() as cursor:
                # Try to find existing supplier
                cursor.execute("SELECT id FROM inventory_supplier WHERE name = %s", [supplier_name])
                result = cursor.fetchone()

                if result:
                    supplier_id = result[0]
                else:
                    # Insert new supplier with default values
                    cursor.execute(
                        "INSERT INTO inventory_supplier (name, phone, email, address) VALUES (%s, %s, %s, %s)",
                        [supplier_name, supplier_contact, 'unknown@example.com', 'Unknown']
                    )
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    supplier_id = cursor.fetchone()[0]

                # Insert the product
                cursor.execute(
                    "INSERT INTO inventory_product (name, brand, quantity, category_id, supplier_id, price) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    [name, brand, quantity, category_id, supplier_id, 0.00]
                )

            return redirect('home')

        except Exception as e:
            # Handle error, e.g., log or show error message
            print(f"Error occurred: {e}")
            return redirect('error_page')  # You can redirect to an error page or show a message

    # For GET request, fetch categories
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM inventory_category")
        categories = cursor.fetchall()

    return render(request, 'inventory/add_product.html', {'categories': categories})
