import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- ЗАГРУЗКА .env (если есть) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- ТОКЕН ---
TOKEN = os.getenv("API_TOKEN")

if not TOKEN:
    print("❌ ОШИБКА: Добавьте API_TOKEN в настройки хостинга.")
    sys.exit()

# --- НАСТРОЙКИ ---
WHITELIST_IDS = [7918010548]
GROUP_URL = "https://t.me/tajikistan_tether"
GROUP_ID = -1003165407671  # <-- ВСТАВЬ ID СВОЕЙ ГРУППЫ

PROFANITY_FILTER_ACTIVE = True
SPAM_FILTER_ACTIVE = True

# --- ПРЕДУПРЕЖДЕНИЕ ---
WARNING_TEXT = (
    "🚨 ВНИМАНИЕ! ОФИЦИАЛЬНОЕ ПРЕДУПРЕЖДЕНИЕ 🚨\n\n"
    "Зафиксированы случаи, когда мошенники копируют сообщения из нашей группы, "
    "создают похожие каналы и выдают себя за официальную площадку.\n\n"
    "❗ Они копируют тексты и оформление.\n"
    "❗ Они могут писать в личные сообщения.\n"
    "❗ Они могут создавать фейковые группы.\n\n"
    "⚠️ ВАЖНО:\n"
    "Откуп проводится исключительно через ЭТУ официальную группу.\n"
    "Если вас добавляют в другие похожие чаты или пишут от имени проекта — "
    "это мошенники.\n\n"
    "Администрация не несёт ответственности за переводы средств третьим лицам.\n\n"
    "🛡 Подписывайтесь только на нашу официальную группу."
)

SPAM_WORDS = [
    "заработок","подпишись","сигналы","профит","доход","раскрутка","казино",
    "ставки","в лс","писать в лс","http","https",".com",".ru",".net",".org","t.me"
]

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

# --- КУРС ---
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
    builder.row(types.InlineKeyboardButton(text="👥 Войти в группу", url=GROUP_URL))
    await message.answer(
        "👋 Привет!\n\n"
        "Курс USDT можно узнать в группе по команде /курс или /rate",
        reply_markup=builder.as_markup()
    )

# --- /set ---
@dp.message(Command("set"))
async def set_rate(message: types.Message, command: CommandObject):
    global current_custom_rate
    if message.from_user.id in WHITELIST_IDS:
        if command.args:
            current_custom_rate = command.args
            save_rate(current_custom_rate)
            await message.answer(
                f"✅ Курс обновлен: **{current_custom_rate} TJS**",
                parse_mode="Markdown"
            )
        else:
            await message.answer("⚠️ Используй: /set 12.50", parse_mode="Markdown")

# --- /rate ---
@dp.message(Command("rate", "курс"))
async def get_rate_cmd(message: types.Message):
    try:
        await message.delete()
    except:
        pass

    text = (
        f"🇹🇯 **Актуальный курс USDT/TJS**\n\n"
        f"💰 **Курс**: {current_custom_rate} TJS\n\n"
        f"🤝По UID или через сделку\n"
        f"📞Менеджер @nazar7zoda\n"
    )

    await message.answer(text, parse_mode="Markdown")

# --- УДАЛЕНИЕ ---
async def delete_msg(message: types.Message):
    try:
        await message.delete()
    except:
        pass

# --- АНТИСПАМ ---
@dp.message()
async def aggressive_filter(message: types.Message):

    if message.from_user.id in WHITELIST_IDS:
        return

    text_content = (message.text or message.caption or "").lower()

    if SPAM_FILTER_ACTIVE and text_content:
        for word in SPAM_WORDS:
            if word in text_content:
                await delete_msg(message)
                return

    if PROFANITY_FILTER_ACTIVE and text_content:
        for word in PROFANITY_WORDS:
            if word in text_content:
                await delete_msg(message)
                return

# --- АВТО-ПРЕДУПРЕЖДЕНИЕ КАЖДЫЙ ЧАС ---
async def hourly_warning():
    while True:
        try:
            await bot.send_message(GROUP_ID, WARNING_TEXT)
        except Exception as e:
            print("Ошибка отправки предупреждения:", e)
        await asyncio.sleep(3600)

# --- ЗАПУСК ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print(f"🚀 Бот запущен! Курс: {current_custom_rate}")

    asyncio.create_task(hourly_warning())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
