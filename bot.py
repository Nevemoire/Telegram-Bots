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

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

conn = psycopg2.connect(dbname = 'daqpsemmol11kn', user = 'fnwjyuhqrjdbcv', password = '4ae63588868e2423ddb7cc3bd4e71ae5892179b86dca5a90272b747aa933bac9', host = 'ec2-46-137-75-170.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot_id = '1072920015'


def adminctrl(update, context):
    for bot_id in context.bot.get_chat_administrators(update.message.chat_id):
        return True
    return False


@run_async
def start(update, context):
    keyboard = [[InlineKeyboardButton("😎 Общение", callback_data='flood'),
                 InlineKeyboardButton("👾 Развлечение", callback_data='games')],

                [InlineKeyboardButton("🧐 Тематические", callback_data='discussion'),
                 InlineKeyboardButton("⭐️ Партнёрские чаты", callback_data='partners')],

                [InlineKeyboardButton("Случайный чат", callback_data='random'),
                 InlineKeyboardButton("Добавить чат", callback_data='add')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        '''Приветствуем! 👋

Вам скучно? Ищете как бы себя развлечь, с кем подискутировать на серьёзные темы или, может быть, хотите просто пообщаться с такими же людьми?

Специально для вас мы создали бота, объединяющего людей самых разных возрастов, профессий и интересов.

У нас вы сможете найти чат на любой вкус. А если вдруг не найдёте - не проблема, создайте свой и добавьте в нашу базу, а мы поможем вам привлечь собеседников!

Выбирайте какие чаты вам интересны 👇''', reply_markup=reply_markup)


@run_async
def button(update, context):
    text = ''
    query = update.callback_query
    if ('flood' in query.data) or ('games' in query.data) or ('discussion' in query.data):
        category = query.data
        cursor.execute('SELECT name, link FROM chats WHERE category = %s', (category,))
    elif 'partners' in query.data:
        cursor.execute('SELECT name, link FROM chats WHERE partners = 1')
    elif 'random' in query.data:
        cursor.execute('SELECT name, link FROM chats ORDER BY random() LIMIT 1')
    elif 'add' in query.data:
        update.message.reply_text('Пока мы автоматизируем данную функцию, вы можете написать @daaetoya или @aotkh чтобы узнать как добавить свой чат.')

        return
    result = cursor.fetchall()
    try:
        for info in result:
            text += f'\n<b>{info[0]}</b> - <a href="{info[1]}">войти</a>.'

        query.edit_message_text(text=text, parse_mode='HTML')
    except:
        query.answer(text='Пока что в базе данных нет таких чатов.', show_alert=True)
    


@run_async
def addChatToDB(update, context):
    try:
        if '-' not in str(update.message.chat.id):
            update.message.reply_text('Добавлять в базу можно только чаты!')
        elif ('flood' not in update.message.text) and ('games' not in update.message.text) and ('discussion' not in update.message.text):
            update.message.reply_text('Укажи категорию чата.')
        elif ('flood' in update.message.text) or ('games' in update.message.text) or ('discussion' in update.message.text):
            chat_id = update.message.chat.id
            name = update.message.chat.title
            if bool(update.message.chat.username):
                link = "https://t.me/" + update.message.chat.username   
            elif adminctrl(update, context):
                if bool(update.message.chat.invite_link):
                    link = update.message.chat.invite_link        
                else:
                    link = context.bot.exportChatInviteLink(chat_id)
            print(context.bot.id)
            category = context.args[0]
            cursor.execute('INSERT INTO chats (id, name, link, category, partners) VALUES (%s, %s, %s, %s, 0)', (chat_id, name, link, category,))
            conn.commit()
        else:
            update.message.reply_text('Что-то пошло не так.')
    except:
        update.message.reply_text('Произошла ошибка.')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # updater = Updater("TOKEN", use_context=True)
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('addchat', addChatToDB, filters=Filters.user(username='@daaetoya')|Filters.user(username='@aotkh')))
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
