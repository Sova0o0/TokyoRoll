# admin_panel/views.py (полностью переработанный dashboard)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Count, Sum, Q
from django.core.cache import cache
from .decorators import admin_required
from main.models import Category, Product
from orders.models import Order, OrderItem, PromoCode
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def admin_login(request):
    """Страница входа в админ-панель"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_panel:dashboard')
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                phone = username.replace('+', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
                if phone.startswith('7'):
                    phone = phone[1:]
                try:
                    user = User.objects.get(username=phone)
                except User.DoesNotExist:
                    pass
        
        if user:
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user and (auth_user.is_staff or auth_user.is_superuser):
                login(request, auth_user)
                return redirect('admin_panel:dashboard')
            else:
                error = 'Неверный пароль или недостаточно прав'
        else:
            error = 'Пользователь не найден'
    
    return render(request, 'admin_panel/login.html', {'error': error})

def admin_logout(request):
    logout(request)
    return redirect('admin_panel:login')

@admin_required
def dashboard(request):
    """Главная страница админ-панели - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ"""
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # ✅ Все агрегации в одном запросе
    stats = Order.objects.aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total_price'),
        today_orders=Count('id', filter=Q(created_at__date=today)),
        today_revenue=Sum('total_price', filter=Q(created_at__date=today)),
        week_orders=Count('id', filter=Q(created_at__date__gte=week_ago)),
    )
    
    # ✅ Простые счетчики (очень быстрые)
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    
    # ✅ Статусы одним запросом
    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    order_statuses = {item['status']: item['count'] for item in status_counts}
    for status in ['new', 'preparing', 'delivering', 'completed', 'cancelled']:
        order_statuses.setdefault(status, 0)
    
    # ✅ ИСПРАВЛЕНО: убираем .only(), оставляем только select_related
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        'total_orders': stats['total_orders'] or 0,
        'total_users': total_users,
        'total_products': total_products,
        'total_categories': total_categories,
        'today_orders': stats['today_orders'] or 0,
        'week_orders': stats['week_orders'] or 0,
        'total_revenue': stats['total_revenue'] or 0,
        'today_revenue': stats['today_revenue'] or 0,
        'recent_orders': recent_orders,
        'order_statuses': order_statuses,
    }
    return render(request, 'admin_panel/dashboard.html', context)

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ ==========
@admin_required
def orders_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Поиск по имени или телефону
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(customer_name__icontains=search.lower()) |
            Q(customer_name__icontains=search.upper()) |
            Q(customer_name__icontains=search.capitalize()) |
            Q(phone__icontains=search) |
            Q(user__username__icontains=search.lower()) |
            Q(user__username__icontains=search.upper()) |
            Q(user__username__icontains=search.capitalize())
        )
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Фильтр по типу доставки
    delivery_type = request.GET.get('delivery_type')
    if delivery_type:
        orders = orders.filter(delivery_type=delivery_type)
    
    # Фильтр по дате
    date_from = request.GET.get('date_from')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    return render(request, 'admin_panel/orders/list.html', {'orders': orders})

@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_panel/orders/detail.html', {'order': order})

@admin_required
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()
        return redirect('admin_panel:order_detail', order_id=order.id)
    return render(request, 'admin_panel/orders/edit.html', {'order': order})

@admin_required
def products_list(request):
    products = Product.objects.select_related('category').all().order_by('-id')
    
    # Поиск по названию
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search.lower()) |
            Q(name__icontains=search.upper()) |
            Q(name__icontains=search.capitalize())
        )
    
    # Фильтр по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Фильтр по наличию
    available = request.GET.get('available')
    if available == 'yes':
        products = products.filter(available=True)
    elif available == 'no':
        products = products.filter(available=False)
    
    # Получаем все категории для выпадающего списка
    categories = Category.objects.all().order_by('order', 'name')
    
    return render(request, 'admin_panel/products/list.html', {
        'products': products,
        'categories': categories
    })

@admin_required
def product_add(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        price = request.POST.get('price')
        weight = request.POST.get('weight', 0)
        pieces = request.POST.get('pieces', 0)
        composition = request.POST.get('composition', '')
        available = request.POST.get('available') == 'on'
        
        product = Product.objects.create(
            category_id=category_id,
            name=name,
            price=price,
            weight=weight,
            pieces=pieces,
            composition=composition,
            available=available
        )
        
        if request.FILES.get('image'):
            product.image = request.FILES['image']
            product.save()
        
        return redirect('admin_panel:products_list')
    
    categories = Category.objects.all()
    return render(request, 'admin_panel/products/add.html', {'categories': categories})

@admin_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.category_id = request.POST.get('category')
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.weight = request.POST.get('weight', 0)
        product.pieces = request.POST.get('pieces', 0)
        product.composition = request.POST.get('composition', '')
        product.available = request.POST.get('available') == 'on'
        
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        
        product.save()
        return redirect('admin_panel:products_list')
    
    categories = Category.objects.all()
    return render(request, 'admin_panel/products/edit.html', {'product': product, 'categories': categories})

@admin_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_panel:products_list')
    return render(request, 'admin_panel/products/delete.html', {'product': product})

@admin_required
def categories_list(request):
    categories = Category.objects.all().order_by('order')
    return render(request, 'admin_panel/categories/list.html', {'categories': categories})

@admin_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        order = request.POST.get('order', 0)
        category = Category.objects.create(name=name, order=order)
        if request.FILES.get('image'):
            category.image = request.FILES['image']
            category.save()
        return redirect('admin_panel:categories_list')
    return render(request, 'admin_panel/categories/add.html')

@admin_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.order = request.POST.get('order', 0)
        if request.FILES.get('image'):
            category.image = request.FILES['image']
        category.save()
        return redirect('admin_panel:categories_list')
    return render(request, 'admin_panel/categories/edit.html', {'category': category})

@admin_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('admin_panel:categories_list')
    return render(request, 'admin_panel/categories/delete.html', {'category': category})

@admin_required
def promocodes_list(request):
    promocodes = PromoCode.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/promocodes/list.html', {'promocodes': promocodes})

@admin_required
def promocode_add(request):
    if request.method == 'POST':
        promo = PromoCode.objects.create(
            code=request.POST.get('code').upper(),
            discount_type=request.POST.get('discount_type'),
            discount_value=request.POST.get('discount_value'),
            min_order_amount=request.POST.get('min_order_amount', 0),
            max_discount=request.POST.get('max_discount', 0),
            valid_from=request.POST.get('valid_from'),
            valid_to=request.POST.get('valid_to'),
            max_uses=request.POST.get('max_uses', 1),
            is_active=request.POST.get('is_active') == 'on',
            only_first_order=request.POST.get('only_first_order') == 'on',
        )
        return redirect('admin_panel:promocodes_list')
    return render(request, 'admin_panel/promocodes/add.html')

@admin_required
def promocode_edit(request, promocode_id):
    promo = get_object_or_404(PromoCode, id=promocode_id)
    if request.method == 'POST':
        promo.code = request.POST.get('code').upper()
        promo.discount_type = request.POST.get('discount_type')
        promo.discount_value = request.POST.get('discount_value')
        promo.min_order_amount = request.POST.get('min_order_amount', 0)
        promo.max_discount = request.POST.get('max_discount', 0)
        promo.valid_from = request.POST.get('valid_from')
        promo.valid_to = request.POST.get('valid_to')
        promo.max_uses = request.POST.get('max_uses', 1)
        promo.is_active = request.POST.get('is_active') == 'on'
        promo.only_first_order = request.POST.get('only_first_order') == 'on'
        promo.save()
        return redirect('admin_panel:promocodes_list')
    return render(request, 'admin_panel/promocodes/edit.html', {'promo': promo})

@admin_required
def promocode_delete(request, promocode_id):
    promo = get_object_or_404(PromoCode, id=promocode_id)
    if request.method == 'POST':
        promo.delete()
        return redirect('admin_panel:promocodes_list')
    return render(request, 'admin_panel/promocodes/delete.html', {'promo': promo})

@admin_required
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Поиск по пользователям
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search.lower()) |
            Q(username__icontains=search.upper()) |
            Q(username__icontains=search.capitalize()) |
            Q(email__icontains=search.lower()) |
            Q(email__icontains=search.upper()) |
            Q(email__icontains=search.capitalize()) |
            Q(first_name__icontains=search.lower()) |
            Q(first_name__icontains=search.upper()) |
            Q(first_name__icontains=search.capitalize()) |
            Q(last_name__icontains=search.lower()) |
            Q(last_name__icontains=search.upper()) |
            Q(last_name__icontains=search.capitalize())
        )
    
    return render(request, 'admin_panel/users/list.html', {'users': users})

@admin_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    from django.db.models import Sum
    total_spent = orders.aggregate(total=Sum('total_price'))['total'] or 0
    
    return render(request, 'admin_panel/users/detail.html', {
        'user': user,
        'orders': orders,
        'total_spent': total_spent
    })

@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Обновляем основные данные
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        
        # Обновляем права (is_staff - админ, is_superuser - суперпользователь)
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        user.save()
        
        # Обновление пароля
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
        
        # Обновление адресов доставки (если есть модель UserProfile)
        address = request.POST.get('address')
        if address and hasattr(user, 'profile'):
            user.profile.address = address
            user.profile.save()
        
        return redirect('admin_panel:user_detail', user_id=user.id)
    
    return render(request, 'admin_panel/users/edit.html', {'user': user})

@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        return redirect('admin_panel:users_list')
    
    return render(request, 'admin_panel/users/delete.html', {'user': user})