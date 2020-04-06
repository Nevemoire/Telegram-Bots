#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those
functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random
import psycopg2
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
                        host=os.environ['host'])
cursor = conn.cursor()


def start(update, context):
    update.message.reply_text('Meow')


def set_exp(update, context):
    cur_time = int(time.time())
    exp_time = cur_time - 600
    cursor.execute('UPDATE exp = exp + 10 WHERE lastmsg >= %s', (exp_time,))
    conn.commit()
    logger.info('Set exp done!')


def echo(update, context):
    cur_time = int(time.time())
    ids = update.message.from_user.id
    cursor.execute('SELECT id FROM users')
    members = cursor.fetchall()
    if ids in int(members):
        cursor.execute('UPDATE users SET lastmsg = %s WHERE id = %s', (cur_time, ids,))
    else:
        name = update.message.from_user.full_name
        cursor.execute('INSERT INTO users (id, name, lastmsg) VALUES (%s, %s, %s)', (ids, name, cur_time,))
        logger.info(f'New user {update.message.from_user.full_name}!')
    chance = random.randint(0, 1000)
    if chance <= 1:
        update.message.reply_text('Кстати, ты - пидор чата.')
        cursor.execute('UPDATE users SET exp = exp + 5 WHERE id = %s', (ids,))
        context.chat_data['pidor'] = update.message.from_user.full_name
    else:
        pass
    msg = update.message.from_user.text
    wrd = context.chat_data['krokoword']
    if (msg.lower() == wrd.lower()) and (update.message.from_user.id != context.chat_data['kroko_inv']):
        update.message.reply_text('А вот и победитель! +5 очков')
        cursor.execute('UPDATE users SET exp = exp + 5 WHERE id = %s', (ids,))
        job = context.chat_data['kroko_job']
        job.enabled=False
        job.schedule_removal()
        del context.chat_data['krokoword']
        del context.chat_data['kroko_job']
        del context.chat_data['kroko_inv']
    else:
        pass 
    conn.commit()


def get_word(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)


def pidor(update, context):
    pidor = context.chat_data['pidor']
    update.message.reply_text(f'Текущий пидор чата: {pidor}')


def krokodie(update, context):
    krokoword = context.chat_data['krokoword']
    context.bot.send_message(chat_id=context.job.context, text=f'Время истекло!\nНикто не смог отгадать слово: {krokoword}')
    del context.chat_data['krokoword']
    del context.chat_data['kroko_job']
    del context.chat_data['kroko_inv']


def krokodil(update, context):
    if 'kroko_job' not in context.chat_data:
        keyboard = [[InlineKeyboardButton("Слово", callback_data=f'krokoword {update.message.from_user.id}')], [InlineKeyboardButton("Поменять (-5 очков)", callback_data=f'krokochange {update.message.from_user.id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.chat_data['krokodil'] = (get_word('russian.txt'))
        update.message.reply_text(f'Начинаем!\nОбъясняет: {update.message.from_user.full_name}\nВремени: 5 минут', reply_markup=reply_markup)
        context.chat_data['kroko_job'] = context.job_queue.run_once(krokodie, 300, context=update.message.chat_id)
        context.chat_data['kroko_inv'] = update.message.from_user.id
    else:
        update.message.reply_text('Игра уже идёт!')


def button(update, context):
    query = update.callback_query
    cursor.execute('SELECT id FROM users')
    all_users = cursor.fetchall()
    if query.from_user.id in all_users:
        if ('krokoword' in query.data) and (query.from_user.id in query.data):
            query.answer(f'{context.chat_data["krokodil"]}', show_alert=True)
        elif ('krokochange' in query.data) and (query.from_user.id in query.data):
            cursor.execute('SELECT exp FROM users WHERE  id = %s', (query.from_user.id,))
            balance = int(cursor.fetchone())
            if balance >= 5:
                context.chat_data['krokodil'] = (get_word('russian.txt'))
                query.answer(f'context.chat_data["krokodil"]', show_alert=True)
                cursor.execute('UPDATE users SET exp = exp - 5 WHERE id = %s', (query.from_user.id,))
                conn.commit()
            else:
                query.answer('Недостаточно очков!', show_alert=True)
        elif (query.from_user.id not in query.data):
            query.answer('Пресекаем попытку взлома! -1 очко', show_alert=True)
            cursor.execute('UPDATE users SET exp = exp - 1 WHERE id = %s', (query.from_user.id,))
            conn.commit()
    else:
        qury.answer('Неавторизованный вход!', show_alert=True)


def pussy(update, context):
    try:
        fID = update.message.photo.file_id
        fType = photo
    except:
        fID = update.message.document.file_id
        fType = gif
    update.message.reply_text(f'{fID} ({fType})')
    cursor.execute('INSER INTO pussy (id, type) VALUES (%s, %s)', (fID, fType,))
    conn.commit()


def showPussy(update, context):
    cursor.execute('SELECT id, type FROM pussy ORDER BY random() LIMIT 1')
    pussy = cursor.fetchall()
    if pussy[1] == 'photo':
        context.bot.send_photo(chat_id=update.message.chat_id, photo=pussy[0])
    elif pussy[1] == 'gif':
        context.bot.send_animation(chat_id=update.message.chat_id, animation=pussy[0])
    else:
        logger.info('GIF/PHOTO ERROR')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # TOKEN='792500219:AAHxYVirYrEwIAJ_kqAucaI9PovVuyEYVgo'
    # REQUEST_KWARGS={
    # 'proxy_url': 'socks5h://207.97.174.134:1080'
    # Optional, if you need authentication:
    # 'urllib3_proxy_kwargs': {
    #     'username': 'PROXY_USER',
    #     'password': 'PROXY_PASS',
    # }

    # updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    j = updater.job_queue
    j.run_repeating(set_exp, interval=600, first=600)

    # log all errors
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("krokodil", krokodil), pass_job_queue=True)
    dp.add_handler(CommandHandler("pidor", pidor))
    dp.add_handler(CommandHandler("pussy", showPussy))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler((Filters.photo | Filters.document.gif) & (Filters.user(username="@bhyout") | Filters.user(username="@sslte")), pussy))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
