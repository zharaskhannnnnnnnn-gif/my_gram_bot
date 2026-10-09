import telebot
from telebot import types

TOKEN = "8800027665:AAGfM8tZin6NqlzZirqgvfE9_beOuhWBQJ4"
ADMIN_ID = 8831958470

SPONSOR_1_URL = "https://t.me/OnlineSmsM5_bot?start=l_Jsusiwkwk015"
SPONSOR_2_URL = "https://t.me/chatik5_gpt_bot?start=utm_Hsjsuskwk015"

REFERRAL_REWARD = 3000
MIN_WITHDRAW = 30000

bot = telebot.TeleBot(TOKEN)

users = {}
withdraw_requests = []

def get_user_data(user_id):
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "referred_by": None}
    return users[user_id]

def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔗 Реферальная ссылка")
    btn2 = types.KeyboardButton("💰 Баланс")
    btn3 = types.KeyboardButton("💸 Вывод средств")
    markup.add(btn1, btn2)
    markup.add(btn3)
    
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 Админ-панель"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id and user_data["referred_by"] is None:
            user_data["referred_by"] = referrer_id
            ref_data = get_user_data(referrer_id)
            ref_data["balance"] += REFERRAL_REWARD
            ref_data["referrals"] += 1
            try:
                bot.send_message(
                    referrer_id, 
                    f"🎉 По вашей ссылке перешел новый пользователь!\nВам начислено +{REFERRAL_REWARD} Грамм."
                )
            except Exception:
                pass

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🤖 Запустить Бота 1", url=SPONSOR_1_URL)
    btn2 = types.InlineKeyboardButton("🤖 Запустить Бота 2", url=SPONSOR_2_URL)
    check_btn = types.InlineKeyboardButton("✅ Я перешёл и запустил обеих", callback_data="check_sub")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(check_btn)
    
    bot.send_message(
        message.chat.id,
        "⚠️ **Для доступа к боту выполните условия:**\n\nПерейдите в ботов наших спонсоров и нажмите там `/start`:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    bot.answer_callback_query(call.id, "✅ Доступ открыт!")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        "Добро пожаловать в главное меню!",
        reply_markup=main_keyboard(call.from_user.id)
    )

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    text = message.text

    if text == "🔗 Реферальная ссылка":
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={user_id}"
        msg = (
            f"🔗 **Ваша реферальная ссылка:**\n{link}\n\n"
            f"За каждого перешедшего друга вы получите {REFERRAL_REWARD} Грамм.\n"
            f"Приглашено рефералов: {user_data['referrals']}"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "💰 Баланс":
        bot.send_message(
            message.chat.id, 
            f"💳 **Ваш баланс:** {user_data['balance']} Грамм\n👥 **Приглашено:** {user_data['referrals']} чел."
        )

    elif text == "💸 Вывод средств":
        if user_data['balance'] < MIN_WITHDRAW:
            bot.send_message(
                message.chat.id, 
                f"❌ Минимальная сумма для вывода: {MIN_WITHDRAW} Грамм.\nВаш баланс: {user_data['balance']} Грамм."
            )
        else:
            msg = bot.send_message(
                message.chat.id, 
                f"✅ У вас достаточно средств для вывода ({user_data['balance']} Грамм).\n\n"
                f"Введите реквизиты для вывода (номер карты / QIWI / кошелек):"
            )
            bot.register_next_step_handler(msg, process_withdraw)

    elif text == "👑 Админ-панель" and user_id == ADMIN_ID:
        show_admin_panel(message.chat.id)

def process_withdraw(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    requisites = message.text
    amount = user_data['balance']

    if amount < MIN_WITHDRAW:
        bot.send_message(message.chat.id, "❌ Недостаточно средств.")
        return

    req_info = {
        "user_id": user_id,
        "username": message.from_user.username or "Нет юзернейма",
        "amount": amount,
        "requisites": requisites
    }
    withdraw_requests.append(req_info)
    user_data['balance'] = 0

    bot.send_message(
        message.chat.id, 
        "⏳ Ваша заявка на вывод принята и отправлена администратору на проверку!"
    )

    try:
        bot.send_message(
            ADMIN_ID,
            f"🚨 **Новая заявка на вывод!**\n\n"
            f"👤 ID: `{user_id}` (@{req_info['username']})\n"
            f"💰 Сумма: {amount} Грамм\n"
            f"💳 Реквизиты: `{requisites}`",
            parse_mode="Markdown"
        )
    except Exception:
        pass

def show_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    btn2 = types.InlineKeyboardButton("📋 Заявки на вывод", callback_data="admin_withdraws")
    btn3 = types.InlineKeyboardButton("📢 Сделать рассылку", callback_data="admin_broadcast")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)

    bot.send_message(chat_id, "⚙️ **Админ-панель управления:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "admin_stats":
        bot.send_message(
            call.message.chat.id,
            f"📊 **Статистика бота:**\n\n"
            f"👥 Всего пользователей: {len(users)}\n"
            f"⏳ Активных заявок на вывод: {len(withdraw_requests)}"
        )

    elif call.data == "admin_withdraws":
        if not withdraw_requests:
            bot.send_message(call.message.chat.id, "🎉 Активных заявок на вывод нет.")
            return

        text = "📋 **Заявки на вывод средств:**\n\n"
        for idx, req in enumerate(withdraw_requests, start=1):
            text += (
                f"{idx}. ID: `{req['user_id']}` (@{req['username']})\n"
                f"   Сумма: {req['amount']} Грамм\n"
                f"   Реквизиты: `{req['requisites']}`\n\n"
            )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif call.data == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, "✍️ Введите текст сообщения для рассылки всем пользователям:")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    text = message.text
    count = 0
    for uid in users:
        try:
            bot.send_message(uid, text)
            count += 1
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ Рассылка успешно отправлена {count} пользователям!")

bot.polling(none_stop=True)
