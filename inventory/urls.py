from django.urls import path
from .views import create_purchase_order
from . import views
from .views import create_supplier

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

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('employee/', views.employee_list, name='employee-list'),
    path('purchase/orders/', views.purchase_order_list, name='purchase_order_list'),
    path('create_supplier/', create_supplier, name='create_supplier'),
    path('purchase/create/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase/success/<int:order_id>/', views.purchase_order_success, name='purchase_order_success'),
]





