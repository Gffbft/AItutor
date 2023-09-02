import engine
import os

import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(BOT_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)

chat = engine.ChatEngine("English", "Serbian", "A1", "A2",lessonCount=5, mistake="conjugation of verbs", plan="Members of family")
output = 0

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    output, message_from_tutor = chat.conversation(message.text)
    bot.reply_to(message, str(message_from_tutor))
    if output == 1:
        print("урок закончен харе писать")


bot.infinity_polling()


while output == 0:
    message = input()
    output = chat.conversation(message)
chat.mistakes_to_topics()
