import logging
from pathlib import Path
from io import BytesIO
import pandas as pd
import plotly.graph_objects as go
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, data_dir: Path):
        self.app = ApplicationBuilder().token(token).build()
        self.data_dir = Path(data_dir)
        self.last_trade: str | None = None
        self.profit_total: float = 0.0
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('status', self.status))
        self.app.add_handler(CommandHandler('chart', self.chart))
        self.app.add_handler(CommandHandler('log', self.log))
        self.app.add_handler(CommandHandler('last_trade', self.last_trade))
        self.app.add_handler(CommandHandler('profit', self.profit))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('MoneyMaker Bot active.')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('System running.')

    async def chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text('Usage: /chart SYMBOL')
            return
        symbol = context.args[0].upper()
        path = self.data_dir / f"{symbol}.csv"
        if not path.exists():
            await update.message.reply_text('No data for symbol')
            return
        df = pd.read_csv(path).tail(100)
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                             open=df['Open'],
                                             high=df['High'],
                                             low=df['Low'],
                                             close=df['Close'])])
        buf = BytesIO()
        fig.write_image(buf, format='png')
        buf.seek(0)
        await update.message.reply_photo(buf)

    async def log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Logs are not implemented in this demo.')

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(update.message.text)

    async def last_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.last_trade:
            await update.message.reply_text(f'Last trade: {self.last_trade}')
        else:
            await update.message.reply_text('No trades yet.')

    async def profit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Total profit: {self.profit_total:.2f}')

    def notify_trade(self, text: str):
        for chat in self.app.bot_data.get('chats', []):
            self.app.create_task(self.app.bot.send_message(chat, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Confirm', callback_data='ok')]])))
        self.last_trade = text

    def record_profit(self, amount: float):
        self.profit_total += amount

    def run(self):
        logger.info('Starting Telegram bot')
        self.app.add_handler(CommandHandler('register', self.register))
        self.app.add_handler(MessageHandler(filters.ALL, self.catch_all))
        self.app.run_polling()

    async def register(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chats = self.app.bot_data.setdefault('chats', set())
        chats.add(update.effective_chat.id)
        await update.message.reply_text('Chat registered.')

    async def catch_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass
