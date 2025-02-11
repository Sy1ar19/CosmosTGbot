from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

TG_BOT_API = os.getenv('TG_BOT_API')
LCD_URL = os.getenv('LCD_URL')
COINGECKO_API_URL = os.getenv('COINGECKO_API_URL')
