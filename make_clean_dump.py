import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TokyoRoll.settings')
django.setup()

from django.core import management

with open('data_dump.json', 'w', encoding='utf-8') as f:
    management.call_command('dumpdata', 
        exclude=['accounts.UserProfile', 'bot'], 
        stdout=f, 
        indent=2, 
        natural_foreign=True, 
        natural_primary=True)

print("Дамп создан без UserProfile и bot")