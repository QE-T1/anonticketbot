from telegram.ext import Application

from config import TOKEN
from database import init_db

init_db()

app = Application.builder().token(TOKEN).build()

app.run_polling()
