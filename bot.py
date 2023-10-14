#!/usr/bin/python3
import mysql.connector
import datetime
import aiofiles
import asyncio
import bd, RFID, admin_bot, threading, time
from threading import Thread
from multiprocessing import Process, Queue
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, TypeHandler, CommandHandler, Filters
from telegram_bot_pagination import InlineKeyboardPaginator
from urllib3.contrib.socks import SOCKSProxyManager

import logging

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a", format="%(asctime)s %(levelname)s %(message)s")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")

logger = logging.getLogger(__name__)

NAME, LAST_NAME, STUD_TYPE, BUTTON, WELCOME = range(5)
user_type_markup = ReplyKeyboardMarkup([['Студент', 'Преподаватель']], resize_keyboard=True)

# def check(context: CallbackContext):
#     print(admin_bot.usrQ)
#     if len(admin_bot.usrQ) != 0:
#         for i in admin_bot.usrQ:
#             context.bot.send_message(chat_id=593344137, text="Получено подтверждение от преподавателя, теперь вы можете войти в кабинет по своему пропуску!")
#         admin_bot.usqQ.clear()
#     else:
#         context.bot.send_message(chat_id=593344137, text="catch")

def get_lesson():
    with open("lesson.txt", "r") as file:
        lesson = file.read()
    return lesson

def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="А?")

def error_handler(update: Update, context: CallbackContext) -> None:
    global updater
    for i in range(2):
        try:
            context.bot.send_message(chat_id=593344137, text="error")
        except:
            updater = None
            updater = Updater("6040908427:AAG5SU0Trmc_RLzFBWFzvlmk8NPlYUsHke8")
            logger.error(msg="Trying to resolve exception", exc_info=context.error)
            continue
        break

def lesson(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(bd.select_message())

def cancel(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('До встречи, авиатор!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def cancel_main(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Попробуйте написать команду /start', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def feedback(update: Update, context: CallbackContext) -> None:
    context.bot.send_contact(chat_id=update.effective_chat.id, phone_number='+7 905 420-02-16', first_name='Алексей', last_name='Рычагов')

def start(update, context: CallbackContext) -> int:
    user = update.effective_user.to_dict()
    bd.insert_tg_user(user.get('id'), update.effective_chat.id, user.get('first_name'), user.get('last_name'), user.get('username'))

    start_text="Привет! Давай знакомиться. Кто ты?\n\n/start, чтобы начать заново.\n/cancel, чтобы выйти из настройки.\n/feedback, написать админу(сначала /cancel, чтобы выйти из настроек)."
    context.bot.send_message(chat_id=update.effective_chat.id, text = start_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи имя:', reply_markup=ForceReply())

    return NAME

def last_name(update: Update, context: CallbackContext) -> int:
    first_name = str(update.message.text)
    if (first_name.isalpha() == True) and (len(first_name) <= 48):
        result = bd.insert_name(update.effective_chat.id, first_name)
        if result == 'Запись успешно вставлена в таблицу пользователей':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введи фамилию:', reply_markup=ForceReply())
            return LAST_NAME
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='\nКажется что-то пошло не так, попробуй перезапустить бота командой /start и проверить данные!')
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, ограничьтесь алфавитными символами')
        return NAME

def stud_type(update: Update, context: CallbackContext) -> int:
    last_name = str(update.message.text)

    if (last_name.isalpha() == True) and (len(last_name) <= 48):
        result = bd.insert_last_name(update.effective_chat.id, last_name)
        if result == 'Запись успешно вставлена в таблицу пользователей':

            keyboard = [
                [
                    InlineKeyboardButton("Студент", callback_data='Студент'),
                    InlineKeyboardButton("Пром.дизайнер", callback_data='Пром.дизайнер'),
                ],
                [InlineKeyboardButton("Авиамоделист", callback_data='Авиамоделист')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)

            return STUD_TYPE
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='\nКажется что-то пошло не так, попробуй перезапустить бота командой /start и проверить данные!')
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, ограничься алфавитными символами')
        return LAST_NAME

def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    variant = query.data

    query.answer()

    query.edit_message_text(text=f"Выбранный вариант: {variant}")
    bd.insert_stud_type(update.effective_chat.id, variant)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Введи номер академической группы:', reply_markup=ForceReply())
    return WELCOME

def group(update: Update, context: CallbackContext) -> int:
    last_name = str(update.message.text)

    if (last_name.isalpha() == True) and (len(last_name) <= 48):
        result = bd.insert_last_name(update.effective_chat.id, last_name)
        if result == 'Запись успешно вставлена в таблицу пользователей':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введи номер академической группы:', reply_markup=ForceReply())
            return WELCOME
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='\nКажется что-то пошло не так, попробуй перезапустить бота командой /start и проверить данные!')
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, ограничься алфавитными символами', reply_markup=ForceReply())
        return LAST_NAME

def welcome(update: Update, context: CallbackContext) -> int:
    group = str(update.message.text)
    bd.insert_info(update.effective_chat.id, update.effective_chat.username, 'Обновил данные')
    if bd.ddos_check(update.effective_chat.id) <= 3:
        if len(group) <= 16:
            result = bd.insert_group(update.effective_chat.id, group)
            text = result + ", добро пожаловать в наш авиаклуб, чтобы получить доступ в мастерскую тебе необходимо прислонить свой пропуск к считывателю у двери кабинета Л829. Как будешь готов, напиши команду /key"
            update.message.reply_text(text)
            return WELCOME
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='\nГруппа введена некорректно, попробуй проверить данные и перезапустить бота командой /start')
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='\nПревышено число регистраций, попробуй снова через час.')
        return ConversationHandler.END
    
