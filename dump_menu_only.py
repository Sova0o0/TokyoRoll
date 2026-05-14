import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TokyoRoll.settings')
django.setup()

from django.core import management

# Исключаем всё, что связано с пользователями и заказами
exclude_apps = [
    'auth',
    'accounts',
    'sessions',
    'admin',
    'contenttypes',
    'bot',
    'orders',      # исключаем заказы
    'cart',        # исключаем корзины
]

with open('menu_only.json', 'w', encoding='utf-8') as f:
    management.call_command('dumpdata', 
        exclude=exclude_apps,
        stdout=f, 
        indent=2, 
        natural_foreign=True, 
        natural_primary=True)

print("Дамп создан (только main: категории и товары)")