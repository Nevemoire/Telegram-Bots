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
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
                        host=os.environ['host'])
# conn = psycopg2.connect(dbname='d19olitilh6q1s', user='oukggnzlpirgzh', password='a4e84b7de4257e36cecc14b60bb0ff570f7ce52d5d24b1c7eb275c96f403af36',
#                         host='ec2-79-125-23-20.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()

LIST_OF_ADMINS = [391206263]


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def start(update, context):
    # args = context.args
    # if len(args) == 0:
    #     update.message.reply_text('Meow')
    #     meow = update.message.chat_id
    #     logger.info(f'Meow: {meow}')
    # else:
    #     check_hash = args[0]
    #     update.message.reply_text(check_hash)
    update.message.reply_text('Meow')


# def checkquery(update, context):
#     """Handle the inline query."""
#     query = update.inline_query
#     cursor.execute('SELECT id FROM users')
#     members = cursor.fetchall()
#     if str(ids) in str(members):
#         possible_chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
#         check_hash = ''.join(random.choice(possible_chars) for x in range(10))
#         keyboard = [[InlineKeyboardButton("Активировать", callback=f'cheque {check_hash} {query.from_user.id} {query.query}')]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         text = query.query
#         cursor.execute('SELECT exp FROM users WHERE id = %s', (query.from_user.id,))
#         balance = cursor.fetchone()
#         try:
#             if int(query.query) > int(balance[0]):
#                 results = [
#                     InlineQueryResultArticle(
#                         id=uuid4(),
#                         title=f"Недостаточно средств",
#                         description=f"Вы не можете выписать чек на эту сумму",
#                         thumb_url="https://i.pinimg.com/originals/49/0d/c0/490dc04a6916f957f560297b919b330a.jpg",
#                         input_message_content=InputTextMessageContent('Недостаточно средств :('))]
#             else:
#                 results = [
#                     InlineQueryResultArticle(
#                         id=uuid4(),
#                         title=f"Чек на сумму {query.query} монет.",
#                         description=f"Баланс после списания: {int(balance[0])-int(query.query)} монет.",
#                         thumb_url="https://i.pinimg.com/originals/ee/d5/19/eed519321feadb35c297ddd3ec14b397.png",
#                         reply_markup=reply_markup,
#                         input_message_content=InputTextMessageContent(f'{query.from_user.full_name} выписал(-a) чек на сумму {query.query} монет.'))]
#         except:
#             results = [
#                     InlineQueryResultArticle(
#                         id=uuid4(),
#                         title=f"Укажите сумму чека",
#                         description=f"Баланс: {balance[0]} монет.",
#                         thumb_url="https://i.pinimg.com/originals/ee/d5/19/eed519321feadb35c297ddd3ec14b397.png",
#                         input_message_content=InputTextMessageContent('Привет! Как дела?)'))]

