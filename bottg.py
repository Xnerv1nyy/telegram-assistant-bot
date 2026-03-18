import telebot
from telebot import types
import sqlite3

TOKEN = "7908505184:AAGbGrjOg0NQvFWEagk0YIcF1l6dUUmVUdI"
ADMIN_ID = 7510288395

bot = telebot.TeleBot(TOKEN)


# 🔹 Подключение к БД
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    phone TEXT
)
""")
conn.commit()


# 🔹 Главное меню
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 Отправить номер", callback_data="phone"),
        types.InlineKeyboardButton("🧮 Калькулятор", callback_data="calc")
    )
    markup.add(
        types.InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
    )
    return markup


# 🔹 Старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот\n\nВыбери действие 👇",
        reply_markup=main_menu()
    )


# 🔹 Inline обработка
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "phone":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("📲 Поделиться контактом", request_contact=True)
        markup.add(btn)
        markup.add("🔙 Назад")

        bot.send_message(call.message.chat.id, "Нажми кнопку 👇", reply_markup=markup)

    elif call.data == "calc":
        bot.send_message(call.message.chat.id, "✏️ Введи пример (2+2)")

    elif call.data == "help":
        bot.send_message(
            call.message.chat.id,
            "📌 Возможности:\n📱 Сбор данных\n🧮 Калькулятор\n👑 Админка"
        )


# 🔹 Контакт → запись в БД
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username
    phone = message.contact.phone_number

    # проверка на существование
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, phone) VALUES (?, ?, ?)",
            (user_id, username, phone)
        )
        conn.commit()

        bot.send_message(ADMIN_ID, f"👤 Новый пользователь:\nID: {user_id}\n@{username}\n📱 {phone}")

        bot.send_message(message.chat.id, "✅ Сохранено")
    else:
        bot.send_message(message.chat.id, "Ты уже есть в базе 😉")


# 🔹 Калькулятор
@bot.message_handler(func=lambda m: any(x in m.text for x in "+-*/"))
def calc_handler(message):
    try:
        result = eval(message.text)
        bot.send_message(message.chat.id, f"💡 {result}")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка")


# 🔹 Назад
@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back(message):
    bot.send_message(message.chat.id, "Главное меню 👇", reply_markup=main_menu())


# 🔹 Админ: список
@bot.message_handler(commands=['users'])
def users_list(message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    if users:
        text = "\n".join([f"ID: {u[0]}, @{u[1]}, 📱 {u[2]}" for u in users])
        bot.send_message(message.chat.id, f"📋 Пользователи:\n{text}")
    else:
        bot.send_message(message.chat.id, "База пустая")


# 🔹 Админ: рассылка
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = message.text.replace("/broadcast ", "")

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for user in users:
        try:
            bot.send_message(user[0], f"📢 {msg}")
        except:
            pass

    bot.send_message(message.chat.id, "✅ Рассылка завершена")


bot.polling()
