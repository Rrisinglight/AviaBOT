import bd, mysql.connector
from mysql.connector import Error
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from telegram.ext import Updater, CallbackContext, ConversationHandler, MessageHandler, TypeHandler, CommandHandler, Filters
from telegram_bot_pagination import InlineKeyboardPaginator
import rdm6300


TYPE, NAME, WELCOME = range(3)
type_now = int
user_type_markup = ReplyKeyboardMarkup([['Студент', 'Преподаватель']], resize_keyboard=True)
user_data = []

def user_info(text, type_now):
    if type_now == 1:
        user_data.append(text.split())
    else:
        user_data.append(text)

def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="А?")

def feedback(update: Update, context: CallbackContext) -> None:
    context.bot.send_contact(chat_id = 593344137, phone_number = '+7 905 420 0216', first_name = 'Алексей', last_name = 'Рычагов')

def key(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.to_dict()

    # reader = rdm6300.Reader('/dev/ttyS0')
    # context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, приложите пропуск")
    # while True:
    #     card = reader.read()
    #     if card:
    #         print(f"[{card.value}] считывающая карта {card}")
    #         break
    card = 4534
    bd.insert_key(user['id'], card)


def start(update, context: CallbackContext) -> int:
    text="Давай знакомиться. Кто ты?\n\n/start, чтобы начать заново.\n/cancel, чтобы выйти.\n/feedback, написать админу(сначала /cancel, чтобы выйти из настройки)."
    update.message.reply_text(text, reply_markup=user_type_markup)

    return TYPE

def stud(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи имя и фамилию', reply_markup=ForceReply())

    return NAME

def prep(update: Update, context: CallbackContext) -> int:
    erchan = ReplyKeyboardMarkup([['Вставай, на работу пора']], resize_keyboard=True, one_time_keyboard=True)
    user = update.effective_user.to_dict()
    print(user)
    if user['username'] == 'eugerhan':
        print('Добро пожаловать!')
        
        return ConversationHandler.END
    else:
        update.message.reply_text('Ерхан это ты?', reply_markup=erchan)
        return TYPE

def group(update: Update, context: CallbackContext) -> int:

    user_info(update.message.text, NAME)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи номер академической группы', reply_markup=ForceReply())

    return WELCOME

def welcome(update: Update, context: CallbackContext) -> int:

    user_info(update.message.text, WELCOME)
    user = update.effective_user.to_dict()

    result = bd.insert_varibles_into_table(user['id'], user_data[0][0], user_data[0][1], user_data[1])

    if result == 'Запись успешно вставлена в таблицу пользователей':
        text = str(user_data[0][0]) + ", добро пожаловать в наш авиаклуб, чтобы получить доступ в мастерскую тебе необходимо прислонить свой пропуск к считывателю у двери кабинета Л829. Как будешь готов, напиши команду /key"
        update.message.reply_text(text)
        return WELCOME
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=result+'\n Проверьте данные!')
        return ConversationHandler.END

def select(update: Update, context: CallbackContext) -> None:
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')

        sql_select_Query = "select * from users"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        # get all records
        records = cursor.fetchall()
        context.bot.send_message(chat_id = update.effective_chat.id, text = 'Общее количество строк в таблице: ' + str(cursor.rowcount))

        for row in records:
            text = "tg_id = " + str(row[0]) + '\n' + "first_name = " + str(row[1]) + '\n' + "last_name = " + str(row[2]) + '\n' + "academ_group = " + str(row[3]) + '\n' + "RFID = " + str(row[4])
            context.bot.send_message(chat_id=update.effective_chat.id, text = text)

    except mysql.connector.Error as e:
        print("Ошибка при чтении данных из таблицы MySQL", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Соединение с MySQL закрыто")

def cancel(update: Update, context: CallbackContext) -> None:

    update.message.reply_text('До встречи, авиатор!', reply_markup=ReplyKeyboardRemove())
    print(user_data)

    return ConversationHandler.END

def main() -> None:

    updater = Updater("5838936536:AAHWgfvpzUMWoUzsP37X2xZNrDSvlWxbizc")

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states = {
            TYPE: [
                MessageHandler(Filters.text(['Вставай, на работу пора']), stud),
                MessageHandler(Filters.text(['Студент']), stud),
                MessageHandler(Filters.text(['Преподаватель']), prep),
            ],
            NAME: [
                MessageHandler(Filters.text & ~(Filters.command), group),
            ],
            WELCOME: [
                MessageHandler(Filters.text & ~(Filters.command), welcome),
            ]
            
        },
        fallbacks = [CommandHandler('cancel', cancel)],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('feedback', feedback))
    updater.dispatcher.add_handler(CommandHandler('select', select))
    updater.dispatcher.add_handler(CommandHandler('key', key))

    updater.start_polling()

    print('Started')

    updater.idle()


if __name__ == "__main__":
    main()