#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
from telegram.ext.dispatcher import run_async
import psycopg2
from functools import wraps
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, Filters

# conn = psycopg2.connect(dbname = 'daqpsemmol11kn', user = 'fnwjyuhqrjdbcv', password = '4ae63588868e2423ddb7cc3bd4e71ae5892179b86dca5a90272b747aa933bac9', host = 'ec2-46-137-75-170.eu-west-1.compute.amazonaws.com')
conn = psycopg2.connect(dbname = os.environ['dbname'], user = os.environ['user'], password = os.environ['password'], host = os.environ['host'])
cursor = conn.cursor()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot_id = os.environ['bot_id']
# bot_id = 1098805537
LIST_OF_ADMINS = [391206263, 79799667]


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@run_async
def adminctrl(update, context):
    for bot_id in context.bot.get_chat_administrators(update.message.chat_id):
        return True
    return False


def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


@run_async
def add_group(update, context):
    for member in update.message.new_chat_members:
        if bot_id in str(member.id):
            update.message.reply_text(f"""
Чтобы добавить свой чат в нашу базу данных, <u>выдайте</u> боту права:
<b>1)</b> Удалять сообщения.
<b>2)</b> Приглашать пользователей.

Далее, напишите:
/addchat news/discussion/flood/games, где:
<u>news</u> - обсуждение новостей и т.п.,
<u>discussion</u> - обсуждение по интересам,
<u>flood</u> - общение на любые темы,
<u>games</u> - игровые чаты.

Важно:
<b>1)</b> Указывать можно только одну категорию для одного чата.
<b>2)</b> Запрещено удалять бота, иначе ваш чат будет удалён из нашей базы.

Все новости, обновления и другую важную информацию мы публикуем здесь: @chattygram""", parse_mode='HTML')
        else:
            pass


@run_async
def getId(update, context):
    text = f'@chattygrambot {update.message.chat_id}'
    keyboard = [[InlineKeyboardButton("Поделиться чатом", url=f"tg://msg?text={text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try: 
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        context.bot.send_message(chat_id=update.message.from_user.id, text='Нажмите кнопку 👇 и поделитесь с друзьями.', reply_markup=reply_markup)
    except:
        try:
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            update.message.reply_text('Нажмите кнопку 👇 и поделитесь с друзьями.', reply_markup=reply_markup)
        except:
            update.message.reply_text('Нажмите кнопку 👇 и поделитесь с друзьями.', reply_markup=reply_markup)


@run_async
def inlinequery(update, context):
    """Handle the inline query."""
    cursor.execute('SELECT id FROM chats')
    all_chats = cursor.fetchall()
    chat_id = update.inline_query.query
    if not chat_id:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Этого чата нет в нашей базе.",
                input_message_content=InputTextMessageContent("Привет! Как дела?\nУ меня не получилось поделиться чатом :/"))]
    else:
        if str(chat_id) not in str(all_chats):\
            results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Этого чата нет в нашей базе.",
                input_message_content=InputTextMessageContent("Привет! Как дела?\nУ меня не получилось поделиться чатом :/"))]
        else:
            try:
                cursor.execute('SELECT link FROM chats WHERE id = %s', (chat_id,))
                link = cursor.fetchone()
                keyboard = [[InlineKeyboardButton("Присоединиться", url=link[0])]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="Поделиться чатом",
                        input_message_content=InputTextMessageContent("Вас пригласили в чат!"),
                        reply_markup=reply_markup)]
            except TypeError as error:
                return
            except:
                return

    update.inline_query.answer(results)


@restricted
def message(update, context):
    s = update.message.text
    f = open("chats.txt", "w")
    f.write("Мы опубликовали вашу рассылку в этих чатах:\n\n")
    able, unable = 1, 1
    cursor.execute('SELECT id, name, link from chats')
    ids = cursor.fetchall()
    for chats in ids:
        try:
            context.bot.send_message(chat_id=chats[0], text=s.split(' ', 1)[1])
            f.write(f"{able}) {chats[1]} - {chats[2]}\n")
            able += 1
        except:
            cursor.execute("UPDATE chats SET unable = 1 WHERE id = %s", (chats[0],))
            conn.commit()
            unable += 1
    update.message.reply_text(f'Рассылку получили <u>{able-1}</u>/{able+unable-2} чатов.', parse_mode='HTML')
    f.close()
    context.bot.send_document(chat_id=update.message.chat.id, document=open('chats.txt', 'rb'))


@run_async
def start(update, context):
    update.message.reply_text(
        '''Приветствуем! 👋

Вам скучно? Ищете как бы себя развлечь, с кем подискутировать на серьёзные темы или, может быть, хотите просто пообщаться с такими же людьми?

Специально для вас мы создали бота, объединяющего людей самых разных возрастов, профессий и интересов.

У нас вы сможете найти чат на любой вкус. А если вдруг не найдёте - не проблема, создайте свой и добавьте в нашу базу, а мы поможем вам привлечь собеседников!''')
    callchats(update, context, update.message.chat_id)


