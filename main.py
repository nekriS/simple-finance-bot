from data import load_data
from data import save_data
from login import get_login
import warnings
import sys
import os
import telebot
from telebot import types
import datetime
import calendar
import numpy as np

warnings.filterwarnings('ignore')

folder = 'data'
path_json = 'data/json'
default_category_json = 'default_categories.json'
users_file = 'users.json'

if not os.path.isdir(folder):
    os.mkdir(folder)
if not os.path.isdir(path_json):
    os.mkdir(path_json)

path_json_users = path_json + ('/' + users_file)
default_category = path_json + ('/' + default_category_json)

offset = datetime.timedelta(hours=3)
timezone = datetime.timezone(offset, name='MSK')

memory = {}

# Подключение бота
bot = telebot.TeleBot(get_login("telegram"));
# Создаем главное меню
keyboard_main = types.InlineKeyboardMarkup();
key_lk = types.InlineKeyboardButton(text='📆 Дневная сводка', callback_data='lk');
key_finance = types.InlineKeyboardButton(text='📈 Статистика за 7 дней', callback_data='statistic');
keyboard_main.add(key_lk);
keyboard_main.add(key_finance);
key_set= types.InlineKeyboardButton(text='⚙ Настроить', callback_data='setting');
keyboard_main.add(key_set);

# Создаем меню настроек
keyboard_setting = types.InlineKeyboardMarkup();
len_period = types.InlineKeyboardButton(text='📆 Изменить длину периода', callback_data='len_period');
len_limit = types.InlineKeyboardButton(text='💵 Изменить дневной лимит', callback_data='len_limit');
excel = types.InlineKeyboardButton(text='0️⃣ Экспорт в Excel', callback_data='excel');
clear = types.InlineKeyboardButton(text='💣 Сбросить мои данные', callback_data='clear');
back = types.InlineKeyboardButton(text='👈 Назад', callback_data='back_1');
keyboard_setting.add(len_period);
keyboard_setting.add(len_limit);
keyboard_setting.add(excel);
keyboard_setting.row(clear, back);


keyboard_len = types.InlineKeyboardMarkup();
week = types.InlineKeyboardButton(text='Неделя', callback_data='week');
month = types.InlineKeyboardButton(text='Месяц', callback_data='month');
keyboard_len.row(week, month);
back = types.InlineKeyboardButton(text='👈 Назад', callback_data='back_2');
keyboard_len.add(back);
#keyboard_cat = types.InlineKeyboardMarkup();


# def log(text):
#     now = datetime.datetime.now(tz=timezone)  
#     nowf = now.strftime("%d.%m.%Y %H:%M:%S")
#     print(nowf + ": " + text)

def log(text):
    
    if text != "" and text != " ":
        
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        log_directory = 'log'
        log_file_name = f'log_{today_date}.txt'
        log_file_path = os.path.join(log_directory, log_file_name)

        # Проверяем наличие каталога "log" и создаем его, если его нет
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Формируем строку для записи: "дата-время > текст"
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        log_entry = f"{today_date} {current_time} > {text}"

        # Проверяем existence файла и записываем данные
        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(log_entry+"\n")

        print(log_entry)



def create_buts_cat(id, operation):
    keyboard_cat = types.InlineKeyboardMarkup();
    information = load_data(path_json + "/" + str(id) + ".json")

    i = 0
    cat_0 = types.InlineKeyboardButton(text="def", callback_data="def");
    
    if operation < 0:
        cats = information["categories"]["expenses"]
    elif operation > 0:
        cats = information["categories"]["income"]


    for cat in cats:
        cat_1 = cat_0
        cat_0 = types.InlineKeyboardButton(text=cat, callback_data="cat_"+str(i));
        if ((i + 1) % 2) == 0:
            keyboard_cat.row(cat_0, cat_1);
        elif (i + 1) == len(cats):
            keyboard_cat.add(cat_0);
        #keyboard_cat.add(cat_0);
        i += 1 
    return keyboard_cat

def add_operation(id, num, cat):

    information = load_data(path_json + "/" + str(id) + ".json")
    information["balance"] = information["balance"] + num

    now = datetime.datetime.now(tz=timezone)  
    nowf = now.strftime("%d.%m.%Y")

    if not(nowf in information["operations"]):
        information["operations"][nowf] = []


    cat_str = "None"

    try:
        if num < 0:
            cat_str = information["categories"]["expenses"][cat]
        elif num > 0:
            cat_str = information["categories"]["income"][cat]
        else:
            pass
    except:
        log(f"Couldn't get the category! id: {id}, cat_id: {cat}")
        pass
    
    information["operations"][nowf].append([nowf, num, cat_str])

    save_data(information, path_json + "/" + str(id) + ".json")

    log(f"Operation was added: {num}, id: {id}, cat_id: {cat}")

    pass

