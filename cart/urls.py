from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('count/', views.get_cart_count, name='cart_count'),
    path('update-user-data/', views.update_user_data, name='update_user_data'), 
]