import os
import django
from django.core import management

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TokyoRoll.settings')
django.setup()

with open('data_dump.json', 'w', encoding='utf-8') as f:
    management.call_command('dumpdata', '--natural-foreign', '--natural-primary',
                            stdout=f, indent=2)
    print("✅ Дамп базы данных создан в UTF-8: data_dump.json")