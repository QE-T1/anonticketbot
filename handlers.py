from telegram.ext import CommandHandler, MessageHandler, filters
from config import GROUP_ID
from database import create_ticket, set_group_message

async def start(update, context):
	await update.message.reply_text("testhello")

async def redirect_msg(update, context):
	user = update.effective_user

	text = update.message.text_html
	
	ticket_id = create_ticket(user, text)

	msg = await context.bot.send_message(
		chat_id=GROUP_ID,
		text=text,
		parse_mode="HTML"
		)
	set_group_message(ticket_id, msg.message_id)
	
	await update.message.reply_text("sended")

def register_handler(app):
	app.add_handler(CommandHandler("start", start))

	app.add_handler(
		MessageHandler(
			filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
			redirect_msg,
		)
	)
