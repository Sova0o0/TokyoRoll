from django.urls import path, include  
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/', include('cart.urls')),
    path('category/<int:category_id>/products/', views.get_category_products, name='get_category_products'), 
    path('category/<int:category_id>/', views.category_view, name='category'),
]