@run_async
def callchats(update, context, chat_id):
    keyboard = [[InlineKeyboardButton("😎 Общение", callback_data='flood'),
                 InlineKeyboardButton("👾 Развлечение", callback_data='games')],

                [InlineKeyboardButton("🧐 Обсуждение", callback_data='discussion'),
                 InlineKeyboardButton("🗞 Новости", callback_data='news')],

                [InlineKeyboardButton("⭐️ Официальные чаты", callback_data='partners')],

                [InlineKeyboardButton("🎲 Случайный", callback_data='random'),
                 InlineKeyboardButton("🔥 Добавить чат", callback_data='add')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text='Выбирайте какие чаты вам интересны 👇', reply_markup=reply_markup)


@run_async
def chats(update, context):
    keyboard = [[InlineKeyboardButton("😎 Общение", callback_data='flood'),
                 InlineKeyboardButton("👾 Развлечение", callback_data='games')],

                [InlineKeyboardButton("🧐 Обсуждение", callback_data='discussion'),
                 InlineKeyboardButton("🗞 Новости", callback_data='news')],

                [InlineKeyboardButton("⭐️ Официальные чаты", callback_data='partners')],

                [InlineKeyboardButton("🎲 Случайный", callback_data='random'),
                 InlineKeyboardButton("🔥 Добавить чат", callback_data='add')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выбирайте какие чаты вам интересны 👇', reply_markup=reply_markup)


@run_async
def button(update, context):
    query = update.callback_query
    if ('flood' in query.data) or ('games' in query.data) or ('discussion' in query.data) or ('news' in query.data):
        category = query.data
        if 'flood' in query.data:
            title = '<u>Чаты для общения</u> 😎\n'
        elif 'games' in query.data:
            title = '<u>Игровые чаты</u> 👾\n'
        elif 'news' in query.data:
            title = '<u>Новостные чаты</u> 🗞\n'
        else:
            title = '<u>Чаты по интересам</u> 🧐\n'
        cursor.execute('SELECT name, link FROM chats WHERE category = %s ORDER BY random() LIMIT 10', (category,))
    elif 'partners' in query.data:
        cursor.execute('SELECT name, link FROM chats WHERE partners = 1')
        title = '<u>Официальные чаты</u> ⭐️\n'
    elif 'random' in query.data:
        cursor.execute('SELECT name, link FROM chats ORDER BY random() LIMIT 1')
        title = '<u>Случайный чат</u> 🎲\n'
    elif 'add' in query.data:
        query.edit_message_text(text='Пока мы автоматизируем данную функцию, вы можете написать @daaetoya или @aotkh чтобы узнать как добавить свой чат.')

        return
    elif 'other' in query.data:
        callchats(update, context, query.message.chat.id)

        return
    result = cursor.fetchall()
    text = title
    for info in result:
        text += f'\n<b>{info[0]}</b> - <a href="{info[1]}">войти</a>.'
    keyboard = [[InlineKeyboardButton("Другие чаты", callback_data='other')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup, disable_web_page_preview=True)


@run_async
def addChatToDB(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    print('ok')
    if '-' not in str(update.message.chat.id):
        update.message.reply_text('Добавлять в базу можно только чаты!')
    elif ('flood' not in update.message.text) and ('games' not in update.message.text) and ('discussion' not in update.message.text) and ('news' not in update.message.text):
        update.message.reply_text('Укажите категорию чата.')
    elif str(update.message.chat.id) in str(all_chats):
        print('ok1')
        name = update.message.chat.title
        if bool(update.message.chat.username):
            link = "https://t.me/" + update.message.chat.username
            print('ok2') 
        elif adminctrl(update, context):
            if bool(update.message.chat.invite_link):
                link = update.message.chat.invite_link
                print('ok3')        
            else:
                link = context.bot.exportChatInviteLink(chat_id)
                print('ok4')
        category = context.args[0]
        print('ok5')
        cursor.execute('UPDATE chats SET name = %s, link = %s, category = %s, partners = 0 WHERE id = %s', (name, link, category, chat_id,))
        conn.commit()
        print('ok6')
        update.message.reply_text('Данные обновлены.')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # updater = Updater("939504559:AAEf7LZ1r1-bHuFcFKdC73LhJblco1EJ0Jc", use_context=True)
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, add_group))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('chats', chats))
    dp.add_handler(CommandHandler('id', getId))
    dp.add_handler(CommandHandler('message', message))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(CommandHandler('addchat', addChatToDB))
    dp.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
