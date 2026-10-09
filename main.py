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
MIN_WITHDRAW = 30000

bot = telebot.TeleBot(TOKEN)

users = {}
withdraw_requests = []

def get_user_data(user_id, username="no_username"):
    if user_id not in users:
        users[user_id] = {
            "balance": 0, 
            "referrals": 0, 
            "referred_by": None, 
            "invited_list": [],
            "username": username,
            "start_time": time.time(),
            "reward_given": False  # Флаг: выдан ли бонус за подписку
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

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id == ADMIN_ID:
        show_admin_panel(message.chat.id)

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

    # Проверяем: если пользователь уже прошёл проверку спонсоров и подписан
    if user_data.get("reward_given") and check_channels_sub(user_id):
        try:
            bot.send_photo(
                message.chat.id,
                photo=WELCOME_PHOTO,
                caption="💎 **ДОБРО ПОЖАЛОВАТЬ В ГЛАВНОЕ МЕНЮ!**\n\nПриглашайте друзей и зарабатывайте **Граммы** прямо сейчас!\nИспользуйте меню ниже для навигации 👇",
                reply_markup=main_keyboard(user_id),
                parse_mode="Markdown"
            )
        except Exception:
            bot.send_message(
                message.chat.id,
                "💎 **ДОБРО ПОЖАЛОВАТЬ В ГЛАВНОЕ МЕНЮ!**\n\nПриглашайте друзей и зарабатывайте **Граммы** прямо сейчас!\nИспользуйте меню ниже для навигации 👇",
                reply_markup=main_keyboard(user_id),
                parse_mode="Markdown"
            )
    else:
        # Если не подписан или новый пользователь — просим подписаться
        send_sponsor_check(message.chat.id)
        

def send_sponsor_check(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_ch1 = types.InlineKeyboardButton("📢 Канал 1 (@AbaddonGram)", url=CHANNEL_1_LINK)
    btn_ch2 = types.InlineKeyboardButton("💬 Чат 2 (@GramLudickers)", url=CHANNEL_2_LINK)
    btn1 = types.InlineKeyboardButton("🤖 Спонсор 3 (Бот)", url=SPONSOR_1_URL)
    btn2 = types.InlineKeyboardButton("🤖 Спонсор 4 (Бот)", url=SPONSOR_2_URL)
    check_btn = types.InlineKeyboardButton("🔄 Я подписался на всех спонсоров", callback_data="check_sub")
    
    markup.add(btn_ch1)
    markup.add(btn_ch2)
    markup.add(btn1)
    markup.add(btn2)
    markup.add(check_btn)
    
    bot.send_message(
        chat_id,
        "📌 **ОБЯЗАТЕЛЬНОЕ УСЛОВИЕ ДЛЯ ДОСТУПА**\n\n"
        "Чтобы начать зарабатывать, вы должны быть подписаны и запустить **всех спонсоров**:\n\n"
        "1️⃣ Подпишитесь на **@AbaddonGram**\n"
        "2️⃣ Вступите в **@GramLudickers**\n"
        "3️⃣ Запустите первого бота\n"
        "4️⃣ Запустите второго бота\n\n"
        "После выполнения нажмите кнопку **«Я подписался на всех спонсоров»** 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    user_id = call.from_user.id
    username = call.from_user.username or "Нет юзернейма"
    user_data = get_user_data(user_id, username)
    
    time_passed = time.time() - user_data.get("start_time", 0)
    is_subbed = check_channels_sub(user_id)
    
    if time_passed < 12 or not is_subbed:
        bot.answer_callback_query(
            call.id, 
            "❌ Вы не подписались на всех спонсоров! Подпишитесь на ресурсы и повторите попытку.", 
            show_alert=True
        )
        return

    # НАЧИСЛЕНИЕ НАГРАДЫ ПРИГЛАСИТЕЛЮ ТОЛЬКО ПОСЛЕ ПОДТВЕРЖДЕНИЯ ПОДПИСКИ
    referrer_id = user_data.get("referred_by")
    if referrer_id and not user_data.get("reward_given"):
        ref_data = get_user_data(referrer_id)
        ref_data["balance"] += REFERRAL_REWARD
        ref_data["referrals"] += 1
        ref_data["invited_list"].append({"id": user_id, "username": username})
        user_data["reward_given"] = True  # Чтобы бонус не выдавался повторно
        
        try:
            bot.send_message(
                referrer_id, 
                f"🎉 **Новый реферал подтвержден!**\n\nПользователь выполнил все условия подписки.\nВам начислено: **+{REFERRAL_REWARD} Грамм**!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    bot.answer_callback_query(call.id, "✅ Доступ успешно открыт!")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    try:
        bot.send_photo(
            call.message.chat.id,
            photo=WELCOME_PHOTO,
            caption="💎 **ДОБРО ПОЖАЛОВАТЬ В ГЛАВНОЕ МЕНЮ!**\n\nПриглашайте друзей и зарабатывайте **Граммы** прямо сейчас!\nИспользуйте меню ниже для навигации 👇",
            reply_markup=main_keyboard(user_id),
            parse_mode="Markdown"
        )
    except Exception:
        bot.send_message(
            call.message.chat.id,
            "💎 **ДОБРО ПОЖАЛОВАТЬ В ГЛАВНОЕ МЕНЮ!**\n\nПриглашайте друзей и зарабатывайте **Граммы** прямо сейчас!\nИспользуйте меню ниже для навигации 👇",
            reply_markup=main_keyboard(user_id),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    user_data = get_user_data(user_id, username)
    text = message.text

    if text == "🔗 Реферальная ссылка":
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={user_id}"
        msg = (
            f"🚀 **ВАША РЕФЕРАЛЬНАЯ ССЫЛКА**\n\n"
            f"🔗 `{link}`\n\n"
            f"💰 **Награда за реферала:** `{REFERRAL_REWARD} Грамм`\n"
            f"👥 **Вы уже пригласили:** `{user_data['referrals']} чел.`\n\n"
            f"📋 *Отправляйте ссылку друзьям и получайте бонусы за каждого перешедшего!*"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "💰 Баланс":
        msg = (
            f"📊 **ВАШ ЛИЧНЫЙ КАБИНЕТ**\n\n"
            f"💳 **Текущий баланс:** `{user_data['balance']} Грамм`\n"
            f"👥 **Всего рефералов:** `{user_data['referrals']} чел.`\n"
            f"🎯 **Минималка для вывода:** `{MIN_WITHDRAW} Грамм`"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "💸 Вывод средств":
        if user_data['balance'] < MIN_WITHDRAW:
            msg = (
                f"❌ **НЕДОСТАТОЧНО СРЕДСТВ ДЛЯ ВЫВОДА**\n\n"
                f"💳 **Ваш баланс:** `{user_data['balance']} Грамм`\n"
                f"🎯 **Минимальная сумма:** `{MIN_WITHDRAW} Грамм`\n\n"
                f"🔹 *Вам не хватает ещё `{MIN_WITHDRAW - user_data['balance']} Грамм`. Приглашайте больше друзей!*"
            )
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            msg = bot.send_message(
                message.chat.id, 
                f"✅ **У ВАС ДОСТАТОЧНО СРЕДСТВ!**\n\n"
                f"💰 **Сумма к выводу:** `{user_data['balance']} Грамм`\n\n"
                f"👇 **Отправьте ответным сообщением реквизиты** (номер карты, QIWI или крипто-кошелек):",
                parse_mode="Markdown"
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
        bot.send_message(message.chat.id, "❌ **Ошибка:** недостаточно средств.", parse_mode="Markdown")
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
        "⏳ **ЗАЯВКА УСПЕШНО СОЗДАНА!**\n\nВаш запрос на вывод отправлен администратору. Ожидайте поступления средств.",
        parse_mode="Markdown"
    )

    try:
        bot.send_message(
            ADMIN_ID,
            f"🚨 **НОВАЯ ЗАЯВКА НА ВЫВОД!**\n\n"
            f"👤 **Пользователь:** `{user_id}` (@{req_info['username']})\n"
            f"💰 **Сумма:** `{amount} Грамм`\n"
            f"💳 **Реквизиты:** `{requisites}`",
            parse_mode="Markdown"
        )
    except Exception:
        pass

def show_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    btn2 = types.InlineKeyboardButton("📋 Заявки на вывод", callback_data="admin_withdraws")
    btn3 = types.InlineKeyboardButton("👥 Кто кого пригласил", callback_data="admin_refs_tree")
    btn4 = types.InlineKeyboardButton("📢 Сделать рассылку", callback_data="admin_broadcast")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)

    bot.send_message(chat_id, "👑 **ПАНЕЛЬ АДМИНИСТРАТОРА**\n\nВыберите нужное действие:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "admin_stats":
        bot.send_message(
            call.message.chat.id,
            f"📊 **СТАТИСТИКА ПРОЕКТА**\n\n"
            f"👥 **Всего пользователей:** `{len(users)}` чел.\n"
            f"⏳ **Ожидают вывода:** `{len(withdraw_requests)}` заявок",
            parse_mode="Markdown"
        )

    elif call.data == "admin_withdraws":
        if not withdraw_requests:
            bot.send_message(call.message.chat.id, "🎉 **Активных заявок на вывод нет!**", parse_mode="Markdown")
            return

        text = "📋 **СПИСОК ЗАЯВОК НА ВЫВОД:**\n\n"
        for idx, req in enumerate(withdraw_requests, start=1):
            text += (
                f"**{idx}.** Пользователь: `{req['user_id']}` (@{req['username']})\n"
                f"   💰 Сумма: `{req['amount']} Грамм`\n"
                f"   💳 Реквизиты: `{req['requisites']}`\n\n"
            )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif call.data == "admin_refs_tree":
        has_refs = False
        text = "👥 **СПИСОК РЕФЕРАЛОВ (Кто ➡️ Кого):**\n\n"
        
        for uid, udata in users.items():
            if udata["invited_list"]:
                has_refs = True
                inviter_tag = f"@{udata['username']}" if udata['username'] != "Нет юзернейма" else "без юзернейма"
                
                invited_formatted = []
                for item in udata["invited_list"]:
                    tag = f"@{item['username']}" if item['username'] != "Нет юзернейма" else f"`{item['id']}`"
                    invited_formatted.append(tag)
                
                invited_str = ", ".join(invited_formatted)
                text += f"👑 **Пригласитель:** `{uid}` ({inviter_tag})\n➡️ **Приглашённые:** {invited_str}\n\n"

        if not has_refs:
            text = "👥 **Пока никто никого не пригласил.**"

        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif call.data == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, "✍️ **Введите текст сообщения для рассылки всем пользователям:**", parse_mode="Markdown")
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
    bot.send_message(message.chat.id, f"✅ **Рассылка завершена!** Доставлено `{count}` пользователям.", parse_mode="Markdown")

bot.polling(none_stop=True)
