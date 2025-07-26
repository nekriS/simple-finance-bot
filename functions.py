import datetime
import system as st
import numpy as np
import inspect
import calendar
from telebot import types
import time
import csv

DEFAULT_USER = {
    "properties": {
        "id": "#id",
        "first_name": "#first_name",
        "last_name": "#last_name",
        "username": "#username",
        "is_premium": "#is_premium",
        "is_pay": False,
        "days": "month",
        "days_limit": 650,
        "currecy": "\u20bd",
        "timezone": 3 
    },
    "categories": {
        "expenses": [
            "🔄 Перевод себе",
			"💸 Переводы людям",
			"🔌 ЖКХ, связь, интернет",
			"🛒 Супермаркеты",
			"📦 Маркетплейсы",
			"💊 Медицина",
			"🚇 Транспорт",
			"🍽️ Кафе, рестораны",
			"🧩 Прочее"
		],
		"income": [
            "🔄 Перевод себе",
			"👔 Зарплата",
			"📈 Капитализация",
			"🎁 Переводы от людей",
			"🔁 Возврат",
			"🧩 Прочее"
		]
    },
    "bills": {
        "main": ["Основной", 0, "💵"]
    },
    "operations": {}
}

def get_category(user, operation):
    try:
        if operation[0] > 0:
            return user["categories"]["income"][operation[1]]
        elif operation[0] < 0:
            return user["categories"]["expenses"][operation[1]]
    except:
        st.log("ERROR with category!")
    
    return ""

def get_csv_month(id):

    table = [["operation", "category", "time", "from", "to", "date"]]
    user = st.load_data(f"data/{id}.json")

    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=int(user["properties"]["timezone"]))))   

    for day in range (0, 30):
        date = now - datetime.timedelta(days=day)
        date_formate = date.strftime("%d.%m.%Y")
        
        if date_formate in user["operations"]:
            for operation in user["operations"][date_formate]:
                operation[1] = get_category(user, operation)
                operation.append(date_formate)
                table.append(operation)


    with open(f'data/month_{now.strftime("%d%m")}_{id}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(table)
    
    time.sleep(5)
    reply_message = "✅️ Файл сформирован!"

    return reply_message, f'data/month_{now.strftime("%d%m")}_{id}.csv'

def get_all_balance(bills):
    balance = 0
    for bill, value in bills.items():
        balance += value[1]
    return balance


def get_bill_list(id):
    user = st.load_data(f"data/{id}.json")
    bills = user["bills"]

    bills_list = ""
    for bill, value in bills.items():
        bills_list += f"""
{value[2]} {value[0]} : {round(value[1], 2)}{user["properties"]["currecy"]}"""
    reply_message = f"""*Список счетов:*
{bills_list}

Общий баланс: *{get_all_balance(bills)}*{user["properties"]["currecy"]}
"""
    return reply_message

def add_operation(id, value, category, bill=-1):

    user = st.load_data(f"data/{id}.json")
    
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=int(user["properties"]["timezone"]))))  
    nowf = now.strftime("%d.%m.%Y")
    time = now.strftime("%H:%M:%S")
    type_operation = 0

    # 0 - no operation
    # 1 - earnings
    # 2 - expenses
    # 3 - transfer

    if not(nowf in user["operations"]):
        user["operations"][nowf] = []
    
    if bill == -1:
        user["bills"]["main"][1] = user["bills"]["main"][1] + value
        if value > 0:
            bill_to = "main"
            bill_from = ""
            type_operation = 1
            user["operations"][nowf].append([time, type_operation, value, category, bill_from, bill_to])
            cat_str = user["categories"]["income"][category]
        else:
            bill_to = ""
            bill_from = "main"
            type_operation = 2
            user["operations"][nowf].append([time, type_operation, value, category, bill_from, bill_to])
            cat_str = user["categories"]["expenses"][category]
    else:
        user["bills"]["main"][1] = user["bills"]["main"][1] + value
        bills_ = list(user["bills"].keys())
        user["bills"][bills_[bill]][1] = user["bills"][bills_[bill]][1] - value
        if value > 0:
            bill_to = "main"
            bill_from = bills_[bill]
            type_operation = 3
            user["operations"][nowf].append([time, type_operation, value, category, bill_from, bill_to])
            cat_str = user["categories"]["income"][category]
        else:
            bill_to = bills_[bill]
            bill_from = "main"
            type_operation = 3
            user["operations"][nowf].append([time, type_operation, value, category, bill_from, bill_to])
            cat_str = user["categories"]["expenses"][category]

    st.save_data(user, f"data/{id}.json")
    st.log(f"Operation was added: {value}, id: {id}, cat_id: {category}")

    reply_message = f"""✅️ Операция успешно добавлена!
Категория: {cat_str}
Остаток: {user["bills"]["main"][1]}{user["properties"]["currecy"]}
"""
    return reply_message

