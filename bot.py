#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler)

import logging
import psycopg2
import config
import os
import datetime
from importlib import reload

conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'], host=os.environ['host'])

cursor = conn.cursor()

now = datetime.datetime.now()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

(CHOOSING, FRST, PREFRST, OK, UN, UP, PR, TYPING_REPLY,
 PROMOCODE, PAYMENT, CHECKOUT, SUC_PAYMENT, PRFL) = range(13)

reply_keyboard = [['Бесплатная подписка', 'Платная подписка'],
                  ['Ввести промокод', 'Стать партнёром'],
                  ['Связь с нами', 'Личный кабинет']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
first_keyboard = [['Проверить подписку']]
first = ReplyKeyboardMarkup(first_keyboard, one_time_keyboard=True, resize_keyboard=True)

commands = ('Бесплатная подписка, Платная подписка, Ввести промокод,'
            'Связь с нами, Стать партнёром, Личный кабинет, Я блоггер, Я администратор')
ignorelist = commands.split(', ')
members = 'creator, administrator, member'
memberslist = members.split(', ')
back = 'Назад'


def start(bot, update, user_data):
    name = update.message.from_user.full_name
    update.message.reply_text(
        f'Привет, {name}!')
    nick = update.message.from_user.username
    userid = update.message.from_user.id
    user_data['usrid'] = userid
    user_data['username'] = nick
    user_data['name'] = name
    member = bot.get_chat_member('@bigbetz', userid)
    if member.status in memberslist:
        update.message.reply_text('''Я твой персональный бот-прогнозист!
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
        update.message.reply_text(
            'Для начала, будь добр(-а), подпишись на наш главный канал: @bigbetz', reply_markup=first)

        return FRST


def first_time(bot, update, user_data):
    userid = user_data['usrid']
    nick = user_data['username']
    name = user_data['name']
    member = bot.get_chat_member('@bigbetz', userid)
    if member.status in memberslist:
        update.message.reply_text('Благодарим за подписку! :)', reply_markup=markup)
        update.message.reply_text('''Я твой персональный бот-прогнозист!
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
        update.message.reply_text('Ошибка! Проверь что ты подписался(-ась) на канал @bigbetz '
                                  'и нажми кнопку заново.', reply_markup=first)

        return FRST


def delete_promos(bot, update):
    cursor.execute("UPDATE users SET (promo, mypromo) VALUES (NULL, NULL) WHERE id=391206263")
    update.message.reply_text("Готово.")
      
      
def add_partner(bot, update, user_data):
    reload(config)
    user = str(user_data['usrid'])
    if user in config.admin:
        update.message.reply_text('Введи юзернейм. (Без @)')

        return UN
    else:
        update.message.reply_text('Ты не админ.')

        return CHOOSING


def message(bot, update, user_data):
    reload(config)
    user = str(user_data['usrid'])
    if user in config.admin:
        update.message.reply_text('Введи прогноз на событие.')

        return PR
    else:
        update.message.reply_text('Ты не админ.')

        return CHOOSING


def message_pr(bot, update):
    sends = -1
    prediction = update.message.text
    cursor.execute("SELECT id FROM users WHERE free_sub = 1")
    while True:
        chat_id = '%s' % cursor.fetchone()
        sends += 1
        if chat_id == 'None':
            break
        bot.send_message(text=prediction, chat_id=chat_id)
    update.message.reply_text(f'Кол-во отосланных предиктов: {sends}')

    return CHOOSING


def partner_un(bot, update, user_data):
    username = update.message.text
    update.message.reply_text('@' + username)
    user_data['partner'] = username
    update.message.reply_text('Введи промокод для пользователя @' + username)

    return UP


def partner_promo(bot, update, user_data):
    promocode = update.message.text
    username = user_data['partner']
    name = user_data['name']
    update.message.reply_text(promocode)
    cursor.execute("UPDATE users SET mypromo = %s WHERE nickname=%s", (promocode, username))
    update.message.reply_text('Готово!')
    conn.commit()
    cursor.execute("SELECT id FROM users WHERE nickname=%s", (username,))
    chatid = "%s" % cursor.fetchone()
    try:
        bot.send_message(
            text=f'''{name}, мы изменили ваш промокод. Узнать новый можно в личном кабинете. С уважением, команда BIG Betz.''', chat_id=int(chatid))
    except:
        bot.send_message(
            text=f'Пользователь {chatid} ({username}) не получил уведомление.', chat_id='@bigbetz_orders')

    return CHOOSING


def profile(bot, update):
    reply_keyboardz = [['Назад']]
    state = ReplyKeyboardMarkup(reply_keyboardz, one_time_keyboard=True, resize_keyboard=True)
    keyboard = [[InlineKeyboardButton("Мой промокод", callback_data="promocode")],
                [InlineKeyboardButton("Счётчик рефералов", callback_data="promo_patrons")],
                [InlineKeyboardButton("Баланс", callback_data="balance"),
                 InlineKeyboardButton("Статистика", callback_data="stats")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Добро пожаловать в личный кабинет.', reply_markup=state)
    update.message.reply_text('Выбери действие 👇', reply_markup=reply_markup)

    return PRFL


def profile_action(bot, update, user_data):
    IDS = user_data['usrid']
    cursor.execute("SELECT mypromo FROM users WHERE id=%s", (IDS,))
    promocode = "%s" % cursor.fetchone()
    query = update.callback_query

    if query.data == "promocode":
        if promocode == "None":
            query.answer("Ты не являешься партнёром.")

            return PRFL
        else:
            query.answer("Промокод: " + promocode)

            return PRFL
    elif query.data == "promo_patrons":
        cursor.execute("SELECT COUNT(*) FROM users WHERE promo=%s", (promocode,))
        patrons = "%s" % cursor.fetchone()
        query.answer("У тебя " + patrons + " рефералов")

        return PRFL
    elif query.data == "balance":
        cursor.execute("SELECT earnings FROM users WHERE id=%s", (IDS,))
        earnings = "%s" % cursor.fetchone()
        query.answer("К выплате: " + earnings + " рублей")
    elif query.data == "stats":
        query.answer("Статистика 👇")
        stats(bot, update, user_data)

        return PRFL
    else:
        update.message.reply_text("Ошибка!")

        return PRFL


def contact_us(bot, update):
    update.message.reply_text("""По всем вопросам писать: @daaetoya
Сразу уточняйте *причину* обращения.
*Важно!* Рассматриваются только сообщения с пометками: #Реклама, #Сотрудничество, #Баг.""", parse_mode='MARKDOWN'
                              , reply_markup=markup)

    return CHOOSING


def partnership(bot, update, user_data):
    ID = user_data['usrid']
    cursor.execute('SELECT is_partner FROM users WHERE id=%s', (ID,))
    ppartner = '%s' % cursor.fetchone()
    if ppartner == '1':
        update.message.reply_text('Ты уже являешься партнёром.')

        return CHOOSING
    else:
        update.message.reply_text('Укажи свой промокод (Оптимальное кол-во символов: 4).')

        return OK


def confirmation(bot, update, user_data):
    text = update.message.text
    cursor.execute("SELECT mypromo FROM users WHERE mypromo IS NOT NULL")
    promolist = "%s" % cursor.fetchall()
    if text in ignorelist:
        update.message.reply_text('Сейчас бот не реагирует на эту комманду.')
        pass

        return OK
    elif text in back:
        update.message.reply_text('Главное меню 👾', reply_markup=markup)

        return CHOOSING
    elif text in promolist:
        update.message.reply_text('Такой промокод уже есть! Введи другой.')
        
        return OK
    else:
        update.message.reply_text('''Готово! Теперь ты официальный партнёр BIG Betz 😎''', reply_markup=markup)
        User = user_data['usrid']
        Nick = user_data['username']
        Promo = update.message.text
        cursor.execute("UPDATE users SET mypromo = %s WHERE id=%s", (Promo, User))
        cursor.execute("UPDATE users SET is_partner = 1 WHERE id=%s", (User,))
        conn.commit()
        bot.send_message(
            text=f'Пользователь {User} (@{Nick}) стал партнёром. Promo: {Promo}', chat_id='@bigbetz_orders')

        return CHOOSING


def free_subscription(bot, update, user_data):
    usrid = user_data['usrid']
    cursor.execute('SELECT free_sub FROM users WHERE id = %s', (usrid,))
    if_sub = "%s" % cursor.fetchone()
    if if_sub == '0':
        update.message.reply_text('Ты успешно подписался(-ась) на бесплатную рассылку.')
        cursor.execute("UPDATE users SET free_sub = 1 WHERE id=%s", (usrid,))
    elif if_sub == '1':
        update.message.reply_text('Ты успешно отписался(-ась) от бесплатной рассылки.')
        cursor.execute("UPDATE users SET free_sub = 0 WHERE id=%s", (usrid,))
    else:
        update.message.reply_text('Что-то пошло не так..')
    conn.commit()

    return CHOOSING


def custom_promo(bot, update, user_data):
    IDS = user_data['usrid']
    reply_keyboardz = [['Назад']]
    state = ReplyKeyboardMarkup(reply_keyboardz, one_time_keyboard=True, resize_keyboard=True)
    cursor.execute("SELECT promo FROM users WHERE id=%s", (IDS,))
    promocode = "%s" % cursor.fetchone()
    if promocode == "None":
        update.message.reply_text('Введи промокод чтобы получить скидку 20%.', reply_markup=state)

        return PROMOCODE
    else:
        update.message.reply_text('Ты уже использовал(-а) промокод :(')

        return CHOOSING


def promo(bot, update, user_data):
    code = update.message.text
    user = user_data['usrid']
    cursor.execute("SELECT mypromo FROM users WHERE id=%s", (user,))
    ownpromo = "%s" % cursor.fetchone()
    cursor.execute("SELECT mypromo FROM users WHERE mypromo IS NOT NULL")
    promolist = "%s" % cursor.fetchall()
    if code in ownpromo:
        update.message.reply_text("Свой промокод вводить нельзя! Введи другой.")
        
        return PROMOCODE
    elif code in promolist:
        update.message.reply_text("Промокод принят!")
        update.message.reply_text("Скидка на следующую оплату - 20%", reply_markup=markup)
        cursor.execute("UPDATE users SET code_active = 1 WHERE id=%s", (user,))
        cursor.execute("UPDATE users SET promo = %s WHERE id=%s", (code, user))
        cursor.execute("SELECT id FROM users WHERE mypromo = %s", (code,))
        target = "%s" % cursor.fetchone()
        cursor.execute("SELECT nickname FROM users WHERE mypromo = %s", (code,))
        username = "%s" % cursor.fetchone()
        try:
            bot.send_message(
                text='Только что 1 из пользователей использовал твой промокод.', chat_id=int(target))
        except:
            bot.send_message(
                text=f'Пользователь {target} (@{username}) не получил уведомление о новом реферале.', chat_id='@bigbetz_orders')
        conn.commit()

        return CHOOSING
    elif code in back:
        update.message.reply_text("Главное меню 👾", reply_markup=markup)

        return CHOOSING
    else:
        update.message.reply_text("Такого промокода нет! Попробуй ввести другой.")

        return PROMOCODE


def custom_choice(bot, update, user_data):
    reply_keyboardz = [['Назад']]
    state = ReplyKeyboardMarkup(reply_keyboardz, one_time_keyboard=True, resize_keyboard=True)
    keyboard = [[InlineKeyboardButton("Неделя", callback_data="1"),
                 InlineKeyboardButton("2 недели", callback_data="2")],
                [InlineKeyboardButton("Месяц", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('''Отлично 😎''', reply_markup=state)
    update.message.reply_text('Теперь выбери длительность подписки 👇', reply_markup=reply_markup)

    return TYPING_REPLY


def received_information(bot, update, user_data):
    query = update.callback_query
    user_data['choice'] = query.data
    IDS = user_data['usrid']
    # text = update.message.text
    cursor.execute("SELECT code_active FROM users WHERE id = %s", (IDS,))
    code_active = "%s" % cursor.fetchone()
    if code_active == "1":
        keyboard = [[InlineKeyboardButton("Перейти к оплате (Скидка 20%)", callback_data="Оплата")]]
    else:
        keyboard = [[InlineKeyboardButton("Перейти к оплате", callback_data="Оплата")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        cursor.execute(
            "SELECT tariff, price, patrons FROM betsdb WHERE id=%s", (query.data,))

        bot.edit_message_text(text='👇',
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
    user = user_data['usrid']
    try:
        cursor.execute("SELECT code_active FROM users WHERE id = %s", (user,))
        code_active = "%s" % cursor.fetchone()
        chat_id = update.effective_message.chat_id
        cursor.execute("SELECT tariff FROM betsdb WHERE id=%s", (IDS,))
        tariff = "%s" % cursor.fetchone()
        title = tariff
        description = "BIG Bets Company"
        # select a payload just for you to recognize its the donation from your bot
        payload = "Custom-Payload"
        # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
        provider_token = os.environ['provider_token']
        start_parameter = "test-payment"
        currency = "RUB"
        # price in dollars
        cursor.execute("SELECT price FROM betsdb WHERE id=%s", (IDS,))
        pricez = "%s" % cursor.fetchone()
        if code_active == '1':
            price = round(int(pricez) / 100 * 80)
        else:
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


def precheckout_callback(bot, update):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message="Ошибка. Оплата не принята.")
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


# finally, after contacting to the payment provider...
def successful_payment_callback(bot, update, user_data):
    IDS = user_data['choice']
    usrid = user_data['usrid']
    nick = user_data['username']
    cursor.execute("SELECT code_active FROM users WHERE id = %s", (usrid,))
    code_active = "%s" % cursor.fetchone()
    if code_active == '1':
        cursor.execute("UPDATE users SET code_active = 0 WHERE id=%s", (usrid,))
        conn.commit()
    else:
        pass
    cursor.execute("SELECT tariff FROM betsdb WHERE id=%s", (IDS,))
    tariff = "%s" % cursor.fetchone()
    # do something after successful receive of payment?
    update.effective_message.reply_text('''Благодарим за оплату!
Ожидай, мы скоро добавим тебя в закрытую группу.''', reply_markup=markup)
    cursor.execute("UPDATE betsdb SET patrons = patrons+1 WHERE id=?", (IDS,))
    cursor.execute("SELECT price FROM betsdb WHERE id=%s", (IDS,))
    product_price = "%d" % cursor.fetchone()
    if code_active == '1':
        tsprice = round(int(product_price) * 0.8)
    else:
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
    bot.send_message(
        text=f'''Пользователь {usrid} (@{nick}) оплатил {tsprice} рублей.
Тариф: {tariff}.
Дата: {now.day}.{now.month}.{now.year}''', chat_id='@bigbetz_orders')


def get_back(bot, update):
    update.message.reply_text("Главное меню 👾", reply_markup=markup)

    return CHOOSING


def paid_sub(bot, update):
    update.message.reply_text('''Эта функция пока-что недоступна.
Однако, у тебя есть *возможность* вступить в наш закрытый чат по предоплате и получить *скидку 50%*.
Текущие расценки _(без скидки)_:
*Неделя* - 1500р.
*2 недели* - 2500р.
*Месяц* - 4000р.
Писать: @daaetoya''', parse_mode='MARKDOWN')

    return CHOOSING


def stats(bot, update, user_data):
    userid = user_data['usrid']
    cursor.execute("SELECT COUNT(*) FROM users")
    max_users = "%s" % cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM users WHERE mypromo IS NOT NULL")
    max_partners = "%s" % cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM users WHERE promo IS NOT NULL")
    max_referrals = "%s" % cursor.fetchone()
    cursor.execute("SELECT SUM(earnings) FROM users WHERE mypromo IS NOT NULL")
    max_earnings = "%s" % cursor.fetchone()
    bot.send_message(text=f"""Кол-во пользователей: {max_users}
Кол-во партнёров: {max_partners}
Кол-во привлечённых пользователей: {max_referrals}
Наши партнёры заработали: {max_earnings} рублей""", chat_id=userid)

    return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def partner_beta(bot, update):
    update.message.reply_text('Эта функция пока-что недоступна. Следи за новостями в нашем канале: @BIGBetz')

    return CHOOSING


def restore(bot, update):
    update.message.reply_text('Исправлено!', reply_markup=markup)

    return CHOOSING


def rules(bot, update):
    update.message.reply_text('''*Правила BIG Betz*
    
1. Пользоваться ботом могут только лица достигшие совершеннолетия (18+).
2. Перед оплатой убедись что в настройках профиля поле @username не пустое.
3. Заново проверь пункт 2.

_* - если пункт 2 нарушен, мы не сможем добавить тебя в закрытую группу.
Такая оплата расценивается как пожертвование и возврату не подлежит._
''', parse_mode='MARKDOWN')

    return CHOOSING


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ['token'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            CHOOSING:
                [
                 RegexHandler('^Ввести промокод$', custom_promo, pass_user_data=True),
                 RegexHandler('^Связь с нами$', contact_us),
                 RegexHandler('^Стать партнёром$', partnership, pass_user_data=True),
                 RegexHandler('^Платная подписка$', paid_sub),
                 # RegexHandler('^Платная подписка$', custom_choice, pass_user_data=True),
                 RegexHandler('^Бесплатная подписка$', free_subscription, pass_user_data=True),
                 RegexHandler('^Личный кабинет$', profile),
                 RegexHandler('^Проверить подписку$', first_time),
                 CommandHandler('add', add_partner, pass_user_data=True),
                 CommandHandler('stats', stats, pass_user_data=True),
                 CommandHandler('delete', delete_promos),
                 CommandHandler('send', message, pass_user_data=True)],

            FRST:
                [MessageHandler(Filters.text, first_time, pass_user_data=True)],

            PRFL:
                [CallbackQueryHandler(profile_action, pass_user_data=True)],

            OK:
                [MessageHandler(Filters.text, confirmation, pass_user_data=True)],

            UN:
                [MessageHandler(Filters.text, partner_un, pass_user_data=True)],

            UP:
                [MessageHandler(Filters.text, partner_promo, pass_user_data=True)],

            PR:
                [MessageHandler(Filters.text, message_pr)],

            PROMOCODE:
                [MessageHandler(Filters.text, promo, pass_user_data=True)],

            PAYMENT:
                [CallbackQueryHandler(button, pass_user_data=True)],

            TYPING_REPLY: [CallbackQueryHandler(received_information, pass_user_data=True)],
                },

        fallbacks=[RegexHandler('^Назад$', get_back),
                   CommandHandler('help', restore),
                   CommandHandler('rules', rules)]
    )
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

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