def key(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Приложите карту к считывателю")

    size = q.qsize()

    RFID.signal = True
    for i in range(12):
        if q.qsize() == size:
            RFID.action_key()
        else:
            time.sleep(1)
            break
    RFID.signal = False

    if q.qsize() == size:
        context.bot.send_message(chat_id=update.effective_chat.id, text="\nВы не поднесли карту, пожалуйста, пройдите регистрацистрацию заново и поднесите карту, после использования команды /key")
        return ConversationHandler.END
    else:
        card = q.get()
        while q.empty() != True:
            q.get()
        if bd.in_table(card) == True:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ключ уже зарегистрирован в системе")
            return ConversationHandler.END
        else:
            bd.insert_key(update.effective_chat.id, card)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ключ успешно записан: " + str(card))
            context.bot.send_message(chat_id=update.effective_chat.id, text="Осталось дождаться подтверждения от преподавателя.\nНапиши @eugerhan, если уже долго ждёшь подтверждения.")
            bd.insert_info(update.effective_chat.id, update.effective_chat.username, 'Привязал новый ключ')
            context.bot.send_message(chat_id=593344137, text="Новый пользователь ожидает подтверждения, перейдите в @Door_admin_bot")
            
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
                MessageHandler(Filters.text & ~(Filters.command), stud_type)
            ],
            STUD_TYPE: [
                CallbackQueryHandler(button, pattern='^' + 'Студент' + '$'),
                CallbackQueryHandler(button, pattern='^' + 'Пром.дизайнер' + '$'),
                CallbackQueryHandler(button, pattern='^' + 'Авиамоделист' + '$')
            ],
            BUTTON: [
                MessageHandler(Filters.text & ~(Filters.command), group),
            ],
            WELCOME: [
                MessageHandler(Filters.text & ~(Filters.command), welcome),
                CommandHandler('key', key)
            ]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
    )
    
    #updater.dispatcher.add_error_handler(error_handler)
    updater.dispatcher.add_handler(conv_handler)

    updater.dispatcher.add_handler(CommandHandler('feedback', feedback))
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel_main))
    updater.dispatcher.add_handler(CommandHandler('lesson', lesson))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~(Filters.command), echo))
    # jq = updater.job_queue
    # jq.run_repeating(check, interval=5)

    updater.start_polling()

    print('Started')

    updater.idle()


if __name__ == "__main__":
    global q, lesson_content
    lesson_content = get_lesson()
    q = Queue()
    button_tred = Thread(name='button', target=RFID.push_button, daemon=True)
    blink_tred = Thread(name='blink', target=RFID.action_blink, daemon=True)
    door_tred = Thread(name='door', target=RFID.door, args=(q,))
    admin_tred = Process(name='admin', target=admin_bot.main)
    admin_tred.start()
    door_tred.start()
    button_tred.start()
    blink_tred.start()
    main()