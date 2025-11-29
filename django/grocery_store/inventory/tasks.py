from celery import shared_task
from django.core.mail import send_mail
from .models import Product
from datetime import datetime, timedelta
import telegram
from django.conf import settings


@shared_task
def send_telegram_notification():
    expiring_products = Product.objects.filter(expiry_date__lte=datetime.now().date() + timedelta(days=20))
    print(expiring_products)
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    message = "The following products are expiring soon:\n" + "\n".join(product_list)

    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)

