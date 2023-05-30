import bd, RFID, admin_bot, mysql.connector, threading, time
from threading import Thread
from multiprocessing import Process, Queue
from mysql.connector import Error
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, TypeHandler, CommandHandler, Filters
from telegram_bot_pagination import InlineKeyboardPaginator

import logging

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")


NAME, LAST_NAME, WELCOME = range(3)
type_now = int
user_type_markup = ReplyKeyboardMarkup([['Студент', 'Преподаватель']], resize_keyboard=True)
user_data = []

def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="А?")

def cancel(update: Update, context: CallbackContext) -> None:

    update.message.reply_text('До встречи, авиатор!', reply_markup=ReplyKeyboardRemove())
    print(user_data)

    return ConversationHandler.END

def cancel_main(update: Update, context: CallbackContext) -> None:

    update.message.reply_text('Попробуйте написать команду /start', reply_markup=ReplyKeyboardRemove())
    print(user_data)

    return ConversationHandler.END

def feedback(update: Update, context: CallbackContext) -> None:
    context.bot.send_contact(chat_id = 593344137, phone_number = '+7 905 420-02-16', first_name = 'Алексей', last_name = 'Рычагов')

def start(update, context: CallbackContext) -> int:
    global user
    user = update.effective_user.to_dict()

    bd.insert_tg_user(user.get('id'), update.effective_chat.id, user.get('first_name'), user.get('last_name'), user.get('username'))

    start_text="Привет! Давай знакомиться. Кто ты?\n\n/start, чтобы начать заново.\n/cancel, чтобы выйти.\n/feedback, написать админу(сначала /cancel, чтобы выйти из настроек)."
    context.bot.send_message(chat_id=update.effective_chat.id, text = start_text)
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
    context.bot.send_message(chat_id=update.effective_chat.id, text="Приложите карту к считывателю")

    size = q.qsize()
    RFID.action_key()

    if q.qsize() == size:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Вы не поднесли карту")
        return ConversationHandler.END
    else:
        card = q.get()
        if bd.in_table(card) == True:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ключ уже зарегистрирован в системе")
            return ConversationHandler.END
        else:
            bd.insert_key(user['id'], card)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ключ успешно записан: " + str(card))
            context.bot.send_message(chat_id=update.effective_chat.id, text="Осталось дождаться подтверждения от преподавателя.\nНапиши @eugerhan, чтобы он скорее дал тебе доступ в мастерскую")
            return ConversationHandler.END

def main() -> None:

    updater = Updater("5838936536:AAHWgfvpzUMWoUzsP37X2xZNrDSvlWxbizc")

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states = {
            NAME: [
                MessageHandler(Filters.text & ~(Filters.command), last_name),
            ],
            LAST_NAME: [
                MessageHandler(Filters.text & ~(Filters.command), group),
            ],
            WELCOME: [
                MessageHandler(Filters.text & ~(Filters.command), welcome),
                CommandHandler('key', key)
            ]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('feedback', feedback))
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel_main))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~(Filters.command), echo))

    updater.start_polling()

    print('Started')

    updater.idle()


if __name__ == "__main__":
    global q
    global door_tred, lock
    q = Queue()
    button_tred = Thread(name='button', target=RFID.push_button, daemon=True)
    door_tred = Thread(name='door', target=RFID.door, args=(q,), daemon=True)
    admin_tred = Process(name='admin', target=admin_bot.main)
    admin_tred.start()
    door_tred.start()
    button_tred.start()
    main()