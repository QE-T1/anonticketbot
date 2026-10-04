from telegram.ext import Application

from config import TOKEN
from handlers import register_handler
from database import init_db

init_db()

app = Application.builder().token(TOKEN).build()

register_handler(app)

app.run_polling()
