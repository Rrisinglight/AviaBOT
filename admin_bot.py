#!/usr/bin/python3
import bd, RFID, aiofiles
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, TypeHandler, CommandHandler, Filters
from telegram_bot_pagination import InlineKeyboardPaginator

LESSON = 1

user_type_markup = ReplyKeyboardMarkup([['Список подтверждённых студентов'], ['Список студентов ожидающих подтверждения']], resize_keyboard=True)

def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="А?")

def prohibit(update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Нет доступа")

def start(update, context: CallbackContext) -> int:
    text="Добро пожаловать!\n\n/message, чтобы разослать всем студентам сообщение\n/dump, скачать дамп базы данных"
    update.message.reply_text(text, reply_markup=user_type_markup)

def dump(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ждите в ближайшем обновлении")

def open(update: Update, context: CallbackContext) -> None:
    RFID.door_open()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Дверь открыта")

def lesson_catch(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Назначьте время для занятия(просто сообщение): ", reply_markup=ForceReply())
    return LESSON

def lesson_assign(update: Update, context: CallbackContext) -> None:
    bd.insert_message(update.message.text)
    update.message.reply_text('Сообщение пользователям: ' + bd.select_message(), reply_markup=user_type_markup)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Занятие не назначено!', reply_markup=user_type_markup)
    bd.insert_message('Сообщение пользователям: Занятие проходит каждый четверг в 12:00! Если появятся какие-то изменения, вам придёт уведомление от бота.')
    return ConversationHandler.END

def catch_user(update: Update, context: CallbackContext):
    query = update.callback_query
    button = str(query.data.split('#')[0])
    try:
        page = int(query.data.split('#')[1])
    except ValueError:
        page = 0
    username = user_pages[page-1]
    username = username[username.find("@")+1:username.rfind("*")]

    if button == 'Дать доступ':
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(bd.approve(username, 1)))
        usrQ.append(update.effective_chat.id)
        print(usrQ)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(bd.approve(username, 0)))

def select_waiting(update: Update, context: CallbackContext):
    global user_pages
    user_pages = []

    records = bd.select(0)

    context.bot.send_message(chat_id = update.effective_chat.id, text = 'Количество студентов в списке: ' + str(records[1]))

    for row in records[0]:
        user_pages.append(f"*@{row[1]}*" + '\n' + str(row[2]) + " " + str(row[3]) + '\n' + "Группа = " + str(row[4]) + '\n' "Статус: " + str(bool(row[5])))
    
    paginator = InlineKeyboardPaginator(
        len(user_pages),
        data_pattern='await#{page}'
    )

    paginator.add_after(InlineKeyboardButton('Дать доступ', callback_data='Дать доступ#{}'))
    
    try:
        update.message.reply_text(
            text=user_pages[0],
            reply_markup=paginator.markup,
            parse_mode='Markdown'
        )
    except IndexError:
        next

def select_approved(update: Update, context: CallbackContext):
    global user_pages
    user_pages = []

    records = bd.select(1)

    context.bot.send_message(chat_id = update.effective_chat.id, text = 'Количество студентов в списке: ' + str(records[1]))

    for row in records[0]:
        user_pages.append(f"*@{row[1]}*" + '\n' + str(row[2]) + " " + str(row[3]) + '\n' + "Группа = " + str(row[4]) + '\n' "Статус: " + str(bool(row[5])))
    
    paginatorA = InlineKeyboardPaginator(
        len(user_pages),
        data_pattern='сonfirm#{page}'
    )

    paginatorA.add_after(InlineKeyboardButton('Забрать доступ', callback_data='Забрать доступ#{}'))

    try:
        update.message.reply_text(
            text=user_pages[0],
            reply_markup=paginatorA.markup,
            parse_mode='Markdown'
        )
    except IndexError:
        next

def approvedUsers_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    page = int(query.data.split('#')[1])

    paginatorA = InlineKeyboardPaginator(
        len(user_pages),
        current_page=page,
        data_pattern='сonfirm#{page}'
    )

    paginatorA.add_after(InlineKeyboardButton('Забрать доступ', callback_data='Забрать доступ#{}'.format(page)))

    query.edit_message_text(
        text=user_pages[page - 1],
        reply_markup=paginatorA.markup,
        parse_mode='Markdown'
    )

def waitingUsers_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        len(user_pages),
        current_page=page,
        data_pattern='await#{page}'
    )

    paginator.add_after(InlineKeyboardButton('Дать доступ', callback_data='Дать доступ#{}'.format(page)))

    query.edit_message_text(
        text=user_pages[page - 1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


def main() -> None:
    global usrQ
    usrQ = []

    lesson_handler = ConversationHandler(
        entry_points = [CommandHandler('lesson_assign', lesson_catch)],
        states = {
            LESSON: [
                MessageHandler(Filters.text & ~(Filters.command), lesson_assign),
            ]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
    )

    updater = Updater("6040908427:AAG5SU0Trmc_RLzFBWFzvlmk8NPlYUsHke8")

    updater.dispatcher.add_handler(MessageHandler(~Filters.chat(username="eugerhan") & ~Filters.chat(username="risinglight") & Filters.chat_type.private, prohibit))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('open', open))
    updater.dispatcher.add_handler(lesson_handler)
    
    updater.dispatcher.add_handler(MessageHandler(Filters.text(['Список студентов ожидающих подтверждения']), select_waiting))
    updater.dispatcher.add_handler(MessageHandler(Filters.text(['Список подтверждённых студентов']), select_approved))
    updater.dispatcher.add_handler(CallbackQueryHandler(waitingUsers_callback, pattern='^await#'))
    updater.dispatcher.add_handler(CallbackQueryHandler(approvedUsers_callback, pattern='^сonfirm#'))
    updater.dispatcher.add_handler(CallbackQueryHandler(catch_user, pattern='^Дать доступ#'))
    updater.dispatcher.add_handler(CallbackQueryHandler(catch_user, pattern='^Забрать доступ#'))

    #updater.dispatcher.add_handler(CommandHandler('message', message))

    updater.dispatcher.add_handler(CommandHandler('dump', dump))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~(Filters.command), echo))
    

    updater.start_polling()

    print('Started_admin')

    updater.idle()