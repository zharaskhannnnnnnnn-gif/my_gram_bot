import asyncio
import sqlite3
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# ================= КОНФИГУРАЦИЯ =================
TOKEN = "8800027665:AAGfM8tZin6NqlzZirqgvfE9_beOuhWBQJ4"
ADMIN_ID = 8831958470

CHANNEL_1_ID = "@AbaddonGram"
CHANNEL_2_ID = "@GramLudickers"

CHANNEL_1_LINK = "https://t.me/AbaddonGram"
CHANNEL_2_LINK = "https://t.me/GramLudickers"
SPONSOR_1_URL = "https://t.me/chatik5_gpt_bot?start=utm_Hsjsuskwk015"
SPONSOR_2_URL = "https://t.me/OnlineSmsM5_bot?start=l_Jsusiwkwk015"

WELCOME_PHOTO = "https://i.ibb.co.com/5gG4DhXC/1791558072252.jpg"

REFERRAL_REWARD = 5000
DAILY_BONUS_REWARD = 500
MIN_WITHDRAW = 30000

# ================= БАЗА ДАННЫХ =================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            lang TEXT DEFAULT 'ru',
            balance INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            referred_by INTEGER,
            reward_given INTEGER DEFAULT 0,
            is_subbed INTEGER DEFAULT 0,
            start_time REAL,
            last_bonus_time REAL DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdraws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            amount INTEGER,
            requisites TEXT,
            status TEXT DEFAULT '⏳ В обработке'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_user_data(user_id, username="no_username"):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, lang, balance, referrals, referred_by, reward_given, is_subbed, start_time, last_bonus_time FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        now_time = time.time()
        cursor.execute(
            "INSERT INTO users (user_id, username, lang, balance, referrals, referred_by, reward_given, is_subbed, start_time, last_bonus_time) VALUES (?, ?, 'ru', 0, 0, NULL, 0, 0, ?, 0)",
            (user_id, username, now_time)
        )
        conn.commit()
        cursor.execute("SELECT user_id, username, lang, balance, referrals, referred_by, reward_given, is_subbed, start_time, last_bonus_time FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    else:
        if username != "no_username" and row[1] != username:
            cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
            conn.commit()

    conn.close()
    return {
        "user_id": row[0],
        "username": row[1],
        "lang": row[2],
        "balance": row[3],
        "referrals": row[4],
        "referred_by": row[5],
        "reward_given": bool(row[6]),
        "is_subbed": bool(row[7]),
        "start_time": row[8],
        "last_bonus_time": row[9]
    }

def update_user_field(user_id, field, value):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

def get_user_last_withdraw(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT amount, status FROM withdraws WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# ================= ТЕКСТЫ И ПЕРЕВОДЫ =================
TEXTS = {
    "ru": {
        "welcome": (
            "💎 <b>ПОЛУЧАЙ ПО 5 000 ГРАММ ЗА ДРУГА В ABADDON GRAM!</b>\n\n"
            "Получай Граммы за приглашенных друзей и ежедневные бонусы 🚀\n\n"
            "<u>Чтобы активировать бота:</u>\n"
            "1️⃣ Подпишись на наших спонсоров (это займет 5 секунд).\n"
            "2️⃣ Нажми <b>«Я выполнил(а) ✅»</b>"
        ),
        "welcome_desc": (
            "💎 <b>Получи свою личную ссылку</b> — жми <b>«🔗 Заработать Граммы»</b>\n"
            "👥 <b>Приглашай друзей</b> — <b>5 000 Грамм</b> за каждого!\n\n"
            "✅ <b>Дополнительно:</b>\n"
            "— Ежедневные награды и бонусы (Профиль)\n"
            "— Участие в конкурсах на топ рефералов"
        ),
        "check_btn": "Я выполнил(а) ✅",
        "not_subbed_alert": "⚠️ Вы выполнили не все условия! Убедитесь, что подписались на каналы и запустили ботов.",
        "access_granted": "🎉 Доступ успешно открыт!",
        "btn_ref": "🔗 Заработать Граммы",
        "btn_cabinet": "👤 Профиль",
        "btn_withdraw": "🏆 Вывод Грамм",
        "btn_bonus": "🎁 Ежедневный бонус",
        "btn_lang": "🌐 Язык / Тіл",
        "btn_chat": "💬 Наши отзывы",
        "ref_msg": (
            "💎 <b>Приглашай друзей и получай по 5 000 Грамм от Abaddon Gram за каждого, кто активирует бота по твоей ссылке!</b>\n\n"
            "🔗 <u>Твоя личная ссылка (нажми чтобы скопировать):</u>\n\n"
            "<code>{link}</code>"
        ),
        "cabinet_msg": (
            "👤 <b>ВАШ ПРОФИЛЬ</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🆔 <b>ID:</b> <code>{id}</code>\n"
            "💳 <b>Баланс:</b> <code>{balance} Грамм</code>\n"
            "👥 <b>Приглашено:</b> <code>{refs} друзей</code>\n"
            "🎯 <b>Минимум на вывод:</b> <code>{min} Грамм</code>\n\n"
            "📋 <b>Статус последней заявки:</b> {wd_status}"
        ),
        "no_withdraw": "<i>У вас еще не было заявок на вывод</i>",
        "no_money": "❌ <b>НЕДОСТАТОЧНО ГРАММОВ</b>\n\n💳 <b>Ваш баланс:</b> <code>{balance} Грамм</code>\n🎯 <b>Порог вывода:</b> <code>{min} Грамм</code>",
        "withdraw_ready": "✅ <b>ДОСТУПЕН ВЫВОД СРЕДСТВ!</b>\n\n💰 <b>К выплате:</b> <code>{balance} Грамм</code>\n\n👇 <b>Отправьте реквизиты ответным сообщением:</b>",
        "withdraw_success": "⏳ <b>ЗАЯВКА СФОРМИРОВАНА!</b>\n\nЗапрос отправлен администрации.",
        "bonus_success": "🎉 <b>ЕЖЕДНЕВНЫЙ БОНУС!</b>\n\nВам зачислено <b>+{reward} Грамм</b>!",
        "bonus_wait": "⏳ <b>ВЫ УЖЕ ПОЛУЧАЛИ БОНУС!</b>\n\nСледующий бонус будет доступен через: <b>{hours} ч. {mins} мин.</b>",
        "unsubbed_warning": "⚠️ <b>ДОСТУП ОГРАНИЧЕН!</b>\n\nВы отписались от наших каналов. Подпишитесь обратно!",
        "ref_notify": "💎 <b>Вам начислено +{reward} Грамм!</b>\n\n👤 Твой реферал @{username} подтвердил подписку!"
    },
    "kk": {
        "welcome": (
            "💎 <b>ABADDON GRAM-ДА ӘР ДОС ҮШІН 5 000 ГРАММ АЛЫҢЫЗ!</b>\n\n"
            "Шақырылған достар мен күнделікті бонустар үшін Грамм жинаңыз 🚀\n\n"
            "<u>Боты іске қосу үшін:</u>\n"
            "1️⃣ Демеушілерге тіркеліңіз.\n"
            "2️⃣ <b>«Мен орындадым ✅»</b> түймесін басыңыз"
        ),
        "welcome_desc": (
            "💎 <b>Жеке сілтемеңізді алыңыз</b> — <b>«🔗 Грамм табу»</b> басыңыз\n"
            "👥 <b>Достарды шақырыңыз</b> — әрқайсысына <b>5 000 Грамм</b>!"
        ),
        "check_btn": "Мен орындадым ✅",
        "not_subbed_alert": "⚠️ Сіз барлық шарттарды орындамадыңыз!",
        "access_granted": "🎉 Кіру сәтті ашылды!",
        "btn_ref": "🔗 Грамм табу",
        "btn_cabinet": "👤 Профиль",
        "btn_withdraw": "🏆 Грамм шығару",
        "btn_bonus": "🎁 Күнделікті бонус",
        "btn_lang": "🌐 Тіл / Язык",
        "btn_chat": "💬 Біздің пікірлер",
        "ref_msg": "💎 <b>Достарды шақырыңыз және 5 000 Грамм алыңыз!</b>\n\n🔗 <code>{link}</code>",
        "cabinet_msg": "👤 <b>СІЗДІҢ ПРОФИЛІҢІЗ</b>\n\n🆔 <b>ID:</b> <code>{id}</code>\n💳 <b>Баланс:</b> <code>{balance} Грамм</code>\n👥 <b>Шақырылғандар:</b> <code>{refs} дос</code>\n\n📋 <b>Соңғы өтініш статусы:</b> {wd_status}",
        "no_withdraw": "<i>Шығаруға өтініштер жоқ</i>",
        "no_money": "❌ <b>ГРАММ ЖЕТКІЛІКСІЗ</b>",
        "withdraw_ready": "✅ <b>АҚША ШЫҒАРУ ТАПСЫРЫСЫ!</b>\n\n👇 <b>Реквизиттеріңізді жазыңыз:</b>",
        "withdraw_success": "⏳ <b>ӨТІНІШ ҚАБЫЛДАНДЫ!</b>",
        "bonus_success": "🎉 <b>КҮНДЕЛІКТІ БОНУС!</b> +{reward} Грамм!",
        "bonus_wait": "⏳ <b>БОНУС АЛЫП ҚОЙДЫҢЫЗ!</b> {hours} сағ. {mins} мин. күтіңіз.",
        "unsubbed_warning": "⚠️ <b>КІРУ ШЕКТЕЛДІ!</b> Арналарға қайта тіркеліңіз.",
        "ref_notify": "💎 <b>Сізге +{reward} Грамм қосылды!</b>"
    }
}

# ================= FSM (СОСТОЯНИЯ) =================
class WithdrawState(StatesGroup):
    waiting_for_requisites = State()

# ================= КЛАВИАТУРЫ =================
def get_main_keyboard(user_id, lang):
    t = TEXTS[lang]
    keyboard = [
        [KeyboardButton(text=t["btn_ref"])],
        [KeyboardButton(text=t["btn_cabinet"]), KeyboardButton(text=t["btn_withdraw"])],
        [KeyboardButton(text=t["btn_bonus"]), KeyboardButton(text=t["btn_lang"])],
        [KeyboardButton(text=t["btn_chat"])]
    ]
    if int(user_id) == ADMIN_ID:
        keyboard.append([KeyboardButton(text="⚡ Админ-Панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kk"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])

# ================= ПРОВЕРКА ПОДПИСКИ =================
async def check_channels_sub(bot: Bot, user_id: int):
    try:
        m1 = await bot.get_chat_member(CHANNEL_1_ID, user_id)
        if m1.status in ['left', 'kicked']:
            return False
        m2 = await bot.get_chat_member(CHANNEL_2_ID, user_id)
        if m2.status in ['left', 'kicked']:
            return False
        return True
    except Exception:
        return False

# ================= ИНИЦИАЛИЗАЦИЯ =================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= ХЕНДЛЕРЫ =================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    user_data = get_user_data(user_id, username)
    
    update_user_field(user_id, "start_time", time.time())
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id and user_data["referred_by"] is None and not user_data["reward_given"]:
            update_user_field(user_id, "referred_by", referrer_id)

    if user_data["is_subbed"] and await check_channels_sub(bot, user_id):
        await send_main_menu(message, user_id, user_data['lang'])
    else:
        await message.answer("🌐 <b>Выберите язык / Тілді таңдаңыз:</b>", reply_markup=get_lang_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("lang_"))
async def lang_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    selected_lang = callback.data.split("_")[1]
    update_user_field(user_id, "lang", selected_lang)
    
    user_data = get_user_data(user_id)
    await callback.message.delete()
    
    if user_data["is_subbed"] and await check_channels_sub(bot, user_id):
        await send_main_menu(callback.message, user_id, selected_lang)
    else:
        await send_sponsor_check(callback.message, selected_lang)

async def send_sponsor_check(message: types.Message, lang: str):
    t = TEXTS[lang]
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Канал 1", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton(text="💬 Чат 2", url=CHANNEL_2_LINK)],
        [InlineKeyboardButton(text="🤖 Бот №1", url=SPONSOR_1_URL)],
        [InlineKeyboardButton(text="🤖 Бот №2", url=SPONSOR_2_URL)],
        [InlineKeyboardButton(text=t["check_btn"], callback_data="check_sub")]
    ])
    await message.answer(t["welcome"], reply_markup=markup, parse_mode="HTML")

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "Нет юзернейма"
    user_data = get_user_data(user_id, username)
    lang = user_data['lang']
    t = TEXTS[lang]
    
    time_passed = time.time() - user_data["start_time"]
    is_subbed = await check_channels_sub(bot, user_id)
    
    if time_passed < 5 or not is_subbed:
        await callback.answer(t["not_subbed_alert"], show_alert=True)
        return

    update_user_field(user_id, "is_subbed", 1)

    referrer_id = user_data["referred_by"]
    if referrer_id and not user_data["reward_given"]:
        ref_data = get_user_data(referrer_id)
        ref_lang = ref_data['lang']
        update_user_field(referrer_id, "balance", ref_data["balance"] + REFERRAL_REWARD)
        update_user_field(referrer_id, "referrals", ref_data["referrals"] + 1)
        update_user_field(user_id, "reward_given", 1)
        
        try:
            await bot.send_message(
                referrer_id, 
                TEXTS[ref_lang]["ref_notify"].format(reward=REFERRAL_REWARD, username=username),
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer(t["access_granted"])
    await callback.message.delete()
    await send_main_menu(callback.message, user_id, lang)

async def send_main_menu(message: types.Message, user_id: int, lang: str):
    t = TEXTS[lang]
    try:
        await message.answer_photo(
            photo=WELCOME_PHOTO,
            caption=t["welcome_desc"],
            reply_markup=get_main_keyboard(user_id, lang),
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(
            t["welcome_desc"],
            reply_markup=get_main_keyboard(user_id, lang),
            parse_mode="HTML"
        )

# ================= ГЛАВНОЕ МЕНЮ И КНОПКИ =================
@dp.message(F.text.in_(["🔗 Заработать Граммы", "🔗 Грамм табу"]))
async def cmd_ref(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    await message.answer(TEXTS[user_data['lang']]["ref_msg"].format(link=link), parse_mode="HTML")

@dp.message(F.text.in_(["👤 Профиль"]))
async def cmd_cabinet(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    lang = user_data['lang']
    t = TEXTS[lang]
    
    last_wd = get_user_last_withdraw(user_id)
    wd_status = f"<b>{last_wd[0]} Грамм</b> — {last_wd[1]}" if last_wd else t["no_withdraw"]

    msg = t["cabinet_msg"].format(
        id=user_id, 
        balance=user_data['balance'], 
        refs=user_data['referrals'], 
        min=MIN_WITHDRAW, 
        wd_status=wd_status
    )
    await message.answer(msg, parse_mode="HTML")

@dp.message(F.text.in_(["🏆 Вывод Грамм", "🏆 Грамм шығару"]))
async def cmd_withdraw(message: types.Message, state: FSMContext):
    user_data = get_user_data(message.from_user.id)
    lang = user_data['lang']
    t = TEXTS[lang]

    if user_data['balance'] < MIN_WITHDRAW:
        await message.answer(t["no_money"].format(balance=user_data['balance'], min=MIN_WITHDRAW), parse_mode="HTML")
    else:
        await message.answer(t["withdraw_ready"].format(balance=user_data['balance']), parse_mode="HTML")
        await state.set_state(WithdrawState.waiting_for_requisites)

@dp.message(WithdrawState.waiting_for_requisites)
async def process_withdraw(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    lang = user_data['lang']
    requisites = message.text
    amount = user_data['balance']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO withdraws (user_id, username, amount, requisites, status) VALUES (?, ?, ?, ?, ?)",
                   (user_id, message.from_user.username or "Нет юзернейма", amount, requisites, "⏳ В обработке"))
    conn.commit()
    conn.close()

    update_user_field(user_id, "balance", 0)
    await state.clear()
    await message.answer(TEXTS[lang]["withdraw_success"], parse_mode="HTML")

    try:
        await bot.send_message(
            ADMIN_ID,
            f"🚨 <b>НОВАЯ ЗАЯВКА НА ВЫВОД!</b>\n👤 Юзер: @{message.from_user.username} (<code>{user_id}</code>)\n💰 Сумма: <code>{amount} Грамм</code>\n💳 Реквизиты: <code>{requisites}</code>",
            parse_mode="HTML"
        )
    except Exception:
        pass

@dp.message(F.text.in_(["🎁 Ежедневный бонус", "🎁 Күнделікті бонус"]))
async def cmd_bonus(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    lang = user_data['lang']
    t = TEXTS[lang]
    
    now = time.time()
    diff = now - user_data["last_bonus_time"]
    
    if diff >= 86400:
        update_user_field(user_id, "balance", user_data["balance"] + DAILY_BONUS_REWARD)
        update_user_field(user_id, "last_bonus_time", now)
        await message.answer(t["bonus_success"].format(reward=DAILY_BONUS_REWARD), parse_mode="HTML")
    else:
        remaining = 86400 - diff
        hours = int(remaining // 3600)
        mins = int((remaining % 3600) // 60)
        await message.answer(t["bonus_wait"].format(hours=hours, mins=mins), parse_mode="HTML")

@dp.message(F.text.in_(["🌐 Язык / Тіл"]))
async def cmd_lang(message: types.Message):
    await message.answer("🌐 <b>Выберите язык / Тілді таңдаңыз:</b>", reply_markup=get_lang_keyboard(), parse_mode="HTML")

@dp.message(F.text.in_(["💬 Наши отзывы", "💬 Біздің пікірлер"]))
async def cmd_chat(message: types.Message):
    await message.answer(f"💬 <b>Наше сообщество:</b> {CHANNEL_2_LINK}", parse_mode="HTML")

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📋 Выплаты", callback_data="admin_withdraws")]
        ])
        await message.answer("⚡ <b>Панель администратора:</b>", reply_markup=markup, parse_mode="HTML")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM withdraws")
    wd_count = cursor.fetchone()[0]
    conn.close()
    await callback.message.answer(f"📊 <b>Статистика:</b>\n👥 Пользователей: {users_count}\n⏳ Заявок: {wd_count}", parse_mode="HTML")

@dp.callback_query(F.data == "admin_withdraws")
async def admin_withdraws(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, amount, requisites, status FROM withdraws")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        await callback.message.answer("🎉 Заявок нет.")
        return
    text = "📋 <b>Заявки:</b>\n\n"
    for r in rows:
        text += f"ID: {r[0]} | Юзер: {r[1]} | Сумма: {r[2]} | Реф: {r[3]} | Статус: {r[4]}\n"
    await callback.message.answer(text, parse_mode="HTML")

# ================= ЗАПУСК БОТА =================
async def main():
    print("Бот на aiogram успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
