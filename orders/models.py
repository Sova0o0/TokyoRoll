from django.db import models
from django.contrib.auth.models import User
from main.models import Product

class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Процент'),
        ('fixed', 'Фиксировантная сумма'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percent', verbose_name="Тип скидки")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Значение скидки")
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Минимальная сумма заказа")
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Максимальная скидка (для процентов)")
    valid_from = models.DateTimeField(verbose_name="Действует с")
    valid_to = models.DateTimeField(verbose_name="Действует до")
    max_uses = models.IntegerField(default=1, verbose_name="Максимум использований")
    used_count = models.IntegerField(default=0, verbose_name="Использовано раз")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    only_first_order = models.BooleanField(default=False, verbose_name="Только для первого заказа")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
    
    def __str__(self):
        return self.code
    
    def is_valid(self, order_amount):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_to and
                self.used_count < self.max_uses and
                order_amount >= self.min_order_amount)
    
    def calculate_discount(self, order_amount):
        discount_value = float(self.discount_value)
        order_amount = float(order_amount)
        
        if self.discount_type == 'percent':
            discount = order_amount * (discount_value / 100)
            if self.max_discount and float(self.max_discount) > 0:
                discount = min(discount, float(self.max_discount))
            return discount
        else:
            return min(discount_value, order_amount)


class PromoCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_usage')
    promocode = models.ForeignKey('PromoCode', on_delete=models.CASCADE, related_name='usages')
    used_at = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField('Order', on_delete=models.CASCADE, null=True, blank=True, related_name='promo_usage_detail')
    
    class Meta:
        unique_together = ['user', 'promocode']  
        verbose_name = "Использование промокода"
        verbose_name_plural = "Использования промокодов"
    
    def __str__(self):
        return f"{self.user.username} - {self.promocode.code}"


class Order(models.Model):
    DELIVERY_CHOICES = [
        ('delivery', 'Доставка'),
        ('pickup', 'Самовывоз'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('preparing', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    comment = models.TextField(blank=True, verbose_name="Комментарий к заказу")
    promocode = models.CharField(max_length=50, blank=True, verbose_name="Промокод")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Скидка")
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='delivery', verbose_name="Тип доставки")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"