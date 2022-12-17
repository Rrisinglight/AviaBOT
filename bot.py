import bd, RFID, mysql.connector
from mysql.connector import Error
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, TypeHandler, CommandHandler, Filters
from telegram_bot_pagination import InlineKeyboardPaginator

TYPE, NAME, LAST_NAME, WELCOME, PREP = range(5)
type_now = int
user_type_markup = ReplyKeyboardMarkup([['Студент', 'Преподаватель']], resize_keyboard=True)
user_data = []

def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="А?")

def cancel(update: Update, context: CallbackContext) -> None:

    update.message.reply_text('До встречи, авиатор!', reply_markup=ReplyKeyboardRemove())
    print(user_data)

    return ConversationHandler.END

def feedback(update: Update, context: CallbackContext) -> None:
    context.bot.send_contact(chat_id = 593344137, phone_number = '+7 905 420 0216', first_name = 'Алексей', last_name = 'Рычагов')

def start(update, context: CallbackContext) -> int:
    global user
    user = update.effective_user.to_dict()
    bd.insert_tg_user(user['id'], user['first_name'], user['last_name'], user['username'])

    text="Давай знакомиться. Кто ты?\n\n/start, чтобы начать заново.\n/cancel, чтобы выйти.\n/feedback, написать админу(сначала /cancel, чтобы выйти из настройки)."
    update.message.reply_text(text, reply_markup=user_type_markup)

    return TYPE


def prep(update: Update, context: CallbackContext) -> int:
    erchan = ReplyKeyboardMarkup([['Вставай, на работу пора']], resize_keyboard=True, one_time_keyboard=True)

    if user['username'] == 'risinglight':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать!\n\n/select, чтобы посмотреть список студентов\n/approve, чтобы дать доступ к мастерской\n/reject, отобрать доступ")
        return PREP
    else:
        update.message.reply_text('Ерхан это ты?', reply_markup=erchan)
        return TYPE

def catch_user(update: Update, context: CallbackContext):
    query = update.callback_query
    page = str(query.data)
    page = int(page[12:])

    username = user_pages[page-1]
    username = username[username.find("@")+1:username.rfind("*")]

    context.bot.send_message(chat_id=update.effective_chat.id, text=str(bd.approve(username, 1)))

def dump(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ещё не готово")

#заменить на пагинацию
def select(update, context):
    
    global user_pages
    user_pages = []

    records = bd.select()
    context.bot.send_message(chat_id = update.effective_chat.id, text = 'Количество студентов, ожидающих подтверждения: ' + str(records[1]))

    for row in records[0]:
        user_pages.append(f"*@{row[1]}*" + '\n' + str(row[2]) + " " + str(row[3]) + '\n' + "Группа = " + str(row[4]) + '\n' "Подтверждён: " + str(bool(row[5])))

    paginator = InlineKeyboardPaginator(
        len(user_pages),
        data_pattern='character#{page}'
    )

    update.message.reply_text(
        text=user_pages[0],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )

def characters_page_callback(update, context):
    
    query = update.callback_query
    variant = query.data
    query.answer()

    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        len(user_pages),
        current_page=page,
        data_pattern='character#{page}'
    )

    paginator.add_after(InlineKeyboardButton('Дать доступ', callback_data='Дать доступ#{}'.format(page)))

    query.edit_message_text(
        text=user_pages[page - 1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


def stud(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи имя', reply_markup=ForceReply())
    
    return NAME

def last_name(update: Update, context: CallbackContext) -> int:
    
    user_data.append(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи фамилию', reply_markup=ForceReply())

    return LAST_NAME

def group(update: Update, context: CallbackContext) -> int:

    user_data.append(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи номер академической группы', reply_markup=ForceReply())

    return WELCOME

def welcome(update: Update, context: CallbackContext) -> int:

    user_data.append(update.message.text)

    result = bd.insert_varibles_into_table(user['id'], user_data[0], user_data[1], user_data[2])

    if result == 'Запись успешно вставлена в таблицу пользователей':
        text = str(user_data[0]) + ", добро пожаловать в наш авиаклуб, чтобы получить доступ в мастерскую тебе необходимо прислонить свой пропуск к считывателю у двери кабинета Л829. Как будешь готов, напиши команду /key"
        update.message.reply_text(text)
        return WELCOME
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=result+'\nКажется что-то пошло не так, попробуй перезапустить бота командой /start и проверить данные!')
        return ConversationHandler.END


def key(update: Update, context: CallbackContext) -> None:
    bd.kostyl(loop_status=0)
    card = int(RFID.new_card())
    
    if bd.in_table(card) == True:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ключ уже зарегистрирован в системе")
    else:
        bd.insert_key(user['id'], card)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ключ успешно записан" + str(card))
    bd.kostyl(loop_status=1)
    RFID.polling()


def main() -> None:

    updater = Updater("5838936536:AAHWgfvpzUMWoUzsP37X2xZNrDSvlWxbizc")

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states = {
            TYPE: [
                MessageHandler(Filters.text(['Студент']), stud),
                MessageHandler(Filters.text(['Вставай, на работу пора']), stud),
                MessageHandler(Filters.text(['Преподаватель']), prep),
                MessageHandler(Filters.text & ~(Filters.command), echo)
            ],
            NAME: [
                MessageHandler(Filters.text & ~(Filters.command), last_name),
            ],
            LAST_NAME: [
                MessageHandler(Filters.text & ~(Filters.command), group),
            ],
            WELCOME: [
                MessageHandler(Filters.text & ~(Filters.command), welcome),
            ],
            PREP: [
                CommandHandler('select', select),
                CommandHandler('dump', dump),
                MessageHandler(Filters.text & ~(Filters.command), echo)
            ]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
    )
    
    updater.dispatcher.add_handler(CallbackQueryHandler(characters_page_callback, pattern='^character#'))
    updater.dispatcher.add_handler(CallbackQueryHandler(catch_user, pattern='^Дать доступ#'))
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('feedback', feedback))
    updater.dispatcher.add_handler(CommandHandler('key', key))


    updater.start_polling()

    print('Started')

    updater.idle()


if __name__ == "__main__":
    main()