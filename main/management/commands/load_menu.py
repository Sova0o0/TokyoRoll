from django.core.management.base import BaseCommand
from main.models import Category, Product

class Command(BaseCommand):
    help = 'Загружает начальное меню'

    def handle(self, *args, **options):
        # Создаём категории
        categories_data = [
            {'name': 'Сеты', 'slug': 'sety', 'order': 1},
            {'name': 'Роллы', 'slug': 'rolls', 'order': 2},
            {'name': 'Жареные роллы', 'slug': 'zharenye-rolls', 'order': 3},
            {'name': 'Запеченные роллы', 'slug': 'zapechennye-rolls', 'order': 4},
            {'name': 'Классические роллы', 'slug': 'classic-rolls', 'order': 5},
            {'name': 'Суши', 'slug': 'sushi', 'order': 6},
            {'name': 'Закуски', 'slug': 'zakuski', 'order': 7},
            {'name': 'Соусы и дополнения', 'slug': 'sauces', 'order': 8},
        ]
        for cat_data in categories_data:
            Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
        self.stdout.write('Категории созданы')

        # Данные для продуктов (пример, можно расширить)
        products_data = [
            # Сеты (10 штук)
            {'category_slug': 'sety', 'name': 'Сет "Императорский"', 'composition': 'Филадельфия (4шт), Калифорния (4шт), Угорь (4шт), Лосось (4шт), Горячие роллы (8шт), Запеченные (8шт)', 'price': 2490, 'weight': 1250, 'pieces': 32, 'order': 1},
            {'category_slug': 'sety', 'name': 'Сет "Самурай"', 'composition': 'Филадельфия (6шт), Калифорния (6шт), Теплые роллы (6шт), Запеченные (6шт)', 'price': 1990, 'weight': 980, 'pieces': 24, 'order': 2},
            {'category_slug': 'sety', 'name': 'Сет "Токио"', 'composition': 'Угорь (4шт), Лосось (4шт), Креветка (4шт), Том Ям ролл (4шт), Филадельфия (4шт)', 'price': 2190, 'weight': 1100, 'pieces': 20, 'order': 3},
            {'category_slug': 'sety', 'name': 'Сет "Вегетарианский"', 'composition': 'Аво-ролл (4шт), Овощной (4шт), С огурцом (4шт), С помидором (4шт), С сыром (4шт)', 'price': 1290, 'weight': 850, 'pieces': 20, 'order': 4},
            {'category_slug': 'sety', 'name': 'Сет "Острый"', 'composition': 'Острая Калифорния (6шт), Острый лосось (6шт), Острый угорь (6шт), Спайси ролл (6шт)', 'price': 1790, 'weight': 920, 'pieces': 24, 'order': 5},
            {'category_slug': 'sety', 'name': 'Сет "Для компании"', 'composition': 'Филадельфия (8шт), Калифорния (8шт), Угорь (8шт), Лосось (8шт), Креветка (8шт), Запеченный (8шт)', 'price': 3490, 'weight': 1800, 'pieces': 48, 'order': 6},
            {'category_slug': 'sety', 'name': 'Сет "Премиум"', 'composition': 'Угорь с авокадо (4шт), Лосось с трюфелем (4шт), Креветка с манго (4шт), Филадельфия с лососем (4шт), Калифорния с икрой (4шт)', 'price': 2890, 'weight': 1350, 'pieces': 20, 'order': 7},
            {'category_slug': 'sety', 'name': 'Сет "Детский"', 'composition': 'Нежный ролл с курицей (4шт), Ролл с огурцом (4шт), Ролл с сыром (4шт), Мини-суши (4шт)', 'price': 990, 'weight': 600, 'pieces': 16, 'order': 8},
            {'category_slug': 'sety', 'name': 'Сет "Ролломания"', 'composition': 'Горячий ролл (6шт), Жареный ролл (6шт), Запеченный ролл (6шт), Теплый ролл (6шт)', 'price': 1590, 'weight': 880, 'pieces': 24, 'order': 9},
            {'category_slug': 'sety', 'name': 'Сет "Фирменный"', 'composition': 'Секретный ролл шефа (8шт), Филадельфия с угрем (8шт), Калифорния с креветкой (8шт)', 'price': 2390, 'weight': 1200, 'pieces': 24, 'order': 10},
            
            # Роллы (пример 20 штук) - добавь по аналогии, здесь сокращённо
            {'category_slug': 'rolls', 'name': 'Филадельфия', 'composition': 'Лосось, сливочный сыр, огурец, авокадо', 'price': 490, 'weight': 240, 'pieces': 8, 'order': 1},
            {'category_slug': 'rolls', 'name': 'Калифорния', 'composition': 'Краб, авокадо, огурец, икра тобико', 'price': 450, 'weight': 220, 'pieces': 8, 'order': 2},
            # ... и так далее до 20 роллов. Для экономии места я не пишу все 20, но ты можешь добавить.
        ]
        for prod in products_data:
            category = Category.objects.get(slug=prod['category_slug'])
            Product.objects.get_or_create(
                category=category,
                name=prod['name'],
                defaults={
                    'composition': prod.get('composition', ''),
                    'price': prod['price'],
                    'weight': prod.get('weight', 0),
                    'pieces': prod.get('pieces', 0),
                    'order': prod.get('order', 0),
                }
            )
        self.stdout.write('Продукты загружены')