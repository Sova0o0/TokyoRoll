# bot/gigachat_client.py
import requests
import json
import logging
from datetime import datetime, timedelta

# Настройка логирования
logger = logging.getLogger(__name__)

# Пробуем импортировать меню, если ошибка — используем резервное меню
try:
    from menu_data import FULL_MENU_TEXT
    logger.info(f"✅ Меню загружено из menu_data.py, длина: {len(FULL_MENU_TEXT)} символов")
    MENU_LOADED = True
except ImportError as e:
    logger.error(f"❌ Ошибка импорта menu_data.py: {e}")
    # Резервное меню (минимальное)
    FULL_MENU_TEXT = """
🍣 МЕНЮ TOKYOROLL 🍣

🥗 ЗАКУСКИ:
• Мидии в соусе — 220₽
• Креветки в панировке — 260₽
• Наггетсы — 250₽
• Картофель фри — 150₽
• Салат Чука — 190₽

🍣 СУШИ:
• Суши с лососем — 90₽
• Суши с угрем — 110₽

🍱 СЕТЫ:
• Сет «Детский» — 890₽
• Сет «Филадельфия» — 1890₽
"""
    MENU_LOADED = False

class GigaChatClient:
    def __init__(self):
        self.client_id = "019d8d83-3e9c-7948-ae36-a07df3f83d26"  
        self.client_secret = "be586d50-abc7-48fd-9bb2-00781f34d921"  
        self.access_token = None
        self.token_expires_at = None
        print(f"🔧 GigaChatClient инициализирован, меню загружено: {MENU_LOADED}")
        
    def get_access_token(self):
        """Получаем токен доступа"""
        if self.access_token and self.token_expires_at > datetime.now():
            return self.access_token
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': '12345678-1234-1234-1234-123456789012'
        }
        
        data = {
            'scope': 'GIGACHAT_API_PERS',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, verify=False)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                print(f"✅ Токен получен, expires_in: {expires_in}")
                return self.access_token
            else:
                print(f"❌ Ошибка получения токена: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def ask_gigachat(self, question):
        """Задаем вопрос GigaChat с полным меню"""
        print(f"📝 Вопрос пользователя: {question[:100]}...")
        
        access_token = self.get_access_token()
        if not access_token:
            return "Извините, сейчас не могу ответить. Попробуйте позже. 🤖"
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Формируем промпт
        system_prompt = f"""Ты - консультант ресторана доставки суши TokyoRoll.

Вот ПОЛНОЕ МЕНЮ ресторана (все цены актуальны, ОБЯЗАТЕЛЬНО используй эти данные):

{FULL_MENU_TEXT}

ВАЖНЫЕ ПРАВИЛА (нарушай их только если данных нет в меню):
1. Никогда не выдумывай блюда, которых нет в меню выше
2. Если спрашивают про "Детский сет" — он есть в меню за 890₽
3. Если спрашивают про "Сет Премиум" — он есть в меню за 2890₽
4. Если спрашивают про закуски — назови МИДИИ В СОУСЕ (220₽)
5. Отвечай кратко, используй эмодзи 🍣
6. Все цены бери ТОЛЬКО из меню выше

Теперь ответь на вопрос клиента:"""

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
            response = requests.post(url, headers=headers, json=data, timeout=60, verify=False)
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                print(f"✅ Ответ получен, длина: {len(answer)}")
                return answer
            elif response.status_code == 401:
                self.access_token = None
                self.token_expires_at = None
                return self.ask_gigachat(question)
            else:
                print(f"❌ Ошибка GigaChat: {response.status_code} - {response.text[:200]}")
                return "Извините, сервис временно недоступен. Попробуйте позже. 🍣"
        except requests.Timeout:
            print("❌ Таймаут запроса")
            return "Превышено время ожидания ответа. Попробуйте спросить что-то ещё! ⏱️"
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return "Произошла ошибка. Пожалуйста, попробуйте переформулировать вопрос. 🤗"

# Создаем глобальный экземпляр
gigachat = GigaChatClient()