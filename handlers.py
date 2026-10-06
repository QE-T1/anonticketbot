from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ChatMemberHandler
from config import GROUP_ID, RESULT_CHAT_ID
from keyboard import ticket_keyboard, delreply_keyboard
from database import create_ticket, set_group_message, is_banned, ticket_by_group_message, close_ticket, ban_user, get_ticket_user, delete_ticket, save_reply, is_ticket_open, get_ticket, get_ticket_replies, delete_reply, set_nickname, get_nickname
from telegram import Update

WAIT_NICK = 1

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

async def save_reply_handler(update, context):
	message = update.message
	if not message.reply_to_message:
		return
	ticket_id = ticket_by_group_message(
		message.reply_to_message.message_id
		)

	if ticket_id is None:
		return

	if not is_ticket_open(ticket_id):
		return

	author = update.effective_user
	nickname = get_nickname(author.id)
	if nickname is None:
		await message.reply_text("Сначала выбери ник командой /nick")
		return
	reply_id = save_reply(
		ticket_id=ticket_id,
		author_id=author.id,
		author_name=nickname,
		text=message.text_html,
	)
	await message.reply_text(
		"Ответ сохранен",
		reply_markup=delreply_keyboard(reply_id)
	)

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

	elif data.startswith("delreply_"):
		reply_id = int(data.split("_")[1])
		delete_reply(reply_id)
		await query.edit_message_text("Ответ удален")

async def new_member(update: Update, context):
	result = update.chat_member
	if result.new_chat_member.status != "member":
		return
	user = result.new_chat_member.user
	if get_nickname(user.id):
		return
	msg = await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=f"{user.mention_html()}, выбери свой псевдоним следующим сообщением",
		parse_mode="HTML"
	)
	context.chat_data[user.id] = {
		"wait_nick":True,
		"welcome_msg": msg.message_id,
	}

async def group_nickname(update, context):
	user = update.effective_user
	data = context.chat_data.get(user.id)
	if not data or not data.get("wait_nick"):
		return
	nickname = update.message.text.strip()
	set_nickname(user.id, nickname)
	context.chat_data.pop(user.id)
	await update.message.reply_text(
		f"Ник сохранен:{nickname}"
	)

async def nick(update, context):
	context.chat_data[update.effective_user.id] = {"wait_nick":True}
	await update.message.reply_text("Введите новый ник:")

def register_handler(app):
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("nick",nick))
	app.add_handler(
		MessageHandler(
			filters.ChatType.GROUPS & filters.REPLY & filters.TEXT,
			save_reply_handler,
		),
		group=0,
	)
	app.add_handler(
		MessageHandler(
    			filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND,
			group_nickname,
		),
		group=1,
	)

	app.add_handler(
		MessageHandler(
			filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
			redirect_msg,
		)
	)
	app.add_handler(CallbackQueryHandler(button_handler))
	app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))

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
