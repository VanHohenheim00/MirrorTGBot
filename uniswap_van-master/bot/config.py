from aiogram import Bot
from dotenv import load_dotenv
import os

from utils.EtherAPI import EtherAPI

eths = EtherAPI()

load_dotenv()


API_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

# Initialize bot
bot = Bot(token=API_TOKEN)
