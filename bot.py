#!/usr/bin/env python
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
import datetime
import pytz
import psycopg2


from telegram import ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

utc_now = pytz.utc.localize(datetime.datetime.utcnow())
pst_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

SWIM, RUN, BIKE, SWIM_PROVE, RUN_PROVE, BIKE_PROVE, = range(6)

conn = psycopg2.connect(dbname = 'daqpsemmol11kn', user = 'fnwjyuhqrjdbcv', password = '4ae63588868e2423ddb7cc3bd4e71ae5892179b86dca5a90272b747aa933bac9', host = 'ec2-46-137-75-170.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()


def cancel(update, context):
    update.message.reply_text('Отмена! Нажми /start чтобы начать заново.')

    return ConversationHandler.END


def delete(update, context):
    cursor.execute('DELETE FROM users WHERE id = %s', (update.message.from_user.id,))
    conn.commit()
    update.message.reply_text('Готово.')


def start(update, context):
    ids = update.message.from_user.id
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    if str(ids) in str(users):
        pass
        logger.info('reg pass')
    else:
        name = update.message.from_user.full_name
        cursor.execute('INSERT INTO users (id, name) VALUES (%s, %s)', (ids, name,))
        conn.commit()
        logger.info(f'New user: {name}')
    date = pst_now.strftime("%d.%m.%Y")
    cursor.execute('SELECT last_date FROM users WHERE id = %s', (ids,))
    lastDate = cursor.fetchone()
    if str(date) in str(lastDate):
        update.message.reply_text('Ты уже участвовал(-а) сегодня! Возвращайся завтра.')
    else:
        update.message.reply_text(
        'Привет! Участвуешь в челлендже?\nТогда ответь на несколько вопросов :) 👇\n\n'
        '<b>Вопрос #1.</b> Сколько метров ты сегодня проплыл(-а)?\n-----------------------\n'
        f'Дата прохождения: <b>{date}</b>\n\n/skip - Пропустить вопрос (тренировки не было).\n/cancel - Отмена (заполню позже).\n\n'
        'В случае ошибки, отмени диалог с ботом и начни заново - /start.', parse_mode='HTML')
        logger.info(f'{date} - {lastDate}')

        return SWIM


def swim(update, context):
    ftext = update.message.text
    try:
        text = int(ftext)
    except:
        update.message.reply_text('Ответ должен содержать только цифры! Напиши ещё раз.')
        return SWIM
    context.user_data['swim'] = text
    update.message.reply_text('Пришли скрин с доказательством результата.')

    return SWIM_PROVE


def swim_prove(update, context):
    update.message.reply_text('Запомнили! 👌\n<b>Вопрос #2.</b> Сколько метров ты сегодня накрутил(-а) на велосипеде?\n-----------------------\n/skip - Пропустить вопрос.\n/cancel - Отмена.', parse_mode='HTML')
    context.bot.forward_message(chat_id='@mission226contest', from_chat_id=update.message.chat_id, message_id=update.message.message_id)

    return BIKE


def skip_swim(update, context):
    update.message.reply_text('Пропускаем :(\n\n<b>Вопрос #2.</b> Сколько метров ты сегодня накрутил(-а) на велосипеде?\n-----------------------\n/skip - Пропустить вопрос.\n/cancel - Отмена.', parse_mode='HTML')
    context.user_data['swim'] = 0

    return BIKE


def bike(update, context):
    ftext = update.message.text
    try:
        text = int(ftext)
    except:
        update.message.reply_text('Ответ должен содержать только цифры! Напиши ещё раз.')
        return BIKE
    context.user_data['bike'] = text
    update.message.reply_text('Пришли скрин с доказательством результата.')

    return BIKE_PROVE


def bike_prove(update, context):
    update.message.reply_text('Запомнили! 👌\n<b>Вопрос #3.</b> Сколько метров ты сегодня пробежал(-а)?\n-----------------------\n/skip - Пропустить вопрос.\n/cancel - Отмена.', parse_mode='HTML')
    context.bot.forward_message(chat_id='@mission226contest', from_chat_id=update.message.chat_id, message_id=update.message.message_id)

    return RUN


def skip_bike(update, context):
    update.message.reply_text('Пропускаем :(\n\n<b>Вопрос #3.</b> Сколько метров ты сегодня пробежал(-а)?\n-----------------------\n/skip - Пропустить вопрос.\n/cancel - Отмена.', parse_mode='HTML')
    context.user_data['bike'] = 0

    return RUN


def run(update, context):
    ftext = update.message.text
    try:
        text = int(ftext)
    except:
        update.message.reply_text('Ответ должен содержать только цифры! Напиши ещё раз.')
        return RUN
    context.user_data['run'] = text
    update.message.reply_text('Пришли скрин с доказательством результата.')

    return RUN_PROVE


def run_prove(update, context):
    swim = context.user_data['swim']
    run = context.user_data['run']
    bike = context.user_data['bike']
    result = int(swim) * 6 + int(run) * 2 + int(bike)
    date = pst_now.strftime("%d.%m.%Y")
    update.message.reply_text(f'Отлично! 👌\nВаш результат: <code>{result}</code> ⭐', parse_mode='HTML')
    context.bot.forward_message(chat_id='@mission226contest', from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    context.bot.send_message(chat_id='@mission226contest', text=f'🏃‍♂️🏃‍♀️: <b>{update.message.from_user.full_name}</b>\nРезультат: <code>{result}</code> ⭐', parse_mode='HTML')
    cursor.execute('UPDATE users SET pts = pts + %s, last_date = %s WHERE id = %s', (result, date, update.message.from_user.id,))
    conn.commit()

    return ConversationHandler.END


def skip_run(update, context):
    context.user_data['run'] = 0
    swim = context.user_data['swim']
    run = context.user_data['run']
    bike = context.user_data['bike']
    result = int(swim) * 6 + int(run) * 2 + int(bike)
    date = pst_now.strftime("%d.%m.%Y")
    update.message.reply_text(f'Пропускаем :(\n\nВаш результат: {result}.')
    context.bot.send_message(chat_id='@mission226contest', text=f'🏃‍♂️🏃‍♀️: <b>{update.message.from_user.full_name}</b>\nРезультат: <code>{result}</code> ⭐', parse_mode='HTML')
    cursor.execute('UPDATE users SET pts = pts + %s, last_date = %s WHERE id = %s', (result, date, update.message.from_user.id,))
    conn.commit()

    return ConversationHandler.END


def info(update, context):
    try:
        cursor.execute('SELECT pts, last_date, rank() OVER (ORDER BY pts DESC) FROM users WHERE id = %s', (update.message.from_user.id,))
        info = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM users')
        users = cursor.fetchone()
        update.message.reply_text(f'⭐ Результат: {info[0]}\n📅 Последняя запись: {info[1]}\n🌐 Позиция в рейтинге: {info[2]} из {users[0]}')
    except:
        update.message.reply_text('Пользователь отсутствует в базе данных.')


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1112372303:AAHW4PcIX7pRx4b4MyOXySIGmqoHNUW-1AA", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SWIM: [MessageHandler((Filters.text&(~(Filters.command))), swim),
                   CommandHandler('skip', skip_swim)],
            SWIM_PROVE: [MessageHandler(Filters.photo, swim_prove),
                         CommandHandler('skip', skip_swim)],

            BIKE: [MessageHandler((Filters.text&(~(Filters.command))), bike),
                   CommandHandler('skip', skip_bike)],
            BIKE_PROVE: [MessageHandler(Filters.photo, bike_prove),
                         CommandHandler('skip', skip_bike)],

            RUN: [MessageHandler((Filters.text&(~(Filters.command))), run),
                  CommandHandler('skip', skip_run)],
            RUN_PROVE: [MessageHandler(Filters.photo, run_prove),
                        CommandHandler('skip', skip_run)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('del', delete))
    dp.add_handler(CommandHandler('info', info))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
