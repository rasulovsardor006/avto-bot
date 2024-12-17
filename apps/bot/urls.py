from django.urls import path

from apps.bot.views import TelegramWebhook

urlpatterns = [
    path('webhook/', TelegramWebhook.as_view(), name='telegram-webhook')
]
