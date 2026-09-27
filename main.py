import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, LabeledPrice, PreCheckoutQuery
)
import aiosqlite
import os
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ----------------- КОНФИГУРАЦИЯ -----------------
TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "fivematchchat_bot"

# Список администраторов
ADMIN_IDS = [5156464855] 

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ----------------- БАЗА АЙСБРЕЙКЕРОВ (80+ ВОПРОСОВ) -----------------
ICEBREAKERS = [
    # Жизнь и гипотетические ситуации
    "Если бы тебе дали $100,000, но их нужно потратить за 1 час, что бы ты купил(а)?",
    "Какая самая глупая вещь, из-за которой ты злился(ась) или плакал(а)?",
    "В какой фильм или сериал ты хотел(а) бы попасть прямо сейчас?",
    "Что вкуснее: Доширак с сосиской или пицца за 2000 рублей?",
    "Оцени свою неделю от 1 до 10 и объясни, почему не 10.",
    "Если бы ты мог(ла) получить суперсилу, но она работает только по понедельникам, что бы ты выбрал(а)?",
    "Если бы тебе пришлось всю жизнь есть только одно блюдо, что бы это было?",
    "Какая у тебя самая странная привычка, о которой мало кто знает?",
    "Если бы ты мог(ла) переехать в любую точку мира прямо завтра, куда бы отправился(ась)?",
    "Какое твое самое любимое воспоминание из детства?",
    "Если бы за твоей жизнью следил весь мир как в «Шоу Трумана», какой момент был бы самым стыдным?",
    "Ты скорее откажешься от музыки на год или от соцсетей на год?",
    "Если бы ты встретил(а) себя 5 лет назад, какой главный совет ты бы себе дал(а)?",
    "Какая твоя самая спонтанная и безумная покупка?",
    "Если бы у тебя была возможность заглянуть в будущее на 10 лет вперед, что бы ты первым делом проверил(а)?",
    "Каким треком или песней можно охарактеризовать твою сегодняшнюю жизнь?",
    "Если бы тебе предложили $1,000,000 за то, чтобы не пользоваться телефоном месяц, ты бы справился(ась)?",
    "Какой самый лучший совет в жизни тебе когда-либо давали?",
    "Если бы ты мог(ла) свободно говорить на любом языке мира прямо сейчас, какой бы выбрал(а)?",
    "Что для тебя идеальный выходной: тусовка до утра или плед, сериалы и еда?",

    # Вкусы, поп-культура и юмор
    "Какой фильм или сериал ты готов(а) пересматривать бесконечно?",
    "Какой самый переоцененный фильм/сериал по твоему мнению?",
    "Какой трек у тебя сейчас стоит на повторе?",
    "Сладости или соленое? В чем твоя слабость?",
    "Какую последнюю песню ты напевал(а) в душе или про себя?",
    "Если бы ты снимался(ась) в кино, то какого персонажа тебе бы дали сыграть?",
    "Какой самый странный сон тебе снился за последнее время?",
    "Веришь ли ты в инопланетян или параллельные вселенные?",
    "Какая игра (компьютерная или настольная) навсегда в твоем сердце?",
    "Какой твой самый любимый мем всех времен?",
    "Ты сова или жаворонок, или просто вечно уставший человек?",
    "Школа, колледж/универ или работа: какой период кажется самым веселым?",
    "Какое у тебя самое необычное хобби?",
    "Ты веришь в знаки зодиака и астрологию или считаешь это бредом?",
    "Кем ты хотел(а) стать в детстве и насколько это совпало с реальностью?",
    "Какой твой самый любимый напиток (от газировки до кофе)?",
    "Если бы про тебя писали книгу, как бы она называлась?",
    "Какой звук тебя раздражает больше всего в жизни?",
    "Какая твоя любимая еда, когда хочется просто быстро перекусить?",
    "Какой самый угарный или нелепый подарок тебе когда-либо дарили?",

    # Отношения, вайб и психология
    "Что для тебя самое главное в людях: чувство юмора, доброта или интеллект?",
    "Как ты обычно реагируешь, когда тебе кто-то очень нравится?",
    "Что для тебя является абсолютным «зеленым флагом» в человеке при знакомстве?",
    "А что мгновенно отталкивает (главный «ред флаг»)?",
    "Как ты справляешься со стрессом или плохим настроением?",
    "Ты легко заводишь новых друзей или тебе нужно время, чтобы открыться?",
    "Веришь ли ты в дружбу между парнем и девушкой без подвоха?",
    "Что бы ты выбрал(а): уметь читать мысли или уметь становиться невидимым?",
    "Какой самый милый или романтичный поступок делали для тебя?",
    "Ты больше интроверт, экстраверт или где-то посередине?",
    "Как выглядит твой идеальный вечер с близким человеком?",
    "Что тебя может мгновенно поднять настроение, даже если день ужасен?",
    "Если бы ты мог(ла) задать любой один вопрос Вселенной и получить точный ответ, что бы ты спросил(а)?",
    "Чего ты больше всего боишься в жизни (фобии или ментальные страхи)?",
    "Как ты относишься к знакомствам в интернете: это база или случайность?",
    "О чем ты чаще всего думаешь перед сном?",
    "Бывало ли такое, что ты принимал(а) решение за 1 секунду и оно меняло всё?",
    "Что делает человека по-настоящему привлекательным для тебя?",
    "Какой поступок ты считаешь самым смелым в своей жизни?",
    "Ты умеешь прощать людей за серьезные ошибки или держишь обиду?",

    # Быстрые выборы «Что ты выберешь?»
    "Кошки или собаки?",
    "Чай или кофе?",
    "Лето или зима?",
    "Жизнь в шумном мегаполисе или в уютном доме у моря?",
    "Книги или фильмы?",
    "iOS или Android?",
    "Шаурма или бургер?",
    "Тусовка в клубе или ламповые посиделки дома?",
    "Путешествие в прошлое или в будущее?",
    "Всегда говорить только правду или больше никогда не говорить вообще?",
    "Уметь летать или телепортироваться?",
    "Готовить еду самому(ой) или заказывать доставку?",
    "Быть богатым и неизвестным или бедным и знаменитым?",
    "Поехать в горы или на пляж?",
    "Ночь или день?",

    # Нестандартные и провокационные
    "Если бы тебе пришлось остаток жизни жить на необитаемом острове с одним человеком из существующих, кого бы ты взял(а)?",
    "Какая самая большая глупость, которую ты сделал(а) на слабо?",
    "Если бы твои мысли транслировались на экране над твоей головой, как долго ты бы продержался(ась) в обществе?",
    "Какую одну вещь в мире ты бы навсегда отменил(а), если бы у тебя была такая власть?",
    "Ты бы предпочел(ла) знать дату своей смерти или причину?",
    "Если бы ты выиграл(а) 100 миллионов рублей в лотерею, кому первому ты бы рассказал(а)?",
    "Как думаешь, ИИ захватит этот мир или мы успеем дожить спокойно?",
    "Какая твоя самая любимая фраза или цитата?",
    "Если бы тебе предложили поучаствовать в реалити-шоу, ты бы согласился(ась)?",
    "Что ты сделаешь первым делом, когда наступит лето/следующий отпуск?"
]

