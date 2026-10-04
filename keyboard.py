from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def ticket_keyboard(ticket_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Закрыть тикет",
                callback_data=f"close_{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "Удалить тикет",
                callback_data=f"delete_{ticket_id}"
            )
        ],
    ])
