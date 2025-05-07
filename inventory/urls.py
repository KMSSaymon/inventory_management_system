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
]