def get_buttons_with_bills(id):

    keyboard_bills = types.InlineKeyboardMarkup()
    user = st.load_data(f"data/{id}.json")
    bills = user["bills"]
    i = 0
    for bill in bills.keys():
        name_bill = bills[bill][0]
        value_bill = bills[bill][1]
        icon_bill = bills[bill][2]
        bill_button = types.InlineKeyboardButton(text=f"{icon_bill} {name_bill} ({value_bill}{user["properties"]["currecy"]})", callback_data="bill_"+str(i));
        keyboard_bills.add(bill_button)
        i += 1

    return keyboard_bills

def get_buttons_with_categories(id, operation):
    keyboard_cat = types.InlineKeyboardMarkup()
    user = st.load_data(f"data/{id}.json")

    i = 0
    cat_0 = types.InlineKeyboardButton(text="def", callback_data="def");
    
    if operation < 0:
        cats = user["categories"]["expenses"]
    elif operation > 0:
        cats = user["categories"]["income"]

    for cat in cats:
        cat_1 = cat_0
        cat_0 = types.InlineKeyboardButton(text=cat, callback_data="cat_"+str(i))
        if ((i + 1) % 2) == 0:
            keyboard_cat.row(cat_1, cat_0)
        elif (i + 1) == len(cats):
            keyboard_cat.add(cat_0)
        i += 1 

    return keyboard_cat

def get_day_saldo(day_operations):
    summa = 0
    for operation in day_operations:
        summa += operation[2]
    return summa

def get_day_status(id):
    try:

        user = st.load_data(f"data/{id}.json")
        profile = user["properties"]
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=int(user["properties"]["timezone"]))))  
        nowf = now.strftime("%d.%m.%Y")

        balance = round((user["bills"]["main"][1]), 2)

        sum = 0.0
        if nowf in user["operations"]:
            for el in user["operations"][nowf]:
                sum += float(el[2])
        sald = round(sum,2)

        minn = 0.0
        if nowf in user["operations"]:
            for el in user["operations"][nowf]:
                if (el[2] < 0) and (el[1] < 3):
                    minn += float(el[2])
        

        daily_count = float(profile["days_limit"]) 
        ost = round(daily_count + minn,2)


        if profile["days"] == 'week':
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
            ind5 = '🟢'
        else:
            sta = 'дефицит'
            ind5 = '🔴'

        reply_message = f"""
📆 Дневная сводка
*{nowf}*

{ind1} Сальдо: *{sald}*₽
{ind2} Дневной остаток: *{ost}*₽

До конца периода: *{dn}* дней(я)

{ind3} Баланс: *{balance}*₽
{ind4} Свободных средств: *{mn}*₽
{ind5} Статус: {sta}.
    """

        st.log(f"Operation '{inspect.currentframe().f_code.co_name}', user: {id} completed successfully!")
        return reply_message
    except:
        st.log(f"Operation '{inspect.currentframe().f_code.co_name}', user: {id} was not executed!")
        return "❌ Ошибка"

def get_statistic_seven_day(id):
    try:
        values = []
        days = []
        
        user = st.load_data(f"data/{id}.json")
        profile = user["properties"]
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=int(user["properties"]["timezone"]))))  

        for day in range(0, 7):
            date = now - datetime.timedelta(days=day)
            date_formate = date.strftime("%d.%m.%Y")

            days.append(date.strftime("%d.%m"))
            
            if date_formate in user["operations"]:
                values.append(round(get_day_saldo(user["operations"][date_formate]), 2))    
            else:
                values.append(0)

        part = (np.max(values) - 0.01) / 7

        reply_message = f"""
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

        st.log(f"Operation '{inspect.currentframe().f_code.co_name}', user: {id} completed successfully!")
        return reply_message
    except:
        st.log(f"Operation '{inspect.currentframe().f_code.co_name}', user: {id} was not executed!")
        return "❌ Ошибка"

def get_start(object):
    try:
        user = st.load_data(f"data/{object.id}.json")

        for pole in DEFAULT_USER.keys():
            if not(pole in user):
                user[pole] = DEFAULT_USER[pole]

        for pole in DEFAULT_USER["properties"].keys():
            if not(pole in user["properties"]):
                user["properties"][pole] = DEFAULT_USER["properties"][pole]
        
        user["properties"]["id"] = object.id
        user["properties"]["first_name"] = object.first_name
        user["properties"]["last_name"] = object.last_name
        user["properties"]["username"] = object.username
        user["properties"]["is_premium"] = bool(object.is_premium)

        st.save_data(user, f"data/{object.id}.json")
        st.log(f"Profile was created! id: {object.id}")

        return "✅️ Ваш профиль был успешно создан!"
    except:
        st.log(f"Can't create profile! id: {object.id}")
        return "❌ Ошибка при создании профиля!"
    
def get_settings(id):

    user = st.load_data(f"data/{id}.json")

    days = user["properties"]["days"]
    limit = user["properties"]["days_limit"]
    currency = user["properties"]["currecy"]
    days = days.replace("month", "месяц").replace("week", "неделя")

    reply_message = f"""
⚙ *Настройки*

Расчетный период: *{days}*
Дневной лимит: *{limit}{currency}*
Валюта: *{currency}*

"""
    return reply_message
    
    

#getattr(person, attr_name)