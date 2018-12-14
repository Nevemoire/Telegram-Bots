# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler)
import logging
import psycopg2
import config
import os
from importlib import reload

conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'], host=os.environ['host'])

cursor = conn.cursor()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, SEND, FRST, JOIN = range(4)

reply_keyboard = [['Наш топ пользователей'],
                  ['FAQ', 'Случайный автор'],
                  ['Подать заявку', 'Полезные ссылки'],
                  ['Обратная связь', 'Личный кабинет']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

first_keyboard = [['Проверить подписку']]
first = ReplyKeyboardMarkup(first_keyboard, one_time_keyboard=True, resize_keyboard=True)

members = 'creator, administrator, member'
memberslist = members.split(', ')


def start(bot, update, user_data):
    """Send a message when the command /start is issued."""
    name = update.message.from_user.full_name
    update.message.reply_text(f'''Здарова, {name}.
Только тебя и ждали!''')
    nick = update.message.from_user.username
    userid = update.message.from_user.id
    user_data['name'] = name
    user_data['nick'] = nick
    user_data['userid'] = userid
    member = bot.get_chat_member('@whoismdk', userid)
    if member.status in memberslist:
        update.message.reply_text('''Я помогу освоиться тебе в приложении MDK!
Воспользуйся меню ниже чтобы мы понимали друг друга без проблем ;)''', reply_markup=markup)
        cursor.execute("SELECT id FROM users WHERE id=%s", (userid,))
        result = "%s" % cursor.fetchone()
        if result == "None":
            cursor.execute("INSERT INTO users (nickname, namesurname, id) VALUES (%s, %s, %s)", (nick, name, userid))
            conn.commit()
        else:
            pass

        return CHOOSING
    else:
        update.message.reply_text('Для начала, будь добр(-а), подпишись на наш канал с новостями: @whoismdk'
                                  , reply_markup=first)

        return FRST


def first_time(bot, update, user_data):
    userid = user_data['usrid']
    nick = user_data['username']
    name = user_data['name']
    member = bot.get_chat_member('@whoismdk', userid)
    if member.status in memberslist:
        update.message.reply_text('Благодарим за подписку! :)')
        update.message.reply_text('''Я помогу освоиться тебе в приложении MDK!
Воспользуйся меню ниже чтобы мы понимали друг друга без проблем ;)''', reply_markup=markup)
        cursor.execute("SELECT id FROM users WHERE id=%s", (userid,))
        result = "%s" % cursor.fetchone()
        if result == "None":
            cursor.execute("INSERT INTO users (nickname, namesurname, id) VALUES (%s, %s, %s)", (nick, name, userid))
            conn.commit()
        else:
            pass

        return CHOOSING
    else:
        update.message.reply_text('Для начала, будь добр(-а), подпишись на наш главный канал: @whoismdk'
                                  , reply_markup=first)

        return FRST


def bot_faq(bot, update):
    update.message.reply_text('FAQ')

    return CHOOSING


def top_users(bot, update):
    update.message.reply_text('TOP USERS')

    return CHOOSING


def contact_us(bot, update):
    update.message.reply_text('CONTACT US')

    return CHOOSING


def join_us(bot, update):
    update.message.reply_text('Такс, напиши сюда свой юзернейм из приложения в таком формате: @username')

    return JOIN


def user_join(bot, update, user_data):
    user = user_data['usrid']
    name = user_data['name']
    nick = user_data['nick']
    cursor.execute("SELECT mdkname FROM users WHERE mdkname IS NOT NULL")
    users = "%s" % cursor.fetchall()
    mdkname = update.message.reply_text
    if mdkname in users:
        update.message.reply_text('Засранец, этот пользователь уже подтверждён.')
        bot.send_message(text=f'''Пользователь {name} ({nick}) попытался наебать систему и использовать ник {mdkname}
ID: {user}''', chat_id='@whoismdkadmin')
    elif '@' in mdkname:
        bot.send_message(text=f'Пользователь {user} запросил подтверждение на ник: {mdkname}', chat_id='@whoismdkadmin')
        update.message.reply_text('Заявка принята.')

        return CHOOSING
    else:
        update.message.reply_text('Неправильный формат!')

        return CHOOSING


def get_id(bot, update):
    update.message.reply_text(update.message.from_user.id)

    return CHOOSING


def media_links(bot,update):
    update.message.reply_text('LINKS')

    return CHOOSING


def profile(bot,update):
    update.message.reply_text('PROFILE')

    return CHOOSING


def add_user(bot, update):
    update.message.reply_text('ADD')

    return CHOOSING


def message(bot, update, user_data):
    reload(config)
    user = str(user_data['usrid'])
    if user in config.admin:
        update.message.reply_text('Че нужно сообщить?')

        return SEND
    else:
        update.message.reply_text('Ты не админ.')

        return CHOOSING


def message_send(bot, update):
    sends = 0
    blocks = 0
    notification = update.message.text
    cursor.execute("SELECT id FROM users")
    while True:
        try:
            chat_id = '%s' % cursor.fetchone()
            sends += 1
            if chat_id == 'None':
                break
            bot.send_message(text=notification, chat_id=chat_id)
        except:
            blocks += 1
            pass
    update.message.reply_text(f'''Кол-во отосланных сообщений: {sends}
Не дошло: {blocks}''')

    return CHOOSING


def stats(bot, update):
    update.message.reply_text('STATS')

    return CHOOSING


def get_back(bot, update):
    update.message.reply_text("Главное меню 👾", reply_markup=markup)

    return CHOOSING


def restore(bot, update):
    update.message.reply_text('Исправлено!', reply_markup=markup)

    return CHOOSING


def random_user(bot, update):
    cursor.execute(
        "SELECT mdkname, toppost, tags FROM users ORDER BY RANDOM() LIMIT 1")
    update.message.reply_text('''*Автор:* %s
*Лучший пост:* %s
*Теги:* %s''' % cursor.fetchone(), parse_mode='MARKDOWN')

    return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(os.environ['token'])

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states=
        {
            CHOOSING:
                [
                    RegexHandler('^FAQ$', bot_faq),
                    RegexHandler('^Наш топ пользователей$', top_users),
                    RegexHandler('^Случайный автор$', random_user),
                    RegexHandler('^Подать заявку$', join_us),
                    RegexHandler('^Полезные ссылки$', media_links),
                    RegexHandler('^Обратная связь$', contact_us),
                    RegexHandler('^Личный кабинет$', profile),
                    # RegexHandler('^Проверить подписку$', first_time),
                    CommandHandler('add', add_user),
                    CommandHandler('stats', stats),
                    CommandHandler('id', get_id),
                    CommandHandler('send', message, pass_user_data=True),
                    MessageHandler(Filters.text, random_user)],

            FRST:
                [MessageHandler(Filters.text, first_time, pass_user_data=True)],

            SEND:
                [MessageHandler(Filters.text, message_send)],
        },

        fallbacks=[RegexHandler('^Назад$', get_back),
                   CommandHandler('help', restore)]
    )

    dp.add_handler(conv_handler)

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
