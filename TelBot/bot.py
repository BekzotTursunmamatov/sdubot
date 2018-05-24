import config
import telebot
from telebot import types
from SQLighter import SQLighter

bot = telebot.TeleBot(config.token)

# Подключаемся к БД
db_worker = SQLighter(config.database_name)
# Получаем случайную строку из БД
rows = db_worker.select_all()
db_worker.close()
home_list = ["Administration", "Faculties", "Events", "Advertisements", "Contacts", "Info"]
group_rows = []
back = []

@bot.message_handler(commands=['start'])
def home(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
    for n in rows:
        keyboard.add(types.KeyboardButton(text=n[2]))
    keyboard.add(types.KeyboardButton(text="Back"))
    bot.send_message(message.chat.id, "D", reply_markup=keyboard)


def name(message, gname):
    for row in rows:
        db_worker = SQLighter(config.database_name)
        # print(message.text,row[2])
        if gname == row[2]:
            global group_rows
            group_rows = db_worker.select_all_groups(row[1])
            print(group_rows, type(group_rows))
            keyboard = types.ReplyKeyboardMarkup()
            for n in group_rows:
                keyboard.add(types.KeyboardButton(text=n[0]))
            keyboard.add(types.KeyboardButton(text="Back"))
            bot.send_message(message.chat.id, "Group!", reply_markup=keyboard)
        db_worker.close()
def advisor(message,gname):
    db_worker = SQLighter(config.database_name)
    global arows
    arows = db_worker.select_all_advisors(gname)
    print(arows, "ADVISOR")
    if arows:
        print("Not empty")
        bot.send_message(message.chat.id, arows[0])
        arows = []
    else:
        print("Empty")

    db_worker.close()


'''@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    for row in rows:
        if call.data == row[2]:
            name(call.message, row[2])

    for row in group_rows:
        print(row, " Row")
        if call.data == row[0]:
            advisor(call.message, row[0])
            bot.send_message(chat_id, "Advisor")'''
'''def MHandler(Array):
    for row in Array:
        print(row[2])
        @bot.message_handler(func=lambda message: message.text == "'%s'" % (row[2]), content_types=["text"])
        def buy(message):
            print("Back was pressed")
            name(message, row[2])
            bot.send_message(message.chat.id, "Back was pressed")'''

@bot.message_handler(func=lambda message: True)
def asd(message):
    for row in rows:
        if message.text == row[2]:
            back.append(["name", row[2]])
            name(message, row[2])
    for row in group_rows:
        if message.text == row[0]:
            advisor(message, row[0])
    if message.text == "Back":
        if len(back)!= 0:
            command = back[len(back)-1]
            print(back)
            if command[0] == "name":
                name(message, command[1])
                print("Removed")
                print(back)
                back.remove(command)
        elif len(back) == 0:
            home(message)

if __name__ == '__main__':
    bot.polling(none_stop=True)

'''bt1 = types.InlineKeyboardButton(text = "Получил", callback_data = 1)
    bt2 = types.InlineKeyboardButton(text = "Не получил", callback_data = 0)
    reply_markup = types.InlineKeyboardMarkup([bt1,bt2])
    bot.send_message(call.chat.id, "Dean!", reply_markup=reply_markup)'''