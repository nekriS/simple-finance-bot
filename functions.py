
from data import load_data, save_data
import calendar
import numpy as np
from telebot import types
import datetime
import csv
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
    time = now.strftime("%H:%M:%S")

    if not(nowf in information["operations"]):
        information["operations"][nowf] = []


    # cat_str = "None"

    # try:
    #     if num < 0:
    #         cat_str = information["categories"]["expenses"][cat]
    #     elif num > 0:
    #         cat_str = information["categories"]["income"][cat]
    #     else:
    #         pass
    # except:
    #     log(f"Couldn't get the category! id: {id}, cat_id: {cat}")
    #     pass
    
    information["operations"][nowf].append([num, cat, time])

    save_data(information, path.path_json + "/" + str(id) + ".json")

    log(f"Operation was added: {num}, id: {id}, cat_id: {cat}")

    pass

def create_profile(path, object):
    #загружаем бд с данными пользователей
    users = load_data(path.path_users)
    result = True

    if not(str(object.id) in users):
        users[str(object.id)] = {}
        users[str(object.id)]["id"] = object.id
        users[str(object.id)]["first_name"] = object.first_name
        users[str(object.id)]["last_name"] = object.last_name
        users[str(object.id)]["username"] = object.username
        users[str(object.id)]["is_premium"] = bool(object.is_premium)
    else:
        result = False

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
    #if not("balance" in inf):
    #    inf["balance"] = 0
    if not("bills" in inf):
        bills = {}
        bills["main"] = 0
        inf["bills"] = bills    
    if not("operations" in inf):
        inf["operations"] = {}

    save_data(inf, path.path_json + "/" + str(object.id) + ".json")
    save_data(users, path.path_users)

    return result

def get_day_saldo(day_operations):
    summa = 0
    for operation in day_operations:
        summa += operation[0]
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

{days[6]} {("🟢" if values[6] > 0 else "🔴") * int(abs(values[6]) // part)} {"+" if values[6] > 0 else ""}{values[6]}{profile["currecy"]}
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

def get_bills(path, id):
    information = load_data(path.path_json + "/" + str(id) + ".json")
    bills = information["bills"]

    message = ""
    for bill, value in bills.items():
        message += f"""
{bill.replace("main", "Платежный")} : {value}
"""
    return message

def main_menu(bot, path, memory, id):
    #texts = "Главное меню: "

    users = load_data(path.path_users)
    user = load_data(path.path_json + "/" + str(id) + ".json")

    now = datetime.datetime.now(tz=memory.timezone)  
    nowf = now.strftime("%d.%m.%Y")

    balance = round((user["balance"]),2)

    sum = 0.0
    if nowf in user["operations"]:
        for el in user["operations"][nowf]:
            sum += float(el[0])
    sald = round(sum,2)

    minn = 0.0
    if nowf in user["operations"]:
        for el in user["operations"][nowf]:
            if el[0] < 0:
                minn += float(el[0])
    

    daily_count = float(users[str(id)]["days_limit"]) 
    ost = round(daily_count + minn,2)


    if users[str(id)]["days"] == 'week':
        dayss = 7
        #print(now.weekday())
        dn = str(dayss - int(now.weekday()))
    else:
        dayss = calendar.monthrange(2021, int(now.strftime("%m")))[1]
        dn = str(dayss+1 - int(now.strftime("%d")))

    
    mn = round(float(balance)-((int(dn))*daily_count),2)


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

    message_ = f"""
📆 Дневная сводка
*{nowf}*

{ind1} Сальдо: *{sald}*₽
{ind2} Дневной остаток: *{ost}*₽

До конца периода: *{dn}* дней(я)

{ind3} Баланс: *{balance}*₽
{ind4} Свободных средств: *{mn}*₽
{ind5} Статус: {sta}.
    """
    
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

import time

def get_category(user, operation):
    try:
        if operation[0] > 0:
            return user["categories"]["income"][operation[1]]
        elif operation[0] < 0:
            return user["categories"]["expenses"][operation[1]]
    except:
        log("ERROR with category!")
    
    return ""

def get_time(operation):
    if len(operation) > 2:
        return operation[2]
    else:
        return 0



def get_csv_month(bot, path, memory, id):

    bot.send_message(id, text="Формируем файл CSV...")

    table = [["date", "operation", "category"]]
    user = load_data(path.path_json + "/" + str(id) + ".json")

    now = datetime.datetime.now(tz=memory.timezone)  

    for day in range (0, 30):
        date = now - datetime.timedelta(days=day)
        date_formate = date.strftime("%d.%m.%Y")
        
        if date_formate in user["operations"]:
            for operation in user["operations"][date_formate]:

                #table.append([date.strftime("%d.%m.%Y") , round(get_day_saldo(user["operations"][date_formate]), 2)])
                table.append([date.strftime("%d.%m.%Y") , get_time(operation) , round(operation[0]), get_category(user, operation) ])  

    print(table)
    with open(f'data/month_{now.strftime("%d%m")}_{id}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(table)
    
    time.sleep(5)

    bot.send_document(id, document=open(f'data/month_{now.strftime("%d%m")}_{id}.csv', 'rb'), caption="✅️ Файл сформирован!")

    os.remove(f'data/month_{now.strftime("%d%m")}_{id}.csv')
    
    main_menu(bot, path, memory, id)

    
