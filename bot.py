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
from telegram.ext.dispatcher import run_async
import psycopg2
import config
import os
import datetime
from importlib import reload

conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
                        host=os.environ['host'])

cursor = conn.cursor()

today = datetime.datetime.today()

reply_keyboard = [['О боте 👾', 'О авторе 👨🏻‍💻'],
                  ['Пример 💶', 'Контакты 📲'],
                  ['Статистика 📊'],['Хочу такого бота 🚀']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


(CHOOSING, TYPING_REPLY, PAYMENT) = range(3)


commands = (
    'О боте 👾, О авторе 👨🏻‍💻, Пример 💶, Контакты 📲, Статистика 📊, Хочу такого бота 🚀')
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


def start(update, context):
    name = update.message.from_user.full_name
    update.message.reply_text(
        f'Привет, {name}!')
    nick = update.message.from_user.username
    userid = update.message.from_user.id
    context.user_data['usrid'] = userid
    context.user_data['username'] = nick
    context.user_data['name'] = name
    update.message.reply_text('''Воспользуйся меню ниже для взаимодействия с ботом.
    
 Не знаешь с чего начать? Возможности бота описаны в разделе "О боте".''', reply_markup=markup)
    cursor.execute("SELECT id FROM users WHERE id=%s", (userid,))
    result = "%s" % cursor.fetchone()
    if result == "None":
        cursor.execute("INSERT INTO users (nickname, namesurname, id, totalspent) VALUES (%s, %s, %s, 0)", (nick, name, userid))
        conn.commit()
    else:
        pass

    return CHOOSING


@run_async  
def about_bot(update, context):
    update.message.reply_text("""*Возможности бота*
    
- Запись, считывание и хранение информации в базах данных.
- Массовая рассылка сообщений пользователям.
- Функция обратной связи. (Для тех, кто не хочет палить свой аккаунт tg. Пересылает сообщения пользователей в личку или на указанный канал.)
- *Форматирование* _текста_ `разными` [способами](http://www.example.com/)
    
Доступные команды:
/start - запустить/перезагрузить бота
/photo - бот пришлёт фото
/doc - бот пришлёт документ
/stats - статистика бота

Также, при заказе я учту и реализую все ваши пожелания.""", parse_mode='MARKDOWN')

    return CHOOSING


@run_async  
def about_author(update, context):
    update.message.reply_text("""Привет! Меня зовут Данил.
Студент, начинающий разработчик (учу python) и front-end (js/react) девелопер.

Пара работ из моего портфолио:
- https://poli-trade.com.ua
- https://mjm-corp.ee
- https://active-sp.ru (калькулятор, презентация, рекламные макеты и др.)

Также, ссылка на мой сайт: https://nevermore.red

Есть вопросы и/или предложения? Пиши мне: @daaetoya""")

    return CHOOSING


@run_async  
def contacts(update, context):
    update.message.reply_text("""Telegram: @daaetoya
Instagram: [daniel.nvmr](https://instagram.com/daniel.nvmr)""", parse_mode="MARKDOWN", disable_web_page_preview=True)

    return CHOOSING
  

@run_async  
def echo(update, context):
    doc = update.message.document
    update.message.reply_text(doc.file_id)
    
    return CHOOSING
 

@run_async  
def order(update, context):
    update.message.reply_text("Проконсультироваться и заказать бота можно у @daaetoya ;)")

    return CHOOSING
  

@run_async  
def photo(update, context):
    avatar = 'https://images.pexels.com/photos/207962/pexels-photo-207962.jpeg?auto=compress&cs=tinysrgb&h=750&w=1260'
    context.bot.send_photo(update.message.chat_id, photo=avatar)

    return CHOOSING

@run_async  
def doc(update, context):
    doc = 'BQADAgAD3AMAApBwiEjvdRoQ7cnNDgI'
    context.bot.send_document(update.message.chat_id, document=doc)
    
    return CHOOSING


def custom_choice(update, context):
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


def received_information(update, context):
    query = update.callback_query
    context.user_data['choice'] = query.data
    # text = update.message.text
    keyboard = [[InlineKeyboardButton("Перейти к оплате", callback_data="Оплата")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        cursor.execute(
            "SELECT tariff, price, patrons FROM betsdb WHERE id=%s", (query.data,))

        context.bot.edit_message_text(text='''*Инструкция*
        
Оплата работает в тестовом режиме, не вводите данные настоящих карт!
Чтобы провести тестовую оплату используйте данные ниже:
Карта: 4242 4242 4242 4242
Действительна до: любая дата, но не раньше сегодняшнего дня
CVV: любое трёхзначное число

👇''', chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode='MARKDOWN')

        query.answer('Отличный выбор 😎')

        update.effective_message.reply_text('''*Тариф:* %s
*Цена:* %s рублей
*Уже купили:* %s человек''' % cursor.fetchone(), parse_mode='MARKDOWN', reply_markup=reply_markup)
    except:
        update.effective_message.reply_text("*Ошибка!* Что-то пошло не так..", parse_mode='MARKDOWN')

        return TYPING_REPLY

    return PAYMENT


def button(update, context):
    IDS = context.user_data['choice']
    chat_id = update.effective_message.chat_id
    try:
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
      context.bot.sendInvoice(chat_id, title, description, payload,
                          provider_token, start_parameter, currency, prices, photo_url='https://images.pexels.com/photos/207962/pexels-photo-207962.jpeg')

      return CHOOSING
    except:
      update.effective_message.reply_text('''Бесплатные услуги оплачивать не нужно.

*Ваш код*''')
      
      return CHOOSING
      


# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update, context):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


# finally, after contacting to the payment provider...
def successful_payment_callback(update, context):
    IDS = context.user_data['choice']
    usrid = context.user_data['usrid']
    name = context.user_data['name']
    date = today.strftime("%d-%m-%Y %H:%M UTC")
    cursor.execute("SELECT tariff FROM betsdb WHERE id=%s", (IDS,))
    tariff = "%s" % cursor.fetchone()
    # do something after successful receive of payment?
    update.effective_message.reply_text('''Благодарим за проведение тестовой оплаты!
Посмотреть как выглядят заказы: @orderspaymentstg''', reply_markup=markup)
    cursor.execute("UPDATE betsdb SET patrons = patrons+1 WHERE id=%s", (IDS,))
    cursor.execute("SELECT price FROM betsdb WHERE id=%s", (IDS,))
    product_price = "%s" % cursor.fetchone()
    tsprice = int(product_price)
    cursor.execute("SELECT totalspent FROM users WHERE id=%s", (usrid,))
    ts = "%s" % cursor.fetchone()
    ts = int(ts) + int(tsprice)
    cursor.execute("UPDATE users SET totalspent = %s WHERE id=%s", (str(ts), usrid))
    conn.commit()
    context.bot.send_message(
        text=f'''Пользователь [{name}](tg://user?id={usrid}) оплатил *{tsprice}* рублей.
*Тариф*: {tariff}.
*Дата*: {date}''', chat_id='@orderspaymentstg', parse_mode='MARKDOWN')


def get_back(update, context):
    update.message.reply_text("Главное меню 👾", reply_markup=markup)

    return CHOOSING


def stats(update, context):
    userid = context.user_data['usrid']
    cursor.execute("SELECT COUNT(*) FROM users")
    max_users = "%s" % cursor.fetchone()
    cursor.execute("SELECT SUM(totalspent) FROM users")
    max_earnings = "%s" % cursor.fetchone()
    context.bot.send_message(text=f"""Кол-во пользователей: {max_users}
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
        entry_points=[CommandHandler('start', start)],
        allow_reentry=True,

        states={
            CHOOSING: [MessageHandler(Filters.regex('^О боте 👾$'), about_bot),
                       MessageHandler(Filters.regex('^О авторе 👨🏻‍💻$'), about_author),
                       MessageHandler(Filters.regex('^Пример 💶$'), custom_choice),
                       MessageHandler(Filters.regex('^Контакты 📲$'), contacts),
                       MessageHandler(Filters.regex('^Статистика 📊$'), stats),
                       MessageHandler(Filters.regex('^Хочу такого бота 🚀$'), order),
                       CommandHandler('stats', stats),
                       CommandHandler('photo', photo),
                       CommandHandler('doc', doc),
                       MessageHandler(Filters.document, echo)],

            PAYMENT:    [CallbackQueryHandler(button)],

            TYPING_REPLY: [CallbackQueryHandler(received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Назад$'), get_back)]
    )

    # Pre-checkout handler to final check
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

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
