from django.urls import path
from .views import TelegramWebhook

urlpatterns = [
    path('webhook/', TelegramWebhook.as_view(), name='telegram_webhook'),
]
