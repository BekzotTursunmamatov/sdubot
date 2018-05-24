import datetime
import config
import telebot
import cherrypy
import telegram
import requests
import copy
import Info
from SQLighter import SQLighter
from telebot import types

WEBHOOK_HOST = '85.117.103.144'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = 'C:/OpenSSL-Win32/bin/webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'C:/OpenSSL-Win32/bin//webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

db_worker = SQLighter(config.database_name)


menu_dict = dict()
last_menu = list()



global steps
steps = list()
sl = dict()
weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
adkey = types.KeyboardButton("💺Administrator")
unikey = types.KeyboardButton("🏢University")
fackey = types.KeyboardButton("👨‍🎓👩‍⚕Faculties")
evkey = types.KeyboardButton("🎈SDUlife")

keyboard.row(adkey, unikey)
keyboard.row(fackey, evkey)
keyboard.add(types.KeyboardButton("📅Timatable"))
back_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
back_keyboard.row(types.KeyboardButton("🔙Back"), types.KeyboardButton("🏚Home"))


@bot.message_handler(commands=['start'])
def start_message(message):
    msg = bot.send_message(message.chat.id, "Please choose one of them:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, handle_menu)


def handle_menu(message):
    if message.text == "🔙Back":
        steps.remove(steps[-1])
        set_keyboard(message, step_links())
    elif message.text == "🏚Home":
        steps.clear()
        global sl
        sl = copy.deepcopy(Info.menu_dict)
        start_message(message)
    else:
        steps.append(message.text)
        print()
        print(type(sl[message.text]))
        if type(sl[message.text]) is dict:
            print(message.text)
            set_keyboard(message, step_links())

        elif type(sl[message.text]) is int:
            print(sl[message.text], steps[-2], steps[-3])
            handle_timetable(message,steps[-3], steps[-2], sl[message.text])

        elif type(sl[message.text]) is str:
            if message.text == "About":
                msg = bot.send_message(message.chat.id,  sl["About"], reply_markup=back_keyboard)
                bot.register_next_step_handler(msg, handle_menu)
            elif message.text == "Photo":
                photo_url = sl['Photo']
                r = requests.get(photo_url, stream=True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    msg = bot.send_photo(message.chat.id, r.raw, reply_markup=back_keyboard)
                    bot.register_next_step_handler(msg, handle_menu)
                r.close()
            elif message.text == "Today":
                msg = bot.send_message(message.chat.id, sl["Today"], parse_mode=telegram.ParseMode.HTML, reply_markup=back_keyboard)
                bot.register_next_step_handler(msg, handle_menu)
        elif type(sl[message.text]) is list:
            handle_list_type(message)
        else:
            steps.remove(steps[-1])
            bot.send_message(message.chat.id, text="Please click the button!")
            set_keyboard(message, step_links())

sl = copy.deepcopy(Info.menu_dict)

def step_links():
    global sl
    sl = copy.deepcopy(Info.menu_dict)
    for step in steps:
        sl = sl[step]
    return  sl

def set_keyboard(message,diction):
    add_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    print(diction)
    global last_menu
    for key in diction.keys():
        add_keyboard.row(types.KeyboardButton(key))
        last_menu.append(key)
    msg = bot.send_message(message.chat.id, "Choose one variant", reply_markup=add_keyboard)
    bot.register_next_step_handler(msg, handle_menu)


def handle_list_type(message):

    info = sl[message.text][1]
    info = Info.info_dict[info]

    photos = sl[message.text][2]
    photos = Info.info_dict[photos]

    description = sl[message.text][3]
    description = Info.info_dict[description]

    msg = bot.send_message(message.chat.id, text=info, parse_mode="HTML")
    for i in photos:
        r = requests.get(i, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            bot.send_photo(message.chat.id, r.raw)
        r.close()
    bot.register_next_step_handler(msg, handle_menu)
    bot.send_message(message.chat.id, text=description, parse_mode=telegram.ParseMode.HTML, reply_markup=back_keyboard)

def handle_timetable(message, course, group, day):
    db_worker = SQLighter(config.database_name)
    if course == "3course":
        print("3 COURSE")
        if day == 0:
            print("000000")
            if today_tomorrow()[0] < 5:

                timetable = db_worker.select_timetable(course, group, weekdays[today_tomorrow()[0]])
                print(timetable[0][0])
                st = str(timetable[0][0])
                msg = bot.send_message(message.chat.id, text=st, parse_mode="HTML", reply_markup=back_keyboard)
                bot.register_next_step_handler(msg, handle_menu)
            else:
                msg = bot.send_message(message.chat.id, text="Today is a day off!", reply_markup=back_keyboard)
                bot.register_next_step_handler(msg, handle_menu)
        elif day == 1:
            if today_tomorrow()[1] < 5:
                timetable = db_worker.select_timetable(course, group, weekdays[today_tomorrow()[1]])
                st = str(timetable[0][0])
                msg = bot.send_message(message.chat.id, text=st, parse_mode="HTML", reply_markup=back_keyboard)
                bot.register_next_step_handler(msg, handle_menu)
            else:
                msg = bot.send_message(message.chat.id, text="Tomorrow is a day off!", reply_markup=back_keyboard)
                bot.register_next_step_handler(msg, handle_menu)
        elif day == 2:
            timetable = db_worker.select_week(course, group)
            global days
            days = ""
            for s in timetable:
                days = days + s[0]+"\n\n"+s[1]+"\n\n"+s[2]+"\n\n"+s[3]+"\n\n"+s[4]+"\n\n"
                print(days)
            msg = bot.send_message(message.chat.id, text=days, parse_mode="HTML", reply_markup=back_keyboard)
            bot.register_next_step_handler(msg, handle_menu)
    db_worker.close()

def today_tomorrow():
    weekday = datetime.datetime.today().weekday()
    return[weekday, weekday+1]

# Наш вебхук-сервер
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

# Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
bot.remove_webhook()

# Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

 # Собственно, запуск!
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

