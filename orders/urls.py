from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('repeat/<int:order_id>/', views.repeat_order, name='repeat_order'),
    path('check_promo/', views.check_promo, name='check_promo'),
]