from telegram.ext import Application, ChatMemberHandler

from config import TOKEN
from handlers import register_handler, new_member
from database import init_db

init_db()

app = Application.builder().token(TOKEN).build()

register_handler(app)

app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))

app.run_polling()


