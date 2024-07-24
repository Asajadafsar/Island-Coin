from django.urls import path
from .views import TelegramWebhook, UserInfoView, IncreaseCoinsView, RefillTankView

urlpatterns = [
    path('webhook/', TelegramWebhook.as_view(), name='telegram_webhook'),
    path('webhook/<int:user_id>/', UserInfoView.as_view(), name='user_info'),
    path('increase-coins/<int:user_id>/', IncreaseCoinsView.as_view(), name='increase_coins'),
    path('refill-tank/<int:user_id>/', RefillTankView.as_view(), name='refill_tank'),
]
