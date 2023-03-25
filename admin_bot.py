import bd
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, TypeHandler, CommandHandler, Filters
from telegram_bot_pagination import InlineKeyboardPaginator

user_data = []
user_type_markup = ReplyKeyboardMarkup([['Список подтверждённых студентов'], ['Список студентов ожидающих подтверждения']], resize_keyboard=True)

def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="А?")

def prohibit(update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Нет доступа")

def start(update, context: CallbackContext) -> int:
    text="Добро пожаловать!\n\n/message, чтобы разослать всем студентам сообщение\n/dump скачать дамп базы данных"
    update.message.reply_text(text, reply_markup=user_type_markup)

def dump(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ждите в ближайшем обновлении")

def message(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ждите в ближайшем обновлении")

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
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(bd.approve(username, 0)))

def select(update, context):
    
    global user_pages
    user_pages = []

    if update['message']['text'] == 'Список подтверждённых студентов':
        records = bd.select(1)
    else:
        records = bd.select(0)

    context.bot.send_message(chat_id = update.effective_chat.id, text = 'Количество студентов в списке: ' + str(records[1]))

    for row in records[0]:
        user_pages.append(f"*@{row[1]}*" + '\n' + str(row[2]) + " " + str(row[3]) + '\n' + "Группа = " + str(row[4]) + '\n' "Статус: " + str(bool(row[5])))
    
    paginator = InlineKeyboardPaginator(
        len(user_pages),
        data_pattern='character#{page}'
    )

    paginator.add_after(InlineKeyboardButton('Дать доступ', callback_data='Дать доступ#{}'))
    paginator.add_after(InlineKeyboardButton('Забрать доступ', callback_data='Забрать доступ#{}'))
    try:
        update.message.reply_text(
            text=user_pages[0],
            reply_markup=paginator.markup,
            parse_mode='Markdown'
        )
    except IndexError:
        next


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
    paginator.add_after(InlineKeyboardButton('Забрать доступ', callback_data='Забрать доступ#{}'.format(page)))

    query.edit_message_text(
        text=user_pages[page - 1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )

    

def main() -> None:

    updater = Updater("5904027140:AAFQpjwABvsmMjwQjX9rP7XUB8z4QtxgbsE")

    updater.dispatcher.add_handler(MessageHandler(~Filters.chat(username="@risinglight") & Filters.chat_type.private, prohibit))
    updater.dispatcher.add_handler(CommandHandler('start', start))

    updater.dispatcher.add_handler(MessageHandler(Filters.text(['Список студентов ожидающих подтверждения']), select))
    updater.dispatcher.add_handler(MessageHandler(Filters.text(['Список подтверждённых студентов']), select))
    updater.dispatcher.add_handler(CallbackQueryHandler(characters_page_callback, pattern='^character#'))
    updater.dispatcher.add_handler(CallbackQueryHandler(catch_user, pattern='^Дать доступ#'))
    updater.dispatcher.add_handler(CallbackQueryHandler(catch_user, pattern='^Забрать доступ#'))

    updater.dispatcher.add_handler(CommandHandler('message', message))
    updater.dispatcher.add_handler(CommandHandler('dump', dump))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~(Filters.command), echo))

    updater.start_polling()

    print('Started')

    updater.idle()


if __name__ == "__main__":
    main()