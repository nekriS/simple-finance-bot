from data import load_data, save_data
from login import get_login
from functions import create_buts_cat, add_operation, create_profile, statistic_seven_day, main_menu, settings, log, get_csv_month
import warnings
import sys
import os
import telebot
from telebot import types
import datetime
import objects
import time

warnings.filterwarnings('ignore')
# Подключение бота
bot = telebot.TeleBot(get_login("telegram"))
# Описание директорий и структуры файлов
path = objects.path()
# Память
memory = objects.memory()







@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    try:
        operation = memory.cache[str(call.from_user.id)]
    except: 
        operation = 0
        pass

    please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)

    match call.data:
        case "settings":
            settings(bot, path, memory, call.message.chat.id)
        case "len_period":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❓️ Выберите длину расчетного периода:", reply_markup=memory.keyboards["keyboard_len"])  
        case "week":
            users = load_data(path.path_users)
            users[str(call.message.chat.id)]["days"] = "week"
            save_data(users, path.path_users)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: наделя", reply_markup=None)
            main_menu(bot, path, memory, call.from_user.id)
        case "month":
            users = load_data(path.path_users)
            users[str(call.message.chat.id)]["days"] = "month"
            save_data(users, path.path_users)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: месяц", reply_markup=None)
            main_menu(bot, path, memory, call.from_user.id)
        case "statistic_seven":
            statistic_seven_day(bot, path, memory, call.from_user.id)
        case "export":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=memory.keyboards["keyboard_export"])  
        
        case "csv":
            get_csv_month(bot, path, memory, call.from_user.id)
            
        case _:
            if not(operation == 0):
                texts = 'Операция успешно добавлена!'
                
                cat = call.data

                if "cat_" in cat:
                    add_operation(path, memory, call.from_user.id, operation, int(cat[-1]))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texts, reply_markup=None)
                    main_menu(bot, path, memory, call.from_user.id)

                del memory.cache[str(call.from_user.id)] #удаление ячейки
            else:
                main_menu(bot, path, memory, call.from_user.id)
            



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    
    line = message.text
    line = line.replace(' ', '')
    line = line.replace(',', '.')
    
    operation = 0
    #global operation

    if (message.text == "/help") or (message.text == "/start"):
        start(bot, message.from_user)

    elif line[1:].replace('.', '').isnumeric():

        operation = float(line)
        memory.cache[str(message.from_user.id)] = operation
        please_delete_all_buttons(message.chat.id, message.message_id) #удаление всех старых кнопок выше
        texts = 'Выберите категорию: '
        bot.send_message(message.chat.id, text=texts, reply_markup=create_buts_cat(path, message.chat.id, operation))    

    else:
        bot.send_message(message.chat.id, text="Меню:", reply_markup=memory.keyboards["keyboard_main"])

def please_delete_all_buttons(chat_id, message_id, k=1):
    for j in range(k,10):
        try:
            bot.edit_message_reply_markup(chat_id, message_id-j, reply_markup=None)
            break
        except:
            pass

def start(bot, object):
    try:
        if create_profile(path, object):
            bot.send_message(object.id, text="✅️ Ваш профиль был успешно создан!")
            log("Profile was created! id: " + str(object.id))
        else:
            bot.send_message(object.id, text="✅️ Ваш профиль уже существует!")
        main_menu(bot, path, memory, object.id)

        
    except:
        log("Can not create profile! id: " + str(object.id))


def listening(bot):
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        log("Connection to the server was lost! Timeout: 60 seconds.")
        time.sleep(60)
        listening(bot)

def init():
    
    if not os.path.isdir(path.folder):
        os.mkdir(path.folder)
    if not os.path.isdir(path.path_json):
        os.mkdir(path.path_json)

    path.path_users = f"{path.path_json}/{path.users_file}"
    path.path_default_category = f"{path.path_json}/{path.default_category_json}"

    offset = datetime.timedelta(hours=3)
    memory.timezone = datetime.timezone(offset, name='MSK')
    
    # Создаем главное меню
    keyboard_main = types.InlineKeyboardMarkup()

    key_lk = types.InlineKeyboardButton(text='📊 Дневная сводка', callback_data='daily_summary')
    key_stat7 = types.InlineKeyboardButton(text='📅 Статистика за 7 дней', callback_data='statistic_seven')
    key_statmonth= types.InlineKeyboardButton(text='📈 Месячная статистика', callback_data='statistic_month')
    key_set= types.InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')
    key_export= types.InlineKeyboardButton(text='📁 Экспорт данных', callback_data='export')
    key_help= types.InlineKeyboardButton(text='❓ Помощь / FAQ', callback_data='help')

    #keyboard_main.row(key_lk, key_stat7)
    keyboard_main.add(key_lk)
    keyboard_main.add(key_stat7)
    keyboard_main.add(key_statmonth)
    keyboard_main.row(key_export, key_set)
    #keyboard_main.add(key_set)
    #keyboard_main.add(key_export)
    keyboard_main.add(key_help)

    memory.keyboards["keyboard_main"] = keyboard_main

    # меню экспорта
    keyboard_export = types.InlineKeyboardMarkup()
    csv = types.InlineKeyboardButton(text='📄 Экспорт в CSV', callback_data='csv')
    back = types.InlineKeyboardButton(text='👈 Назад', callback_data='back')
    keyboard_export.add(csv)
    keyboard_export.add(back)

    memory.keyboards["keyboard_export"] = keyboard_export
    # Создаем меню настроек
    keyboard_setting = types.InlineKeyboardMarkup()
    len_period = types.InlineKeyboardButton(text='📆 Изменить длину периода', callback_data='len_period')
    len_limit = types.InlineKeyboardButton(text='💵 Изменить дневной лимит', callback_data='len_limit')
    
    clear = types.InlineKeyboardButton(text='💣 Сбросить мои данные', callback_data='clear')
    back = types.InlineKeyboardButton(text='👈 Назад', callback_data='back_1')
    keyboard_setting.add(len_period)
    keyboard_setting.add(len_limit)
    #keyboard_setting.add(excel)
    keyboard_setting.row(clear, back)
    memory.keyboards["keyboard_setting"] = keyboard_setting

    # Меню выбора длины периода
    keyboard_len = types.InlineKeyboardMarkup()
    week = types.InlineKeyboardButton(text='Неделя', callback_data='week')
    month = types.InlineKeyboardButton(text='Месяц', callback_data='month')
    keyboard_len.row(week, month)
    back = types.InlineKeyboardButton(text='👈 Назад', callback_data='settings')
    keyboard_len.add(back)
    memory.keyboards["keyboard_len"] = keyboard_len

    log("Hello...")

    listening(bot)
    

if __name__ == '__main__':
    sys.exit(init())



