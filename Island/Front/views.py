from django.http import JsonResponse
from django.views import View
from django.conf import settings
import telegram
import json
from .models import User, Reward, Inventory
import threading

class TelegramWebhook(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        update = telegram.Update.de_json(data, bot)
        
        if update.message:
            user_id = update.message.from_user.id
            username = update.message.from_user.username
            
            user, created = User.objects.update_or_create(
                user_id=user_id,
                defaults={'username': username}
            )
            
            reward, reward_created = Reward.objects.get_or_create(
                user=user,
                defaults={'coins': 0}
            )
            
            inventory, inventory_created = Inventory.objects.get_or_create(
                user=user,
                defaults={'tank': 10000}
            )
            
            return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'no message'})


class UserInfoView(View):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        reward, created = Reward.objects.get_or_create(
            user=user,
            defaults={'coins': 0}
        )
        
        inventory, created = Inventory.objects.get_or_create(
            user=user,
            defaults={'tank': 10000}
        )
        
        user_info = {
            'level': user.level,
            'coins': reward.coins,
            'tank': inventory.tank
        }
        
        return JsonResponse(user_info)
    
class IncreaseCoinsView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        reward, created = Reward.objects.get_or_create(
            user=user,
            defaults={'coins': 0}
        )
        
        inventory, created = Inventory.objects.get_or_create(
            user=user,
            defaults={'tank': 10000}
        )
        
        if inventory.tank <= 0:
            return JsonResponse({'status': 'error', 'message': 'Tank is empty'}, status=400)
        
        # Check if rocket is active and determine coins increment
        if inventory.rocket_active:
            coins_increment = self.get_coins_increment(user.level)
        else:
            coins_increment = 1
        
        reward.coins += coins_increment
        inventory.tank -= 1
        
        reward.save()
        inventory.save()
        
        return JsonResponse({'status': 'success', 'coins': reward.coins, 'tank': inventory.tank, 'rocket_active': inventory.rocket_active, 'rocket_multiplier': inventory.rocket_multiplier if inventory.rocket_active else 1})
    
    def get_coins_increment(self, level):
        if level == 1:
            return 2
        elif level == 2:
            return 5
        elif level == 3:
            return 10
        elif level == 4:
            return 15
        elif level == 5:
            return 50
        elif level == 6:
            return 100
        else:
            return 1

    
class RefillTankView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        try:
            inventory = Inventory.objects.get(user=user)
        except Inventory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Inventory not found'}, status=404)
        
        if inventory.fullcharge <= 0:
            return JsonResponse({'status': 'error', 'message': 'Cannot refill tank. Fullcharge is empty'}, status=400)
        
        max_tank_capacity = 10000
        if inventory.tank < max_tank_capacity:
            inventory.tank = max_tank_capacity
            inventory.fullcharge -= 1
            inventory.save()
            return JsonResponse({'status': 'success', 'message': 'Tank refilled', 'tank': inventory.tank, 'fullcharge': inventory.fullcharge})
        
        return JsonResponse({'status': 'success', 'message': 'Tank is already full', 'tank': inventory.tank})

class ActivateRocketView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        try:
            inventory = Inventory.objects.get(user=user)
        except Inventory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Inventory not found'}, status=404)
        
        if inventory.rocket <= 0:
            return JsonResponse({'status': 'error', 'message': 'No rockets available'}, status=400)
        
        inventory.rocket_active = True
        inventory.rocket -= 1
        inventory.save()

        def deactivate_rocket():
            inventory.rocket_active = False
            inventory.save()

        timer = threading.Timer(60, deactivate_rocket)  # Timer set to 60 seconds
        timer.start()
        
        return JsonResponse({'status': 'success', 'message': 'Rocket activated', 'rocket': inventory.rocket, 'rocket_active': inventory.rocket_active})
