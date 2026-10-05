from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import GROUP_ID, RESULT_CHAT_ID
from keyboard import ticket_keyboard
from database import create_ticket, set_group_message, is_banned, close_ticket, ban_user, get_ticket_user, delete_ticket, is_ticket_open, get_ticket, get_ticket_replies

async def start(update, context):
	await update.message.reply_text("testhello")

async def redirect_msg(update, context):
	user = update.effective_user
	if is_banned(update.effective_user.id):
		await update.message.reply_text("Вы забанены")
		return

	text = update.message.text_html
	
	ticket_id = create_ticket(user, text)

	msg = await context.bot.send_message(
		chat_id=GROUP_ID,
		text=text,
		reply_markup=ticket_keyboard(ticket_id),
		parse_mode="HTML"
		)
	set_group_message(ticket_id, msg.message_id)
	
	await update.message.reply_text("sended")

async def button_handler(update, context):
	query = update.callback_query
	await query.answer()

	data = query.data

	if data.startswith("close_"):
		ticket_id = int(data.split("_")[1])
		close_ticket(ticket_id)
		result = compile_ticket(ticket_id)
		for part in split_message(result):
			await context.bot.send_message(
				chat_id=RESULT_CHAT_ID,
				text=part,
				parse_mode="HTML"
			)
		await query.message.reply_text(f"Тикет #{ticket_id} Закрыт и отправлен")
	elif data.startswith("block_"):
		ticket_id = int(data.split("_")[1])
		user_id = get_ticket_user(ticket_id)
		if user_id is not None:
			ban_user(user_id, "spam")
			await query.message.reply_text("Пользователь заблокирован")

	elif data.startswith("delete_"):
		ticket_id = int(data.split("_")[1])
		delete_ticket(ticket_id)
		await query.message.reply_text(f"Тикет #{ticket_id} удален")

def register_handler(app):
	app.add_handler(CommandHandler("start", start))

	app.add_handler(
		MessageHandler(
			filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
			redirect_msg,
		)
	)
	app.add_handler(CallbackQueryHandler(button_handler))

def compile_ticket(ticket_id):
	ticket = get_ticket(ticket_id)
	if ticket is None:
		return None
	question = ticket[2]
	replies = get_ticket_replies(ticket_id)
	result = f"Тикет #{ticket_id}\n\n"
	result+= "<b>Вопрос:</b>\n"
	result+= f"<blockquote>{question}</blockquote>\n\n"
	result+= "<b>Ответы:</b>\n\n"
	for author, text in replies:
		result += f"<code>----------------</code>\n"
		result += f"<code>{author}</code>\n"
		result += f"<code>----------------</code>\n"
		result += f"{text}\n"
	return result

def split_message(text, limit=4000):
	parts = []
	while len(text)>limit:
		split_at = text.rfind("\n", 0, limit)
		
		if split_at == -1:
			split_at = limit
		parts.append(text[:split_at])
		text = text[split_at:].lstrip("\n")
	if text:
		parts.append(text)
	return parts
