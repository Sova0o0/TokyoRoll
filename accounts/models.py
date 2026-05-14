from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=100, verbose_name="Название (например, Дом, Работа)")
    address = models.TextField(verbose_name="Адрес")
    entrance = models.CharField(max_length=10, blank=True, verbose_name="Подъезд")
    floor = models.CharField(max_length=10, blank=True, verbose_name="Этаж")
    apartment = models.CharField(max_length=10, blank=True, verbose_name="Квартира")
    comment = models.CharField(max_length=200, blank=True, verbose_name="Комментарий для курьера")
    is_default = models.BooleanField(default=False, verbose_name="Адрес по умолчанию")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.address[:50]}"
    
    class Meta:
        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"
        ordering = ['-is_default', '-created_at']