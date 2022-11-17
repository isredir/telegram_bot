import telebot
from telebot import types
from telebot import TeleBot
import requests
import json
from geopy import geocoders
from datetime import datetime

token_accu = 'gBj1vV4C8jprBzXRFLHpyAriTn7nvO3G'
token = '5509012183:AAH4zUOl5q51qukEnFXj8gZYQ2fQfGSnqVE'

bot = TeleBot(token)

banned = set()
muted = set()
admins = set()

def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude

def code_location(latitude: str, longitude: str, token_accu: str):
    url_location_key = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=' \
                       f'{token_accu}&q={latitude},{longitude}&language=ru'
    resp_loc = requests.get(url_location_key, headers={"APIKey": token_accu})
    json_data = json.loads(resp_loc.text)
    print(json_data)
    code = json_data['Key']
    return code

def get_weather(code_loc: str, token_accu: str):
    url_weather = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{code_loc}?' \
                  f'apikey={token_accu}&language=ru&metric=True'
    response = requests.get(url_weather, headers={"APIKey": token_accu})
    json_data = json.loads(response.text)
    dict_weather = dict()
    dict_weather['link'] = json_data[0]['MobileLink']
    time = 'сейчас'
    dict_weather[time] = {'temp': json_data[0]['Temperature']['Value'], 'sky': json_data[0]['IconPhrase']}
    for i in range(1, len(json_data)):
        time = 'через' + str(i) + 'ч'
        dict_weather[time] = {'temp': json_data[i]['Temperature']['Value'], 'sky': json_data[i]['IconPhrase']}
    return dict_weather

def print_weather(dict_weather, message):
    bot.send_message(message.chat.id, f' Погода в вашем городе:\n'
                                           f' Cейчас: температура: {dict_weather["сейчас"]["temp"]},'
                                           f' {dict_weather["сейчас"]["sky"]}.\n'
                                           f' Через 3 часа: температура: {dict_weather["через3ч"]["temp"]},'
                                           f' {dict_weather["через3ч"]["sky"]}.\n'
                                           f' Через 6 часов: температура: {dict_weather["через6ч"]["temp"]},'
                                           f' {dict_weather["через6ч"]["sky"]}.\n'
                                           f' Через 9 часов: температура: {dict_weather["через9ч"]["temp"]},'
                                           f' {dict_weather["через9ч"]["sky"]}.\n')
    bot.send_message(message.chat.id, f' Подробнее: \n'
                                           f'{dict_weather["link"]}')
    
@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    answers = ['около тысячи', 'около миллиона', '42', 'около миллиарда']
    markup = types.InlineKeyboardMarkup(row_width=4)
    item1 = types.InlineKeyboardButton(answers[0], callback_data='thousand')
    markup.row(item1)
    item2 = types.InlineKeyboardButton(answers[1], callback_data='million')
    markup.row(item2)
    item3 = types.InlineKeyboardButton(answers[2], callback_data='forty_two')
    markup.row(item3)
    item4 = types.InlineKeyboardButton(answers[3], callback_data='milliard')
    markup.row(item4)
    bot.send_message(message.chat.id, "Привет, " + str(message.new_chat_members[0].first_name) + "!\n"
                                      "Как вы думаете, сколько раз надо сложить лист бумаги, чтобы достать до луны?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def reply_to_new_member(call):
    if call.data == 'forty_two':
        bot.send_message(call.message.chat.id, "Правильно! И это не отсылка на Автостопом по галактике. Бумагу действительно достаточно сложить 42 раза")
    else:
        bot.send_message(call.message.chat.id, "Не-а, не угадали!")

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Список команд: \n"
                                      "/ban - забанить пользователя (нужно ответить этой командой на сообщение пользователя)\n"
                                      "/unban - разбанить пользователя\n"
                                      "/mute - замутить пользователя\n"
                                      "/unmute - размутить пользователя\n"
                                      "/promote - сделать админом пользователя\n"
                                      "/leave - выгнать бота из чата\n"
                                      "/stats - показать статистику чата\n"
                                      "/weather - узнать погоду в городе\n"
                                      "/help - вывести справку")

@bot.message_handler(commands=['ban'])
def ban_user(message: types.Message):
    if message.reply_to_message.from_user.first_name not in banned:
        try:
            bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            banned.add(message.reply_to_message.from_user.first_name)
            bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " получает бан!")
        except Exception as e:
            bot.reply_to(message, "Пользователя " + str(message.reply_to_message.from_user.first_name) + " нельзя забанить!")
            print(e)
    else:
        bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " уже был забанен!")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.reply_to_message.from_user.first_name in banned:
        try:
            bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            banned.remove(message.reply_to_message.from_user.first_name)
            bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " больше не забанен!")
        except Exception as e:
            bot.reply_to(message, "Пользователя " + str(message.reply_to_message.from_user.first_name) + " нельзя разбанить!")
            print(e)
    else:
        bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " не забанен!")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message.from_user.first_name not in muted:
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            muted.add(message.reply_to_message.from_user.first_name)
            bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " получает мут!")
        except Exception as e:
            bot.reply_to(message, "Пользователя " + str(message.reply_to_message.from_user.first_name) + " нельзя замутить!")
            print(e)
    else:
        bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " уже в муте!")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message.from_user.first_name in muted:
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, 
                             can_send_media_messages=True, can_send_polls=True, 
                             can_send_other_messages=True, can_add_web_page_previews=True, 
                             can_change_info=True, can_invite_users=True, can_pin_messages=True)
            muted.remove(message.reply_to_message.from_user.first_name)
            bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " больше не в муте!")
        except Exception as e:
            bot.reply_to(message, "Пользователя " + str(message.reply_to_message.from_user.first_name) + " нельзя размутить!")
            print(e)
    else:
        bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " не муте!")

@bot.message_handler(commands=['promote'])
def promote_user(message: types.Message):
    if message.reply_to_message.from_user.first_name not in admins:
        try:
            bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                can_delete_messages= True, can_pin_messages=True, can_change_info=True,
                                can_invite_users=True, can_restrict_members=True, can_edit_messages=True,
                                can_manage_chat=True, can_manage_video_chats=True, can_manage_voice_chats=True)
            admins.add(message.reply_to_message.from_user.first_name)
            bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " теперь админ!")
        except Exception as e:
            bot.reply_to(message, "У бота недостаточно прав!")
            print(e)
    else:
        bot.reply_to(message, "Пользователь " + str(message.reply_to_message.from_user.first_name) + " уже админ!")
                            

@bot.message_handler(commands=['leave'])
def leave_chat(message):
    bot.send_message(message.chat.id, "До свидания!")
    bot.leave_chat(message.chat.id)

@bot.message_handler(commands=['stats'])
def leave_chat(message):
    bot.send_message(message.chat.id, "Всего участников: " + str(bot.get_chat_member_count(message.chat.id)) + "\n" +
                                      "Админов:" + str(len(admins) + 2))

@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id,
                         message.from_user.first_name + " Укажите ваш город, ответив на это сообщение.")

@bot.message_handler(content_types=["text"])
def weather_in_city(message):
    if message.reply_to_message != None and message.reply_to_message.text == message.from_user.first_name + " Укажите ваш город, ответив на это сообщение.":
        try:
            city = message.text
            print(city)
            latitude, longitude = geo_pos(city)
            code_loc = code_location(latitude, longitude, token_accu)
            you_weather = get_weather(code_loc, token_accu)
            print_weather(you_weather, message)
        except AttributeError as e:
            bot.send_message(message.chat.id,
                            f'Направильное название города')

bot.polling(none_stop=True, interval=0)
