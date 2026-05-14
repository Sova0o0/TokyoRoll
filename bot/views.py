import os
import json
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import ChatMessage

load_dotenv()

# Отключаем предупреждения SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GigaChatClient:
    def __init__(self):
        self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
        self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        self.authorization_key = os.getenv('GIGACHAT_AUTH_KEY')
        self.access_token = None
        self.token_expires_at = None
        
    def get_access_token(self):
        if self.access_token and self.token_expires_at and self.token_expires_at > datetime.now():
            return self.access_token
        
        if not self.client_id or not self.client_secret:
            return None
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': '12345678-1234-1234-1234-123456789012',
            'Authorization': f'Basic {self.authorization_key}'
        }
        data = {'scope': 'GIGACHAT_API_PERS'}
        
        try:
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                return self.access_token
            return None
        except:
            return None
    
    def ask(self, question, menu_context):
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        system_prompt = f"""Ты - TokyoBot, консультант ресторана японской кухни TokyoRoll.
Используй ТОЛЬКО информацию из меню ниже. Если спрашивают про блюдо, которого нет в меню, скажи что его нет.
Все цены указывай в рублях (₽), НЕ в йенах и НЕ в долларах.
Отвечай дружелюбно, используй эмодзи, будь полезным и вежливым.

Вот ТОЧНОЕ меню ресторана TokyoRoll:

{menu_context}

Правила:
1. Если спрашивают про сет "Калифорния" - это 24 ролла, цена 1490₽
2. Если спрашивают про сет "Филадельфия" - это 32 суши, цена 1890₽
3. Если спрашивают про сет "Токио" - это 40 суши, цена 2190₽
4. Если спрашивают про ролл "Калифорния" - это отдельный ролл, цена 450₽, состав: краб, авокадо, огурец, икра тобико
5. Если спрашивают про ролл "Филадельфия" - это отдельный ролл, цена 490₽, состав: лосось, сливочный сыр, огурец, авокадо

Всегда уточняй, о каком именно блюде спрашивает клиент - о сете или об отдельном ролле."""
        
        data = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.5,
            "max_tokens": 600
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            return None
        except:
            return None

gigachat = GigaChatClient()

# ТОЧНОЕ МЕНЮ из скриншотов
MENU_CONTEXT = """
=== СЕТЫ ===
1. Сет "Филадельфия": 32 суши (филадельфия, калифорния, угорь, лосось с авокадо и сливочным сыром). Цена: 1890₽. Скидка 20%.
2. Сет "Калифорния": 24 ролла (классические, горячие, запеченные с крабом и авокадо). Цена: 1490₽. Скидка 15%.
3. Сет "Токио": 40 суши и роллов премиум-класса + бесплатный соус. Цена: 2190₽. Скидка 25%.

=== ОТДЕЛЬНЫЕ РОЛЛЫ ===
1. Ролл "Филадельфия": лосось, сливочный сыр, огурец, авокадо. Цена: 490₽.
2. Ролл "Калифорния": краб, авокадо, огурец, икра тобико. Цена: 450₽.
3. Ролл с угрем: цена: 520₽.
4. Запеченные роллы: цена: 480₽.
5. Горячие роллы: цена: 500₽.

=== КАТЕГОРИИ МЕНЮ ===
- Сеты: 18 позиций
- Классические роллы: 25 позиций
- Горячие роллы: 15 позиций
- Запеченные роллы: 20 позиций
- Теплые роллы: 12 позиций
- Жареные роллы: 10 позиций
- Лапша WOK: 8 позиций
- Азиатская кухня: 15 позиций
"""

# Локальный бот (резервный вариант)
def get_local_response(message):
    msg = message.lower()
    
    if 'сет калифорния' in msg or 'сет калифорни' in msg:
        return "🍱 **Сет Калифорния**\n\n📖 24 ролла (классические, горячие, запеченные с крабом и авокадо)\n💰 Цена: 1490₽\n🎯 Скидка 15%!\n\nОтличный выбор для компании из 2 человек!"
    
    if 'сет филадельфия' in msg or 'сет филадельфи' in msg:
        return "🍱 **Сет Филадельфия**\n\n📖 32 суши (филадельфия, калифорния, угорь, лосось с авокадо)\n💰 Цена: 1890₽\n🎯 Скидка 20%!\n\nИдеально для компании из 2-3 человек!"
    
    if 'сет токио' in msg:
        return "🍱 **Сет Токио**\n\n📖 40 суши и роллов премиум-класса + бесплатный соус\n💰 Цена: 2190₽\n🎯 Скидка 25%!\n\nДля большой компании из 4-5 человек!"
    
    if 'ролл калифорния' in msg and 'сет' not in msg:
        return "🍣 **Ролл Калифорния**\n\n📖 Состав: краб, авокадо, огурец, икра тобико, нори, рис\n🔥 Калории: 280 ккал\n💰 Цена: 450₽"
    
    if 'ролл филадельфия' in msg and 'сет' not in msg:
        return "🍣 **Ролл Филадельфия**\n\n📖 Состав: лосось, сливочный сыр, огурец, авокадо, нори, рис\n🔥 Калории: 320 ккал\n💰 Цена: 490₽"
    
    if any(w in msg for w in ['привет', 'здравствуй']):
        return "🌸 Привет! Я TokyoBot! Рад помочь с выбором блюд в ресторане TokyoRoll! 🍣\n\nЧто желаете узнать? Сеты, роллы или составы блюд?"
    
    if any(w in msg for w in ['посоветуй', 'какой лучше', 'что выбрать']):
        return "🎯 **Мои рекомендации:**\n\n1. 🍱 **Сет Филадельфия** (1890₽) - самый популярный!\n2. 🍣 **Ролл Филадельфия** (490₽) - классика\n3. 🍱 **Сет Калифорния** (1490₽) - отличный выбор\n\nХотите узнать подробнее о каком-то блюде?"
    
    if 'спасиб' in msg:
        return "😊 Пожалуйста! Всегда рад помочь! Обращайтесь, если будут вопросы! 🍣"
    
    if 'помощь' in msg or 'что ты умеешь' in msg:
        return """🤖 **TokyoBot умеет:**\n\n• Рассказывать о сетах (Филадельфия, Калифорния, Токио)\n• Описывать состав роллов\n• Сообщать цены в рублях\n• Рекомендовать блюда\n\n**Примеры:**\n• "Расскажи про сет Филадельфия"\n• "Что входит в ролл Калифорния?"\n• "Сколько стоит сет Токио?"\n• "Какой сет лучше для компании?" """
    
    return '🍣 **Чем могу помочь?**\n\nСпросите меня о:\n• Сетах (Филадельфия, Калифорния, Токио)\n• Роллах и их составе\n• Ценах и калориях\n\nНапример: "Расскажи про сет Филадельфия" или "Что входит в ролл Калифорния?"'

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'response': 'Напишите что-нибудь 😊'})
            
            print(f"Пользователь: {message}")
            
            response = gigachat.ask(message, MENU_CONTEXT)
            
            if not response:
                print("Использую локального бота")
                response = get_local_response(message)
            
            try:
                ChatMessage.objects.create(
                    user_message=message[:500],
                    bot_response=response[:1000]
                )
            except:
                pass
            
            return JsonResponse({'response': response})
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return JsonResponse({'response': 'Извините, произошла ошибка. Попробуйте позже.'}, status=500)
    
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)