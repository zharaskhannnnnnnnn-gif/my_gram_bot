import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN", "8800027665:AAGfM8tZin6NqlzZirqgvfE9_beOuhWBQJ4")
ADMIN_ID = 8831958470

bot = telebot.TeleBot(TOKEN)

REFERRAL_REWARD = 6000
MIN_WITHDRAW = 30000

users_db = {}


def get_or_create_user(user_id):
  if user_id not in users_db:
    users_db[user_id] = {"balance": 0, "referrals": 0, "referrer": None}
  return users_db[user_id]


def get_main_keyboard(user_id):
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn_profile = types.KeyboardButton("👤 Профиль / Баланс")
  btn_ref = types.KeyboardButton("🔗 Реферальная ссылка")
  btn_withdraw = types.KeyboardButton("💸 Вывод средств")
  keyboard.add(btn_profile, btn_ref)
  keyboard.add(btn_withdraw)

  if user_id == ADMIN_ID:
    keyboard.add(types.KeyboardButton("👑 Админ-панель"))

  return keyboard


@bot.message_handler(commands=['start'])
def start_cmd(message):
  user_id = message.chat.id
  get_or_create_user(user_id)

  args = message.text.split()
  if len(args) > 1:
    referrer_id = args[1]
    if (
        referrer_id.isdigit()
        and int(referrer_id) != user_id
        and users_db[user_id]["referrer"] is None
    ):
      ref_id = int(referrer_id)
      if ref_id in users_db:
        users_db[user_id]["referrer"] = ref_id
        users_db[ref_id]["balance"] += REFERRAL_REWARD
        users_db[ref_id]["referrals"] += 1

        try:
          bot.send_message(
              ref_id,
              f"🎉 По вашей ссылке зарегистрировался новый игрок!\n"
              f"Начислено: +{REFERRAL_REWARD} Грамм.",
          )
        except Exception:
          pass

  bot.send_message(
      user_id,
      "👋 Добро пожаловать в реферального бота!\n\n"
      f"Приглашай друзей и получай **{REFERRAL_REWARD} Грамм** за каждого!",
      parse_mode="Markdown",
      reply_markup=get_main_keyboard(user_id),
  )


@bot.message_handler(
    func=lambda msg: msg.text
    in [
        "👤 Профиль / Баланс",
        "🔗 Реферальная ссылка",
        "💸 Вывод средств",
        "👑 Админ-панель",
    ]
)
def handle_menu(message):
  user_id = message.chat.id
  user = get_or_create_user(user_id)

  if message.text == "👤 Профиль / Баланс":
    text = (
        f"📊 **Ваш профиль:**\n\n"
        f"🆔 Ваш ID: `{user_id}`\n"
        f"💰 Баланс: **{user['balance']} Грамм**\n"
        f"👥 Приглашено рефералов: **{user['referrals']}**"
    )
    bot.send_message(user_id, text, parse_mode="Markdown")

  elif message.text == "🔗 Реферальная ссылка":
    bot_username = bot.get_me().username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    text = (
        f"🔗 **Ваша реферальная ссылка:**\n`{ref_link}`\n\n"
        f"За каждого перешедшего ты получишь **{REFERRAL_REWARD} Грамм**."
    )
    bot.send_message(user_id, text, parse_mode="Markdown")

  elif message.text == "💸 Вывод средств":
    if user["balance"] < MIN_WITHDRAW:
      bot.send_message(
          user_id,
          f"❌ Минимальная сумма для вывода: **{MIN_WITHDRAW} Грамм**.\n"
          f"Ваш баланс: {user['balance']} Грамм.",
          parse_mode="Markdown",
      )
    else:
      msg = bot.send_message(
          user_id,
          f"✅ Введите реквизиты для вывода **{user['balance']} Грамм** (номер карты, QIWI, ЮMoney или ник):",
      )
      bot.register_next_step_handler(msg, process_withdraw)

  elif message.text == "👑 Админ-панель" and user_id == ADMIN_ID:
    total_users = len(users_db)
    text = (
        f"⚙️ **Админ-панель:**\n\n" f"👥 Всего пользователей в базе: {total_users}"
    )

    markup = types.InlineKeyboardMarkup()
    btn_broadcast = types.InlineKeyboardButton(
        "📢 Сделать рассылку", callback_data="admin_broadcast"
    )
    markup.add(btn_broadcast)

    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)


def process_withdraw(message):
  user_id = message.chat.id
  user = get_or_create_user(user_id)
  details = message.text

  if user["balance"] < MIN_WITHDRAW:
    bot.send_message(user_id, "Ошибка: недостаточно средств.")
    return

  amount = user["balance"]
  user["balance"] = 0

  bot.send_message(
      user_id,
      f"🚀 Заявка на вывод **{amount} Грамм** принята!\n"
      f"Реквизиты: `{details}`",
      parse_mode="Markdown",
  )

  admin_msg = (
      f"🚨 **НОВАЯ ЗАЯВКА НА ВЫВОД!**\n\n"
      f"👤 Пользователь: [{message.from_user.first_name}](tg://user?id={user_id})\n"
      f"🆔 ID: `{user_id}`\n"
      f"💰 Сумма: **{amount} Грамм**\n"
      f"💳 Реквизиты: `{details}`"
  )
  try:
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
  except Exception:
    pass


@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def callback_admin(call):
  if call.from_user.id == ADMIN_ID:
    msg = bot.send_message(
        ADMIN_ID, "📝 Введите текст для рассылки всем пользователям:"
    )
    bot.register_next_step_handler(msg, process_broadcast)


def process_broadcast(message):
  if message.from_user.id != ADMIN_ID:
    return

  text = message.text
  success = 0
  failed = 0

  bot.send_message(ADMIN_ID, "⏳ Рассылка запущена...")

  for uid in users_db:
    try:
      bot.send_message(uid, text)
      success += 1
    except Exception:
      failed += 1

  bot.send_message(
      ADMIN_ID,
      f"✅ **Рассылка завершена!**\n\n"
      f"Успешно: {success}\n"
      f"Не удалось: {failed}",
      parse_mode="Markdown",
  )


if __name__ == "__main__":
  bot.polling(none_stop=True)
