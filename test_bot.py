from telegram import Bot
import os 

TOKEN = os.environ.get('TELEGRAM_TOKEN')
MY_TELEGRAM_ID = os.environ.get('MY_TELEGRAM_ID')

bot = Bot(TOKEN)
bot.send_message(MY_TELEGRAM_ID, 'test')
