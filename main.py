import sqlite3
import time
import telebot
from telebot import types

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

bot = telebot.TeleBot(TOKEN)

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

# ================= ПРОВЕРКА ПОДПИСКИ =================
def check_channels_sub(user_id):
    try:
        m1 = bot.get_chat_member(CHANNEL_1_ID, user_id)
        if m1.status in ['left', 'kicked']:
            return False
        m2 = bot.get_chat_member(CHANNEL_2_ID, user_id)
        if m2.status in ['left', 'kicked']:
            return False
        return True
    except Exception:
        return False

# ================= ТЕКСТЫ И СТИЛЬ (КАК НА СКРИНЕ) =================
TEXTS = {
    "ru": {
        "welcome": (
            "💎 <b>ПОЛУЧАЙ ПО 5 000 ГРАММ ЗА ДРУГА В ABADDON GRAM!</b>\n\n"
            "Получай Граммы за приглашенных друзей и ежедневные бонусы 🚀\n\n"
            "<u>Чтобы активировать бота:</u>\n"
            "1️⃣ Подпишись на наших спонсоров (это займет 5 секунд).\n"
            "2️⃣ Нажими <b>«Я выполнил(а) ✅»</b>"
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
            "<code>{link}</code>\n\n"
            "🚀 <b>Как набрать много переходов по ссылке?</b>\n"
            "• Отправь её друзьям в личные сообщения 👥\n"
            "• Поделись ссылкой в истории своего ТГ или в канале 📱\n"
            "• Оставь её в комментариях или чатах 💬"
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
        "no_money": (
            "❌ <b>НЕДОСТАТОЧНО ГРАММОВ</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "💳 <b>Ваш баланс:</b> <code>{balance} Грамм</code>\n"
            "🎯 <b>Порог вывода:</b> <code>{min} Грамм</code>\n\n"
            "⚡ <i>Вам не хватает ещё <code>{needed} Грамм</code>. Приглашайте друзей!</i>"
        ),
        "withdraw_ready": (
            "✅ <b>ДОСТУПЕН ВЫВОД СРЕДСТВ!</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "💰 <b>К выплате:</b> <code>{balance} Грамм</code>\n\n"
            "👇 <b>Отправьте ответным сообщением реквизиты</b> (Карта / Kaspi / QIWI / Crypto):"
        ),
        "withdraw_success": "⏳ <b>ЗАЯВКА СФОРМИРОВАНА!</b>\n\nЗапрос отправлен администрации. Выплата произойдет в течение 24 часов.",
        "bonus_success": "🎉 <b>ЕЖЕДНЕВНЫЙ БОНУС!</b>\n\nВам зачислено <b>+{reward} Грамм</b>!\nВозвращайтесь через 24 часа за новым бонусом.",
        "bonus_wait": "⏳ <b>ВЫ УЖЕ ПОЛУЧАЛИ БОНУС!</b>\n\nСледующий бонус будет доступен через: <b>{hours} ч. {mins} мин.</b>",
        "unsubbed_warning": "⚠️ <b>ДОСТУП ОГРАНИЧЕН!</b>\n\nВы отписались от наших каналов. Подпишитесь обратно, чтобы продолжить работу!",
        "ref_notify": "💎 <b>Вам начислено +{reward} Грамм!</b>\n\n👤 Твой реферал @{username} успешно подтвердил подписку!"
    },
    "kk": {
        "welcome": (
            "💎 <b>ABADDON GRAM-ДА ӘР ДОС ҮШІН 5 000 ГРАММ АЛЫҢЫЗ!</b>\n\n"
            "Шақырылған достар мен күнделікті бонустар үшін Грамм жи
