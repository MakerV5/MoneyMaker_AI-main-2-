import logging
from threading import Thread

from bot.telegram_bot import TelegramBot
from dashboard.app import app as dashboard_app

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'


def run_dashboard():
    dashboard_app.run(host='0.0.0.0', port=5000)


def main():
    bot = TelegramBot(TELEGRAM_TOKEN)
    t1 = Thread(target=bot.run)
    t2 = Thread(target=run_dashboard)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == '__main__':
    main()