def create_profile(object):
    #загружаем бд с данными пользователей
    users = load_data(path_json_users)

    if not(str(object.id) in users):
        users[str(object.id)] = {}
        users[str(object.id)]["id"] = object.id
        users[str(object.id)]["first_name"] = object.first_name
        users[str(object.id)]["last_name"] = object.last_name
        users[str(object.id)]["username"] = object.username
        users[str(object.id)]["is_premium"] = bool(object.is_premium)

    if not("is_pay" in users[str(object.id)]):
        users[str(object.id)]["is_pay"] = False #для примера, потом убрать, иначе будет стирать историю покупок подписки
    #users[str(object.id)] = tmp
    if not("days" in users[str(object.id)]):
        users[str(object.id)]["days"] = "month"
    if not("days_limit" in users[str(object.id)]):
        users[str(object.id)]["days_limit"] = 500
    if not("currecy" in users[str(object.id)]):
        users[str(object.id)]["currecy"] = "₽"

    #загружаем бд с данными конкретного пользователя
    inf = load_data(path_json + "/" + str(object.id) + ".json")
    if not("categories" in inf):
        d_cat = load_data(default_category)
        inf["categories"] = d_cat["categories"]
    if not("balance" in inf):
        inf["balance"] = 0
    if not("operations" in inf):
        inf["operations"] = {}

    save_data(inf, path_json + "/" + str(object.id) + ".json")
    save_data(users, path_json_users)
    return users

def start(bot, object):
    try:
        create_profile(object)
        bot.send_message(object.id, text="✅️ Ваш профиль был успешно создан!")
        main_menu(object.id)

        log("Profile was created! id: " + str(object.id))
    except:
        log("Can not create profile! id: " + str(object.id))

    
    #print(users)

def get_day_saldo(day_operations):
    summa = 0
    for operation in day_operations:
        summa += operation[1]
    return summa

def statistic_seven_day(id):
    try:
        values = []
        days = []
        
        user = load_data(path_json + "/" + str(id) + ".json")
        users = load_data(path_json_users)
        profile = users[str(id)]

        now = datetime.datetime.now(tz=timezone)  

        for day in range(0, 7):
            date = now - datetime.timedelta(days=day)
            date_formate = date.strftime("%d.%m.%Y")

            days.append(date.strftime("%d.%m"))
            
            if date_formate in user["operations"]:
                values.append(round(get_day_saldo(user["operations"][date_formate]), 2))    
            else:
                values.append(0)

        part = (np.max(values) - 0.01) / 7

        

        message = f"""
📈 *Статистика за последние 7 дней*

{days[6]} {("🟢" if values[6] > 0 else "🔴") * int(abs(values[6]) // part)} {"+" if values[5] > 0 else ""}{values[6]}{profile["currecy"]}
{days[5]} {("🟢" if values[5] > 0 else "🔴") * int(abs(values[5]) // part)} {"+" if values[5] > 0 else ""}{values[5]}{profile["currecy"]}
{days[4]} {("🟢" if values[4] > 0 else "🔴") * int(abs(values[4]) // part)} {"+" if values[4] > 0 else ""}{values[4]}{profile["currecy"]}
{days[3]} {("🟢" if values[3] > 0 else "🔴") * int(abs(values[3]) // part)} {"+" if values[3] > 0 else ""}{values[3]}{profile["currecy"]}
{days[2]} {("🟢" if values[2] > 0 else "🔴") * int(abs(values[2]) // part)} {"+" if values[2] > 0 else ""}{values[2]}{profile["currecy"]}
{days[1]} {("🟢" if values[1] > 0 else "🔴") * int(abs(values[1]) // part)} {"+" if values[1] > 0 else ""}{values[1]}{profile["currecy"]}
{days[0]} {("🟢" if values[0] > 0 else "🔴") * int(abs(values[0]) // part)} {"+" if values[0] > 0 else ""}{values[0]}{profile["currecy"]}

Всего: *{round(np.sum(values), 2)}*{profile["currecy"]}
Среднее: *{round(np.mean(values), 2)}*{profile["currecy"]} 
""".replace("-", "−").replace("  ", " ")

        bot.send_message(id, text=message, reply_markup=keyboard_main, parse_mode='markdown')
    
        log(f"Operation 'statistic_seven_day', user: {id} completed successfully!")

    except:

        log(f"Operation 'statistic_seven_day', user: {id} was not executed!")


