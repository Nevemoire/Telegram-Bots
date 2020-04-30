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
import string
from uuid import uuid4
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, CallbackQueryHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
                        host=os.environ['host'])
# conn = psycopg2.connect(dbname='d19olitilh6q1s', user='oukggnzlpirgzh', password='a4e84b7de4257e36cecc14b60bb0ff570f7ce52d5d24b1c7eb275c96f403af36',
#                         host='ec2-79-125-23-20.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()

all_user_data = set()

LIST_OF_ADMINS = [391206263]
channel_username = '@theclownfiesta'
memberz = 'creator, administrator, member'
memberslist = memberz.split(', ')


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@restricted
def ban(update, context):
    target = update.message.reply_to_message.from_user.id
    cursor.execute('UPDATE users SET banned = 1 WHERE id = %s', (target,))
    conn.commit()
    update.message.reply_text('Пользователь забанен.')


@restricted
def unban(update, context):
    target = update.message.reply_to_message.from_user.id
    cursor.execute('UPDATE users SET banned = 0 WHERE id = %s', (target,))
    conn.commit()
    update.message.reply_text('Пользователь разбанен.')


@restricted
def message(update, context):
    keyboard = [[InlineKeyboardButton("Обсудить 🙋", url="t.me/clownfiestachat")], [InlineKeyboardButton("Новости и обновления", url="t.me/theclownfiesta")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    s = update.message.text
    cursor.execute('SELECT id FROM chats')
    ids = cursor.fetchall()
    for chats in ids:
        try:
            context.bot.send_message(chat_id=chats[0], text=s.split(' ', 1)[1], reply_markup=reply_markup)
        except:
            cursor.execute("UPDATE chats SET unable = 1 WHERE id = %s", (chats[0],))


@restricted
def compensate(update, context):
    cursor.execute("UPDATE users SET exp = exp + 1004")
    conn.commit()
    update.message.reply_text('Готово!')


@restricted
def stats(update, context):
    cursor.execute('SELECT id from chats')
    ids = cursor.fetchall() 
    for chats in ids:
        try:
            chatUsers = context.bot.get_chat_members_count(chats[0])
            cursor.execute('UPDATE chats SET users = %s WHERE id = %s', (chatUsers, chats[0],))
            conn.commit()
        except:
            cursor.execute('UPDATE chats SET unable = 2 WHERE id = %s', (chats[0],))
            conn.commit()
    cursor.execute('SELECT COUNT(id) FROM users')
    allUsers = cursor.fetchone()
    cursor.execute('SELECT COUNT(id), SUM(users) FROM chats')
    info = cursor.fetchone()
    update.message.reply_text(f'Всего чатов: {info[0]}\nВсего участников: {info[1]}\nАктивных участников: {allUsers[0]}')


# def raffle(update, context):
#     user_says = context.args
#     try:
#         prize = int(user_says[0])
#     except:
#         update.message.reply_text('Ошибка.')
#     keyboard = [[InlineKeyboardButton("Участвую!", callback_data="giveaway")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     cursor.execute('SELECT id FROM chats')
#     ids = cursor.fetchall()
#     for chats in ids:
#         try:
#             context.bot.send_message(chat_id=chats[0], text=f'Всем привет!\nМы тут решили провести розыгрыш на {prize} монет!\n\nЕсть всего 1 условие - подписаться на официальный канал: @theclownfiesta.\nСписок победителей появится там же, удачи!', reply_markup=reply_markup)
#         except:
#             cursor.execute("UPDATE chats SET unable = 1 WHERE id = %s", (chats[0],))


def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def get_word(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)


def new_user(update, context):
    logger.info('hey')
    for member in update.message.new_chat_members:
        if member.id != context.bot.get_me().id:
            cursor.execute('SELECT id FROM hello ORDER BY random() LIMIT 1')
            hgif = cursor.fetchall()
            hello = hgif[0]
            context.bot.send_animation(chat_id=update.message.chat_id, animation=hello[0], caption=f'Здарова, {update.message.from_user.full_name}!')
        elif member.id == context.bot.get_me().id:
            userscount = context.bot.get_chat_members_count(update.message.chat.id)
            name = update.message.chat.title
            chatid = update.message.chat_id
            cursor.execute('SELECT id FROM chats')
            chats = cursor.fetchall()
            if str(chatid) in str(chats):
                update.message.reply_text('Мне кажется, или я уже был в этом чате? Осуждаю.\n\nЛадно, ладно. Я не злопамятный, можем начать всё с чистого листа.')
                cursor.execute('UPDATE chats SET name = %s, users = %s, unable = 0 WHERE id = %s', (name, userscount, chatid,))
                context.bot.send_message(chat_id=391206263, text=f'Бота снова добавили в {name} ({userscount})!')
            elif str(chatid) not in str(chats):
                update.message.reply_text("""
Всем пис в этом чатике!
С этого момента я буду вас развлекать.

Список всех команд: /help
Новости, розыгрыши и т.п. здесь: @theclownfiesta""")
                cursor.execute('INSERT INTO chats (id, name) VALUES (%s, %s)', (update.message.chat_id, update.message.chat.title,))
                context.bot.send_message(chat_id=391206263, text=f'Бота добавили в {name} ({userscount})!')
            conn.commit()
        else:
            pass


def set_exp(context):
    cur_time = int(time.time())
    exp_time = cur_time - 600
    cursor.execute('UPDATE users SET exp = exp + 10 WHERE lastmsg >= %s', (exp_time,))
    conn.commit()
    logger.info('Set exp done!')


def krokodie(context):
    context.bot.send_message(chat_id=context.job.context, text='Время истекло!\nНачать игру заново - /krokodil')
    cursor.execute('UPDATE games SET state = 2 WHERE chatid = %s', (context.job.context,))
    conn.commit()


def krokoreload(context):
    cursor.execute('UPDATE games SET state = 0')
    conn.commit()


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
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        cursor.execute('SELECT id, type FROM pussy ORDER BY random() LIMIT 1')
        pussy = cursor.fetchall()
        pussies = pussy[0]
        if pussies[1] == 'photo':
            context.bot.send_photo(chat_id=update.message.chat_id, photo=pussies[0])
        elif pussies[1] == 'gif':
            context.bot.send_animation(chat_id=update.message.chat_id, animation=pussies[0])
        else:
            logger.info('GIF/PHOTO ERROR')
    else:
        pass


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
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        cursor.execute('SELECT id, type FROM memes ORDER BY random() LIMIT 1')
        meme = cursor.fetchall()
        memes = meme[0]
        if memes[1] == 'photo':
            context.bot.send_photo(chat_id=update.message.chat_id, photo=memes[0], caption=f'Thx for memes: @mem_hunter')
        elif memes[1] == 'gif':
            context.bot.send_animation(chat_id=update.message.chat_id, animation=memes[0], caption=f'Thx for memes: @mem_hunter')
        else:
            logger.info('GIF/PHOTO ERROR')
    else:
        pass


def start(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
    # args = context.args
    # if len(args) == 0:
    #     update.message.reply_text('Meow')
    #     meow = update.message.chat_id
    #     logger.info(f'Meow: {meow}')
    # else:
    #     check_hash = args[0]
    #     update.message.reply_text(check_hash)
        update.message.reply_text('Meow')
    else:
        pass


def checkquery(update, context):
    """Handle the inline query."""
    query = update.inline_query
    name = update.inline_query.from_user.full_name
    id_int = update.inline_query.from_user.id
    ids = str(id_int)
    cursor.execute('SELECT id FROM users')
    members = cursor.fetchall()
    if ids in str(members):
        # if ids not in all_user_data:
        possible_chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        check_hash = ''.join(random.choice(possible_chars) for x in range(10))
        # all_user_data = check_hash
        all_user_data.add(ids)
        keyboard = [[InlineKeyboardButton("Активировать", callback_data=f'cheque {check_hash} {query.from_user.id} {query.query}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = query.query
        cursor.execute('SELECT exp FROM users WHERE id = %s', (query.from_user.id,))
        balance = cursor.fetchone()
        try:
            if int(query.query) > int(balance[0]):
                results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="Недостаточно средств",
                        description="Жаль, но не получится выписать чек на эту сумму:(",
                        thumb_url="https://i.pinimg.com/originals/49/0d/c0/490dc04a6916f957f560297b919b330a.jpg",
                        input_message_content=InputTextMessageContent('Недостаточно средств :('))]
            elif int(query.query) < 100:
                results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="Мин. сумма чека: 100 монет",
                        description="Жаль, но не получится выписать чек на эту сумму:(",
                        thumb_url="https://i.pinimg.com/originals/49/0d/c0/490dc04a6916f957f560297b919b330a.jpg",
                        input_message_content=InputTextMessageContent('Упс, ошибка :('))]
            else:
                results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=f"Чек на сумму {query.query} монет.",
                        description=f"Баланс после списания: {int(balance[0])-int(query.query)} монет.",
                        thumb_url="https://i.pinimg.com/originals/ee/d5/19/eed519321feadb35c297ddd3ec14b397.png",
                        reply_markup=reply_markup,
                        input_message_content=InputTextMessageContent(f'От: {name}\nЧек на: {query.query} монет.'))]
        except:
            results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=f"Укажите сумму чека",
                        description=f"Баланс: {balance[0]} монет.",
                        thumb_url="https://i.pinimg.com/originals/ee/d5/19/eed519321feadb35c297ddd3ec14b397.png",
                        input_message_content=InputTextMessageContent('Привет! Как дела?)'))]

        query.answer(results, cache_time=0, is_personal=True)
        # elif ids in all_user_data:
        #     results = [
        #                 InlineQueryResultArticle(
        #                     id=uuid4(),
        #                     title=f"Нельзя создавать больше одного чека одновременно.",
        #                     description=f"Баланс: {balance[0]} монет.",
        #                     thumb_url="https://i.pinimg.com/originals/ee/d5/19/eed519321feadb35c297ddd3ec14b397.png",
        #                     input_message_content=InputTextMessageContent('Привет! Как дела?)'))]
        #     query.answer(results, cache_time=0, is_personal=True)


