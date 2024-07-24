from django.http import JsonResponse
from django.views import View
from django.conf import settings
import telegram
import json
from .models import User

class TelegramWebhook(View):
    def post(self, request, *args, **kwargs):
        # Parse the incoming update
        try:
            data = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        update = telegram.Update.de_json(data, bot)
        
        # Check if there is a message
        if update.message:
            user_id = update.message.from_user.id
            username = update.message.from_user.username
            
            # Save or update user information
            user, created = User.objects.update_or_create(
                user_id=user_id,
                defaults={'username': username}
            )
            
            # Respond to Telegram
            return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'no message'})
