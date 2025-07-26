import time
import os
import sys
import system as st
import functions as fn
import warnings
import telebot
from login import keys
from objects import keyboards

warnings.filterwarnings('ignore')

HIERARCHY = {
    "data": {}
}

KEYBOARDS = {
    "keyboard_main": [
        [True, '📊 Дневная сводка', 'daily_summary'],
        [True, '📅 Статистика за 7 дней', 'statistic_seven'],
        [False, '📈 Месячная статистика', 'statistic_month'],
        [True, '🧾 Счета', 'bills'],
        [True, '📁 Экспорт данных', 'export'],
        [True, '⚙️ Настройки', 'settings', '❓ Помощь / FAQ', 'help']
    ],
    "keyboard_bill": [
        [False, '📄 Добавить счет', 'add_bill'],
        [False, '📄 Удалить счет', 'del_bill'],
        [False, '📄 Актуализация счетов', 'del_bill'],
        [True, '👈 Назад', 'back']
    ],
    "keyboard_setting": [
        [True, '📆 Изменить длину периода', 'len_period'],
        [True, '💵 Изменить дневной лимит', 'len_limit'],
        [True, '💣 Сбросить мои данные', 'clear', '👈 Назад', 'back_1']
    ],
    "keyboard_len": [
        [True, 'Неделя', 'week'],
        [True, 'Месяц', 'month'],
        [True, '👈 Назад', 'settings']
    ],
    "keyboard_export": [
        [True, '📄 Экспорт в CSV', 'csv'],
        [True, '👈 Назад', 'back']
    ]
}

print("Starting...")
st.create_hierarchy(HIERARCHY)
bot = telebot.TeleBot(keys().telegram)
keyboard = keyboards(KEYBOARDS)
cache = dict()

def please_delete_all_buttons(chat_id, message_id, k=1):
    for j in range(k,10):
        try:
            bot.edit_message_reply_markup(chat_id, message_id-j, reply_markup=None)
            break
        except:
            pass

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        operation = cache[str(call.from_user.id)]
    except: 
        operation = 0

    please_delete_all_buttons(call.message.chat.id, call.message.message_id, 0)

    match call.data:
        case "settings":
            reply_message = fn.get_settings(call.from_user.id)
            bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_setting, parse_mode='markdown')
        case "statistic_seven":
            reply_message = fn.get_statistic_seven_day(call.from_user.id)
            bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')    
        case "bills":
            reply_message = fn.get_bill_list(call.from_user.id)
            bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_bill, parse_mode='markdown')
        case "len_period":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❓️ Выберите длину расчетного периода:", reply_markup=keyboard.keyboard_len) 
        case "week":
            user = st.load_data(f"data/{call.from_user.id}.json")
            user["properties"]["days"] = "week"
            st.save_data(user, f"data/{call.from_user.id}.json")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: неделя", reply_markup=None)
            
            reply_message = fn.get_day_status(call.from_user.id)
            bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')
        case "month":
            user = st.load_data(f"data/{call.from_user.id}.json")
            user["properties"]["days"] = "month"
            st.save_data(user, f"data/{call.from_user.id}.json")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅️ Расчетный период изменен на: месяц", reply_markup=None)
            
            reply_message = fn.get_day_status(call.from_user.id)
            bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')
        case "export":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=keyboard.keyboard_export) 
        case "csv":
            bot.send_message(call.message.chat.id, text="Формируем файл CSV...")
            reply_message, file = fn.get_csv_month(call.from_user.id)
            bot.send_document(call.from_user.id, document=open(file, 'rb'), caption=reply_message)
            os.remove(file)

            reply_message = fn.get_day_status(call.from_user.id)
            bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')
        case _:
            if not(operation == 0):
                cat = call.data
                if "cat_" in cat:
                    if int(cat[-1]) == 0:
                        reply_message = 'Выберите счет: '
                        bot.send_message(call.message.chat.id, text=reply_message, reply_markup=fn.get_buttons_with_bills(call.from_user.id)) 
                    else:
                        reply_message = fn.add_operation(call.from_user.id, operation, int(cat[-1]))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=reply_message, reply_markup=None)
                        del cache[str(call.from_user.id)]
                        
                        reply_message = fn.get_day_status(call.from_user.id)
                        bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')
                if "bill_" in cat:
                    reply_message = fn.add_operation(call.from_user.id, operation, 0, int(cat[-1]))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=reply_message, reply_markup=None)
                    del cache[str(call.from_user.id)]                
                    
                    reply_message = fn.get_day_status(call.from_user.id)
                    bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')
            else:
                reply_message = fn.get_day_status(call.from_user.id)
                bot.send_message(call.message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')
        

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    
    line = message.text
    line = line.replace(' ', '')
    line = line.replace(',', '.')

    please_delete_all_buttons(message.chat.id, message.message_id, 0)

    if (message.text == "/help") or (message.text == "/start"):
        reply_message = fn.get_start(message.from_user)
        bot.send_message(message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main)
    elif line[1:].replace('.', '').isnumeric():
        operation = float(line)
        cache[str(message.from_user.id)] = operation
        reply_message = 'Выберите категорию: '
        bot.send_message(message.chat.id, text=reply_message, reply_markup=fn.get_buttons_with_categories(message.chat.id, operation))    
    else:
        reply_message = fn.get_day_status(message.from_user.id)
        bot.send_message(message.chat.id, text=reply_message, reply_markup=keyboard.keyboard_main, parse_mode='markdown')

def listening(bot):
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        st.log("Connection to the server was lost! Timeout: 10 seconds.")
        time.sleep(10)
        listening(bot)

def init():
    st.log("Hello...")
    listening(bot)

if __name__ == '__main__':
    sys.exit(init())