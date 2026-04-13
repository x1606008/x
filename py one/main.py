import asyncio
import logging
import sys
import random
import datetime
from collections import defaultdict


from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "8600455704:AAFwyd1AijMWpbDQiZNs7D33tffOspjYSXA"

# Admin IDs
admin_ids = [123456789]  # Replace with actual admin user IDs

# User states for context
user_states = {}  # user_id -> {'state': 'asking_name', 'name': None}

# Learned words
learned_words = {}  # word -> response

# Keyword usage statistics
keyword_usage = defaultdict(int)

# Keywords with synonyms
keywords = {
    'salom': ['salom', 'assalom', 'hi', 'hello', 'qale'],
    'vaqt': ['vaqt', 'soat', 'time', 'vaqti'],
    'sana': ['sana', 'date', 'kun'],
    'hazil': ['hazil', 'joke', 'kulgi'],
    'yordam': ['yordam', 'help', 'yordam bering'],
    'rahmat': ['rahmat', 'thank you', 'thanks', 'rahmatli'],
    'xayr': ['xayr', 'goodbye', 'bye', 'hayr'],
    'ism': ['ism', 'name', 'nomi'],
    'yosh': ['yosh', 'age', 'yoshi'],
    'ob-havo': ['ob-havo', 'weather', 'havo'],
    'yangilik': ['yangilik', 'news', 'yangiliklar'],
    'musiqa': ['musiqa', 'music', 'qo\'shiq'],
    'film': ['film', 'movie', 'kino'],
    'kitob': ['kitob', 'book', 'kitoblar'],
    'sport': ['sport', 'sports', 'sportchi'],
    "o'yin": ["o'yin", 'game', 'oyin'],
    'taom': ['taom', 'food', 'ovqat'],
    'ichimlik': ['ichimlik', 'drink', 'suv'],
    'sayohat': ['sayohat', 'travel', 'sayohat qilish'],
    'ish': ['ish', 'work', 'ishlash'],
    "o'qish": ["o'qish", 'study', 'oqish'],
    'sevgi': ['sevgi', 'love', 'muhabbat'],
    "do'st": ["do'st", 'friend', 'dost'],
    'oila': ['oila', 'family', 'oilaviy'],
    'hayot': ['hayot', 'life', 'hayotiy'],
    'statistika': ['statistika', 'statistics', 'stat'],
    'tozalash': ['tozalash', 'clear', 'toza'],
}

responses = {
    'salom': [
        "Salom!",
        "Assalomu alaykum!",
        "Yaxshimisiz?",
        "Salom, qalaysiz?",
    ],
    'vaqt': lambda: f"Hozirgi vaqt: {datetime.now().strftime('%H:%M:%S')}",
    'sana': lambda: f"Bugungi sana: {datetime.now().strftime('%Y-%m-%d')}",
    'hazil': [
        "Nima hazil? Men botman, hazil aytolmayman! 😄",
        "Hazil: Nega kompyuterlar hech qachon och qolmaydi? Chunki ular har doim 'byte' qiladi! 😂",
        "Hazil: Robotlar nima ichadi? 'Oil'! 🛢️",
    ],
    'yordam': "Yordam kerakmi? Quyidagi tugmalardan foydalaning.",
    'rahmat': [
        "Arzimaydi!",
        "Rahmat, xursandman!",
        "Doim yordamga tayyor!",
    ],
    'xayr': [
        "Xayr!",
        "Ko'rishguncha!",
        "Salomat bo'ling!",
    ],
    'ism': "Ismingiz nima?",
    'yosh': "Yoshingiz nechida?",
    'ob-havo': "Ob-havo haqida ma'lumot beraman, lekin hozir aniq bilmayman. ☀️",
    'yangilik': "Yangiliklar: Bugun dunyoda tinchlik hukm surmoqda! 📰",
    'musiqa': "Musiqa tinglash yaxshi! 🎵",
    'film': "Film ko'rish zavqli! 🎬",
    'kitob': "Kitob o'qish foydali! 📚",
    'sport': "Sport bilan shug'ullanish sog'liq uchun yaxshi! ⚽",
    "o'yin": "O'yin o'ynash qiziq! 🎮",
    'taom': "Taom tayyorlash san'at! 🍲",
    'ichimlik': "Ichimlik ichish tetiklik beradi! 🥤",
    'sayohat': "Sayohat qilish hayotni boyitadi! ✈️",
    'ish': "Ish qilish muvaffaqiyat kaliti! 💼",
    "o'qish": "O'qish bilim beradi! 📖",
    'sevgi': "Sevgi eng go'zal his! ❤️",
    "do'st": "Do'stlar hayotning mazasi! 👫",
    'oila': "Oila eng muhim! 👨‍👩‍👧",
    'hayot': "Hayot go'zal, uni qadrlang! 🌸",
    'statistika': lambda: f"Statistika: {dict(keyword_usage)}",
    'tozalash': "Ma'lumotlar tozalandi.",
}

dp = Dispatcher()

def find_keywords(message_text):
    """Find all matching keywords in the message."""
    msg = message_text.lower()
    found = set()
    for key, syns in keywords.items():
        if any(syn in msg for syn in syns):
            found.add(key)
    return found

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}! Men aqlli botman. Yordam uchun 'yordam' yozing.")

@dp.message()
async def message_handler(message: Message) -> None:
    user_id = message.from_user.id
    text = message.text
    if not text:
        return
    found = find_keywords(text)
    if not found:
        # Check learned words
        if text.lower() in learned_words:
            await message.answer(learned_words[text.lower()])
        else:
            learned_words[text.lower()] = f"Tushundim: {text}"
            await message.answer("Kechirasiz, tushunmadim 🤔 Lekin saqlab qoldim.")
        return

    responses_list = []
    for key in found:
        if key in ['statistika', 'tozalash'] and user_id not in admin_ids:
            continue
        keyword_usage[key] += 1
        resp = responses[key]
        if callable(resp):
            if key == 'statistika':
                resp = resp()
            elif key == 'tozalash':
                user_states.clear()
                learned_words.clear()
                keyword_usage.clear()
                resp = resp
            else:
                resp = resp()
        else:
            resp = random.choice(resp) if isinstance(resp, list) else resp
        responses_list.append(resp)

    # Context handling
    if 'salom' in found and user_id not in user_states:
        user_states[user_id] = {'state': 'asking_name'}
        responses_list.append("Ismingiz nima?")
    elif user_id in user_states and user_states[user_id]['state'] == 'asking_name':
        user_states[user_id]['name'] = text
        user_states[user_id]['state'] = 'has_name'
        responses_list.append(f"Tanishganimdan xursandman, {text}!")

    # Handle help with keyboard
    if 'yordam' in found:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Vaqt"), KeyboardButton(text="Sana")],
                [KeyboardButton(text="Hazil"), KeyboardButton(text="Yordam")],
            ],
            resize_keyboard=True
        )
        await message.answer('\n'.join(responses_list), reply_markup=keyboard)
        return

    full_response = '\n'.join(responses_list)
    await message.answer(full_response)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())