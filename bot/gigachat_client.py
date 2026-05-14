# bot/gigachat_client.py
import requests
import json
from datetime import datetime, timedelta
from main.models import Category, Product

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
    
    def get_menu_context(self):
        """Получаем всё меню из базы данных"""
        try:
            categories = Category.objects.filter(is_active=True).order_by('order')
            menu_text = "Вот наше текущее меню:\n\n"
            
            for category in categories:
                products = Product.objects.filter(category=category, available=True)
                if products.exists():
                    menu_text += f"📁 **{category.name}**\n"
                    for product in products[:10]:  # Ограничиваем 10 товаров на категорию
                        menu_text += f"  • {product.name} — {product.price}₽"
                        if product.weight:
                            menu_text += f" ({product.weight}г)"
                        if product.pieces:
                            menu_text += f", {product.pieces}шт"
                        if product.composition:
                            menu_text += f"\n    Состав: {product.composition[:100]}"
                        menu_text += "\n"
                    menu_text += "\n"
            
            return menu_text
        except Exception as e:
            print(f"Ошибка загрузки меню: {e}")
            return "Меню загружается..."
    
    def ask_gigachat(self, question, context=""):
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
        
        # Получаем актуальное меню из БД
        full_menu = self.get_menu_context()
        
        # Формируем промпт с полным меню
        system_prompt = f"""Ты - консультант ресторана доставки суши TokyoRoll. 
Твоя задача помогать клиентам выбирать блюда, рассказывать о составе и давать рекомендации.

ПРАВИЛА:
- Отвечай дружелюбно, кратко и по делу (максимум 3-4 предложения)
- Используй эмодзи для украшения ответов
- Если не знаешь ответ, честно скажи и предложи посмотреть меню
- Не выдумывай цены и блюда, которых нет в меню

{f'Актуальное меню (цены актуальны):\n{full_menu}' if full_menu else 'Меню временно недоступно. Расскажи в общих чертах о суши, роллах и сетях.'}

Если клиент спрашивает про цену или состав конкретного блюда, отвечай используя только информацию из меню выше."""
        
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
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            elif response.status_code == 401:
                # Токен устарел, пробуем обновить
                self.access_token = None
                self.token_expires_at = None
                return self.ask_gigachat(question, context)
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