from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Category, Product
from cart.models import Cart, CartItem

def get_cart(request):
    """Получаем или создаем корзину"""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def home(request):
    categories = Category.objects.prefetch_related('product_set').all()
    
    # Получаем популярные сеты (первые 3 из категории "Сеты")
    popular_sets = []
    try:
        sets_category = Category.objects.get(name='Сеты')
        popular_sets = Product.objects.filter(category=sets_category, available=True)[:3]
        print(f"Найдено популярных сетов: {len(popular_sets)}")
    except Category.DoesNotExist:
        print("Категория 'Сеты' не найдена")
    
    # Получаем количество товаров в корзине
    cart_count = 0
    if request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart:
            cart_count = sum(item.quantity for item in cart.items.all())
    
    return render(request, 'main/home.html', {
        'categories': categories,
        'popular_sets': popular_sets,
        'cart_count': cart_count,
    })

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, available=True)
    
    return render(request, 'main/category.html', {
        'category': category,
        'products': products
    })

def get_category_products(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        products = Product.objects.filter(category=category, available=True)
        data = {
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': str(p.price),
                    'weight': p.weight,
                    'pieces': p.pieces,
                    'composition': p.composition
                }
                for p in products
            ]
        }
        return JsonResponse(data)
    except Category.DoesNotExist:
        return JsonResponse({'products': []})