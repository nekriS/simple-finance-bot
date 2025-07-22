from telebot import types

class keyboards:
    def __init__(self, 
                 keyboards=dict()):
        for keyboard in keyboards.keys():
            board = types.InlineKeyboardMarkup()
            for button in keyboards[keyboard]:
                if button[0]:
                    if len(button) <= 3:
                        key_button = types.InlineKeyboardButton(text=button[1], callback_data=button[2])
                        board.add(key_button)
                    else:
                        key_button1 = types.InlineKeyboardButton(text=button[1], callback_data=button[2])
                        key_button2 = types.InlineKeyboardButton(text=button[3], callback_data=button[4])
                        board.row(key_button1, key_button2)
            setattr(self, keyboard, board)
            