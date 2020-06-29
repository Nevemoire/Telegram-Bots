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

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

SWIM, RUN, BIKE, SWIM_PROVE, RUN_PROVE, BIKE_PROVE, = range(6)



def cancel(update, context):
    update.message.reply_text('Отмена! Нажми /start чтобы начать заново.')

    return ConversationHandler.END


def start(update, context):
    update.message.reply_text(
        'Привет! Участвуешь в челлендже?\nТогда ответь на несколько вопросов :) 👇\n\n'
        'Вопрос #1. Сколько метров ты сегодня проплыл(-а)?\n\n/skip - если ты сегодня не плавал(-а).\n\n'
        'В случае ошибки, нажми /cancel для отмены и начни заново (/start).')

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
    update.message.reply_text('Запомнили! 👌\nВопрос #2. Сколько метров ты сегодня накрутил(-а) на велосипеде?\n\n/skip - если ты сегодня не ездил(-а) на велосипеде.')
    context.bot.forward_message(chat_id='@mission226contest', from_chat_id=update.message.chat_id, message_id=update.message.message_id)

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
    update.message.reply_text('Запомнили! 👌\nВопрос #3. Сколько метров ты сегодня пробежал(-а)?\n\n/skip - если ты сегодня не бегал(-а).')
    context.bot.forward_message(chat_id='@mission226contest', from_chat_id=update.message.chat_id, message_id=update.message.message_id)

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
    update.message.reply_text(f'Отлично! 👌\nВаш результат: {result} ⭐')
    context.bot.forward_message(chat_id='@mission226contest', from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    context.bot.send_message(chat_id='@mission226contest', text=f'Пользователь {update.message.from_user.full_name} показывает результат {result} ⭐')

    return ConversationHandler.END


def skip_swim(update, context):
    update.message.reply_text('Пропускаем :(\nВопрос #2. Сколько метров ты сегодня накрутил(-а) на велосипеде?\n\n/skip - если ты сегодня не ездил(-а) на велосипеде.')
    context.user_data['swim'] = 0

    return BIKE


def skip_bike(update, context):
    update.message.reply_text('Пропускаем :(\nВопрос #3. Сколько метров ты сегодня пробежал(-а)?\n\n/skip - если ты сегодня не бегал(-а).')
    context.user_data['bike'] = 0

    return RUN


def skip_run(update, context):
    context.user_data['run'] = 0
    swim = context.user_data['swim']
    run = context.user_data['run']
    bike = context.user_data['bike']
    result = int(swim) * 6 + int(run) * 2 + int(bike)
    update.message.reply_text(f'Пропускаем :(\nВаш результат: {result}.')
    context.bot.send_message(chat_id='@mission226contest', text=f'Пользователь {update.message.from_user.full_name} показывает результат {result} ⭐')

    return ConversationHandler.END


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

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
