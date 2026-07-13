from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    keyboard = [
        ["🏠 Купить", "🏡 Продать"],
        ["🏢 Снять", "📞 Связаться"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def property_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⬅️", callback_data="prev"),
            InlineKeyboardButton("➡️", callback_data="next"),
        ],
        [
            InlineKeyboardButton("📍 Показать на карте", callback_data="map")
        ],
        [
            InlineKeyboardButton("📝 Оставить заявку", callback_data="request")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)