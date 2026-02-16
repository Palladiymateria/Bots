import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- БЕЗОПАСНЫЙ ИМПОРТ ---
# Бот попробует загрузить .env, но если его нет (на хостинге), он не сломается
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- ПОЛУЧЕНИЕ ТОКЕНА ---
# Бот берет токен из настроек хостинга
TOKEN = os.getenv("API_TOKEN")

# Если токен забыли добавить в настройки
if not TOKEN:
    print("❌ ОШИБКА: Токен не найден! Добавьте переменную API_TOKEN в настройках хостинга.")
    sys.exit()

# --- КОНФИГУРАЦИЯ ---
WHITELIST_IDS = [7918010548]  # ID Админов
MY_NICK = "@NoNameOkey"
GROUP_URL = "https://t.me/tajikistan_tether"

ALLOWED_USERNAMES = ["nazar7zoda", "x774n", "chinascorp", "didar_p2p", "dovud_p2p", "nonameokey"]

# Флаги (Оба включены при запуске)
PROFANITY_FILTER_ACTIVE = True 
SPAM_FILTER_ACTIVE = True      

# 1. СПИСОК СПАМА (Управляется через /spam)
SPAM_WORDS = [
    "заработок","подпишись", "сигналы", "профит", "доход", "раскрутка", "казино",
    "ставки", "vsem_privet", "в лс", "писать в лс", "p2p связки",
    "http", "https", ".com", ".ru", ".net", ".org", "t.me"
]

# 2. СПИСОК МАТОВ (Управляется через /mode)
PROFANITY_WORDS = [
    "хуй", "хyй", "xуй", "xuy", "хуе", "хуё", "хуи", "хуя",
    "пизд", "пuзд", "pizd", "пезд",
    "ебал", "еби", "ебь", "еба", "ёб", "yeb", "ипать", "еблан", "долбоеб",
    "бляд", "блят", "бля", "blya",
    "сука", "сучк", "суча", "suka",
    "муда", "муди", "мyд", "muda",
    "пидор", "пидар", "пидр", "pidor", "педик",
    "гандон", "гондон", "gandon",
    "манда", "залуп", "чмо", "лох", "дерьмо", "шлюх", "дроч"
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_saved_rate():
    if os.path.exists("rate.txt"):
        with open("rate.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Не установлен"

def save_rate(new_rate):
    with open("rate.txt", "w", encoding="utf-8") as f:
        f.write(str(new_rate))

current_custom_rate = get_saved_rate()

# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"), F.chat.type == "private")
async def start_private(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👥 Войти в группу", url=GROUP_URL))
    await message.answer(
        f"👋 Привет! Я бот Nazarooov.\n\n"
        f"Курс USDT можно узнать в нашей группе по команде /курс или /rate",
        reply_markup=builder.as_markup()
    )

@dp.message(Command("set"))
async def set_rate(message: types.Message, command: CommandObject):
    global current_custom_rate
    if message.from_user.id in WHITELIST_IDS:
        if command.args:
            current_custom_rate = command.args
            save_rate(current_custom_rate)
            await message.answer(f"✅ Курс обновлен: **{current_custom_rate} TJS**", parse_mode="Markdown")
        else:
            await message.answer("⚠️ Ошибка! Пиши: `/set 12.50`", parse_mode="Markdown")

@dp.message(Command("rate", "курс"))
async def get_rate_cmd(message: types.Message):
    global current_custom_rate
    try: await message.delete()
    except: pass

    try:
        text = (
            f"🇹🇯 **Актуальный курс USDT/TJS**\n\n"
            f"💰 **Курс**: {current_custom_rate} TJS\n\n"
            f"🤝По UID или через сделку\n"
            f"📞Менеджер @nazar7zoda\n"
        )
        await message.answer(text, parse_mode="Markdown")
    except Exception:
        pass

# --- УПРАВЛЕНИЕ РЕЖИМАМИ ---

@dp.message(Command("mode"))
async def toggle_profanity_mode(message: types.Message):
    global PROFANITY_FILTER_ACTIVE
    if message.from_user.id not in WHITELIST_IDS: return

    PROFANITY_FILTER_ACTIVE = not PROFANITY_FILTER_ACTIVE
    status_text = "✅ ВКЛЮЧЕН (Маты запрещены)" if PROFANITY_FILTER_ACTIVE else "❌ ОТКЛЮЧЕН (Маты разрешены)"

    try: await message.delete()
    except: pass

    try:
        msg = await message.answer(f"🤬 Фильтр МАТОВ: **{status_text}**", parse_mode="Markdown")
        await asyncio.sleep(4)
        await msg.delete()
    except: pass

@dp.message(Command("spam"))
async def toggle_spam_mode(message: types.Message):
    global SPAM_FILTER_ACTIVE
    if message.from_user.id not in WHITELIST_IDS: return

    SPAM_FILTER_ACTIVE = not SPAM_FILTER_ACTIVE
    status_text = "✅ ВКЛЮЧЕН (Ссылки и реклама удаляются)" if SPAM_FILTER_ACTIVE else "❌ ОТКЛЮЧЕН (Ссылки разрешены)"

    try: await message.delete()
    except: pass

    try:
        msg = await message.answer(f"🛡 Фильтр СПАМА: **{status_text}**", parse_mode="Markdown")
        await asyncio.sleep(4)
        await msg.delete()
    except: pass

# --- ГЛАВНЫЙ ФИЛЬТР ---

async def delete_msg(message: types.Message):
    try: await message.delete()
    except: pass

@dp.message()
async def aggressive_anti_spam(message: types.Message):
    # 1. Удаляем системные сообщения (вступил/вышел)
    if message.content_type in [types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER]:
        await delete_msg(message)
        return

    # 2. Админов не трогаем
    if message.from_user.id in WHITELIST_IDS: return

    # --- ПРОВЕРКА СПАМА (ЗАВИСИТ ОТ /spam) ---
    if SPAM_FILTER_ACTIVE:
        # Пересылки
        if message.forward_from or message.forward_from_chat:
            await delete_msg(message)
            return
        # Боты
        if message.via_bot:
            await delete_msg(message)
            return

        text_content = (message.text or message.caption or "").lower()
        if text_content:
            # Ссылки и юзернеймы
            entities = message.entities or message.caption_entities or []
            for entity in entities:
                if entity.type in ["url", "text_link"]:
                    await delete_msg(message)
                    return
                if entity.type == "mention":
                    raw_mention = text_content[entity.offset:entity.offset + entity.length]
                    clean_username = raw_mention.replace("@", "").strip().lower()
                    if clean_username not in ALLOWED_USERNAMES:
                        await delete_msg(message)
                        return
            
            # Арабская вязь
            if any("\u0600" <= char <= "\u06FF" for char in text_content):
                await delete_msg(message)
                return
            
            # Слова-спам
            for word in SPAM_WORDS:
                if word in text_content:
                    await delete_msg(message)
                    return

    # --- ПРОВЕРКА МАТОВ (ЗАВИСИТ ОТ /mode) ---
    if PROFANITY_FILTER_ACTIVE:
        text_content = (message.text or message.caption or "").lower()
        if text_content:
            for word in PROFANITY_WORDS:
                if word in text_content:
                    await delete_msg(message)
                    return

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print(f"🚀 Бот запущен! Курс: {current_custom_rate}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
