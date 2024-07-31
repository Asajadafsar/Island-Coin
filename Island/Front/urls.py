from django.urls import path
from .views import TelegramWebhook, UserInfoView, IncreaseCoinsView, RefillTankView, ActivateRocketView,\
    GetDailyRewardView, SubscribeAVChannelView, PlayHamsterKombatView, WatchAVVideoView,\
    GenerateInviteLinkView, RegisterInviteView, InvitedFriendsListView, RankingView, IncreaseUserCoinsView, \
    GetUserCoinsView



urlpatterns = [
    path('webhook/', TelegramWebhook.as_view(), name='telegram_webhook'),
    path('webhook/<int:user_id>/', UserInfoView.as_view(), name='user_info'),
    path('increase-coins/<int:user_id>/', IncreaseCoinsView.as_view(), name='increase_coins'),
    path('refill-tank/<int:user_id>/', RefillTankView.as_view(), name='refill_tank'),
    path('daily_reward/<int:user_id>/', GetDailyRewardView.as_view(), name='daily_reward'),
    path('activate-rocket/<int:user_id>/', ActivateRocketView.as_view(), name='activate_rocket'),
    path('subscribe_av_channel/<int:user_id>/', SubscribeAVChannelView.as_view(), name='subscribe_av_channel'),
    path('play_hamster_kombat/<int:user_id>/', PlayHamsterKombatView.as_view(), name='play_hamster_kombat'),
    path('watch_av_video/<int:user_id>/', WatchAVVideoView.as_view(), name='watch_av_video'),
    path('generate_invite_link/<int:user_id>/', GenerateInviteLinkView.as_view(), name='generate_invite_link'),
    path('register_invite/', RegisterInviteView.as_view(), name='register_invite'),
    path('ranking/<int:level>/', RankingView.as_view(), name='ranking'),
    path('invited_friends_list/<int:user_id>/', InvitedFriendsListView.as_view(), name='invited_friends_list'),
    
     path('increase_user_coins/<int:user_id>/', IncreaseUserCoinsView.as_view(), name='increase_user_coins'),
    path('get_user_coins/<int:user_id>/', GetUserCoinsView.as_view(), name='get_user_coins'),
]

