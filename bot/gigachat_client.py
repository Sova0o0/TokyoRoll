# bot/gigachat_client.py
import requests
import json
from datetime import datetime, timedelta

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
            response = requests.post(url, headers=headers, data=data)
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
    
    def ask_gigachat(self, question, context=""):
        """Задаем вопрос GigaChat"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Формируем промпт с контекстом меню
        system_prompt = f"""Ты - консультант ресторана доставки суши TokyoRoll. 
        Твоя задача помогать клиентам выбирать блюда, рассказывать о составе и давать рекомендации.
        
        Контекст меню:
        {context}
        
        Отвечай дружелюбно, кратко и по делу. Используй эмодзи для украшения ответов.
        """
        
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
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"Ошибка GigaChat: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

# Создаем глобальный экземпляр
gigachat = GigaChatClient()