# ----------------- СТРУКТУРА ЦЕН TELEGRAM STARS (XTR) -----------------
PRICES_PREMIUM = {
    "buy_prem_1": {"title": "PREMIUM на 1 день", "price": 49, "days": 1, "type": "premium"},
    "buy_prem_7": {"title": "PREMIUM на 7 дней", "price": 299, "days": 7, "type": "premium"},
    "buy_prem_30": {"title": "PREMIUM на 30 дней", "price": 799, "days": 30, "type": "premium"},
    "buy_prem_365": {"title": "PREMIUM на 1 год", "price": 2199, "days": 365, "type": "premium"},
}

PRICES_NSFW = {
    "buy_nsfw_1": {"title": "Пошлый чат на 1 день", "price": 149, "days": 1, "type": "nsfw"},
    "buy_nsfw_7": {"title": "Пошлый чат на 7 дней", "price": 399, "days": 7, "type": "nsfw"},
    "buy_nsfw_30": {"title": "Пошлый чат на 30 дней", "price": 999, "days": 30, "type": "nsfw"},
    "buy_nsfw_365": {"title": "Пошлый чат на 1 год", "price": 2199, "days": 365, "type": "nsfw"},
}

# ----------------- СОСТОЯНИЯ FSM -----------------
class ProfileStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_age = State()

class AdminStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_broadcast = State()

# ----------------- БАЗА ДАННЫХ -----------------
DB_PATH = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                gender TEXT DEFAULT 'Не указан',
                age INTEGER DEFAULT 0,
                is_premium INTEGER DEFAULT 0,
                nsfw_access INTEGER DEFAULT 0,
                target_gender TEXT DEFAULT 'любой',
                target_age_min INTEGER DEFAULT 0,
                target_age_max INTEGER DEFAULT 99,
                invited_count INTEGER DEFAULT 0,
                referred_by INTEGER DEFAULT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS required_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                channel_link TEXT NOT NULL,
                title TEXT NOT NULL
            )
        """)
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def register_user(user_id: int, referrer_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        user = await get_user(user_id)
        if not user:
            await db.execute(
                "INSERT INTO users (user_id, referred_by) VALUES (?, ?)",
                (user_id, referrer_id)
            )
            if referrer_id:
                await db.execute(
                    "UPDATE users SET invited_count = invited_count + 1 WHERE user_id = ?",
                    (referrer_id,)
                )
            await db.commit()

async def get_required_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM required_channels") as cursor:
            return await cursor.fetchall()

# ----------------- ХРАНИЛИЩЕ СЕССИЙ ЧАТА -----------------
waiting_queue = []
active_chats = {}
chat_stats = {}

def get_session_key(u1: int, u2: int):
    return tuple(sorted([u1, u2]))

# ----------------- КЛАВИАТУРЫ (INLINE) -----------------
def kb_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Искать собеседника", callback_data="main_search")],
        [InlineKeyboardButton(text="👥 Поиск по полу и возрасту", callback_data="main_filter_search")],
        [
            InlineKeyboardButton(text="🥳 PREMIUM", callback_data="main_premium"),
            InlineKeyboardButton(text="🔞 Пошлый чат", callback_data="main_nsfw")
        ],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="main_profile")]
    ])

def kb_icebreaker():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Вбросить тему", callback_data="trigger_icebreaker")]
    ])

async def kb_sponsors():
    channels = await get_required_channels()
    buttons = []
    row = []
    
    for ch in channels:
        row.append(InlineKeyboardButton(text=ch['title'], url=ch['channel_link']))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="💎 Отключить рекламу", callback_data="remove_ads")])
    buttons.append([InlineKeyboardButton(text="Продолжить", callback_data="start_search_after_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_profile(is_premium: bool):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Изменить возраст и пол", callback_data="profile_edit_info")],
        [InlineKeyboardButton(text="👩‍❤️‍👨 Пригласить друга", callback_data="profile_referral")]
    ])

def kb_gender_select():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👩 Девушка", callback_data="set_gender_female"),
            InlineKeyboardButton(text="👨 Парень", callback_data="set_gender_male")
        ]
    ])

def kb_age_select():
    buttons = []
    row = []
    for age in range(10, 24):
        row.append(InlineKeyboardButton(text=str(age), callback_data=f"set_age_{age}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    row.append(InlineKeyboardButton(text="24+", callback_data="set_age_24"))
    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_premium_buy():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день - 49★", callback_data="buy_prem_1")],
        [InlineKeyboardButton(text="7 дней - 299★", callback_data="buy_prem_7")],
        [InlineKeyboardButton(text="30 дней - 799★", callback_data="buy_prem_30")],
        [InlineKeyboardButton(text="1 год - 2199★", callback_data="buy_prem_365")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])

def kb_premium_page():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🥳 Выбрать период PREMIUM", callback_data="prem_select_period")],
        [InlineKeyboardButton(text="🎁 Бесплатный премиум за друзей", callback_data="profile_referral")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])

def kb_nsfw_buy():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день - 149★", callback_data="buy_nsfw_1")],
        [InlineKeyboardButton(text="7 дней - 399★", callback_data="buy_nsfw_7")],
        [InlineKeyboardButton(text="30 дней - 999★", callback_data="buy_nsfw_30")],
        [InlineKeyboardButton(text="1 год - 2199★", callback_data="buy_nsfw_365")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])

def kb_remove_ads():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👩‍❤️‍👨 Рефералка", callback_data="profile_referral")],
        [InlineKeyboardButton(text="🥳 Купить PREMIUM", callback_data="prem_select_period")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])

def kb_decision():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Продолжить общение", callback_data="decision_continue"),
            InlineKeyboardButton(text="🔴 Пропустить", callback_data="decision_stop")
        ]
    ])

def kb_filter_settings(gender: str, age_str: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"👥 Пол: {gender}", callback_data="filter_set_gender"),
            InlineKeyboardButton(text=f"📅 Возраст: {age_str}", callback_data="filter_set_age")
        ],
        [InlineKeyboardButton(text="🚀 Начать поиск", callback_data="start_search_after_sub")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])

def kb_admin_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📌 Управление каналами", callback_data="admin_channels")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")]
    ])

async def kb_admin_channels_list():
    channels = await get_required_channels()
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"❌ Удалить: {ch['title']}", callback_data=f"admin_del_ch_{ch['id']}")])
    buttons.append([InlineKeyboardButton(text="➕ Добавить канал", callback_data="admin_add_channel")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ----------------- ПРОВЕРКА ПОДПИСОК -----------------
async def check_all_subscriptions(user_id: int) -> bool:
    channels = await get_required_channels()
    if not channels:
        return True
    
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch['channel_id'], user_id=user_id)
            if member.status not in ["creator", "administrator", "member"]:
                return False
        except Exception:
            continue
    return True

# ----------------- ФУНКЦИЯ И ГЕНЕРАТОР АЙСБРЕЙКЕРОВ -----------------
async def send_icebreaker_to_chat(user_id: int):
    if user_id not in active_chats:
        return False, "Вы не находитесь в диалоге!"

    partner_id = active_chats[user_id]
    session_key = get_session_key(user_id, partner_id)
    session = chat_stats.get(session_key)

    if not session:
        return False, "Ошибка сессии диалога."

    if 'used_icebreakers' not in session:
        session['used_icebreakers'] = []

    available_questions = [q for q in ICEBREAKERS if q not in session['used_icebreakers']]
    
    if not available_questions:
        session['used_icebreakers'] = []
        available_questions = ICEBREAKERS

    q = random.choice(available_questions)
    session['used_icebreakers'].append(q)

    ice_text = f"🎲 **Вброс темы для обсуждения:**\n\n_{q}_"
    
    await bot.send_message(user_id, ice_text, reply_markup=kb_icebreaker(), parse_mode="Markdown")
    await bot.send_message(partner_id, ice_text, reply_markup=kb_icebreaker(), parse_mode="Markdown")
    return True, None

@dp.callback_query(F.data == "trigger_icebreaker")
async def cb_trigger_icebreaker(call: types.CallbackQuery):
    success, err_text = await send_icebreaker_to_chat(call.from_user.id)
    if not success:
        await call.answer(err_text, show_alert=True)
    else:
        await call.answer()

@dp.message(Command("icebreaker"))
async def cmd_icebreaker(message: types.Message):
    success, err_text = await send_icebreaker_to_chat(message.from_user.id)
    if not success:
        await message.answer(err_text)

# ----------------- ХЕНДЛЕРЫ ОПЛАТЫ TELEGRAM STARS -----------------
@dp.callback_query(F.data.startswith("buy_prem_") | F.data.startswith("buy_nsfw_"))
async def process_buy_stars(call: types.CallbackQuery):
    item_code = call.data
    item_data = PRICES_PREMIUM.get(item_code) or PRICES_NSFW.get(item_code)
    
    if not item_data:
        await call.answer("Тариф не найден", show_alert=True)
        return

    title = item_data["title"]
    description = f"Активация подписки '{title}' в бота 5Match"
    payload = f"{item_data['type']}:{item_data['days']}:{call.from_user.id}"
    
    prices = [LabeledPrice(label=title, amount=item_data["price"])]

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",  # Пустой токен для Telegram Stars
        currency="XTR",     # Валюта Telegram Stars
        prices=prices,
        start_parameter="buy_subscription"
    )
    await call.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    payload_parts = payment_info.invoice_payload.split(":")
    
    sub_type = payload_parts[0]
    days = int(payload_parts[1])
    user_id = message.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        if sub_type == "premium":
            await db.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (user_id,))
            text_success = f"🥳 **Поздравляем!** PREMIUM успешно активирован на {days} дн. Настройки фильтра пола и возраста теперь доступны!"
        else:
            await db.execute("UPDATE users SET nsfw_access = 1 WHERE user_id = ?", (user_id,))
            text_success = f"🔥 **Доступ открыт!** Режим «Пошлый чат» успешно активирован на {days} дн."
        
        await db.commit()

    await message.answer(text_success, parse_mode="Markdown", reply_markup=kb_main_menu())

# ----------------- ХЕНДЛЕРЫ КОМАНД -----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    referrer_id = None
    if command.args and command.args.isdigit():
        referrer_id = int(command.args)
        if referrer_id == message.from_user.id:
            referrer_id = None

    await register_user(message.from_user.id, referrer_id)
    
    text = (
        "👋 **Добро пожаловать в 5Match!**\n\n"
        "⚡ В нашем анонимном чате действует правило **5 сообщений**.\n"
        "Выбирай действие ниже:"
    )
    await message.answer(text, reply_markup=kb_main_menu(), parse_mode="Markdown")

@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    user_id = message.from_user.id
    if user_id in waiting_queue:
        waiting_queue.remove(user_id)
        await message.answer("Поиск остановлен.", reply_markup=kb_main_menu())
        return

    partner_id = active_chats.pop(user_id, None)
    if partner_id:
        active_chats.pop(partner_id, None)
        session_key = get_session_key(user_id, partner_id)
        chat_stats.pop(session_key, None)

        await message.answer("Вы завершили диалог.", reply_markup=kb_main_menu())
        await bot.send_message(partner_id, "Собеседник завершил диалог.", reply_markup=kb_main_menu())
    else:
        await message.answer("Вы не находитесь в диалоге.", reply_markup=kb_main_menu())

# ----------------- АДМИН-ПАНЕЛЬ -----------------
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    await message.answer("⚙️ **Панель администратора**", reply_markup=kb_admin_main(), parse_mode="Markdown")

@dp.callback_query(F.data == "admin_home")
async def cb_admin_home(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    await call.message.edit_text("⚙️ **Панель администратора**", reply_markup=kb_admin_main(), parse_mode="Markdown")

@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            count = (await cursor.fetchone())[0]
    await call.answer(f"📊 Всего пользователей в базе: {count}", show_alert=True)

@dp.callback_query(F.data == "admin_channels")
async def cb_admin_channels(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        return
    reply_markup = await kb_admin_channels_list()
    await call.message.edit_text("📌 **Список обязательных каналов:**", reply_markup=reply_markup, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_add_channel")
async def cb_admin_add_channel(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminStates.waiting_for_channel)
    text = (
        "➕ **Добавление канала**\n\n"
        "Отправьте данные строго в формате:\n"
        "`@channel_username | https://t.me/link | Название Кнопки`\n\n"
        "*Важно:* Бот должен быть заранее назначен администратором в добавляемом канале!"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

@dp.message(AdminStates.waiting_for_channel)
async def process_add_channel(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        parts = [p.strip() for p in message.text.split("|")]
        if len(parts) != 3:
            raise ValueError
        
        ch_id, ch_link, ch_title = parts[0], parts[1], parts[2]

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO required_channels (channel_id, channel_link, title) VALUES (?, ?, ?)",
                (ch_id, ch_link, ch_title)
            )
            await db.commit()

        await state.clear()
        await message.answer("✅ Канал успешно добавлен!", reply_markup=kb_admin_main())
    except Exception:
        await message.answer("❌ Ошибка формата! Отправьте строго в формате:\n`@username | https://t.me/link | Название`")

@dp.callback_query(F.data.startswith("admin_del_ch_"))
async def cb_admin_del_channel(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        return
    ch_pk = int(call.data.replace("admin_del_ch_", ""))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM required_channels WHERE id = ?", (ch_pk,))
        await db.commit()
    
    await call.answer("Канал удален!")
    reply_markup = await kb_admin_channels_list()
    await call.message.edit_text("📌 **Список обязательных каналов:**", reply_markup=reply_markup, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminStates.waiting_for_broadcast)
    await call.message.edit_text("📢 Отправьте сообщение (текст или фото) для массовой рассылки всем пользователям:")

@dp.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()

    users = [r[0] for r in rows]
    status_msg = await message.answer(f"🚀 Рассылка начата... Всего получателей: {len(users)}")

    success = 0
    blocked = 0

    for u_id in users:
        try:
            if message.photo:
                await bot.send_photo(u_id, message.photo[-1].file_id, caption=message.caption)
            else:
                await bot.send_message(u_id, message.text)
            success += 1
        except Exception:
            blocked += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ **Рассылка завершена!**\n\n"
        f"👤 Успешно доставлено: {success}\n"
        f"🚫 Заблокировали бота: {blocked}",
        parse_mode="Markdown"
    )

# ----------------- INLINE МЕНЮ И ПОИСК -----------------
@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "🚀 **Главное меню 5Match**\n\nВыберите действие ниже:",
        reply_markup=kb_main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "main_profile")
async def cb_profile(call: types.CallbackQuery):
    user = await get_user(call.from_user.id)
    gender = user["gender"]
    age = user["age"] if user["age"] > 0 else "Не указан"
    is_prem = bool(user["is_premium"])

    status_text = "Вы 🥳 **VIP пользователь**" if is_prem else "Вы не 👑 **VIP пользователь**"
    text = f"🆔 — `{call.from_user.id}`\n\n🧑‍🤝‍🧑 Пол — {gender}\n🔞 Возраст — {age}\n\n{status_text}"
    await call.message.edit_text(text, reply_markup=kb_profile(is_prem), parse_mode="Markdown")

@dp.callback_query(F.data == "profile_referral")
async def cb_referral(call: types.CallbackQuery):
    user_id = call.from_user.id
    user = await get_user(user_id)
    count = user["invited_count"] if user else 0
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    text = (
        "🦋 Приглашайте пользователей по своей ссылке и получайте 👑 VIP статус на 1 час за каждого!\n\n"
        f"🌸 Приглашено: {count}\n\n"
        f"Ваша персональная ссылка:\n{ref_link}"
    )
    await call.message.edit_text(text, disable_web_page_preview=True)

@dp.callback_query(F.data == "profile_edit_info")
async def cb_edit_info(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.waiting_for_gender)
    await call.message.edit_text("Выбери ниже, какого ты пола?", reply_markup=kb_gender_select())

@dp.callback_query(F.data.startswith("set_gender_"), ProfileStates.waiting_for_gender)
async def cb_set_gender(call: types.CallbackQuery, state: FSMContext):
    gender = "Парень" if call.data == "set_gender_male" else "Девушка"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, call.from_user.id))
        await db.commit()
    
    await state.set_state(ProfileStates.waiting_for_age)
    await call.message.edit_text("Выбери ниже, сколько тебе лет?", reply_markup=kb_age_select())

@dp.callback_query(F.data.startswith("set_age_"), ProfileStates.waiting_for_age)
async def cb_set_age(call: types.CallbackQuery, state: FSMContext):
    age_val = call.data.replace("set_age_", "")
    age = 24 if age_val == "24" else int(age_val)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET age = ? WHERE user_id = ?", (age, call.from_user.id))
        await db.commit()
    
    await state.clear()
    await call.answer("Данные успешно обновлены!", show_alert=True)
    await cb_profile(call)

@dp.callback_query(F.data == "main_premium")
async def cb_premium(call: types.CallbackQuery):
    text = (
        "Общайтесь с 🥳 **PREMIUM** без ограничений\n\n"
        "⚡ **Преимущества**\n"
        "• Приоритетный поиск\n"
        "• Фильтр по активности\n"
        "• Поиск по полу и возрасту\n"
        "• Отключение всей рекламы\n"
        "• Виден пол и возраст собеседника\n"
        "• Общение без подписок на задания\n"
        "• Скрываемый значок 🥳 PREMIUM в диалоге"
    )
    await call.message.edit_text(text, reply_markup=kb_premium_page(), parse_mode="Markdown")

@dp.callback_query(F.data == "prem_select_period")
async def cb_prem_select(call: types.CallbackQuery):
    text = (
        "🥳 **PREMIUM — и функция откроется**\n\n"
        "👥 **Поиск по полу и возрасту**\n"
        "_Выбирайте, с кем общаться: пол, возраст, автопоиск_\n\n"
        "Выберите период 🥳 **PREMIUM** для покупки"
    )
    await call.message.edit_text(text, reply_markup=kb_premium_buy(), parse_mode="Markdown")

@dp.callback_query(F.data == "main_filter_search")
async def cb_filter_search(call: types.CallbackQuery):
    user = await get_user(call.from_user.id)
    if not user["is_premium"]:
        text = (
            "🥳 **PREMIUM — и функция откроется**\n\n"
            "👥 **Поиск по полу и возрасту**\n"
            "_Выбирайте, с кем общаться: пол, возраст, автопоиск и автоскип_\n\n"
            "Выберите период 🥳 **PREMIUM** для покупки"
        )
        await call.message.edit_text(text, reply_markup=kb_premium_buy(), parse_mode="Markdown")
    else:
        g = user["target_gender"]
        a_str = f"{user['target_age_min']}-{user['target_age_max']}" if user["target_age_min"] > 0 else "любой"
        text = f"⚙️ **Настройки подбора собеседников**\n\nПол: {g}\nВозраст: {a_str}"
        await call.message.edit_text(text, reply_markup=kb_filter_settings(g, a_str), parse_mode="Markdown")

@dp.callback_query(F.data == "main_nsfw")
async def cb_nsfw(call: types.CallbackQuery):
    text = (
        "🔥 **Пошлый чат**\n"
        "_Общение без ограничений: «Интим 18+» и «Продажа/Покупка 18+»_\n\n"
        "Выберите период 🔥 **Пошлый чат** для покупки"
    )
    await call.message.edit_text(text, reply_markup=kb_nsfw_buy(), parse_mode="Markdown")

@dp.callback_query(F.data == "remove_ads")
async def cb_remove_ads(call: types.CallbackQuery):
    text = (
        "💎 **Отключить рекламу**\n\n"
        "Получите PREMIUM статус или приглашайте друзей, чтобы не подписываться на каналы!"
    )
    await call.message.edit_text(text, reply_markup=kb_remove_ads())

@dp.callback_query(F.data == "main_search")
async def cb_main_search(call: types.CallbackQuery):
    user = await get_user(call.from_user.id)

    if not user["is_premium"]:
        is_sub = await check_all_subscriptions(call.from_user.id)
        if not is_sub:
            sponsors_kb = await kb_sponsors()
            text = "💭 Собеседник найден, для начала общения подпишитесь на спонсоров"
            await call.message.edit_text(text, reply_markup=sponsors_kb)
            return

    await start_queue_search(call)

@dp.callback_query(F.data == "start_search_after_sub")
async def cb_search_after_sub(call: types.CallbackQuery):
    is_sub = await check_all_subscriptions(call.from_user.id)
    if not is_sub:
        await call.answer("Вы подписались не на все каналы!", show_alert=True)
        return
    await start_queue_search(call)

async def start_queue_search(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id in active_chats:
        await call.answer("Вы уже в диалоге!", show_alert=True)
        return
    if user_id in waiting_queue:
        await call.answer("Вы уже ищете собеседника...", show_alert=True)
        return

    if waiting_queue:
        partner_id = waiting_queue.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        s_key = get_session_key(user_id, partner_id)
        chat_stats[s_key] = {user_id: 5, partner_id: 5, 'status': 'challenge', 'used_icebreakers': []}

        msg_text = (
            "🎉 **Собеседник найден!**\n\n"
            "⚡ **Челлендж 5Lines начался!**\n"
            "У вас есть по **5 сообщений**, чтобы заинтересовать друг друга.\n"
            "Осталось сообщений: 💬 **5/5**"
        )
        await bot.send_message(partner_id, msg_text, reply_markup=kb_icebreaker(), parse_mode="Markdown")
        await call.message.edit_text(msg_text, reply_markup=kb_icebreaker(), parse_mode="Markdown")
    else:
        waiting_queue.append(user_id)
        await call.message.edit_text("⏳ Ищем собеседника... Нажмите /stop для отмены.")

# ----------------- ОБРАБОТКА ДИАЛОГОВИЧЕСКИХ СООБЩЕНИЙ -----------------
@dp.message()
async def process_chat_messages(message: types.Message):
    user_id = message.from_user.id
    if user_id not in active_chats:
        await message.answer("Вы не в диалоге. Нажмите /start для выхода в меню.")
        return

    partner_id = active_chats[user_id]
    s_key = get_session_key(user_id, partner_id)
    session = chat_stats.get(s_key)
    if not session:
        return

    if session['status'] == 'challenge':
        if session[user_id] <= 0:
            await message.answer("⏳ Вы уже исчерпали свой лимит в 5 сообщений! Ожидайте ответа собеседника.")
            return

        session[user_id] -= 1
        remains = session[user_id]

        if message.text:
            await bot.send_message(partner_id, f"{message.text}\n\n_(Осталось сообщений: {remains}/5)_", parse_mode="Markdown")
        elif message.photo:
            await bot.send_photo(partner_id, message.photo[-1].file_id, caption=f"{message.caption or ''}\n\n_(Осталось сообщений: {remains}/5)_", parse_mode="Markdown")

        if session[user_id] == 0 and session[partner_id] == 0:
            text_finish = "🔒 **5 сообщений отправлено!**\nХотите продолжить общение?"
            await bot.send_message(user_id, text_finish, reply_markup=kb_decision(), parse_mode="Markdown")
            await bot.send_message(partner_id, text_finish, reply_markup=kb_decision(), parse_mode="Markdown")
            return

    elif session['status'] == 'unlimited':
        if message.text:
            await bot.send_message(partner_id, message.text)
        elif message.photo:
            await bot.send_photo(partner_id, message.photo[-1].file_id, caption=message.caption)

# ----------------- РЕГИСТРАЦИЯ КОМАНД И ЗАПУСК -----------------
async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="stop", description="❌ Завершить диалог / Поиск"),
        BotCommand(command="icebreaker", description="🎲 Вбросить тему"),
        BotCommand(command="admin", description="⚙️ Админ-панель")
    ]
    await bot.set_my_commands(commands)

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    await setup_bot_commands(bot)
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
