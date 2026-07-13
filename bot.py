import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID
from properties import properties
from excel import save_to_excel
from database import create_database, save_to_database
from keyboards import main_menu, property_keyboard

user_state = {}
user_data = {}


def property_caption(obj):
    return (
        f"{obj['title']}\n\n"
        f"📍 {obj['address']}\n"
        f"📐 {obj['area']}\n"
        f"💰 {obj['price']}\n\n"
        f"{obj['description']}"
    )


def get_photo_path(photo):
    return os.path.join(os.path.dirname(__file__), photo)


async def show_property(message, index=0):
    obj = properties[index]
    photo_path = get_photo_path(obj["photo"])

    if not os.path.exists(photo_path):
        await message.reply_text(f"❌ Фото не найдено: {obj['photo']}")
        return

    with open(photo_path, "rb") as photo:
        await message.reply_photo(
            photo=photo,
            caption=property_caption(obj),
            reply_markup=property_keyboard(),
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Добро пожаловать!\n\nВыберите действие:",
        reply_markup=main_menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_index = context.user_data.get("property_index", 0)

    if query.data == "next":
        new_index = current_index + 1
        if new_index >= len(properties):
            new_index = 0

        context.user_data["property_index"] = new_index
        await show_property(query.message, new_index)
        await query.message.delete()
        return

    elif query.data == "prev":
        new_index = current_index - 1
        if new_index < 0:
            new_index = len(properties) - 1

        context.user_data["property_index"] = new_index
        await show_property(query.message, new_index)
        await query.message.delete()
        return

    elif query.data == "request":
        obj = properties[current_index]
        user_id = query.from_user.id

        user_state[user_id] = "name"
        user_data[user_id] = {
            "type": "🏠 Купить",
            "property": obj["title"],
        }

        await query.message.reply_text(
            f"📝 Вы выбрали:\n\n{obj['title']}\n\n✍️ Введите ваше имя:"
        )
        return

    elif query.data == "map":
        obj = properties[current_index]
        latitude, longitude = obj["location"]

        await query.message.reply_location(
            latitude=latitude,
            longitude=longitude
        )
        return
        
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "📞 Связаться":
        await update.message.reply_text("Телефон: +7 (999) 123-45-67")
        return

    if text == "🏠 Купить":
        context.user_data["property_index"] = 0
        await show_property(update.message, 0)
        return

    if text in ["🏡 Продать", "🏢 Снять"]:
        user_state[user_id] = "name"
        user_data[user_id] = {"type": text, "property": "Не выбран"}
        await update.message.reply_text("✍️ Введите ваше имя:")
        return

    if user_state.get(user_id) == "name":
        user_data[user_id]["name"] = text
        user_state[user_id] = "phone"
        await update.message.reply_text("📞 Введите телефон:")
        return

    if user_state.get(user_id) == "phone":
        user_data[user_id]["phone"] = text
        user_state[user_id] = "text"
        await update.message.reply_text("📝 Напишите комментарий:")
        return

    if user_state.get(user_id) == "text":
        user_data[user_id]["text"] = text
        data = user_data.pop(user_id, {})
        user_state.pop(user_id, None)

        admin_text = (
            f"📩 Новая заявка\n\n"
            f"Тип: {data.get('type')}\n"
            f"Объект: {data.get('property')}\n"
            f"Имя: {data.get('name')}\n"
            f"Телефон: {data.get('phone')}\n\n"
            f"Комментарий:\n{data.get('text')}\n\n"
            f"Username: @{update.effective_user.username}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        save_to_excel(data)

        save_to_database(data)

        await update.message.reply_text("✅ Спасибо! Заявка отправлена агенту.")
        return

    await update.message.reply_text("Используйте кнопки меню 👇")


def main():
    create_database()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    print("🏠 Бот недвижимости v2.0 запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
