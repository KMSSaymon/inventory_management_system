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
    path('purchase/orders/', views.purchase_order_list, name='purchase_order_list'),
    path('create_supplier/', create_supplier, name='create_supplier'),
    path('purchase/create/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase/success/<int:order_id>/', views.purchase_order_success, name='purchase_order_success'),
    path('purchase-order/<int:order_id>/arrived/', views.mark_order_arrived, name='mark_order_arrived'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),

    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
  
    path('sells/create/', views.create_sell, name='create_sell'),
    path('sells/report/', views.sells_report, name='sells_report'),
    path('invoice/<int:sell_id>/', views.invoice_view, name='invoice'),

    path('customers/', views.customer_list, name='customer_list'),



]





