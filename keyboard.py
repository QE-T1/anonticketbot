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
        [
            InlineKeyboardButton(
                "БАН",
                callback_data=f"block_{ticket_id}"
            )
        ]
    ])

def delreply_keyboard(reply_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Удалить ответ",
                callback_data=f"delreply_{reply_id}"
            )]
    ])