#         query.answer(results, cache_time=0, is_personal=True)


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
        name = update.message.from_user.full_name
        cursor.execute('SELECT id FROM users')
        members = cursor.fetchall()
        cursor.execute('SELECT id FROM chats')
        chats = cursor.fetchall()
        if str(ids) in str(members):
            cursor.execute('UPDATE users SET lastmsg = %s WHERE id = %s', (cur_time, ids,))
        else:
            cursor.execute('INSERT INTO users (id, name, lastmsg) VALUES (%s, %s, %s)', (ids, name, cur_time,))
            conn.commit()
            logger.info(f'New user {update.message.from_user.full_name}!')
        if str(chatid) in str(chats):
            pass
        else:
            cursor.execute('INSERT INTO chats (id) VALUES (%s)', (chatid,))
            conn.commit()
            logger.info(f'New chat {update.message.chat_id}!')
        chance = random.randint(0, 1000)
        logger.info(f'Random: {chance}')
        if chance <= 5:
            cursor.execute('SELECT pidor FROM users WHERE id = %s', (ids,))
            pcount = cursor.fetchone()
            if int(pcount[0]) == 0:
                update.message.reply_text('Поздравляем! Ты впервые стал(-а) пидором чата! 🥳')
            elif (int(pcount[0]) > 0) and (int(pcount[0]) < 5):
                update.message.reply_text(f'Кстати, ты - пидор чата. Уже {int(pcount[0])+1} раз.')
            else:
                update.message.reply_text(f'Может хватит?! 😡\nТы пидор чата уже {int(pcount[0])+1} раз.')
            cursor.execute('UPDATE users SET exp = exp + 5, pidor = pidor + 1 WHERE id = %s', (ids,))
            cursor.execute('UPDATE chats SET pidor_last = %s, pidor_time = %s, pidor_total = pidor_total + 1 WHERE id = %s', (name, cur_time, chatid,))
            context.chat_data['pidor'] = update.message.from_user.full_name
        else:
            pass
        if 'krokoword' in context.chat_data:
            msg = update.message.text
            wrd = context.chat_data['krokoword']
            message = context.chat_data['message']
            cursor.execute('SELECT state FROM games WHERE chatid = %s', (update.message.chat_id,))
            state = cursor.fetchone()
            if (msg.lower() == wrd.lower()) and (str(update.message.from_user.id) not in str(context.chat_data['kroko_inv'])) and ('1' in str(state[0])):
                update.message.reply_text('Ты угадал(-а)! Держи 5 монет за правильный ответ.\n\nНачать заново - /krokodil')
                context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Игра закончилась!\nНачать заново - /krokodil')
                cursor.execute('UPDATE users SET exp = exp + 5 WHERE id = %s', (ids,))
                cursor.execute('UPDATE games SET state = 0, total = total + 1 WHERE chatid = %s', (chatid,))
                job = context.chat_data['kroko_job']
                job.enabled=False
                job.schedule_removal()
                del context.chat_data['krokoword']
                del context.chat_data['kroko_job']
                del context.chat_data['kroko_inv']
                del context.chat_data['kroko_iname']
                del context.chat_data['message']
            elif (msg.lower() == wrd.lower()) and (str(update.message.from_user.id) not in str(context.chat_data['kroko_inv'])) and ('1' not in str(state[0])):
                update.message.reply_text('Ты угадал(-а)! Только игра уже закончилась:(\n\nНачать заново - /krokodil')
                context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Игра закончилась!\nНачать заново - /krokodil')
                del context.chat_data['krokoword']
                del context.chat_data['kroko_job']
                del context.chat_data['kroko_inv']
                del context.chat_data['kroko_iname']
                del context.chat_data['message']
            else:
                pass
        else:
            pass
        conn.commit()
    except AttributeError as error:
        return
    except:
        update.message.reply_text('Произошла оши-и-и-б... (System Error)')


def bets(update, context):
    ids = update.message.from_user.id
    cursor.execute('SELECT id FROM users')
    members = cursor.fetchall()
    if str(ids) in str(members):
        """Echo the user message."""
        cursor.execute('SELECT exp, bet FROM users WHERE id = %s', (update.message.from_user.id,))
        betinfo = cursor.fetchone()
        balance = int(betinfo[0])
        bet = int(betinfo[1])
        dice = update.message.dice.value
        if balance >= bet:
            if dice <= 3:
                update.message.reply_text(f'Проигрыш! (-{bet} монет)\nРезультат: {dice}')
                cursor.execute('UPDATE users SET exp = exp - %s WHERE id = %s', (bet, ids,))
                conn.commit()
            elif dice > 3:
                update.message.reply_text(f'Выигрыш! (+{bet} монет)\nРезультат: {dice}')
                cursor.execute('UPDATE users SET exp = exp + %s WHERE id = %s', (bet, ids,))
                conn.commit()
            else:
                update.message.reply_text('Произошла ошибка, попробуй позже!')
        elif balance < bet:
            update.message.reply_text('Недостаточно монет!')
        else:
            update.message.reply_text('Произошла ошибка, попробуй позже!')
    else:
        update.message.reply_text('Тебя нет в базе! Чтобы начать использовать возможности этого бота, напиши "Привет!" в ответ на это сообщение:)')


def setBet(update, context):
    ids = update.message.from_user.id
    cursor.execute('SELECT id FROM users')
    members = cursor.fetchall()
    if str(ids) in str(members):
        user_says = context.args
        try:
            bet = int(user_says[0])
            if (bet >= 10) and (bet <= 1000):
                cursor.execute('UPDATE users SET bet = %s WHERE id = %s', (bet, ids,))
                conn.commit()
                update.message.reply_text('Готово! Чтобы сделать ставку, пришли в чат этот эмодзи: 🎲')
            else:
                update.message.reply_text('Недопустимое значение!\nМин. ставка: 10 монет\nМакс. ставка: 1000 монет')
        except:
            update.message.reply_text('Пришли мне команду в формате:\n/bet <ЧИСЛО>,\n\nгде <ЧИСЛО> - сумма ставки.')
    else:
        update.message.reply_text('Тебя нет в базе! Чтобы начать использовать возможности этого бота, напиши "Привет!" в ответ на это сообщение:)')


