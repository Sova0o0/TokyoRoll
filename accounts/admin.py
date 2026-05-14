from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Address

class UserProfileInline(admin.StackedInline):
    """Встраиваем профиль прямо в страницу пользователя"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ['phone', 'avatar']

class CustomUserAdmin(UserAdmin):
    """Расширенная админка пользователя с профилем"""
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_phone(self, obj):
        """Показываем телефон из профиля в списке пользователей"""
        if hasattr(obj, 'profile') and obj.profile.phone:
            return obj.profile.phone
        return '-'
    get_phone.short_description = 'Телефон'
    get_phone.admin_order_field = 'profile__phone'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'avatar']
    search_fields = ['user__username', 'user__first_name', 'phone']
    list_filter = ['phone']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'address', 'is_default']
    list_filter = ['is_default']
    search_fields = ['user__username', 'title', 'address']

# Перерегистрируем модель User с нашей расширенной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)