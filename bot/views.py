from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .gigachat_client import gigachat
import json

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API для чата с ботом"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        response = gigachat.ask_gigachat(message)
        
        if response:
            return JsonResponse({'response': response})
        else:
            return JsonResponse({'response': 'Извините, не могу ответить сейчас. Попробуйте позже! 🍣'})
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат запроса'}, status=400)
    except Exception as e:
        print(f"Ошибка в чате: {e}")
        return JsonResponse({'response': 'Произошла ошибка. Пожалуйста, попробуйте еще раз. 🤗'})

def chat_page(request):
    """Страница чата"""
    return render(request, 'bot/chat.html')