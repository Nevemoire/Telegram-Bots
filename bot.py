# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler)#, PicklePersistence)
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

CHOOSING, SEND, FRST, JOIN, TGS, PST, PRFL, TOP = range(8)

reply_keyboard = [['Как стать топом 🚀'],
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
        update.message.reply_text('С возвращением :)', reply_markup=markup)
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
    userid = user_data['userid']
    nick = user_data['nick']
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
    reply_keyboardz = [['Назад']]
    state = ReplyKeyboardMarkup(reply_keyboardz, one_time_keyboard=True, resize_keyboard=True)
    keyboard = [[InlineKeyboardButton("Руководство по шрифтам", callback_data="fonts_guide")],
                [InlineKeyboardButton("Шаблоны для мемов", callback_data="mem_pics")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Такс, вот с чем я могу помочь тебе сейчас.", reply_markup=state)
    update.message.reply_text('Выбирай 👇', reply_markup=reply_markup)

    return TOP
  
  
def top_users_action(bot, update, user_data):
    IDS = user_data['userid']
    query = update.callback_query

    if query.data == "fonts_guide":
        bot.send_message(text="Отличный гайд по шрифтам: mdk.is/m/AgR1MP", chat_id=IDS)
        query.answer("Благодарочка Eugene_hs 😎")

        return TOP
    elif query.data == "mem_pics":
        bot.send_message(text="""Подборки с шаблонами, забирай:
1. mdk.is/m/Ag7NjA
2. mdk.is/m/Aq1YkA
3. mdk.is/m/AKkNlA
4. mdk.is/m/vnVmgv
5. mdk.is/m/v4NLYA
6. mdk.is/m/P1ZaBA
7. mdk.is/m/P6jREP
8. mdk.is/m/voOJov
9. mdk.is/m/D7JBrA
10. mdk.is/m/AE36Rv
11. mdk.is/m/AE07MP
12. mdk.is/m/AWaqbv
13. mdk.is/m/DLMnJv""", chat_id=IDS, disable_web_page_preview=True)
        query.answer("Благодарочка Eugene_hs и leriben 😎")
        
        return TOP
    else:
        update.message.reply_text("Ошибка!")

        return TOP


def contact_us(bot, update):
    update.message.reply_text('Остались вопросы? Напиши нам: @wimhelpBot')

    return CHOOSING


def join_us(bot, update, user_data):
    user = user_data['userid']
    cursor.execute("SELECT cheated FROM users WHERE id=%s", (user,))
    cheated = "%s" % cursor.fetchone()
    cursor.execute("SELECT joined FROM users WHERE id=%s", (user,))
    joined = "%s" % cursor.fetchone()
    if '1' in cheated:
        update.message.reply_text('''Мы уже поймали тебя на обмане, теперь эта функция заблокирована.

Если ты считаешь что произошла ошибка, пиши: @wimhelpBot''', reply_markup=markup)
        
        return CHOOSING
    elif '1' in joined:
        update.message.reply_text('''Ты уже подавал заявку. Если она всё-ещё не обработана, ожидай подтверждения :)

Если подтверждение длится дольше 2 часов, пиши: @wimhelpBot''', reply_markup=markup)
        
        return CHOOSING
    else:
        update.message.reply_text('Такс, напиши сюда свой юзернейм из приложения. (Пример: admin)')

        return JOIN


def user_join(bot, update, user_data):
    user = user_data['userid']
    name = user_data['name']
    nick = user_data['nick']
    cursor.execute("SELECT mdkname FROM users WHERE mdkname IS NOT NULL")
    users = "%s" % cursor.fetchall()
    mdkname = update.message.text
    if mdkname in users:
        update.message.reply_text('Засранец, этот пользователь уже подтверждён. За попытку обмана мы отбираем возможность подтвердить свой аккаунт.', reply_markup=markup)
        bot.send_message(text=f'''Пользователь {name} (@{nick}) попытался наебать систему и использовать ник {mdkname}
ID: {user}''', chat_id='@whoismdkadmins')
        cursor.execute("UPDATE users SET cheated = 1 WHERE id=%s", (user,))
        conn.commit()
        
        return CHOOSING
    else:
        bot.send_message(text=f'''Пользователь {name} (@{nick}) запросил подтверждение на ник: {mdkname}
ID: {user}''', chat_id='@whoismdkadmins')
        update.message.reply_text(f'''Заявка принята.
Код подтверждения: {user}''', reply_markup=markup)
        update.message.reply_text('Теперь укажи этот код в комментариях к публикации: example.com')
        cursor.execute("UPDATE users SET joined = 1 WHERE id=%s", (user,))
        conn.commit()

        return CHOOSING


def get_id(bot, update):
    update.message.reply_text(update.message.from_user.id)

    return CHOOSING


def media_links(bot,update):
    update.message.reply_text('LINKS')

    return CHOOSING


def profile(bot,update, user_data):
    IDS = user_data['userid']
    cursor.execute("SELECT mdkname FROM users WHERE id=%s", (IDS,))
    mdkname = "%s" % cursor.fetchone()
    cursor.execute("SELECT toppost FROM users WHERE id=%s", (IDS,))
    toppost = "%s" % cursor.fetchone()
    cursor.execute("SELECT tags FROM users WHERE id=%s", (IDS,))
    tags = "%s" % cursor.fetchone()
    reply_keyboardz = [['Назад']]
    state = ReplyKeyboardMarkup(reply_keyboardz, one_time_keyboard=True, resize_keyboard=True)
    keyboard = [[InlineKeyboardButton("Изменить лучший пост", callback_data="change_toppost")],
                [InlineKeyboardButton("Изменить теги", callback_data="change_tags")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'''Имя пользователя MDK: {mdkname}
Лучший пост: {toppost}
Теги: {tags}''', reply_markup=state)
    update.message.reply_text('Выбери действие 👇', reply_markup=reply_markup)

    return PRFL
  
  
def profile_action(bot, update, user_data):
    IDS = user_data['userid']
    query = update.callback_query

    if query.data == "change_tags":
        bot.send_message(text="Напиши сюда новые теги одним сообщением.", chat_id=IDS)

        return TGS
    elif query.data == "change_toppost":
        bot.send_message(text="Укажи новую ссылку на лучший пост.", chat_id=IDS)
        query.answer("Только без 'http://', так будет красивее 😎")
        
        return PST
    else:
        update.message.reply_text("Ошибка!")

        return PRFL
      
      
def custom_tags(bot, update, user_data):
    IDS = user_data['userid']
    new_tags = update.message.text
    cursor.execute("UPDATE users SET tags = %s WHERE id=%s", (new_tags, IDS))
    conn.commit()
    update.message.reply_text(f"Готово! Новые теги: {new_tags}", reply_markup=markup)
    
    return CHOOSING
  
  
def custom_toppost(bot, update, user_data):
    IDS = user_data['userid']
    new_toppost = update.message.text
    cursor.execute("UPDATE users SET toppost = %s WHERE id=%s", (new_toppost, IDS))
    conn.commit()
    update.message.reply_text(f"Готово! Новая ссылка: {new_toppost}", reply_markup=markup)
    
    return CHOOSING


def add_user(bot, update):
    update.message.reply_text('ADD')

    return CHOOSING


def message(bot, update, user_data):
    reload(config)
    user = str(user_data['userid'])
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
        "SELECT mdkname, toppost, tags FROM users WHERE mdkname IS NOT NULL AND tags IS NOT NULL AND toppost IS NOT NULL ORDER BY RANDOM() LIMIT 1")
    update.message.reply_text('''*Автор:* %s
*Лучший пост:* %s
*Теги:* %s''' % cursor.fetchone(), parse_mode='MARKDOWN')

    return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    #pp = PicklePersistence(filename='conversationbot')
    updater = Updater(os.environ['token'])#, persistence=pp)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states=
        {
            CHOOSING:
                [
                    RegexHandler('^FAQ$', bot_faq),
                    RegexHandler('^Как стать топом 🚀$', top_users),
                    RegexHandler('^Случайный автор$', random_user),
                    RegexHandler('^Подать заявку$', join_us, pass_user_data=True),
                    RegexHandler('^Полезные ссылки$', media_links),
                    RegexHandler('^Обратная связь$', contact_us),
                    RegexHandler('^Личный кабинет$', profile, pass_user_data=True),
                    # RegexHandler('^Проверить подписку$', first_time),
                    CommandHandler('add', add_user),
                    CommandHandler('stats', stats),
                    CommandHandler('id', get_id),
                    CommandHandler('send', message, pass_user_data=True)],

            FRST:
                [MessageHandler(Filters.text, first_time, pass_user_data=True)],

            SEND:
                [MessageHandler(Filters.text, message_send)],
          
            JOIN:
                [MessageHandler(Filters.text, user_join, pass_user_data=True)],
            TGS:
                [MessageHandler(Filters.text, custom_tags, pass_user_data=True)],
            PST:
                [MessageHandler(Filters.text, custom_toppost, pass_user_data=True)],
            PRFL:
                [CallbackQueryHandler(profile_action, pass_user_data=True),
            TOP:
                [CallbackQueryHandler(top_users_action, pass_user_data=True)],
        },

        fallbacks=[RegexHandler('^Назад$', get_back),
                   CommandHandler('help', restore)],
        allow_reentry=True
        #name="my_conversation",
        #persistent=True
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