def bets(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        ids = update.message.from_user.id
        cursor.execute('SELECT id FROM users')
        members = cursor.fetchall()
        if str(ids) in str(members):
            cursor.execute('SELECT exp, bet FROM users WHERE id = %s', (update.message.from_user.id,))
            betinfo = cursor.fetchone()
            balance = int(betinfo[0])
            bet = int(betinfo[1])
            dice = update.message.dice.value
            if bet == 0:
                pass
            else:
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
    else:
        pass


def setBet(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        ids = update.message.from_user.id
        cursor.execute('SELECT id FROM users')
        members = cursor.fetchall()
        if str(ids) in str(members):
            member = context.bot.get_chat_member(channel_username, ids)
            if member.status in memberslist:
                maxBet = 10000
            else:
                maxBet = 1000
            user_says = context.args
            try:
                bet = int(user_says[0])
                if (bet == 0) or (bet >= 10) and (bet <= maxBet):
                    cursor.execute('UPDATE users SET bet = %s WHERE id = %s', (bet, ids,))
                    conn.commit()
                    update.message.reply_text('Готово! Чтобы сделать ставку, пришли в чат этот эмодзи: 🎲')
                else:
                    update.message.reply_text(f'Недопустимое значение!\nМин. ставка: 10 монет\nМакс. ставка: 1000 монет или 10.000 монет для подписчиков: {channel_username}\nЧтобы отключить ставки, напиши: /bet 0')
            except:
                update.message.reply_text('Пришли мне команду в формате:\n/bet <ЧИСЛО>,\n\nгде <ЧИСЛО> - сумма ставки.\nОтключить ставки: /bet 0')
        else:
            update.message.reply_text('Тебя нет в базе! Чтобы начать использовать возможности этого бота, напиши "Привет!" в ответ на это сообщение:)')
    else:
        pass


def pidor(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
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
    else:
        pass


def pidor_toggle(update, context):
    try:
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            cursor.execute('SELECT pidor_state FROM chats WHERE id = %s', (update.message.chat_id,))
            pState = cursor.fetchone()
            if '1' in str(pState[0]):
                cursor.execute('UPDATE chats SET pidor_state = 0 WHERE id = %s', (update.message.chat_id,))
                update.message.reply_text('Пидор чата: выкл.')
            elif '0' in str(pState[0]):
                cursor.execute('UPDATE chats SET pidor_state = 1 WHERE id = %s', (update.message.chat_id,))
                update.message.reply_text('Пидор чата: вкл.')
            else:
                update.message.reply_text('Произошла ошибка!')
            conn.commit()
        else:
            update.message.reply_text('Кажется, ты не являешься админом этого чата.')
    except:
        update.message.reply_text('Произошла ошибка!')


def krokodil(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        try:
            cursor.execute('SELECT state FROM games WHERE chatid = %s', (update.message.chat_id,))
            state = cursor.fetchone()
            if ('0' in str(state[0])) or ('2' in str(state[0])):
                cursor.execute('UPDATE games SET total = total + 1 WHERE chatid = %s', (update.message.chat_id,))
                conn.commit()
                cursor.execute('SELECT total FROM games WHERE chatid = %s', (update.message.chat_id,))
                gameid = cursor.fetchone()
                keyboard = [[InlineKeyboardButton("Слово", callback_data=f'krokoword {update.message.from_user.id} {gameid[0]}')], [InlineKeyboardButton("Поменять (-5 монет)", callback_data=f'krokochange {update.message.from_user.id} {gameid[0]}')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                invoker = update.message.from_user.full_name
                context.chat_data['krokoword'] = (get_word('russian.txt'))
                context.chat_data['message'] = update.message.reply_text(f'Игра #{gameid[0]}\nОбъясняет: {invoker}\nВремени: 2 минуты', reply_markup=reply_markup)
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
    else:
        pass


def fbi(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        context.bot.send_animation(chat_id=update.message.chat_id, animation='CgACAgIAAxkBAAIBrF6MQgz-TZJXda7BWdgFSZfY1LAOAAIVAwACuzWoSw_3NpLvCy0dGAQ')
    else:
        pass


def babki(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        cursor.execute('SELECT exp FROM users WHERE id = %s', (update.message.from_user.id,))
        babki = cursor.fetchone()
        update.message.reply_text(f'У тебя {babki[0]} монет!')
    else:
        pass


def tip(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        try:
            target = update.message.reply_to_message.from_user.id
            ids = update.message.from_user.id
            cursor.execute('SELECT id FROM users')
            members = cursor.fetchall()
            if (str(ids) in str(members)) and (str(target) in str(members)):
                member = context.bot.get_chat_member(channel_username, ids)
                if member.status in memberslist:
                    maxTip = 10000
                else:
                    maxTip = 1000
                user_says = context.args
                try:
                    amount = int(user_says[0])
                except:
                    update.message.reply_text('Ошибка! Укажи сумму перевода.')
                    return
                cursor.execute('SELECT exp FROM users WHERE id = %s', (ids,))
                balance = cursor.fetchone()
                if (amount < 10) or (amount > maxTip):
                    update.message.reply_text(f'Ошибка!\nМин. перевод: 10 монет, макс. перевод: 1000 монет или 10.000 монет для подписчиков: {channel_username} за раз.')
                elif str(ids) in str(target):
                    update.message.reply_text('Очень смешно. 🤨')
                elif amount > int(balance[0]):
                    update.message.reply_text('Недостаточно средств!')
                elif ((amount >= 10) and (amount <= maxTip)) and amount <= int(balance[0]):
                    cursor.execute('UPDATE users SET exp = exp - %s, total_tipped = total_tipped + %s WHERE id = %s', (amount, amount, ids,))
                    cursor.execute('UPDATE users SET exp = exp + %s, total_recieved = total_recieved + %s WHERE id = %s', (amount, amount, target,))
                    conn.commit()
                    update.message.reply_text('Перевод успешно выполнен!')
            else:
                update.message.reply_text('Ошибка! Перевод возможен только если оба пользователя присутствуют в базе данных.')
        except:
            update.message.reply_text('Ошибка! Удостоверься, что ты отвечаешь на сообщение, а не на фото, видео и т.п.')
    else:
        pass


def button(update, context):
    query = update.callback_query
    cursor.execute('SELECT banned FROM users WHERE id = %s', (query.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        if ('krokoword' in query.data) or ('krokochange' in query.data):
            data = query.data.split()
            gId = data[2]
            cursor.execute('SELECT total FROM games WHERE chatid = %s', (query.message.chat_id,))
            gameid = cursor.fetchone()
            if str(gId) == str(gameid[0]):
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
            else:
                query.answer('Эта игра уже закончилась!', show_alert=True)
        elif 'cheque' in query.data:
            if (str(query.from_user.id) not in query.data):
                cursor.execute('SELECT id FROM users')
                members = cursor.fetchall()
                if str(query.from_user.id) in str(members):
                    data = query.data.split()
                    qHash = data[1]
                    qInvoker = data[2]
                    qAmount = data[3]
                    qTime = int(time.time())
                    if qInvoker in all_user_data:
                        all_user_data.remove(qInvoker)
                        logger.info(f'From: {qInvoker}, Hash: {qHash}, SUMM: {qAmount}')
                        cursor.execute('SELECT exp FROM users WHERE id = %s', (qInvoker,))
                        balance = cursor.fetchone()
                        if int(qAmount) <= int(balance[0]):
                            # query.edit_message_text()
                            # cursor.execute('INSERT INTO cheques (hash, invoker, reciever, amount, ttime) VALUES (%s, %s, %s, %s, %s)', (qHash, qInvoker, query.from_user.id, qAmount, qTime,))
                            cursor.execute('UPDATE users SET exp = exp - %s, total_tipped = total_tipped + %s WHERE id = %s', (qAmount, qAmount, qInvoker,))
                            cursor.execute('UPDATE users SET exp = exp + %s, total_recieved = total_recieved + %s WHERE id = %s', (qAmount, qAmount, query.from_user.id,))
                            conn.commit()
                            logger.info('Transaction done!')
                            query.answer('Чек успешно активирован!', show_alert=True)
                        else:
                            query.answer('Ошибка!', show_alert=True)
                    elif qInvoker not in all_user_data:
                        query.answer('Кажется, этот чек уже активировали.', show_alert=True)
                    else:
                        query.answer('Ошибка!', show_alert=True)
                else:
                    query.answer('Сперва нужно зарегестрироваться!', show_alert=True)
            elif (str(query.from_user.id) in query.data):
                query.answer('Нельзя активировать собственный чек!', show_alert=True)
            else:
                query.answer('Произошла ошибка.', show_alert=True)
        # elif 'giveaway' in query.data:
        #     cursor.execute('SELECT id FROM users')
        #     members = cursor.fetchall()
        #     if str(query.from_user.id) in str(members):
        #         cursor.execute('SELECT raffle FROM users WHERE id = %s', (query.from_user.id,))
        #         raffle = cursor.fetchone()
        #         if '0' in str(raffle[0]):
        #             cursor.execute('UPDATE users SET raffle = 1 WHERE id = %s', (query.from_user.id,))
        #             conn.commit()
        #             query.answer('Ты теперь участвуешь в розыгрыше!', show_alert=True)
        #             logger.info(f'New raffle participant: {query.from_user.full_name}')
        #         else:
        #             query.answer('Ошибка, ты уже участвуешь в розыгрыше!', show_alert=True)
        #             logger.info(f'Raffle denied: {query.from_user.full_name}')
        else:
            query.answer('Произошла ошибка.', show_alert=True)
    else:
        query.answer('Извини, но ты забанен(-а).', show_alert=True)


def echo(update, context):
    try:
        cur_time = int(time.time())
        pidor_time = cur_time - 14400
        ids = update.message.from_user.id
        chatid = update.message.chat_id
        name = update.message.from_user.full_name
        cursor.execute('SELECT id FROM users')
        members = cursor.fetchall()
        cursor.execute('SELECT id FROM chats')
        chats = cursor.fetchall()
        if str(ids) in str(members):
            cursor.execute('UPDATE users SET name = %s, lastmsg = %s WHERE id = %s', (name, cur_time, ids,))
        else:
            registered = time.strftime('%d.%m.%y')
            cursor.execute('INSERT INTO users (id, name, lastmsg, registered) VALUES (%s, %s, %s, %s)', (ids, name, cur_time, registered,))
            conn.commit()
            logger.info(f'New user {update.message.from_user.full_name}!')
        cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
        banned = cursor.fetchone()
        if '0' in str(banned[0]):
            pass
        else:
            return
        chance = random.randint(0, 1000)
        cursor.execute('SELECT pidor_state FROM chats WHERE id = %s', (update.message.chat_id,))
        pState = cursor.fetchone()
        cursor.execute('SELECT pidor_time FROM chats WHERE id = %s', (update.message.chat_id,))
        pTime = cursor.fetchone()
        logger.info(f'Random: {chance}')
        if (chance <= 5) and ('1' in str(pState[0])):
            if (pidor_time >= int(pTime[0])):
                logger.info('New pidor.')
                cursor.execute('SELECT pidor FROM users WHERE id = %s', (ids,))
                pcount = cursor.fetchone()
                if int(pcount[0]) == 0:
                    update.message.reply_text('Поздравляем! Ты впервые стал(-а) пидором чата! 🥳')
                elif (int(pcount[0]) > 0) and (int(pcount[0]) < 5):
                    update.message.reply_text(f'Кстати, ты - пидор чата. Уже {int(pcount[0])+1} раз.')
                else:
                    update.message.reply_text(f'Может хватит?! 😡\nТы пидор чата уже в {int(pcount[0])+1} раз.')
                cursor.execute('UPDATE users SET exp = exp + 5, pidor = pidor + 1 WHERE id = %s', (ids,))
                cursor.execute('UPDATE chats SET pidor_last = %s, pidor_time = %s, pidor_total = pidor_total + 1 WHERE id = %s', (name, cur_time, chatid,))
                context.chat_data['pidor'] = update.message.from_user.full_name
            else:
                logger.info('Almost new pidor.')
                pass
        else:
            pass
        if 'krokoword' in context.chat_data:
            msg = update.message.text
            wrd = context.chat_data['krokoword']
            message = context.chat_data['message']
            cursor.execute('SELECT state FROM games WHERE chatid = %s', (update.message.chat_id,))
            state = cursor.fetchone()
            if (msg.lower() == wrd.lower()) and (str(update.message.from_user.id) in str(context.chat_data['kroko_inv'])) and ('1' in str(state[0])):
                context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Игра закончилась!\nНачать заново - /krokodil')
                update.message.reply_text('Ты же понимаешь, что так играть не честно?\nМне пришлось оштрафовать тебя на 50 монет и преждевременно закончить игру.\n\nНачать заново - /krokodil')
                cursor.execute('UPDATE users SET exp = exp - 50 WHERE id = %s', (ids,))
                cursor.execute('UPDATE games SET state = 0 WHERE chatid = %s', (chatid,))
                job = context.chat_data['kroko_job']
                job.enabled=False
                job.schedule_removal()
                del context.chat_data['krokoword']
                del context.chat_data['kroko_job']
                del context.chat_data['kroko_inv']
                del context.chat_data['kroko_iname']
                del context.chat_data['message']
            elif (msg.lower() == wrd.lower()) and (str(update.message.from_user.id) not in str(context.chat_data['kroko_inv'])) and ('1' in str(state[0])):
                member = context.bot.get_chat_member(channel_username, ids)
                if member.status in memberslist:
                    krokoWin = 10
                else:
                    krokoWin = 5
                update.message.reply_text(f'Ты угадал(-а)! Держи {krokoWin} монет за правильный ответ.\n\nНачать заново - /krokodil')
                context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Игра закончилась!\nНачать заново - /krokodil')
                cursor.execute('UPDATE users SET exp = exp + %s WHERE id = %s', (krokoWin, ids,))
                cursor.execute('UPDATE games SET state = 0 WHERE chatid = %s', (chatid,))
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
        cursor.execute('UPDATE chats SET messages = messages + 1 WHERE id = %s', (update.message.chat_id,))
        conn.commit()
    except AttributeError as error:
        return
    except:
        update.message.reply_text('Произошла оши-и-и-б... (System Error)')


# def gop(update, context):
#     try:
#         target = update.message.reply_to_message.from_user.id
#         ids = update.message.from_user.id
#         cursor.execute('SELECT id FROM users')
#         members = cursor.fetchall()
#         if (str(ids) in str(members)) and (str(target) in str(members)):
#             user_says = context.args[0]
#             try:
#                 amount = int(user_says)
#             except:
#                 return
#             ids = update.message.from_user.id
#             cursor.execute('SELECT exp FROM users WHERE id = %s', (ids,))
#             balance = cursor.fetchone()
#             exp = int(balance[0])
#             gMin = 10
#             gMax = exp*2
#             risk = amount/gMax*1000
#             result = random.randint(0, 1100)
#             if result > risk:
#     except:
#         update.message.reply_text('Ошибка! Удостоверься, что ты отвечаешь на сообщение, а не на фото, видео и т.п.')


def qHelp(update, context):
    cursor.execute('SELECT banned FROM users WHERE id = %s', (update.message.from_user.id,))
    banned = cursor.fetchone()
    if '0' in str(banned[0]):
        update.message.reply_text('''Список доступных команд:

/krokodil - Игра в угадать слово.
/pidor - Напомнить кто является лучшим человеком чата.
/nya - Котики и другая живность.
/memepls - Мемчики.
/fbi - На случай важных переговоров.
/balance - Узнать свой баланс.

/tip <SUMM> - Перевести денежку (пишется в ответ на сообщение получателя).
/bet <SUMM> - Указать сумму ставки.

Вместо <SUMM> указываем число от 10 до 1000 (10.000 для подписчиков @theclownfiesta).''')
        logger.info('Help requested')
    else:
        pass


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
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_user))
    # dp.add_handler(CommandHandler('raffle', raffle, filters=(Filters.user(username="@daaetoya") | Filters.user(username='@bhyout'))))
    dp.add_handler(CommandHandler('krokodil', krokodil, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler('pidor', pidor))
    dp.add_handler(CommandHandler('pidor_toggle', pidor_toggle))
    dp.add_handler(CommandHandler('fbi', fbi))
    dp.add_handler(CommandHandler('nya', showPussy))
    dp.add_handler(CommandHandler('memepls', showMemes))
    dp.add_handler(CommandHandler('balance', babki))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('ban', ban))
    dp.add_handler(CommandHandler('unban', unban))
    dp.add_handler(CommandHandler('compensate', compensate))
    dp.add_handler(CommandHandler('message', message))
    dp.add_handler(MessageHandler((Filters.dice & (~Filters.forwarded)), bets))
    dp.add_handler(CommandHandler('bet', setBet, pass_args=True))
    dp.add_handler(CommandHandler('tip', tip, pass_args=True))
    dp.add_handler(CommandHandler('help', qHelp))
    dp.add_handler(InlineQueryHandler(checkquery))
    # dp.add_handler(CommandHandler("gop", gop, pass_args=True))
    dp.add_handler(MessageHandler(Filters.group, echo))
    dp.add_handler(MessageHandler((Filters.photo | Filters.document) & (~Filters.group) & (Filters.user(username="@bhyout") | Filters.user(username="@sslte")), pussy))
    dp.add_handler(MessageHandler((Filters.photo | Filters.document) & (~Filters.group) & (Filters.user(username="@balak_in") | Filters.user(username="@aotkh")), memes))
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
