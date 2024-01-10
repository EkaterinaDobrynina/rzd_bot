from telebot import types


commands = {
    'сreate': 'Создать карточку 💫',
    'info': 'Что это такое 🤷',
    'delete': 'Удалить мою анкету ❌',
}


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    сreate = types.KeyboardButton(text=commands['сreate'])
    info = types.KeyboardButton(text=commands['info'])
    delete = types.KeyboardButton(text=commands['delete'])
    keyboard.add(сreate)
    keyboard.add(info)
    keyboard.add(delete)
    return keyboard


def delete_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Yes", callback_data="yes_delete"),
        types.InlineKeyboardButton("No", callback_data="no_delete"))
    return markup


def show_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Анкета", callback_data="show_txt"),
        types.InlineKeyboardButton("Визитка", callback_data="show_jpg"))
    return markup


def markup_choices(choices):
    if not choices:
        return types.ReplyKeyboardRemove(selective=False)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for choice in choices:
        markup.add(types.KeyboardButton(choice))

    return markup