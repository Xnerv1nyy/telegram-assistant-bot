import telebot

TOKEN = "7908505184:AAGbGrjOg0NQvFWEagk0YIcF1l6dUUmVUdI"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я твой ассистент 🤖")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, "/start\n/help\n/calc")

@bot.message_handler(commands=['calc'])
def calc(message):
    try:
        expression = message.text.replace("/calc ", "")
        result = eval(expression)
        bot.send_message(message.chat.id, f"Результат: {result}")
    except:
        bot.send_message(message.chat.id, "Ошибка в выражении")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, f"Ты написал: {message.text}")

bot.polling()