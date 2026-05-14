from django.contrib import admin
from .models import Order, OrderItem, PromoCode, PromoCodeUsage

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'phone', 'total_price', 'status', 'delivery_type', 'created_at']
    list_filter = ['status', 'created_at', 'delivery_type']
    search_fields = ['customer_name', 'phone', 'id']
    readonly_fields = ['created_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('customer_name', 'phone', 'address', 'comment', 'delivery_type')
        }),
        ('Финансы', {
            'fields': ('total_price', 'promocode', 'discount_amount')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_amount', 'only_first_order', 'valid_from', 'valid_to', 'max_uses', 'used_count', 'is_active']
    list_filter = ['discount_type', 'is_active', 'only_first_order', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['used_count', 'created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('code', 'discount_type', 'discount_value', 'is_active', 'only_first_order')
        }),
        ('Условия', {
            'fields': ('min_order_amount', 'max_discount')
        }),
        ('Срок действия', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Лимиты', {
            'fields': ('max_uses', 'used_count')
        }),
    )

@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'promocode', 'used_at', 'order']
    list_filter = ['used_at', 'promocode']
    search_fields = ['user__username', 'promocode__code']
    readonly_fields = ['used_at']