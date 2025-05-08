from django.urls import path
from .views import create_purchase_order
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Product List
    path('products/', views.product_list, name='product_list'),

    # Add Product
    path('products/add/', views.add_product, name='add_product'),

    # Edit Product
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),

    # Delete Product
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),

    path('purchase/create/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase/success/<int:order_id>/', views.purchase_success, name='purchase_success'),

    # inventory/urls.py
    path('customer/orders/', views.customer_order_list, name='customer_order_list'),
    path('customer/orders/add/', views.create_customer_order, name='create_customer_order'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'),

]
