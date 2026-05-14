from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Аутентификация
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Главная
    path('', views.dashboard, name='dashboard'),
    
    # Заказы
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/edit/', views.order_edit, name='order_edit'),
    
    # Товары
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # Категории
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    
    # Промокоды
    path('promocodes/', views.promocodes_list, name='promocodes_list'),
    path('promocodes/add/', views.promocode_add, name='promocode_add'),
    path('promocodes/<int:promocode_id>/edit/', views.promocode_edit, name='promocode_edit'),
    path('promocodes/<int:promocode_id>/delete/', views.promocode_delete, name='promocode_delete'),
    
    # Пользователи
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]