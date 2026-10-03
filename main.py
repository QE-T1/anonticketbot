from telegram.ext import Application

from config import TOKEN

app = Application.builder().token(TOKEN).build()

app.run_polling()
