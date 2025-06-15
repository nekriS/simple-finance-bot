from data import load_data, save_data
from login import get_login
from functions import create_buts_cat, add_operation, create_profile, statistic_seven_day, main_menu, settings, log
import warnings
import sys
import os
import telebot
from telebot import types
import datetime
import objects

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

    if call.data == "/start":
        start(bot, call.from_user)

    elif call.data == "setting":
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        settings(bot, path, memory, call.message.chat.id)

    elif call.data == "len_period":
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❓️ Выберите длину расчетного периода:", reply_markup=memory.keyboards["keyboard_len"])  

    elif call.data == "week":

        users = load_data(path.path_users)
        users[str(call.message.chat.id)]["days"] = "week"
        save_data(users, path.path_users)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: наделя", reply_markup=None)
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        main_menu(bot, path, memory, call.from_user.id)

    elif call.data == "month":

        users = load_data(path.path_users)
        users[str(call.message.chat.id)]["days"] = "month"
        save_data(users, path.path_users)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: месяц", reply_markup=None)
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        main_menu(bot, path, memory, call.from_user.id)

    elif call.data == "statistic":
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        statistic_seven_day(bot, path, memory, call.from_user.id)


    elif not(operation == 0):
        texts = 'Операция успешно добавлена!'
        
        cat = call.data

        if "cat_" in cat:
            add_operation(path, memory, call.from_user.id, operation, int(cat[-1]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texts, reply_markup=None)
            main_menu(bot, path, memory, call.from_user.id)

        del memory.cache[str(call.from_user.id)] #удаление ячейки

    else:
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        main_menu(bot, path, memory, call.from_user.id)
            

def please_delete_all_buttons(chat_id, message_id, k=1):
    for j in range(k,10):
        try:
            bot.edit_message_reply_markup(chat_id, message_id-j, reply_markup=None)
            break
        except:
            pass

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
        

    elif message.text.isnumeric() and not(flag_oper == 0):
        print("Add")
        flag_oper = 0
        texts = 'Главное меню:'
        bot.send_message(message.chat.id, text=texts, reply_markup=memory.keyboards["keyboard_main"])


def start(bot, object):
    try:
        create_profile(path, object)
        bot.send_message(object.id, text="✅️ Ваш профиль был успешно создан!")
        main_menu(bot, path, memory, object.id)

        log("Profile was created! id: " + str(object.id))
    except:
        log("Can not create profile! id: " + str(object.id))


def main():
    
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
    key_lk = types.InlineKeyboardButton(text='📆 Дневная сводка', callback_data='lk')
    key_finance = types.InlineKeyboardButton(text='📈 Статистика за 7 дней', callback_data='statistic')
    keyboard_main.add(key_lk)
    keyboard_main.add(key_finance)
    key_set= types.InlineKeyboardButton(text='⚙ Настроить', callback_data='setting')
    keyboard_main.add(key_set)
    memory.keyboards["keyboard_main"] = keyboard_main

    # Создаем меню настроек
    keyboard_setting = types.InlineKeyboardMarkup()
    len_period = types.InlineKeyboardButton(text='📆 Изменить длину периода', callback_data='len_period')
    len_limit = types.InlineKeyboardButton(text='💵 Изменить дневной лимит', callback_data='len_limit')
    excel = types.InlineKeyboardButton(text='0️⃣ Экспорт в Excel', callback_data='excel')
    clear = types.InlineKeyboardButton(text='💣 Сбросить мои данные', callback_data='clear')
    back = types.InlineKeyboardButton(text='👈 Назад', callback_data='back_1')
    keyboard_setting.add(len_period)
    keyboard_setting.add(len_limit)
    keyboard_setting.add(excel)
    keyboard_setting.row(clear, back)
    memory.keyboards["keyboard_setting"] = keyboard_setting

    # Меню выбора длины периода
    keyboard_len = types.InlineKeyboardMarkup()
    week = types.InlineKeyboardButton(text='Неделя', callback_data='week')
    month = types.InlineKeyboardButton(text='Месяц', callback_data='month')
    keyboard_len.row(week, month)
    back = types.InlineKeyboardButton(text='👈 Назад', callback_data='back_2')
    keyboard_len.add(back)
    memory.keyboards["keyboard_len"] = keyboard_len

    log("Hello...")
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    sys.exit(main())



