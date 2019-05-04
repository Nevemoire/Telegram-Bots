#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Basic example for a bot that can receive payment from user.
"""

import logging

from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters,
                          ConversationHandler, CallbackQueryHandler,
                          PreCheckoutQueryHandler, ShippingQueryHandler)
import psycopg2
import config
import os
import datetime
from importlib import reload

conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
                        host=os.environ['host'])

cursor = conn.cursor()

now = datetime.datetime.now()

reply_keyboard = [['О боте', 'О авторе'],
                  ['Пример', 'Контакты']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


(CHOOSING, TYPING_REPLY, PAYMENT) = range(3)


commands = (
    'О боте, О авторе, Пример, Контакты')
ignorelist = commands.split(', ')
members = 'creator, administrator, member'
memberslist = members.split(', ')
back = 'Назад'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context, user_data):
    name = update.message.from_user.full_name
    update.message.reply_text(
        f'Привет, {name}!')
    nick = update.message.from_user.username
    userid = update.message.from_user.id
    user_data['usrid'] = userid
    user_data['username'] = nick
    user_data['name'] = name
    update.message.reply_text('''Воспользуйся меню ниже для взаимодействия с ботом.''', reply_markup=markup)
    cursor.execute("SELECT id FROM users WHERE id=%s", (userid,))
    result = "%s" % cursor.fetchone()
    if result == "None":
        cursor.execute("INSERT INTO users (nickname, namesurname, id) VALUES (%s, %s, %s)", (nick, name, userid))
        conn.commit()
    else:
        pass

    return CHOOSING


def about_bot(context, update):
    update.message.reply_text("О боте")

    return CHOOSING


def about_author(context, update):
    update.message.reply_text("О авторе")

    return CHOOSING


def contacts(context, update):
    update.message.reply_text("Контакты")

    return CHOOSING


def custom_choice(context, update, user_data):
    reply_keyboardz = [['Назад']]
    state = ReplyKeyboardMarkup(reply_keyboardz, one_time_keyboard=True, resize_keyboard=True)
    keyboard = [[InlineKeyboardButton("Базовый (1000р)", callback_data="1"),
                 InlineKeyboardButton("Стандарт (2500р)", callback_data="2")],
                [InlineKeyboardButton("Про (5000р)", callback_data="3"),
                 InlineKeyboardButton("Презентация (Бесплатно)", callback_data="4")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('''Супер 😎''', reply_markup=state)
    update.message.reply_text('Выбери тариф 👇', reply_markup=reply_markup)

    return TYPING_REPLY


def received_information(context, update, user_data):
    query = update.callback_query
    user_data['choice'] = query.data
    # text = update.message.text
    keyboard = [[InlineKeyboardButton("Перейти к оплате", callback_data="Оплата")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        cursor.execute(
            "SELECT tariff, price, patrons FROM betsdb WHERE id=%s", (query.data,))

        context.bot.edit_message_text(text='👇',
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)

        query.answer('Отличный выбор 😎')

        update.effective_message.reply_text('''*Тариф:* %s
*Цена:* %s рублей
*Уже купили:* %s человек''' % cursor.fetchone(), parse_mode='MARKDOWN', reply_markup=reply_markup)
    except:
        update.effective_message.reply_text(f"""*Ошибка!* Что-то пошло не так..""", parse_mode='MARKDOWN')

        return TYPING_REPLY

    return PAYMENT


def button(bot, update, user_data):
    IDS = user_data['choice']
    try:
        chat_id = update.effective_message.chat_id
        cursor.execute("SELECT tariff FROM betsdb WHERE id=%s", (IDS,))
        tariff = "%s" % cursor.fetchone()
        title = tariff
        description = "Бот для оплат 💳"
        # select a payload just for you to recognize its the donation from your bot
        payload = "Custom-Payload"
        # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
        provider_token = os.environ['provider_token']
        start_parameter = "test-payment"
        currency = "RUB"
        # price in dollars
        cursor.execute("SELECT price FROM betsdb WHERE id=%s", (IDS,))
        pricez = "%s" % cursor.fetchone()
        price = int(pricez)
        # price * 100 so as to include 2 d.p.
        prices = [LabeledPrice(tariff, price * 100)]

        # optionally pass need_name=True, need_phone_number=True,
        # need_email=True, need_shipping_address=True, is_flexible=True
        bot.sendInvoice(chat_id, title, description, payload,
                        provider_token, start_parameter, currency, prices)
    except:
        bot.send_message(text='Бесплатные услуги оплачивать не нужно.',
                         chat_id=update.effective_message.chat_id,
                         message_id=update.effective_message.message_id,
                         reply_markup=markup)
        cursor.execute("UPDATE betsdb SET patrons = patrons+1 WHERE id=%s", (IDS,))
        conn.commit()

    return CHOOSING


# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update, context):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        query.answer(pre_checkout_query_id=query.id, ok=False, error_message="Something went wrong...")
    else:
        query.answer(pre_checkout_query_id=query.id, ok=True)


# finally, after contacting to the payment provider...
def successful_payment_callback(update, context, user_data):
    IDS = user_data['choice']
    usrid = user_data['usrid']
    nick = user_data['username']
    cursor.execute("SELECT tariff FROM betsdb WHERE id=%s", (IDS,))
    tariff = "%s" % cursor.fetchone()
    # do something after successful receive of payment?
    update.effective_message.reply_text('''Благодарим за проведение тестовой оплаты!
    Канал для просмотра успешных заявок: @orderspaymentstg''', reply_markup=markup)
    cursor.execute("UPDATE betsdb SET patrons = patrons+1 WHERE id=?", (IDS,))
    cursor.execute("SELECT price FROM betsdb WHERE id=%s", (IDS,))
    product_price = "%d" % cursor.fetchone()
    tsprice = int(product_price)
    cursor.execute("SELECT totalspent FROM users WHERE id=%s", (usrid,))
    ts = "%d" % cursor.fetchone()
    ts = int(ts) + int(tsprice)
    cursor.execute("UPDATE users SET totalspent = %s WHERE id=%s", (str(ts), usrid))
    try:
        cursor.execute("SELECT promo FROM users WHERE id=%s", (usrid,))
        promoz = "%s" % cursor.fetchone()
        cursor.execute("SELECT earnings FROM users WHERE mypromo=%s", (promoz,))
        earngs = "%d" % cursor.fetchone()
        earngs = round(int(earngs) + (int(tsprice) / 10))
        cursor.execute("UPDATE users SET earnings = %s WHERE mypromo=%s", (str(earngs), promoz))
    except:
        pass
    conn.commit()
    context.bot.send_message(
        text=f'''Пользователь {usrid} (@{nick}) оплатил {tsprice} рублей.
    Тариф: {tariff}.
    Дата: {now.day}.{now.month}.{now.year}''', chat_id='@orderspaymentstg')


def get_back(context, update):
    update.message.reply_text("Главное меню 👾", reply_markup=markup)

    return CHOOSING


def stats(bot, update, user_data):
    userid = user_data['usrid']
    cursor.execute("SELECT COUNT(*) FROM users")
    max_users = "%s" % cursor.fetchone()
    cursor.execute("SELECT SUM(earnings) FROM users")
    max_earnings = "%s" % cursor.fetchone()
    bot.send_message(text=f"""Кол-во пользователей: {max_users}
Всего заработано: {max_earnings} рублей""", chat_id=userid)

    return CHOOSING


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            CHOOSING:
                [MessageHandler(Filters.regex('^О боте$', about_bot),
                 MessageHandler(Filters.regex('^О авторе$', about_author),
                 MessageHandler(Filters.regex('^Пример$', custom_choice, pass_user_data=True),
                 MessageHandler(Filters.regex('^Контакты$', contacts),
                 CommandHandler('stats', stats)],

            PAYMENT:    [CallbackQueryHandler(button, pass_user_data=True)],

            TYPING_REPLY: [CallbackQueryHandler(received_information, pass_user_data=True)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Назад$', get_back)]
    )

    # Pre-checkout handler to final check
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback, pass_user_data=True))

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
