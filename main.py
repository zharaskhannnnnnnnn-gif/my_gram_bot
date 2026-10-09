import time
import telebot
from telebot import types

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

# Хранилище данных в памяти
users = {}
withdraw_requests = []

def get_user_data(user_id, username="no_username"):
    user_id = int(user_id)
    if user_id not in users:
        users[user_id] = {
            "lang": "ru",
            "balance": 0,
            "referrals": 0,
            "referred_by": None,
            "reward_given": False,
            "is_subbed": False,
            "start_time": time.time(),
            "last_bonus_time": 0,
            "username": username
        }
    else:
        if username != "no_username":
            users[user_id]["username"] = username
    return users[user_id]

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

# Тексты и переводы
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

def main_keyboard(user_id, lang):
    t = TEXTS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_ref = types.KeyboardButton(t["btn_ref"])
    btn_cabinet = types.KeyboardButton(t["btn_cabinet"])
    btn_withdraw = types.KeyboardButton(t["btn_withdraw"])
    btn_bonus = types.KeyboardButton(t["btn_bonus"])
    btn_lang = types.KeyboardButton(t["btn_lang"])
    btn_chat = types.KeyboardButton(t["btn_chat"])
    
    markup.row(btn_ref)
    markup.row(btn_cabinet, btn_withdraw)
    markup.row(btn_bonus, btn_lang)
    markup.row(btn_chat)
    
    if int(user_id) == ADMIN_ID:
        markup.add(types.KeyboardButton("⚡ Админ-Панель"))
    return markup

def lang_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kk"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    user_data = get_user_data(user_id, username)
    user_data["start_time"] = time.time()
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id and user_data["referred_by"] is None:
            user_data["referred_by"] = referrer_id

    if user_data.get("is_subbed") and check_channels_sub(user_id):
        send_main_menu(message.chat.id, user_id, user_data['lang'])
    else:
        bot.send_message(message.chat.id, "🌐 <b>Выберите язык / Тілді таңдаңыз:</b>", reply_markup=lang_keyboard(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_callback(call):
    user_id = call.from_user.id
    selected_lang = call.data.split("_")[1]
    user_data = get_user_data(user_id)
    user_data["lang"] = selected_lang
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    if user_data.get("is_subbed") and check_channels_sub(user_id):
        send_main_menu(call.message.chat.id, user_id, selected_lang)
    else:
        send_sponsor_check(call.message.chat.id, selected_lang)

def send_sponsor_check(chat_id, lang="ru"):
    t = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Канал 1", url=CHANNEL_1_LINK),
        types.InlineKeyboardButton("💬 Чат 2", url=CHANNEL_2_LINK),
        types.InlineKeyboardButton("🤖 Бот №1", url=SPONSOR_1_URL),
        types.InlineKeyboardButton("🤖 Бот №2", url=SPONSOR_2_URL),
        types.InlineKeyboardButton(t["check_btn"], callback_data="check_sub")
    )
    bot.send_message(chat_id, t["welcome"], reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    user_id = call.from_user.id
    username = call.from_user.username or "Нет юзернейма"
    user_data = get_user_data(user_id, username)
    lang = user_data['lang']
    t = TEXTS[lang]
    
    time_passed = time.time() - user_data.get("start_time", 0)
    is_subbed = check_channels_sub(user_id)
    
    if time_passed < 5 or not is_subbed:
        bot.answer_callback_query(call.id, t["not_subbed_alert"], show_alert=True)
        return

    user_data["is_subbed"] = True

    referrer_id = user_data.get("referred_by")
    if referrer_id and not user_data.get("reward_given"):
        ref_data = get_user_data(referrer_id)
        ref_lang = ref_data['lang']
        ref_data["balance"] += REFERRAL_REWARD
        ref_data["referrals"] += 1
        user_data["reward_given"] = True
        
        try:
            bot.send_message(
                referrer_id, 
                TEXTS[ref_lang]["ref_notify"].format(reward=REFERRAL_REWARD, username=username),
                parse_mode="HTML"
            )
        except Exception:
            pass

    bot.answer_callback_query(call.id, t
