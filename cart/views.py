from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from main.models import Product
from accounts.models import Address 
from datetime import datetime
import json

PICKUP_ADDRESSES = [
    {
        'id': 1,
        'name': 'Ресторан на Ленина',
        'address': 'Улица Ленина 23',
        'schedule': 'Пн-Вс с 10:00 до 23:00',
        'phone': '8-920-267-11-44',
    },
    {
        'id': 2,
        'name': 'Ресторан на Садовой',
        'address': 'Улица Садовая 11',
        'schedule': 'Пн-Вс с 10:00 до 22:00',
        'phone': '8-920-729-22-77',
    },
    {
        'id': 3,
        'name': 'Ресторан на Кулакова',
        'address': 'Проспект Кулакова 4',
        'schedule': 'Пн-Вс с 10:00 до 23:00',
        'phone': '8-920-708-22-88',
    },
]

def get_cart(request):
    """Получаем или создаем корзину"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def check_working_hours():
    now = datetime.now()
    current_hour = now.hour
    if current_hour < 10 or current_hour >= 23:
        return False
    return True

def submit_order(request):
    if request.method == 'POST':
        if not check_working_hours():
            return JsonResponse({
                'success': False, 
                'closed': True,
                'message': 'Мы сейчас закрыты. Режим работы: с 10:00 до 23:00. Загляните к нам завтра! 🌙'
            })

def cart_view(request):
    """Страница корзины"""
    cart = get_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    
    total = 0
    cart_count = 0
    for item in cart_items:
        total += item.product.price * item.quantity
        cart_count += item.quantity
    
    user_addresses = []
    default_address = None
    user_data = {
        'name': '',
        'phone': '',
    }
    
    if request.user.is_authenticated:
        user_addresses = Address.objects.filter(user=request.user)
        default_address = user_addresses.filter(is_default=True).first()
        
        # Заполняем данные пользователя для автозаполнения
        if request.user.first_name or request.user.last_name:
            user_data['name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        elif request.user.username:
            user_data['name'] = request.user.username
        
        # Телефон (может быть в профиле или в username)
        if hasattr(request.user, 'profile') and request.user.profile.phone:
            user_data['phone'] = request.user.profile.phone
        elif request.user.username and request.user.username.isdigit():
            user_data['phone'] = request.user.username
        
        # Адрес по умолчанию
        if default_address:
            user_data['address'] = default_address.address
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_count,
        'user_authenticated': request.user.is_authenticated,
        'user_data': user_data,
        'user_name': request.user.first_name if request.user.is_authenticated else '',
        'user_addresses': user_addresses,
        'default_address': default_address,
        'pickup_addresses': PICKUP_ADDRESSES,
    })

@login_required
def update_user_data(request):
    """Обновление данных пользователя из корзины (только имя и телефон)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            name = data.get('name', '')
            phone = data.get('phone', '')
            
            # Обновляем имя
            if name:
                name_parts = name.split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                else:
                    user.last_name = ''
                user.save()
            
            # Обновляем телефон в профиле
            if phone:
                if hasattr(user, 'profile'):
                    user.profile.phone = phone
                    user.profile.save()
            
            return JsonResponse({'success': True, 'message': 'Данные сохранены'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'}, status=405)

@csrf_exempt
def add_to_cart(request):
    """Добавление товара в корзину"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = int(data.get('product_id'))
            quantity = int(data.get('quantity', 1))
            
            product = Product.objects.get(id=product_id, available=True)
            
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = sum(item.quantity for item in cart_items)
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} добавлен в корзину',
                'cart_count': cart_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'}, status=405)

@csrf_exempt
def update_cart_item(request, item_id):
    """Обновление количества товара"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            cart_item = get_object_or_404(CartItem, id=item_id)
            
            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            elif action == 'delete':
                cart_item.delete()
                cart_item = None
            
            if cart_item:
                cart_item.save()
            
            cart = get_cart(request)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = sum(item.quantity for item in cart_items)
            request.session['cart_count'] = cart_count
            
            return JsonResponse({'success': True, 'cart_count': cart_count})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'}, status=405)

def clear_cart(request):
    """Очистка корзины"""
    cart = get_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    request.session['cart_count'] = 0
    return redirect('cart')

def get_cart_count(request):
    """Получение количества товаров в корзине (для AJAX)"""
    cart = get_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = sum(item.quantity for item in cart_items)
    return JsonResponse({'cart_count': cart_count})