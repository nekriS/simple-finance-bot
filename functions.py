
from data import load_data, save_data
import calendar
import numpy as np
from telebot import types
import datetime
import sys
import os

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

def create_buts_cat(path, id, operation):
    keyboard_cat = types.InlineKeyboardMarkup();
    information = load_data(path.path_json + "/" + str(id) + ".json")

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

def add_operation(path, memory, id, num, cat):

    information = load_data(path.path_json + "/" + str(id) + ".json")
    information["balance"] = information["balance"] + num

    now = datetime.datetime.now(tz=memory.timezone)  
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

    save_data(information, path.path_json + "/" + str(id) + ".json")

    log(f"Operation was added: {num}, id: {id}, cat_id: {cat}")

    pass

def create_profile(path, object):
    #загружаем бд с данными пользователей
    users = load_data(path.path_users)

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
    inf = load_data(path.path_json + "/" + str(object.id) + ".json")
    if not("categories" in inf):
        d_cat = load_data(path.path_default_category)
        inf["categories"] = d_cat["categories"]
    if not("balance" in inf):
        inf["balance"] = 0
    if not("operations" in inf):
        inf["operations"] = {}

    save_data(inf, path.path_json + "/" + str(object.id) + ".json")
    save_data(users, path.path_users)
    return users

def get_day_saldo(day_operations):
    summa = 0
    for operation in day_operations:
        summa += operation[1]
    return summa

def statistic_seven_day(bot, path, memory, id):
    try:
        values = []
        days = []
        
        user = load_data(path.path_json + "/" + str(id) + ".json")
        users = load_data(path.path_users)
        profile = users[str(id)]

        now = datetime.datetime.now(tz=memory.timezone)  

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

        bot.send_message(id, text=message, reply_markup=memory.keyboards["keyboard_main"], parse_mode='markdown')
    
        log(f"Operation 'statistic_seven_day', user: {id} completed successfully!")

    except:

        log(f"Operation 'statistic_seven_day', user: {id} was not executed!")


def main_menu(bot, path, memory, id):
    #texts = "Главное меню: "

    users = load_data(path.path_users)
    user = load_data(path.path_json + "/" + str(id) + ".json")

    now = datetime.datetime.now(tz=memory.timezone)  
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
    
    bot.send_message(id, text=message_, reply_markup=memory.keyboards["keyboard_main"], parse_mode='markdown')
    pass

def settings(bot, path, memory, id):

    users = load_data(path.path_users)

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
    
    bot.send_message(id, text=texts, reply_markup=memory.keyboards["keyboard_setting"], parse_mode='markdown')