@restricted
def updateUsers(update, context):
    cursor.execute('SELECT id from chats')
    ids = cursor.fetchall() 
    for chats in ids:
        try:
            users = context.bot.get_chat_members_count(chats[0])
            cursor.execute('UPDATE chats SET users = %s WHERE id = %s', (users, chats[0],))
            conn.commit()
        except:
            cursor.execute('UPDATE chats SET unable = 1 WHERE id = %s', (chats[0],))
            conn.commit()
    update.message.reply_text('Кол-во пользователей в чатах обновлено до настоящего момента.')


@restricted
def compensate(update, context):
    cursor.execute("UPDATE users SET exp = exp + 1004")
    conn.commit()
    update.message.reply_text('Готово!')


@restricted
def stats(update, context):
    cursor.execute('SELECT COUNT(id) FROM users')
    users = cursor.fetchone()
    cursor.execute('SELECT COUNT(id), SUM(users) FROM chats')
    info = cursor.fetchone()
    update.message.reply_text(f'Всего чатов: {info[0]}\nВсего участников: {info[1]}\nАктивных участников: {users[0]}')


def get_word(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)


def pidor(update, context):
    try:
        cursor.execute('SELECT pidor_total, pidor_last FROM chats WHERE id = %s', (update.message.chat_id,))
        pInfo = cursor.fetchone()
        if 'pidor' in context.chat_data:
            pidor = context.chat_data['pidor']
            update.message.reply_text(f'Текущий пидор чата: {pidor}')
        elif int(pInfo[0]) > 0:
            update.message.reply_text(f'Последний зарегестрированный пидор: {pInfo[1]}')
        else:
            update.message.reply_text('Пидор чата пока не определён.')
    except IndexError as error:
        update.message.reply_text('Парам-пара-па. Пау! Этот чат пока слишком зелёный.')
    except:
        update.message.reply_text('Произошла оши-и-и-б... (System Error)')


def krokodie(context):
    context.bot.send_message(chat_id=context.job.context, text='Время истекло!\nНикто не смог отгадать слово.')
    cursor.execute('UPDATE games SET state = 2 WHERE chatid = %s', (context.job.context,))
    conn.commit()


