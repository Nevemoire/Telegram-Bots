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
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
#                         host=os.environ['host'])
conn = psycopg2.connect(dbname='d19olitilh6q1s', user='oukggnzlpirgzh', password='a4e84b7de4257e36cecc14b60bb0ff570f7ce52d5d24b1c7eb275c96f403af36',
                        host='ec2-79-125-23-20.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()


def start(update, context):
    update.message.reply_text('Meow')


def new_user(update, context):
    logger.info('hey')
    for member in update.message.new_chat_members:
        if member.id != context.bot.get_me().id:
            cursor.execute('SELECT id FROM hello ORDER BY random() LIMIT 1')
            hgif = cursor.fetchall()
            hello = hgif[0]
            context.bot.send_animation(chat_id=update.message.chat_id, animation=hello[0], caption=f'Здарова, {update.message.from_user.full_name}!')


def set_exp(context):
    cur_time = int(time.time())
    exp_time = cur_time - 600
    cursor.execute('UPDATE users SET exp = exp + 10 WHERE lastmsg >= %s', (exp_time,))
    conn.commit()
    logger.info('Set exp done!')


def echo(update, context):
    try:
        cur_time = int(time.time())
        ids = update.message.from_user.id
        chatid = update.message.chat_id
        cursor.execute('SELECT id FROM users')
        members = cursor.fetchall()
        if str(ids) in str(members):
            cursor.execute('UPDATE users SET lastmsg = %s WHERE id = %s', (cur_time, ids,))
        else:
            name = update.message.from_user.full_name
            cursor.execute('INSERT INTO users (id, name, lastmsg) VALUES (%s, %s, %s)', (ids, name, cur_time,))
            conn.commit()
            logger.info(f'New user {update.message.from_user.full_name}!')
        chance = random.randint(0, 1000)
        logger.info(f'Random: {chance}')
        if chance <= 5:
            update.message.reply_text('Кстати, ты - пидор чата.')
            cursor.execute('UPDATE users SET exp = exp + 5 WHERE id = %s', (ids,))
            context.chat_data['pidor'] = update.message.from_user.full_name
        else:
            pass
        if 'krokoword' in context.chat_data:
            msg = update.message.text
            wrd = context.chat_data['krokoword']
            if (msg.lower() == wrd.lower()) and (str(update.message.from_user.id) not in str(context.chat_data['kroko_inv'])):
                update.message.reply_text('А вот и победитель! +5 монет')
                cursor.execute('UPDATE users SET exp = exp + 5 WHERE id = %s', (ids,))
                cursor.execute('UPDATE games SET state = 0 WHERE chatid = %s', (chatid,))
                job = context.chat_data['kroko_job']
                job.enabled=False
                job.schedule_removal()
                del context.chat_data['krokoword']
                del context.chat_data['kroko_job']
                del context.chat_data['kroko_inv']
                del context.chat_data['kroko_iname']
            else:
                pass
        else:
            pass
        conn.commit()
    except AttributeError as error:
        return
    except:
        update.message.reply_text('Произошла оши-и-и-б... (System Error)')


def get_word(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)


def pidor(update, context):
    if 'pidor' in context.chat_data:
        pidor = context.chat_data['pidor']
        update.message.reply_text(f'Текущий пидор чата: {pidor}')
    else:
        update.message.reply_text('Пидор чата пока не определён.')


def krokodie(context):
    context.bot.send_message(chat_id=context.job.context, text='Время истекло!\nНикто не смог отгадать слово.')
    cursor.execute('UPDATE games SET state = 0 WHERE chatid = %s', (context.job.context,))
    conn.commit()


def krokodil(update, context):
    try:
        cursor.execute('SELECT state FROM games WHERE chatid = %s', (update.message.chat_id,))
        state = cursor.fetchone()
        if '0' in str(state[0]):
            keyboard = [[InlineKeyboardButton("Слово", callback_data=f'krokoword {update.message.from_user.id}')], [InlineKeyboardButton("Поменять (-5 монет)", callback_data=f'krokochange {update.message.from_user.id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            invoker = update.message.from_user.full_name
            context.chat_data['krokoword'] = (get_word('russian.txt'))
            update.message.reply_text(f'Начинаем!\nОбъясняет: {invoker}\nВремени: 5 минут', reply_markup=reply_markup)
            context.chat_data['kroko_job'] = context.job_queue.run_once(krokodie, 300, context=update.message.chat_id)
            context.chat_data['kroko_inv'] = update.message.from_user.id
            context.chat_data['kroko_iname'] = update.message.from_user.full_name
            cursor.execute('UPDATE games SET state = 1 WHERE chatid = %s', (update.message.chat_id,))
            conn.commit()
        elif '1' in str(state[0]):
            update.message.reply_text('Игра уже идёт!')
        else:
            update.message.reply_text('Error!')
    except:
        cursor.execute('INSERT INTO games (chatid, state) VALUES (%s, 0)', (update.message.chat_id,))
        conn.commit()
        update.message.reply_text('Чат зарегестрирован! Напиши /krokodil ещё раз, чтобы начать игру.')


def krokoreload(context):
    cursor.execute('SELECT chatid from games')
    ids = cursor.fetchall()
    for chats in ids:
        try:
            context.bot.send_message(chat_id=chats[0], text='Все крокодилы сброшены после рестарта бота, можете начать игру заново.')
        except:
            pass
    cursor.execute('UPDATE games SET state = 0')
    conn.commit()


def fbi(update, context):
    context.bot.send_animation(chat_id=update.message.chat_id, animation='CgACAgIAAxkBAAIBrF6MQgz-TZJXda7BWdgFSZfY1LAOAAIVAwACuzWoSw_3NpLvCy0dGAQ')


def babki(update, context):
    cursor.execute('SELECT exp FROM users WHERE id = %s', (update.message.from_user.id,))
    babki = cursor.fetchone()
    update.message.reply_text(f'У тебя {babki[0]} бабок!')


def button(update, context):
    query = update.callback_query
    if ('krokoword' in query.data) and (str(query.from_user.id) in query.data):
        query.answer(f'{context.chat_data["krokoword"]}', show_alert=True)
    elif ('krokochange' in query.data) and (str(query.from_user.id) in query.data):
        logger.info('yes')
        cursor.execute('SELECT exp FROM users WHERE  id = %s', (query.from_user.id,))
        balancez = cursor.fetchone()
        balance = int(balancez[0])
        if balance >= 5:
            logger.info('byes')
            context.chat_data['krokoword'] = (get_word('russian.txt'))
            query.answer(f'Новое слово: {context.chat_data["krokoword"]}', show_alert=True)
            cursor.execute('UPDATE users SET exp = exp - 5 WHERE id = %s', (query.from_user.id,))
            conn.commit()
        else:
            query.answer('Недостаточно монет!', show_alert=True)
    elif str(query.from_user.id) not in query.data:
        query.answer(f'В очередь!\nСейчас объясняет: {context.chat_data["kroko_iname"]}', show_alert=True)


def hGif(update, context):
    fID = update.message.document.file_id
    update.message.reply_text(fID)
    cursor.execute('INSERT INTO hello (id) VALUES (%s)', (fID,))
    conn.commit()
    logger.info('New hi gif')


def pussy(update, context):
    try:
        fID = update.message.photo[-1].file_id
        fType = "photo"
    except:
        fID = update.message.document.file_id
        fType = "gif"
    update.message.reply_text(f'{fID} ({fType})')
    cursor.execute('INSERT INTO pussy (id, type) VALUES (%s, %s)', (fID, fType,))
    conn.commit()


def showPussy(update, context):
    cursor.execute('SELECT id, type FROM pussy ORDER BY random() LIMIT 1')
    pussy = cursor.fetchall()
    pussies = pussy[0]
    if pussies[1] == 'photo':
        context.bot.send_photo(chat_id=update.message.chat_id, photo=pussies[0])
    elif pussies[1] == 'gif':
        context.bot.send_animation(chat_id=update.message.chat_id, animation=pussies[0])
    else:
        logger.info('GIF/PHOTO ERROR')


# def gop(update, context):
#     user_says = context.args[0]
#     try:
#         gopstop = int(user_says)
#     except:
#         return
#     cGop = 1000/(gopstop+1)
#     if (gopstop >= 0) and (gopstop <= 10):
#         cButilka = 100
#     elif (gopstop > 10) and (gopstop <= 25):
#         cButilka = 250
#     elif (gopstop > 25) and (gopstop <= 50):
#         cButilka = 500
#     elif (gopstop > 50) and (gopstop <= 100):
#         cButilka = 990
#     else:
#         cButilka = 999


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater('1231333868:AAHiPBXYKNgoHpBTeGbxb2mwe2aBm9hToeI', use_context=True)
    # updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    j = updater.job_queue
    j.run_repeating(set_exp, interval=600, first=0)
    j.run_once(krokoreload, 1)

    # log all errors
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_user))
    dp.add_handler(CommandHandler("krokodil", krokodil, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("pidor", pidor))
    dp.add_handler(CommandHandler("fbi", fbi))
    dp.add_handler(CommandHandler("pussy", showPussy))
    dp.add_handler(CommandHandler("babki", babki))
    # dp.add_handler(CommandHandler("gop", gop, pass_args=True))
    dp.add_handler(MessageHandler(Filters.group, echo))
    dp.add_handler(MessageHandler((Filters.photo | Filters.document) & (~Filters.group) & (Filters.user(username="@bhyout") | Filters.user(username="@sslte")), pussy))
    dp.add_handler(MessageHandler(Filters.document & (~Filters.group) & Filters.user(username="@daaetoya"), hGif))
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
