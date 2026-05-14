import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TokyoRoll.settings')
django.setup()

from main.models import Category, Product

# Данные для товаров
products_data = [
    # Сеты
    {'category': 'Сеты', 'name': 'Сет "Филадельфия"', 'composition': 'Филадельфия (8шт), Калифорния (8шт), с угрем (8шт), с лососем (8шт)', 'price': 1890, 'weight': 960, 'pieces': 32},
    {'category': 'Сеты', 'name': 'Сет "Калифорния"', 'composition': 'Калифорния (24шт)', 'price': 1490, 'weight': 720, 'pieces': 24},
    {'category': 'Сеты', 'name': 'Сет "Токио"', 'composition': 'Угорь (10шт), Лосось (10шт), Тунец (10шт), Креветка (10шт)', 'price': 2190, 'weight': 1200, 'pieces': 40},
    {'category': 'Сеты', 'name': 'Сет "Императорский"', 'composition': 'Филадельфия (8шт), Калифорния (8шт), Угорь (8шт), Лосось (8шт), Креветка (8шт)', 'price': 2590, 'weight': 1350, 'pieces': 40},
    {'category': 'Сеты', 'name': 'Сет "Самурай"', 'composition': 'Филадельфия (6шт), Калифорния (6шт), с угрем (6шт), запеченный (6шт)', 'price': 1690, 'weight': 850, 'pieces': 24},
    {'category': 'Сеты', 'name': 'Сет "Вегетарианский"', 'composition': 'Аво-ролл (6шт), Овощной (6шт), с огурцом (6шт), с сыром (6шт)', 'price': 1290, 'weight': 780, 'pieces': 24},
    {'category': 'Сеты', 'name': 'Сет "Острый"', 'composition': 'Острая Калифорния (8шт), Острый лосось (8шт), Острый угорь (8шт)', 'price': 1790, 'weight': 720, 'pieces': 24},
    {'category': 'Сеты', 'name': 'Сет "Детский"', 'composition': 'Нежный ролл с курицей (4шт), Ролл с огурцом (4шт), Ролл с сыром (4шт)', 'price': 890, 'weight': 450, 'pieces': 12},
    {'category': 'Сеты', 'name': 'Сет "Ролломания"', 'composition': 'Горячий ролл (8шт), Жареный ролл (8шт), Запеченный ролл (8шт)', 'price': 1590, 'weight': 780, 'pieces': 24},
    {'category': 'Сеты', 'name': 'Сет "Премиум"', 'composition': 'Филадельфия с трюфелем (4шт), Калифорния с икрой (4шт), Угорь с авокадо (4шт), Лосось с манго (4шт)', 'price': 2890, 'weight': 1100, 'pieces': 16},
    
    # Роллы (примеры)
    {'category': 'Роллы', 'name': 'Филадельфия', 'composition': 'Лосось, сливочный сыр, огурец, авокадо', 'price': 490, 'weight': 240, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Калифорния', 'composition': 'Краб, авокадо, огурец, икра тобико', 'price': 450, 'weight': 220, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Унаги (с угрем)', 'composition': 'Угорь, огурец, соус унаги', 'price': 520, 'weight': 230, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Том Ям', 'composition': 'Креветка, авокадо, огурец, острый соус', 'price': 550, 'weight': 240, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Спайси лосось', 'composition': 'Лосось, огурец, спайси соус', 'price': 480, 'weight': 230, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Спайси тунец', 'composition': 'Тунец, авокадо, спайси соус', 'price': 500, 'weight': 230, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Аво-ролл', 'composition': 'Авокадо, огурец, кунжут', 'price': 350, 'weight': 200, 'pieces': 8},
    {'category': 'Роллы', 'name': 'Овощной', 'composition': 'Огурец, перец, морковь, салат', 'price': 380, 'weight': 210, 'pieces': 8},
    
    # Жареные роллы
    {'category': 'Жареные роллы', 'name': 'Жареная Филадельфия', 'composition': 'Лосось, сливочный сыр, авокадо, панировка', 'price': 520, 'weight': 250, 'pieces': 8},
    {'category': 'Жареные роллы', 'name': 'Жареная Калифорния', 'composition': 'Краб, авокадо, икра тобико, панировка', 'price': 490, 'weight': 240, 'pieces': 8},
    {'category': 'Жареные роллы', 'name': 'Жареный угорь', 'composition': 'Угорь, огурец, панировка', 'price': 550, 'weight': 250, 'pieces': 8},
    {'category': 'Жареные роллы', 'name': 'Жареный Том Ям', 'composition': 'Креветка, авокадо, острый соус, панировка', 'price': 580, 'weight': 260, 'pieces': 8},
    
    # Запеченные роллы
    {'category': 'Запеченные роллы', 'name': 'Запеченная Филадельфия', 'composition': 'Лосось, сливочный сыр, авокадо, сырная шапка', 'price': 530, 'weight': 260, 'pieces': 8},
    {'category': 'Запеченные роллы', 'name': 'Запеченная Калифорния', 'composition': 'Краб, авокадо, икра тобико, сырная шапка', 'price': 500, 'weight': 250, 'pieces': 8},
    {'category': 'Запеченные роллы', 'name': 'Запеченный угорь', 'composition': 'Угорь, огурец, сырная шапка', 'price': 560, 'weight': 260, 'pieces': 8},
    
    # Классические роллы
    {'category': 'Классические роллы', 'name': 'Классическая Филадельфия', 'composition': 'Лосось, сливочный сыр, огурец', 'price': 470, 'weight': 230, 'pieces': 8},
    {'category': 'Классические роллы', 'name': 'Классическая Калифорния', 'composition': 'Краб, авокадо, огурец', 'price': 430, 'weight': 210, 'pieces': 8},
    {'category': 'Классические роллы', 'name': 'Ролл с лососем', 'composition': 'Лосось, огурец', 'price': 420, 'weight': 200, 'pieces': 8},
    {'category': 'Классические роллы', 'name': 'Ролл с крабом', 'composition': 'Краб, огурец', 'price': 400, 'weight': 200, 'pieces': 8},
    
    # Суши
    {'category': 'Суши', 'name': 'Суши с лососем', 'composition': 'Лосось, рис, васаби', 'price': 90, 'weight': 40, 'pieces': 1},
    {'category': 'Суши', 'name': 'Суши с угрем', 'composition': 'Угорь, рис, соус', 'price': 110, 'weight': 45, 'pieces': 1},
    {'category': 'Суши', 'name': 'Суши с креветкой', 'composition': 'Креветка, рис', 'price': 100, 'weight': 40, 'pieces': 1},
    {'category': 'Суши', 'name': 'Суши с тунцом', 'composition': 'Тунец, рис', 'price': 95, 'weight': 40, 'pieces': 1},
    
    # Закуски
    {'category': 'Закуски', 'name': 'Картофель фри', 'composition': 'Картофель, соль, специи', 'price': 150, 'weight': 150, 'pieces': 0},
    {'category': 'Закуски', 'name': 'Наггетсы', 'composition': 'Куриное филе в панировке', 'price': 180, 'weight': 120, 'pieces': 6},
    {'category': 'Закуски', 'name': 'Креветки в кляре', 'composition': 'Креветки, кляр', 'price': 250, 'weight': 150, 'pieces': 6},
    {'category': 'Закуски', 'name': 'Креветки в панировке', 'composition': 'Креветки, панировка', 'price': 260, 'weight': 150, 'pieces': 6},
    {'category': 'Закуски', 'name': 'Мидии в соусе', 'composition': 'Мидии, сливочный соус', 'price': 220, 'weight': 120, 'pieces': 5},
    {'category': 'Закуски', 'name': 'Осьминог', 'composition': 'Осьминог, соус терияки', 'price': 280, 'weight': 100, 'pieces': 0},
    {'category': 'Закуски', 'name': 'Салат Чука', 'composition': 'Водоросли чука, кунжут', 'price': 190, 'weight': 100, 'pieces': 0},
    
    # Соусы и дополнения
    {'category': 'Соусы и дополнения', 'name': 'Васаби', 'composition': 'Хрен васаби', 'price': 30, 'weight': 20, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Имбирь', 'composition': 'Маринованный имбирь', 'price': 30, 'weight': 30, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Соевый соус', 'composition': 'Соевый соус', 'price': 30, 'weight': 30, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Соус Унаги', 'composition': 'Сладкий соус для угря', 'price': 40, 'weight': 30, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Соус Спайси', 'composition': 'Острый соус', 'price': 40, 'weight': 30, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Соус Терияки', 'composition': 'Японский соус терияки', 'price': 40, 'weight': 30, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Соус Сырный', 'composition': 'Нежный сырный соус', 'price': 50, 'weight': 40, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Соус Кимчи', 'composition': 'Острый корейский соус', 'price': 40, 'weight': 30, 'pieces': 0},
    {'category': 'Соусы и дополнения', 'name': 'Палочки', 'composition': 'Деревянные палочки для еды', 'price': 10, 'weight': 10, 'pieces': 2},
]

for prod in products_data:
    try:
        category = Category.objects.get(name=prod['category'])
        Product.objects.create(
            category=category,
            name=prod['name'],
            composition=prod['composition'],
            price=prod['price'],
            weight=prod['weight'],
            pieces=prod['pieces'],
            available=True
        )
        print(f"Добавлен: {prod['name']}")
    except Exception as e:
        print(f"Ошибка при добавлении {prod['name']}: {e}")

print("\nГотово! Товары добавлены.")