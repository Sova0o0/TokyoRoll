from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .models import UserProfile, Address
import random
import string
import json

# Временное хранилище для кодов восстановления
recovery_codes = {}

def generate_recovery_code():
    return ''.join(random.choices(string.digits, k=6))

# ========== ОСНОВНАЯ СТРАНИЦА ПРОФИЛЯ ==========
@login_required
def profile_view(request):
    # Получаем или создаем профиль
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Если профиль только что создан, заполняем телефон из username
    if created and request.user.username:
        profile.phone = request.user.username
        profile.save()
    
    # Проверяем, что аватар существует физически (если есть в БД)
    if profile.avatar and profile.avatar.name:
        import os
        from django.conf import settings
        avatar_path = os.path.join(settings.MEDIA_ROOT, profile.avatar.name)
        if not os.path.exists(avatar_path):
            profile.avatar = None
            profile.save()
    
    # Получаем заказы пользователя
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Получаем адреса пользователя
    addresses = Address.objects.filter(user=request.user)
    
    # Обновляем username из телефона, если он пустой (для старых пользователей)
    if not request.user.username and profile.phone:
        request.user.username = profile.phone
        request.user.save()
    
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': profile,
        'orders': orders,
        'addresses': addresses,
    })

# ========== ОБНОВЛЕНИЕ ПРОФИЛЯ ==========
@login_required
def update_profile(request):
    if request.method == 'POST':
        # Обновляем основные данные
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Обновляем профиль
        profile = request.user.profile
        profile.phone = request.POST.get('phone', '')
        profile.save()
        
        # Обновляем пароль
        new_password = request.POST.get('new_password')
        if new_password:
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
        
        return JsonResponse({'success': True, 'message': 'Профиль обновлен'})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})

# ========== УПРАВЛЕНИЕ АДРЕСАМИ ==========
@login_required
def add_address(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        entrance = request.POST.get('entrance', '')
        floor = request.POST.get('floor', '')
        apartment = request.POST.get('apartment', '')
        comment = request.POST.get('comment', '')
        is_default = request.POST.get('is_default') == 'on'
        
        # Если адрес по умолчанию, снимаем флаг с других
        if is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        Address.objects.create(
            user=request.user,
            title=title,
            address=address,
            entrance=entrance,
            floor=floor,
            apartment=apartment,
            comment=comment,
            is_default=is_default
        )
        
        return JsonResponse({'success': True, 'message': 'Адрес добавлен'})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.title = request.POST.get('title')
        address.address = request.POST.get('address')
        address.entrance = request.POST.get('entrance', '')
        address.floor = request.POST.get('floor', '')
        address.apartment = request.POST.get('apartment', '')
        address.comment = request.POST.get('comment', '')
        is_default = request.POST.get('is_default') == 'on'
        
        if is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
        else:
            address.is_default = False
        
        address.save()
        return JsonResponse({'success': True, 'message': 'Адрес обновлен'})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})

@login_required
def delete_address(request, address_id):
    if request.method == 'POST':
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True, 'message': 'Адрес удален'})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})

@login_required
def set_default_address(request, address_id):
    if request.method == 'POST':
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.is_default = True
        address.save()
        return JsonResponse({'success': True, 'message': 'Адрес установлен по умолчанию'})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})

# ========== АУТЕНТИФИКАЦИЯ (ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ) ==========
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').replace('+7', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=phone)
            if user.check_password(password):
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Вход выполнен успешно'})
            else:
                return JsonResponse({'success': False, 'message': 'Неверный пароль'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'})
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').replace('+7', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not name:
            return JsonResponse({'success': False, 'message': 'Введите имя'})
        
        if len(phone) != 10:
            return JsonResponse({'success': False, 'message': 'Введите корректный номер телефона'})
        
        if len(password) < 4:
            return JsonResponse({'success': False, 'message': 'Пароль должен содержать минимум 4 символа'})
        
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Пароли не совпадают'})
        
        if User.objects.filter(username=phone).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким телефоном уже существует'})
        
        try:
            # Создаём пользователя
            user = User.objects.create_user(
                username=phone,
                password=password,
                first_name=name
            )
            
            # Автоматически создаём профиль (телефон уже есть в username)
            # Сигнал create_user_profile должен сработать, но на всякий случай проверим
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profile.phone = phone
                profile.save()
            
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Регистрация успешна!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка регистрации: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Выход выполнен'})

@csrf_exempt
def send_recovery_code(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').replace('+7', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        code = generate_recovery_code()
        recovery_codes[phone] = code
        return JsonResponse({
            'success': True, 
            'message': f'Код отправлен (демо: {code})'
        })
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').replace('+7', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        code = request.POST.get('code', '')
        new_password = request.POST.get('new_password', '')
        
        if phone in recovery_codes and recovery_codes[phone] == code:
            try:
                user = User.objects.get(username=phone)
                user.set_password(new_password)
                user.save()
                del recovery_codes[phone]
                return JsonResponse({'success': True, 'message': 'Пароль успешно изменен'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Пользователь не найден'})
        else:
            return JsonResponse({'success': False, 'message': 'Неверный код подтверждения'})
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})