def krokodil(update, context):
    try:
        cursor.execute('SELECT state FROM games WHERE chatid = %s', (update.message.chat_id,))
        state = cursor.fetchone()
        if ('0' in str(state[0])) or ('2' in str(state[0])):
            keyboard = [[InlineKeyboardButton("Слово", callback_data=f'krokoword {update.message.from_user.id}')], [InlineKeyboardButton("Поменять (-5 монет)", callback_data=f'krokochange {update.message.from_user.id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            invoker = update.message.from_user.full_name
            context.chat_data['krokoword'] = (get_word('russian.txt'))
            context.chat_data['message'] = update.message.reply_text(f'Начинаем!\nОбъясняет: {invoker}\nВремени: 2 минуты', reply_markup=reply_markup)
            context.chat_data['kroko_job'] = context.job_queue.run_once(krokodie, 120, context=update.message.chat_id)
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
    cursor.execute('UPDATE games SET state = 0')
    conn.commit()


def fbi(update, context):
    context.bot.send_animation(chat_id=update.message.chat_id, animation='CgACAgIAAxkBAAIBrF6MQgz-TZJXda7BWdgFSZfY1LAOAAIVAwACuzWoSw_3NpLvCy0dGAQ')


def babki(update, context):
    cursor.execute('SELECT exp FROM users WHERE id = %s', (update.message.from_user.id,))
    babki = cursor.fetchone()
    update.message.reply_text(f'У тебя {babki[0]} монет!')


@restricted
def message(update, context):
    s = update.message.text
    cursor.execute('SELECT id FROM chats')
    ids = cursor.fetchall()
    for chats in ids:
        try:
            context.bot.send_message(chat_id=chats[0], text=s.split(' ', 1)[1])
        except:
            cursor.execute("UPDATE chats SET unable = 1 WHERE id = %s", (chats[0],))


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
    # elif 'cheque' in query.data and:
    #     if (str(query.from_user.id) not in query.data):
    #         cursor.execute('SELECT id FROM users')
    #         members = cursor.fetchall()
    #         if str(query.from_user.id) in str(members):
    #             data = query.data.split()
    #             qHash = data[1]
    #             qInvoker = data[2]
    #             qAmount = data[3]
    #             qTime = int(time.time())
    #             if qHash not in context.bot_data:
    #                 context.bot_data[qHash] = qHash
    #                 logger.info(f'New cheque: {qHash}')
    #                 cursor.execute('SELECT exp FROM users WHERE id = %s', (qInvoker,))
    #                 balance = cursor.fetchone()
    #                 if int(qAmount) <= int(balance[0]):
    #                     # query.edit_message_text()
    #                     cursor.execute('INSERT INTO cheques (hash, invoker, reciever, amount, ttime) VALUES (%s, %s, %s, %s, %s)', (qHash, qInvoker, query.from_user.id, qAmount, qTime,))
    #                     cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (qInvoker, qAmount,))
    #                     cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (query.from_user.id, qAmount,))
    #                     conn.commit()
    #                     logger.info('Transaction done!')
    #             elif qHash in context.bot_data:
    #                 query.answer('Этот чек уже использовали!', show_alert=True)
    #             else:
    #                 query.answer('Ошибка!', show_alert=True)
    #     elif (str(query.from_user.id) not in query.data):
    #         query.answer('Нельзя использовать свой чек!', show_alert=True)



# def hGif(update, context):
#     fID = update.message.document.file_id
#     update.message.reply_text(fID)
#     cursor.execute('INSERT INTO hello (id) VALUES (%s)', (fID,))
#     conn.commit()
#     logger.info('New hi gif')


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


def memes(update, context):
    try:
        fID = update.message.photo[-1].file_id
        fType = "photo"
    except:
        fID = update.message.document.file_id
        fType = "gif"
    update.message.reply_text(f'{fID} ({fType})')
    cursor.execute('INSERT INTO memes (id, type) VALUES (%s, %s)', (fID, fType,))
    conn.commit()


def showMemes(update, context):
    cursor.execute('SELECT id, type FROM memes ORDER BY random() LIMIT 1')
    meme = cursor.fetchall()
    memes = meme[0]
    if memes[1] == 'photo':
        context.bot.send_photo(chat_id=update.message.chat_id, photo=memes[0], caption=f'Thx for memes: @mem_hunter')
    elif memes[1] == 'gif':
        context.bot.send_animation(chat_id=update.message.chat_id, animation=memes[0], caption=f'Thx for memes: @mem_hunter')
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

    # updater = Updater('1231333868:AAHiPBXYKNgoHpBTeGbxb2mwe2aBm9hToeI', use_context=True)
    updater = Updater(os.environ['token'], use_context=True)

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
    dp.add_handler(CommandHandler("nya", showPussy))
    dp.add_handler(CommandHandler("memepls", showMemes))
    dp.add_handler(CommandHandler("balance", babki))
    dp.add_handler(CommandHandler('update', updateUsers))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('compensate', compensate))
    dp.add_handler(CommandHandler('message', message))
    dp.add_handler(MessageHandler(Filters.dice, bets))
    dp.add_handler(CommandHandler('bet', setBet, pass_args=True))
    # dp.add_handler(InlineQueryHandler(checkquery))
    # dp.add_handler(CommandHandler("gop", gop, pass_args=True))
    dp.add_handler(MessageHandler(Filters.group, echo))
    dp.add_handler(MessageHandler((Filters.photo | Filters.document) & (~Filters.group) & (Filters.user(username="@bhyout") | Filters.user(username="@sslte")), pussy))
    dp.add_handler(MessageHandler((Filters.photo | Filters.document) & (~Filters.group) & (Filters.user(username="@balak_in") | Filters.user(username="@aotkh") | Filters.user(username="@daaetoya")), memes))
    # dp.add_handler(MessageHandler(Filters.document & (~Filters.group) & Filters.user(username="@daaetoya"), hGif))
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
