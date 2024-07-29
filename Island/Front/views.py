from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils import timezone 
import telegram
import json
from .models import User, Reward, Inventory
import threading
from django.utils.crypto import get_random_string
from django.db.models import Sum



class TelegramWebhook(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        update = telegram.Update.de_json(data, bot)
        
        if update.message:
            from_user = update.message.from_user

            # Check if the necessary fields are present, if not, provide default values
            if not hasattr(from_user, 'first_name'):
                from_user.first_name = ""
            if not hasattr(from_user, 'is_bot'):
                from_user.is_bot = False

            user_id = from_user.id
            username = from_user.username
            
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

        timer = threading.Timer(24 * 60 * 60, deactivate_rocket)  # Timer set to 24 hours
        timer.start()
        
        return JsonResponse({'status': 'success', 'message': 'Rocket activated', 'rocket': inventory.rocket, 'rocket_active': inventory.rocket_active})


class GetDailyRewardView(View):
    DAILY_REWARD_SCHEDULE = [
        100, 200, 500, 1000, 3000, 7000, 10000, 50000
    ]
    
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        reward, created = Reward.objects.get_or_create(user=user)
        today = timezone.now().date()
        
        if reward.last_reward_date and (today - reward.last_reward_date).days > 1:
            reward.current_day = 1
        elif reward.last_reward_date == today:
            return JsonResponse({'status': 'error', 'message': 'Reward already claimed today'}, status=400)
        
        reward.coins += self.DAILY_REWARD_SCHEDULE[reward.current_day - 1]
        reward.current_day += 1
        
        if reward.current_day > len(self.DAILY_REWARD_SCHEDULE):
            reward.current_day = 1
        
        reward.last_reward_date = today
        reward.save()
        
        return JsonResponse({'status': 'success', 'coins': reward.coins, 'current_day': reward.current_day})
    
    
class SubscribeAVChannelView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        reward, created = Reward.objects.get_or_create(user=user)
        
        if reward.subscribed_channel:
            return JsonResponse({'status': 'error', 'message': 'Already subscribed and rewarded'}, status=400)
        
        # channel
        channel_link = "https://t.me/your_channel_link"
        
        # check channel
        is_subscribed = self.check_subscription(user.user_id)
        
        if is_subscribed:
            reward.coins += 5000
            reward.subscribed_channel = True
            reward.save()
            return JsonResponse({'status': 'success', 'coins': reward.coins})
        
        return JsonResponse({'status': 'error', 'message': 'Not subscribed to the channel', 'link': channel_link}, status=400)

    def check_subscription(self, user_id):
        # اینجا باید چک کنید که آیا کاربر در کانال عضو شده است یا خیر
        # با استفاده از API تلگرام
        return True


class PlayHamsterKombatView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        reward, created = Reward.objects.get_or_create(user=user)
        
        if reward.played_hamster_kombat:
            return JsonResponse({'status': 'error', 'message': 'Already played and rewarded'}, status=400)
        
        # link bot hmaster
        bot_link = "https://t.me/your_bot_link"
        
        # check start
        has_started = self.check_bot_start(user.user_id)
        
        if has_started:
            reward.coins += 10000
            reward.played_hamster_kombat = True
            reward.save()
            return JsonResponse({'status': 'success', 'coins': reward.coins})
        
        return JsonResponse({'status': 'error', 'message': 'Bot not started', 'link': bot_link}, status=400)

    def check_bot_start(self, user_id):
        # اینجا باید چک کنید که آیا کاربر ربات را استارت زده است یا خیر
        # با استفاده از API تلگرام
        return True


class WatchAVVideoView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
        reward, created = Reward.objects.get_or_create(user=user)
        
        if reward.watched_av_video:
            return JsonResponse({'status': 'error', 'message': 'Already watched and rewarded'}, status=400)
        
        # link video
        video_link = "https://www.youtube.com/watch?v=your_video_link"
        
        # check viedo user
        has_watched = self.check_video_watch(user.user_id)
        
        if has_watched:
            reward.coins += 3000
            reward.watched_av_video = True
            reward.save()
            return JsonResponse({'status': 'success', 'coins': reward.coins})
        
        return JsonResponse({'status': 'error', 'message': 'Video not watched', 'link': video_link}, status=400)

    def check_video_watch(self, user_id):
        # اینجا باید چک کنید که آیا کاربر ویدیو را تماشا کرده است یا خیر
        # این چک ممکن است با استفاده از یوتیوب API یا روش‌های دیگر انجام شود
        return True


class GenerateInviteLinkView(View):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        if not user.invite_link:
            invite_code = get_random_string(10)
            user.invite_link = f"https://t.me/your_bot?start={invite_code}"
            user.save()

        return JsonResponse({'status': 'success', 'invite_link': user.invite_link})


class RegisterInviteView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('UTF-8'))
            inviter_code = data.get('inviter_code')
            invitee_id = data.get('invitee_id')
            invitee_username = data.get('invitee_username')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        try:
            inviter = User.objects.get(invite_link__endswith=inviter_code)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Inviter not found'}, status=404)

        invitee, created = User.objects.update_or_create(
            user_id=invitee_id,
            defaults={'username': invitee_username}
        )

        if not inviter.invited_users.filter(user_id=invitee_id).exists():
            inviter.invited_users.add(invitee)
            reward, created = Reward.objects.get_or_create(user=inviter)
            reward.coins += 2000
            reward.invited_friends += 1
            reward.save()

        return JsonResponse({'status': 'success', 'coins': reward.coins, 'invited_friends': reward.invited_friends})


class InvitedFriendsListView(View):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        invited_users = user.invited_users.all().values('user_id', 'username')
        return JsonResponse({'status': 'success', 'invited_users': list(invited_users)})


class RankingView(View):
    def get(self, request, level, *args, **kwargs):
        users = User.objects.filter(level=level).annotate(total_coins=Sum('rewards__coins')).order_by('-total_coins')[:10]
        ranking = [
            {'username': user.username, 'coins': user.total_coins}
            for user in users
        ]
        return JsonResponse({'status': 'success', 'ranking': ranking})