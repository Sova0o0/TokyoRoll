from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, PromoCode, PromoCodeUsage
from cart.models import Cart, CartItem
from datetime import datetime
from django.utils import timezone
import json

def check_working_hours():
    now = datetime.now()
    current_hour = now.hour
    return 10 <= current_hour < 23

@csrf_exempt
def check_promo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            promocode = data.get('promocode', '').upper()
            order_amount = float(data.get('order_amount', 0))
            
            print(f"=== ПРОВЕРКА ПРОМОКОДА ===")
            print(f"Код: {promocode}")
            print(f"Сумма: {order_amount}")
            print(f"Пользователь авторизован: {request.user.is_authenticated}")
            
            try:
                promo = PromoCode.objects.get(code=promocode)
                print(f"Найден промокод: {promo.code}")
                print(f"only_first_order: {promo.only_first_order}")
                
                # Проверка на первый заказ (только если промокод помечен как only_first_order)
                if promo.only_first_order and request.user.is_authenticated:
                    # Проверяем, был ли у пользователя уже ЗАВЕРШЕННЫЙ заказ
                    user_orders = Order.objects.filter(
                        user=request.user
                    ).exclude(status='cancelled')
                    
                    print(f"Количество заказов пользователя: {user_orders.count()}")
                    
                    if user_orders.exists():
                        return JsonResponse({
                            'valid': False,
                            'message': 'Этот промокод доступен только для первого заказа'
                        })
                    
                    # Проверяем, не использовал ли пользователь уже этот промокод
                    if PromoCodeUsage.objects.filter(user=request.user, promocode=promo).exists():
                        return JsonResponse({
                            'valid': False,
                            'message': 'Вы уже использовали этот промокод'
                        })
                
                # Остальные проверки (срок действия, лимиты и т.д.)
                if promo.is_valid(order_amount):
                    discount = promo.calculate_discount(order_amount)
                    print(f"✅ Промокод валиден! Скидка: {discount}")
                    return JsonResponse({
                        'valid': True,
                        'discount': float(discount),
                        'message': f'Промокод применен! Скидка: {discount:.0f} ₽'
                    })
                else:
                    print(f"❌ Промокод не прошел валидацию")
                    return JsonResponse({
                        'valid': False,
                        'message': 'Промокод недействителен или истек срок действия'
                    })
                    
            except PromoCode.DoesNotExist:
                print(f"❌ Промокод {promocode} не найден")
                return JsonResponse({'valid': False, 'message': 'Промокод не найден'})
                
        except Exception as e:
            print(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'valid': False, 'message': f'Ошибка: {str(e)}'})
    
    return JsonResponse({'valid': False, 'message': 'Метод не разрешен'})

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        # Проверка времени работы
        if not check_working_hours():
            return JsonResponse({
                'success': False,
                'closed': True,
                'message': 'Мы сейчас закрыты. Режим работы: с 10:00 до 23:00. Загляните к нам позже.'
            })
        
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        comment = request.POST.get('comment', '')
        delivery_type = request.POST.get('delivery_type', 'delivery')
        promocode = request.POST.get('promocode', '')
        final_total = request.POST.get('total', 0)
        
        print(f"=== СОЗДАНИЕ ЗАКАЗА ===")
        print(f"Пользователь: {request.user}")
        print(f"Промокод: {promocode}")
        print(f"Сумма: {final_total}")
        
        # Получаем корзину
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()
        
        if not cart:
            return JsonResponse({'success': False, 'message': 'Корзина пуста'})
        
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return JsonResponse({'success': False, 'message': 'Корзина пуста'})
        
        # Рассчитываем сумму товаров
        subtotal = 0
        for item in cart_items:
            subtotal += item.product.price * item.quantity
        
        # Рассчитываем скидку по промокоду
        discount_amount = 0
        if promocode:
            try:
                promo = PromoCode.objects.get(code=promocode.upper())
                if promo.is_valid(subtotal):
                    discount_amount = promo.calculate_discount(subtotal)
                    print(f"Скидка по промокоду: {discount_amount}")
            except PromoCode.DoesNotExist:
                pass
        
        # Создаем заказ
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            phone=phone,
            address=address if delivery_type == 'delivery' else 'Самовывоз',
            comment=comment,
            promocode=promocode,
            discount_amount=discount_amount,
            total_price=final_total,
            delivery_type=delivery_type
        )
        
        print(f"Заказ создан: #{order.id}")
        
        # Добавляем товары в заказ
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            print(f"Добавлен товар: {item.product.name} x {item.quantity}")
        
        # Если использован промокод и пользователь авторизован, создаем запись об использовании
        if promocode and request.user.is_authenticated:
            try:
                promo = PromoCode.objects.get(code=promocode.upper())
                PromoCodeUsage.objects.create(
                    user=request.user,
                    promocode=promo,
                    order=order
                )
                # Увеличиваем счетчик использований
                promo.used_count += 1
                promo.save()
                print(f"Запись об использовании промокода создана")
            except PromoCode.DoesNotExist:
                print(f"Промокод {promocode} не найден при сохранении")
            except Exception as e:
                print(f"Ошибка при сохранении использования промокода: {e}")
        
        # Очищаем корзину
        cart_items.delete()
        print("Корзина очищена")
        
        return JsonResponse({'success': True, 'order_id': order.id})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})

@csrf_exempt
def repeat_order(request, order_id):
    if request.method == 'POST':
        try:
            old_order = Order.objects.get(id=order_id)
            
            # Получаем или создаем корзину
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            
            # Копируем товары из заказа в корзину
            for item in old_order.items.all():
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()
            
            return JsonResponse({'success': True, 'message': 'Товары добавлены в корзину'})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Заказ не найден'})
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})