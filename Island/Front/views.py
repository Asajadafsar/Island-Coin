from django.http import JsonResponse
from django.views import View
from django.conf import settings
import telegram
import json
from .models import User, Reward, Inventory

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
            
            # Create or update Reward entry
            reward, reward_created = Reward.objects.get_or_create(
                user=user,
                defaults={'coins': 0}  # Default value for coins
            )
            
            # Create or update Inventory entry if not already present
            inventory, inventory_created = Inventory.objects.get_or_create(
                user=user,
                defaults={'tank': 10000}  # Default value for tank
            )
            
            # Respond to Telegram
            return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'no message'})


class UserInfoView(View):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        # Retrieve or create Reward
        reward, created = Reward.objects.get_or_create(
            user=user,
            defaults={'coins': 0}  # Default value for coins
        )
        
        # Retrieve or create Inventory
        inventory, created = Inventory.objects.get_or_create(
            user=user,
            defaults={'tank': 10000}  # Default value for tank
        )
        
        # Prepare user info
        user_info = {
            'level': user.level,
            'coins': reward.coins,
            'tank': inventory.tank  # No need to set to 10000 if default is applied
        }
        
        return JsonResponse(user_info)
    
class IncreaseCoinsView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        # Retrieve or create the reward for the user
        reward, created = Reward.objects.get_or_create(
            user=user,
            defaults={'coins': 0}
        )
        
        # Retrieve or create the inventory for the user
        inventory, created = Inventory.objects.get_or_create(
            user=user,
            defaults={'tank': 10000}
        )
        
        # Check if there is enough tank resource
        if inventory.tank <= 0:
            return JsonResponse({'status': 'error', 'message': 'Tank is empty'}, status=400)
        
        # Increase coins by 1 and decrease tank by 1
        reward.coins += 1
        inventory.tank -= 1
        
        # Save updated reward and inventory
        reward.save()
        inventory.save()
        
        return JsonResponse({'status': 'success', 'coins': reward.coins, 'tank': inventory.tank})
    
    
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
        
        # Check if fullcharge is available
        if inventory.fullcharge <= 0:
            return JsonResponse({'status': 'error', 'message': 'Cannot refill tank. Fullcharge is empty'}, status=400)
        
        # Refill tank
        max_tank_capacity = 10000
        if inventory.tank < max_tank_capacity:
            inventory.tank = max_tank_capacity
            inventory.fullcharge -= 1
            inventory.save()
            return JsonResponse({'status': 'success', 'message': 'Tank refilled', 'tank': inventory.tank, 'fullcharge': inventory.fullcharge})
        
        return JsonResponse({'status': 'success', 'message': 'Tank is already full', 'tank': inventory.tank})