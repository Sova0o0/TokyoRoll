# bot/views.py
import os
import json
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# Загружаем .env из папки bot
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Отключаем предупреждения SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GigaChatClient:
    def __init__(self):
        # Новые данные
        self.client_id = "019d8d83-3e9c-7948-ae36-a07df3f83d26"
        self.client_secret = "4e2e064f-dd23-486a-80be-0c054a493127"
        # Authorization Key (уже готовый base64)
        self.auth_key = "MDE5ZDhkODMtM2U5Yy03OTQ4LWFlMzYtYTA3ZGYzZjgzZDI2OjRlMmUwNjRmLWRkMjMtNDg2YS04MGJlLTBjMDU0YTQ5MzEyNw=="
        self.access_token = None
        self.token_expires_at = None
        print("🔧 GigaChat инициализирован с новыми ключами")
        
    def get_access_token(self):
        """Получаем токен доступа"""
        if self.access_token and self.token_expires_at and self.token_expires_at > datetime.now():
            return self.access_token
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        
        # Используем Authorization Key как есть (он уже закодирован)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {self.auth_key}',
            'RqUID': '12345678-1234-1234-1234-123456789012'
        }
        
        data = {
            'scope': 'GIGACHAT_API_PERS'
        }
        
        try:
            print("🔄 Получение токена...")
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            print(f"Токен ответ: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                print("✅ Токен успешно получен!")
                return self.access_token
            else:
                print(f"❌ Ошибка: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def ask(self, question, menu_context):
        """Задаем вопрос GigaChat"""
        access_token = self.get_access_token()
        if not access_token:
            print("❌ Нет токена доступа")
            return None
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        system_prompt = f"""Ты - TokyoBot, консультант ресторана японской кухни TokyoRoll.
Используй ТОЛЬКО информацию из меню ниже. Отвечай дружелюбно, кратко, используй эмодзи.

Вот меню ресторана TokyoRoll:

{menu_context}

Ответь на вопрос клиента:"""
        
        data = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            elif response.status_code == 401:
                self.access_token = None
                return None
            else:
                print(f"Ошибка GigaChat: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

gigachat = GigaChatClient()

MENU_CONTEXT = """
🍣 ПОЛНОЕ МЕНЮ TOKYOROLL 🍣

🥗 ЗАКУСКИ:
• Картофель фри — 150г — 150₽
• Куриные наггетсы — 6шт/150г — 250₽
• Креветки в панировке — 6шт/150г — 260₽
• Мидии в соусе — 5шт/120г — 220₽
• Осьминог — 100г — 280₽ (соус терияки)
• Салат Чука — 100г — 190₽ (водоросли чука, кунжут)

🍣 СУШИ (1 шт):
• Суши с лососем — 40г — 90₽
• Суши с угрем — 45г — 110₽
• Суши с креветкой — 40г — 100₽
• Суши с тунцом — 40г — 95₽

🍱 КЛАССИЧЕСКИЕ РОЛЛЫ (8 шт):
• Классическая Филадельфия — 230г — 470₽ (лосось, сливочный сыр, огурец)
• Классическая Калифорния — 210г — 430₽ (краб, авокадо, огурец)
• Ролл с лососем — 200г — 420₽ (лосось, огурец)
• Ролл с крабом — 200г — 400₽ (краб, огурец)

🔥 ЗАПЕЧЁННЫЕ РОЛЛЫ (8 шт):
• Запечённая Филадельфия — 260г — 530₽ (лосось, сливочный сыр, авокадо, сырная шапка)
• Запечённая Калифорния — 250г — 500₽ (краб, авокадо, икра тобико, сырная шапка)
• Запечённый Угорь — 260г — 560₽ (угорь, огурец, сырная шапка)

🍤 ЖАРЕНЫЕ РОЛЛЫ (8 шт):
• Жареная Филадельфия — 250г — 520₽ (лосось, сливочный сыр, авокадо, панировка)
• Жареная Калифорния — 240г — 490₽ (краб, авокадо, икра тобико, панировка)
• Жареный Угорь — 250г — 550₽ (угорь, огурец, панировка)
• Жареный Том Ям — 260г — 580₽ (креветка, авокадо, острый соус, панировка)

🍥 РОЛЛЫ (8 шт):
• Филадельфия — 240г — 490₽ (лосось, сливочный сыр, огурец, авокадо)
• Калифорния — 220г — 450₽ (краб, авокадо, огурец, икра тобико)
• Унаги (с угрём) — 230г — 520₽ (угорь, огурец, соус унаги)
• Том Ям — 240г — 550₽ (креветка, авокадо, огурец, острый соус)
• Спайси лосось — 230г — 480₽ (лосось, огурец, спайси соус)
• Спайси тунец — 230г — 500₽ (тунец, авокадо, спайси соус)
• Аво-ролл — 200г — 350₽ (авокадо, огурец, кунжут)
• Овощной ролл — 210г — 380₽ (огурец, перец, морковь, салат)

🏆 СЕТЫ:
• Сет «Филадельфия» — 32шт/960г — 1890₽ (Филадельфия, Калифорния, с угрём, с лососем)
• Сет «Калифорния» — 24шт/720г — 1490₽ (Калифорния 24шт)
• Сет «Токио» — 64шт/1200г — 2490₽ (Угорь, Лосось, Тунец, Креветка, Филадельфия, Калифорния, Краб, Овощной)
• Сет «Императорский» — 40шт/1350г — 2590₽ (Филадельфия, Калифорния, Угорь, Лосось, Креветка)
• Сет «Самурай» — 24шт/850г — 1690₽ (Филадельфия, Калифорния, с угрём, запечённый)
• Сет «Мегапарки» — 24шт/780г — 1290₽ (Аво-ролл, Овощной, с огурцом, с сыром)
• Сет «Острый» — 24шт/720г — 1790₽ (Острая Калифорния, Острый лосось, Острый угорь)
• Сет «Детский» — 12шт/450г — 890₽ (Нежный ролл с курицей, Ролл с огурцом, Ролл с сыром)
• Сет «Ролломания» — 24шт/780г — 1590₽ (Горячий ролл, Жареный ролл, Запечённый ролл)
• Сет «Премиум» — 16шт/1100г — 2890₽ (Филадельфия с трюфелем, Калифорния с икрой, Угорь с авокадо, Лосось с манго)

🧂 СОУСЫ И ДОПОЛНЕНИЯ:
• Васаби — 20г — 30₽
• Имбирь — 30г — 30₽
• Соевый соус — 30г — 30₽
• Соус Унаги — 30г — 40₽ (сладкий соус для угря)
• Соус Спайси — 30г — 40₽ (острый соус)
• Соус Терияки — 30г — 40₽
• Соус Сырный — 40г — 50₽ (нежный сырный соус)
• Соус Кимчи — 30г — 40₽ (острый корейский соус)
• Палочки — 2шт — 10₽

"""

# Локальный бот (резервный вариант, работает всегда)
def get_local_response(message):
    msg = message.lower()
    
    if 'сет калифорния' in msg or 'сет калифорни' in msg:
        return "🍱 **Сет Калифорния**\n\n📖 24 ролла (классические, горячие, запеченные с крабом и авокадо)\n💰 Цена: 1490₽\n🎯 Скидка 15%!\n\nОтличный выбор для компании из 2 человек!"
    
    if 'сет филадельфия' in msg or 'сет филадельфи' in msg:
        return "🍱 **Сет Филадельфия**\n\n📖 32 суши (филадельфия, калифорния, угорь, лосось с авокадо и сливочным сыром)\n💰 Цена: 1890₽\n🎯 Скидка 20%!\n\nИдеально для компании из 2-3 человек!"
    
    if 'сет токио' in msg:
        return "🍱 **Сет Токио**\n\n📖 40 суши и роллов премиум-класса + бесплатный соус\n💰 Цена: 2190₽\n🎯 Скидка 25%!\n\nДля большой компании из 4-5 человек!"
    
    if 'детский сет' in msg or 'сет детский' in msg:
        return "🍱 **Детский сет**\n\n📖 12 шт (нежный ролл с курицей, ролл с огурцом, ролл с сыром)\n💰 Цена: 890₽\n\nОтличный выбор для маленьких гурманов! 🧒"
    
    if 'мидии' in msg:
        return "🦪 **Мидии в соусе**\n\n📖 5шт/120г, мидии в сливочном соусе\n💰 Цена: 220₽\n\nОчень нежное и вкусное блюдо!"
    
    if any(w in msg for w in ['привет', 'здравствуй']):
        return "🌸 Привет! Я TokyoBot! Рад помочь с выбором блюд в ресторане TokyoRoll! 🍣\n\nЧто желаете узнать? Сеты, роллы или составы блюд?"
    
    return '🍣 **Чем могу помочь?**\n\nСпросите меня о:\n• Сетах (Филадельфия, Калифорния, Токио, Детский)\n• Роллах и их составе\n• Закусках (мидии, креветки, наггетсы)\n• Ценах\n\nНапример: "Расскажи про сет Филадельфия" или "Что входит в ролл Калифорния?"'

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'response': 'Напишите что-нибудь 😊'})
            
            print(f"👤 Пользователь: {message}")
            
            # Пробуем GigaChat
            response = gigachat.ask(message, MENU_CONTEXT)
            
            # Если GigaChat не ответил, используем локального бота
            if not response:
                print("🔄 Использую локального бота")
                response = get_local_response(message)
            
            return JsonResponse({'response': response})
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return JsonResponse({'response': 'Извините, произошла ошибка. Попробуйте позже.'}, status=500)
    
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)