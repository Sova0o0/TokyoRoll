import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TokyoRoll.settings')
django.setup()

from django.core import management
from django.contrib.auth.models import User

# Сначала убедимся, что есть хотя бы один суперпользователь
if not User.objects.filter(is_superuser=True).exists():
    print("Нет суперпользователя! Создайте его перед дампом.")
    print("python manage.py createsuperuser")
    exit()

# Исключаем только сессии и contenttypes (они создаются автоматически)
exclude_apps = ['sessions', 'contenttypes']

with open('full_dump.json', 'w', encoding='utf-8') as f:
    management.call_command('dumpdata', 
        exclude=exclude_apps,
        stdout=f, 
        indent=2, 
        natural_foreign=True, 
        natural_primary=True)

print("Полный дамп создан: full_dump.json")
print("Включает: пользователей, категории, товары, промокоды, заказы")