def main_menu(id):
    #texts = "Главное меню: "

    users = load_data(path_json_users)
    user = load_data(path_json + "/" + str(id) + ".json")

    now = datetime.datetime.now(tz=timezone)  
    nowf = now.strftime("%d.%m.%Y")

    balance = str((user["balance"]))

    sum = 0.0
    if nowf in user["operations"]:
        for el in user["operations"][nowf]:
            sum += float(el[1])
    sald = str(sum)

    minn = 0.0
    if nowf in user["operations"]:
        for el in user["operations"][nowf]:
            if el[1] < 0:
                minn += float(el[1])
    

    daily_count = float(users[str(id)]["days_limit"]) 
    ost = str(daily_count + minn)


    if users[str(id)]["days"] == 'week':
        dayss = 7
        #print(now.weekday())
        dn = str(dayss - int(now.weekday()))
    else:
        dayss = calendar.monthrange(2021, int(now.strftime("%m")))[1]
        dn = str(dayss+1 - int(now.strftime("%d")))

    
    mn = str(round(float(balance)-((int(dn))*daily_count),2))


    ind1 = '🟢' if float(sald) >= 0 else '🔴'
    ind2 = '🟢' if float(ost) >= 0 else '🔴'
    ind3 = '🟢' if float(balance) >= 0 else '🔴'
    ind4 = '🟢' if float(mn) >= 0 else '🔴'


    if float(mn) >= 0:
        sta = 'профицит'
        ind5 = '🔴'
    else:
        sta = 'дефицит'
        ind5 = '🔴'

    message_ = """
📆 Дневная сводка
*{}*

{} Сальдо: *{}*₽
{} Дневной остаток: *{}*₽

До конца периода: *{}* дней(я)

{} Баланс: *{}*₽
{} Свободных средств: *{}*₽
{} Статус: {}.
    """.format(nowf, ind1, sald, ind2, ost, dn, ind3, balance, ind4, mn, ind5, sta)
    
    bot.send_message(id, text=message_, reply_markup=keyboard_main, parse_mode='markdown')
    pass

def settings(id):

    users = load_data(path_json_users)

    days = users[str(id)]["days"]
    limit = users[str(id)]["days_limit"]
    currency = users[str(id)]["currecy"]

    days = days.replace("month", "месяц").replace("week", "неделя")

    texts = f"""
⚙ *Настройки*

Расчетный период: *{days}*
Дневной лимит: *{limit}{currency}*
Валюта: *{currency}*

"""
    
    bot.send_message(id, text=texts, reply_markup=keyboard_setting, parse_mode='markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global memory
    try:
        operation = memory[str(call.from_user.id)]
    except:
        operation = 0
        pass

    if call.data == "/start":
        start(bot, call.from_user)

    #elif call.data == "lk":
    #    please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
    #    main_menu(call.from_user.id)
    
    elif call.data == "setting":
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        settings(call.message.chat.id)

    #elif call.data == "back_1":
    #    please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
    #    main_menu(call.from_user.id)
        #bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard_main)

    elif call.data == "len_period":
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❓️ Выберите длину расчетного периода:", reply_markup=keyboard_len)  

    elif call.data == "week":

        users = load_data(path_json_users)
        users[str(call.message.chat.id)]["days"] = "week"
        save_data(users, path_json_users)

        #please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: наделя", reply_markup=None)
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        main_menu(call.from_user.id)

    elif call.data == "month":

        users = load_data(path_json_users)
        users[str(call.message.chat.id)]["days"] = "month"
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        save_data(users, path_json_users)


        #please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: месяц", reply_markup=None)
        main_menu(call.from_user.id)

    elif call.data == "statistic":
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        statistic_seven_day(call.from_user.id)


    elif not(operation == 0):
        texts = 'Операция успешно добавлена!'
        
        cat = call.data

        if "cat_" in cat:
            add_operation(call.from_user.id, operation, int(cat[-1]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texts, reply_markup=None)
            main_menu(call.message.chat.id)

        del memory[str(call.from_user.id)] #удаление ячейки

    else:
        please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)
        main_menu(call.message.chat.id)
            

def please_delete_all_buttons(chat_id, message_id, k=1):
    for j in range(k,10):
        try:
            bot.edit_message_reply_markup(chat_id, message_id-j, reply_markup=None)
            break
        except:
            pass

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global memory
    

    line = message.text
    line = line.replace(' ', '')
    line = line.replace(',', '.')
    
    operation = 0
    #global operation

    if (message.text == "/help") or (message.text == "/start"):
        start(bot, message.from_user)

    elif line[1:].replace('.', '').isnumeric():

        operation = float(line)
        memory[str(message.from_user.id)] = operation
        please_delete_all_buttons(message.chat.id, message.message_id) #удаление всех старых кнопок выше
        texts = 'Выберите категорию: '
        bot.send_message(message.chat.id, text=texts, reply_markup=create_buts_cat(message.chat.id, operation))
        

    elif message.text.isnumeric() and not(flag_oper == 0):
        print("Add")
        flag_oper = 0
        texts = 'Главное меню:'
        bot.send_message(message.chat.id, text=texts, reply_markup=keyboard_main)
        pass   

def main():
    log("Hello...")
    bot.polling(none_stop=True, interval=0)
    pass

if __name__ == '__main__':
    sys.exit(main())



