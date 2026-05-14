from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'available']
    list_filter = ['category', 'available']  # Фильтр по доступности
    list_editable = ['available', 'price']   # Можно менять прямо в списке
    search_fields = ['name']
    
    # Действия для массового изменения доступности
    actions = ['make_available', 'make_unavailable']
    
    def make_available(self, request, queryset):
        queryset.update(available=True)
    make_available.short_description = "Сделать выбранные товары доступными"
    
    def make_unavailable(self, request, queryset):
        queryset.update(available=False)
    make_unavailable.short_description = "Сделать выбранные товары недоступными"