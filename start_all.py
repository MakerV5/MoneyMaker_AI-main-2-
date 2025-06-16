import logging
from logging.handlers import RotatingFileHandler
import os
from threading import Thread
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

from bot.telegram_bot import TelegramBot
import dashboard.app as dashboard_module

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

activity_handler = RotatingFileHandler(LOG_DIR / 'activity.log', maxBytes=1_000_000, backupCount=3)
activity_handler.setLevel(logging.INFO)
error_handler = RotatingFileHandler(LOG_DIR / 'errors.log', maxBytes=1_000_000, backupCount=3)
error_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler(), activity_handler, error_handler]
)
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
users_str = os.getenv('USERS', 'admin:password')
users = {u.split(':')[0]: u.split(':')[1] for u in users_str.split(',')}
DATA_DIR = Path('data')
ASSET = 'BTCUSDT'


def run_dashboard():
    dashboard_module.init(dashboard_module.app, DATA_DIR, ASSET, users)
    uvicorn.run(dashboard_module.app, host='0.0.0.0', port=5000)


def main():
    bot = TelegramBot(TOKEN, DATA_DIR)
    t = Thread(target=run_dashboard, daemon=True)
    t.start()
    bot.run()


if __name__ == '__main__':
    main()
