from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'created_at']
    list_filter = ['created_at']
    inlines = [CartItemInline]
    readonly_fields = ['created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'total_price', 'added_at']
    list_filter = ['cart', 'product']
    search_fields = ['product__name']
    readonly_fields = ['added_at']

    def total_price(self, obj):
        return obj.total_price()
    total_price.short_description = 'Сумма'