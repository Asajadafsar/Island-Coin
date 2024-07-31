from .models import Inventory

def reset_rocket_inventory():
    inventories = Inventory.objects.all()
    for inventory in inventories:
        inventory.rocket = 3
        inventory.save()
        
        # Front/tasks.py

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import User, Reward

@shared_task
def increase_user_coins(user_id):
    try:
        user = User.objects.get(id=user_id)
        reward, created = Reward.objects.get_or_create(user=user, defaults={'coins': 0})
        reward.coins += 1
        reward.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'user_coins_update',
                'data': {
                    'status': 'success',
                    'coins': reward.coins
                }
            }
        )
    except User.DoesNotExist:
        return {'status': 'error', 'message': 'User not found'}
