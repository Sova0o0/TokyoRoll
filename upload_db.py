import os
import django
from django.core import management
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TokyoRoll.settings')
django.setup()

with open('data_dump.json', 'w', encoding='utf-8') as f:
    management.call_command('dumpdata', '--natural-foreign', '--natural-primary',
                            stdout=f, indent=2)

# Проверка, что файл корректный
try:
    with open('data_dump.json', 'r', encoding='utf-8') as f:
        json.load(f)
    print("Дамп базы данных создан и прошел проверку: data_dump.json")
except json.JSONDecodeError as e:
    print(f"Ошибка: файл data_dump.json поврежден - {e}")