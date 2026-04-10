import asyncio
import os
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.getenv("API_TOKEN")

if not TOKEN:
    print("❌ Добавь API_TOKEN в переменные среды")
    sys.exit()

# --- НАСТРОЙКИ ---
WHITELIST_IDS = [7918010548]
GROUP_URL = "https://t.me/tether_tjs"

PROFANITY_FILTER_ACTIVE = True
SPAM_FILTER_ACTIVE = True

SPAM_WORDS = [
    "заработок", "подпишись", "сигналы", "профит",
    "доход", "раскрутка", "казино", "ставки",
    "в лс", "писать в лс", "http", "https",
    ".com", ".ru", ".net", ".org", "t.me"
]

PROFANITY_WORDS = [
    "хуй", "пизд", "ебал", "еба", "бляд",
    "сука", "муда", "пидор", "гандон",
    "манда", "залуп", "чмо", "лох"
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Работа с курсом ---
def get_saved_rate():
    if os.path.exists("rate.txt"):
        with open("rate.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Не установлен"

def save_rate(new_rate):
    with open("rate.txt", "w", encoding="utf-8") as f:
        f.write(str(new_rate))

current_custom_rate = get_saved_rate()

# --- /start ---
@dp.message(Command("start"), F.chat.type == "private")
async def start_private(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👥 Войти в группу", url=GROUP_URL)
    )
    await message.answer(
        "👋 Привет!\n\nКурс USDT можно узнать в группе по команде /курс или /rate",
        reply_markup=builder.as_markup()
    )

# --- /set ---
@dp.message(Command("set"))
async def set_rate(message: types.Message, command: CommandObject):
    global current_custom_rate

    if message.from_user.id not in WHITELIST_IDS:
        return

    if command.args:
        current_custom_rate = command.args
        save_rate(current_custom_rate)
        await message.answer(f"✅ Курс обновлен: {current_custom_rate} TJS")
    else:
        await message.answer("⚠️ Используй: /set 12.50")

# --- /rate ---
@dp.message(Command("rate", "курс"))
async def get_rate_cmd(message: types.Message):
    try:
        await message.delete()
    except:
        pass

    text = (
        "🇹🇯 Актуальный курс USDT/TJS\n\n"
        f"💰 Курс: {current_custom_rate} TJS\n\n"
        "🤝 По UID или через сделку\n"
        "📞 Менеджер @nazar7zoda"
    )
    await message.answer(text)

# --- /mode ---
@dp.message(Command("mode"))
async def toggle_profanity_mode(message: types.Message):
    global PROFANITY_FILTER_ACTIVE

    if message.from_user.id not in WHITELIST_IDS:
        return

    PROFANITY_FILTER_ACTIVE = not PROFANITY_FILTER_ACTIVE

    try:
        await message.delete()
    except:
        pass

    status = "ВКЛЮЧЕН" if PROFANITY_FILTER_ACTIVE else "ОТКЛЮЧЕН"
    msg = await message.answer(f"🤬 Фильтр матов: {status}")
    await asyncio.sleep(4)
    await msg.delete()

# --- /spam ---
@dp.message(Command("spam"))
async def toggle_spam_mode(message: types.Message):
    global SPAM_FILTER_ACTIVE

    if message.from_user.id not in WHITELIST_IDS:
        return

    SPAM_FILTER_ACTIVE = not SPAM_FILTER_ACTIVE

    try:
        await message.delete()
    except:
        pass

    status = "ВКЛЮЧЕН" if SPAM_FILTER_ACTIVE else "ОТКЛЮЧЕН"
    msg = await message.answer(f"🛡 Фильтр спама: {status}")
    await asyncio.sleep(4)
    await msg.delete()

# --- Удаление сообщения ---
async def delete_msg(message: types.Message):
    try:
        await message.delete()
    except:
        pass

# --- ГЛАВНЫЙ ФИЛЬТР ---
@dp.message()
async def aggressive_anti_spam(message: types.Message):

    # ✅ Пропускаем личку
    if message.chat.type == "private":
        return

    if message.from_user.id in WHITELIST_IDS:
        return

    if message.content_type in [
        types.ContentType.NEW_CHAT_MEMBERS,
        types.ContentType.LEFT_CHAT_MEMBER
    ]:
        await delete_msg(message)
        return

    text_content = (message.text or message.caption or "").lower()

    # --- СПАМ ---
    if SPAM_FILTER_ACTIVE and text_content:

        if message.forward_from or message.forward_from_chat:
            await delete_msg(message)
            return

        if message.via_bot:
            await delete_msg(message)
            return

        entities = message.entities or message.caption_entities or []
        for entity in entities:
            if entity.type in ["url", "text_link"]:
                await delete_msg(message)
                return

        for word in SPAM_WORDS:
            if word in text_content:
                await delete_msg(message)
                return

    # --- МАТЫ ---
    if PROFANITY_FILTER_ACTIVE and text_content:
        for word in PROFANITY_WORDS:
            if word in text_content:
                await delete_msg(message)
                return

# --- ЗАПУСК ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print(f"🚀 Бот запущен! Курс: {current_custom_rate}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
