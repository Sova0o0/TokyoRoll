from django.contrib import admin
from .models import UserProfile, Address

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'avatar']
    search_fields = ['user__username', 'user__first_name', 'phone']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'address', 'is_default']
    list_filter = ['is_default']
    search_fields = ['user__username', 'title', 'address']