# bot/gigachat_client.py
import requests
import json
from datetime import datetime, timedelta
from menu_data import FULL_MENU_TEXT  

class GigaChatClient:
    def __init__(self):
        self.client_id = "019d8d83-3e9c-7948-ae36-a07df3f83d26"  
        self.client_secret = "be586d50-abc7-48fd-9bb2-00781f34d921"  
        self.access_token = None
        self.token_expires_at = None
        
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
                return self.access_token
            else:
                print(f"Ошибка получения токена: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    
    def ask_gigachat(self, question):
        """Задаем вопрос GigaChat с полным меню"""
        access_token = self.get_access_token()
        if not access_token:
            return "Извините, сейчас не могу ответить. Попробуйте позже. 🤖"
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Используем полное меню из файла menu_data.py
        system_prompt = f"""Ты - консультант ресторана доставки суши TokyoRoll.

Вот ПОЛНОЕ МЕНЮ ресторана (все цены актуальны):

{FULL_MENU_TEXT}

ВАЖНЫЕ ПРАВИЛА:
1. При вопросе про ЗАКУСКИ обязательно назови: МИДИИ В СОУСЕ (220₽), Креветки в панировке (260₽), Наггетсы (250₽), Картофель фри (150₽), Салат Чука (190₽), Осьминог (280₽)
2. При вопросе про СОУСЫ перечисли все соусы с ценами из меню
3. При вопросе про РОЛЛЫ назови конкретные названия и цены из меню
4. При вопросе про СЕТЫ перечисли все сеты с ценами из меню
5. Если блюда нет в меню - так и скажи, не выдумывай
6. Отвечай кратко, по делу (2-4 предложения), используй эмодзи 🍣
7. Все цены указывай в рублях (₽)

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
            response = requests.post(url, headers=headers, json=data, timeout=30, verify=False)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            elif response.status_code == 401:
                # Токен устарел, пробуем обновить
                self.access_token = None
                self.token_expires_at = None
                return self.ask_gigachat(question)
            else:
                print(f"Ошибка GigaChat: {response.status_code} - {response.text}")
                return "Извините, сервис временно недоступен. Попробуйте позже. 🍣"
        except requests.Timeout:
            return "Превышено время ожидания ответа. Попробуйте спросить что-то ещё! ⏱️"
        except Exception as e:
            print(f"Ошибка: {e}")
            return "Произошла ошибка. Пожалуйста, попробуйте переформулировать вопрос. 🤗"

# Создаем глобальный экземпляр
gigachat = GigaChatClient()