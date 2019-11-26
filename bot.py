#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples


"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import random
import os
import actions
from telegram.ext.dispatcher import run_async
import uuid
from uuid import uuid4
import psycopg2


from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent #, InlineQueryResultCachedAudio
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, ConversationHandler


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ID, MESSAGE = range(2)


members = 'creator, administrator, member'
memberslist = members.split(', ')


conn = psycopg2.connect(dbname='daqpsemmol11kn', user='fnwjyuhqrjdbcv', 
                        password='4ae63588868e2423ddb7cc3bd4e71ae5892179b86dca5a90272b747aa933bac9', host='ec2-46-137-75-170.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
@run_async
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Здарова! Все новости я выкладываю здесь: @rozbiynuki')
    user_says = " ".join(context.args)
    if user_says is not "":
      update.message.reply_text("Ты сказал: " + user_says)
    else:
      pass


def setbd(update, context):
	cursor.execute("""create table users (
id int,
fullname varchar(50) NOT NULL,
username varchar(50) NOT NULL,
balance int NOT NULL,
PRIMARY KEY (id)
);""")
	conn.commit()
	update.message.reply_text('Таблица создана')


def registration(update, context):
	ids = update.message.from_user.id
	fullname = update.message.from_user.full_name
	username = update.message.from_user.username
	balance_Query = "select balance from users where id = %s"
	cursor.execute(balance_Query, (ids,))
	balance = cursor.fetchone()
	error = "None"	
	if error not in str(balance):
		update.message.reply_text('*Ошибка!* Регистрироваться можно только один раз!', parse_mode='MARKDOWN')
	elif (error in str(fullname) or error in str(username)):
		update.message.reply_text('*Ошибка!* _Name_ или _Username_ имеют пустое значение.', parse_mode='MARKDOWN')
	else:
		registration_Query = "INSERT INTO users (id, fullname, username, balance) VALUES (%s, %s, %s, 0)"
		cursor.execute(registration_Query, (ids, fullname, username,))
		conn.commit()
		update.message.reply_text('Регистрация пройдена успешно.')


def getInfo(update, context):
	usrid = update.message.from_user.id
	user_info_Query = "select * from users where id = %s"

	cursor.execute(user_info_Query, (usrid,))
	info = cursor.fetchall()
	for row in info:
		update.message.reply_text(f"""
*Name*: {row[1]}
*Username*: {row[2]}
*Balance*: {row[3]}
*ID*: {row[0]}""", parse_mode="MARKDOWN")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')
    
    
# @run_async  
# def getAudio(update, context):
    # audio = update.message.audio
    # update.message.reply_text(audio.file_id)

@run_async  
def getId(update, context):
    ids = update.message.chat.id
    context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    context.bot.sendMessage(chat_id=update.message.chat.id, text=f'*ID* группы: {ids}\nКопировать без знака "-"!', parse_mode='MARKDOWN')
    
    
@run_async
def echo(update, context):
    text = update.message.text
    userid = update.message.from_user.id
    member = context.bot.get_chat_member('@rozbiynuki', userid)
    command1 = '!8ball'
    command2 = '!love'
    command3 = '!ping'
    gambling1 = '!coinflip'
    invoker = update.message.from_user.full_name
    ginvoker = update.message.from_user.username

    if member.status in memberslist:
      if command1 in update.message.text:
          update.message.reply_text(
              f'Такс.. Розбійник посовещался с паном президентом и говорит: {random.choice(actions.action3)}')
      elif command2 in update.message.text:
      	  target = text.partition(' ')[2]
      	  update.message.reply_text(
              f'Здесь {random.randrange(101)}% совместимости между {invoker} и {target}')
      elif command3 in update.message.text:
      	  update.message.reply_text(update.message.chat.id)
      elif gambling1 in update.message.text:  
      	  try:
      	  	gtarget = text.split(maxsplit=3)[1]
      	  	summ = text.split(maxsplit=3)[2]
      	  	id_Query = "select * from users where username = %s"
      	  	cursor.execute(id_Query, (gtarget,))
      	  	gtarget_id = cursor.fetchall()
      	  	for row in gtarget_id:
      	  		try:
      	  			summint=int(summ)
      	  		except:
      	  			update.message.reply_text('Жаль, но ты не можешь расплатиться своей *натурой* вместо *монет*:(', parse_mode='MARKDOWN')
      	  			break
      	  		
      	  		update.message.reply_text(f'*{ginvoker}* предложил *{gtarget}* сыграть в _Coinflip_ на сумму: *{summint}* монет.', parse_mode="MARKDOWN")
      	  		context.bot.send_message(chat_id=row[0], text=f'{invoker} предлагает тебе сыграть в _Coinflip_ на {summint} монет.', parse_mode="MARKDOWN")

      	  except:
      	  	update.message.reply_text(f'''*Ошибка!* Возможные причины:
*1)* Не могу написать пользователю:(\nПопроси его начать со мной переписку.
*2)* Неправильный формат запроса.\nУбедись что он выглядит примерно так: !coinflip username 100''', parse_mode="MARKDOWN")
      else:
          pass
    else:
      if (command1 in update.message.text or command2 in update.message.text):
        update.message.reply_text('''Ненене, так не пойдёт.
Для начала подпишись на: @Rozbiynuki''')
      else:
        pass


def delete(update, context):
	cursor.execute("TRUNCATE TABLE users")
	conn.commit()


@run_async
def inlinequery(update, context):
    """Handle the inline query."""
    userid = update.inline_query.from_user.id
    target = update.inline_query.query
    name = update.inline_query.from_user.full_name
    member = context.bot.get_chat_member('@rozbiynuki', userid)
    if member.status not in memberslist:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Подпишись на @rozbiynuki!",
                input_message_content=InputTextMessageContent(
                    message_text=f'{name} повязал(-a) сам(-a) себя..\nКажется, причина в отсутствии подписки на <a href="https://t.me/rozbiynuki">наш</a> канал.', parse_mode='HTML', disable_web_page_preview=True))]

        update.inline_query.answer(results)
    elif '@everyone' in str(target):
        chances = random.randint(1,100)
        if int(chances) < 90:
            results = [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Вяжем всех!",
                    input_message_content=InputTextMessageContent(
                        message_text=f'{name} попытался(-ась) повязать весь чатик.\nТеперь его/её ожидает бутылка правосудия.'))]
        else:
            results = [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Вяжем всех!",
                    input_message_content=InputTextMessageContent(
                        message_text=f'{name} повязал(-a) весь чатик!\nВсе пользователи отправляются в обезъянник.'))]
    elif '@' not in str(target):
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Укажи @username или @everyone!",
                input_message_content=InputTextMessageContent(
                    message_text=f'{name} повязал(-a) сам(-a) себя..\nКак же так произошло..'))]

        update.inline_query.answer(results)
    elif (member.status in memberslist) and ('@' in str(target)):
        results = [
            #InlineQueryResultCachedAudio(
                #id=uuid4(),
                #audio_file_id='CQADBAADIBAAAjsPuFMvbgABZjW0M5cWBA'),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Вяжем " + update.inline_query.query,
                input_message_content=InputTextMessageContent(
                    message_text=f'{name} {random.choice(actions.action1)} {target} {random.choice(actions.action2)}'))]

        update.inline_query.answer(results)

    else:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="FATAL ERROR",
                input_message_content=InputTextMessageContent(
                    message_text=f'{name} застрял(-а) в пространстве и времени..'))]

        update.inline_query.answer(results)


def anon(update, context):
    userid = update.message.from_user.id
    member = context.bot.get_chat_member('@rozbiynuki', userid)
    if member.status in memberslist:
    	update.message.reply_text(
        	'''Наконец что-то интересненькое ;)

Для начала, отправь мне *ID* чата, куда хочешь написать.
*Как получить ID?* Просто отправь в чат комманду /id.
_Не волнуйся, бот быстренько удалит твоё сообщение, никто не спалит._

*P.S.* Ты же вкурсе, чтобы сообщение отправилось, я должен присутствовать в этом чате? Конечно, вкурсе.

/cancel - чтобы отменить.''',
        	parse_mode='MARKDOWN')
    	context.user_data['user'] = update.message.from_user.full_name

    	return ID
    else:
        update.message.reply_text('''Ненене, так не пойдёт.
Для начала подпишись на: @Rozbiynuki''')
	
        return ConversationHandler.END


def anonId(update, context):
    context.user_data['groupid'] = update.message.text
    update.message.reply_text('Отлично, теперь напиши сообщение для отправки.')

    return MESSAGE


def anonMessage(update, context):
    groupid = context.user_data['groupid']
    user = context.user_data['user']
    message = update.message.text
    try:
        context.bot.sendMessage(chat_id=f'-{groupid}', text=f'*Какой-то анон написал(-а):*\n{message}', parse_mode='MARKDOWN')
        context.bot.sendMessage(chat_id=-1001184148918, text=f'*{user} написал(-а):*\n{message}', parse_mode='MARKDOWN')

        return ConversationHandler.END
    except:
        update.message.reply_text(f'Что-то пошло не так :(\nТы точно удалил(-а) знак "-" перед числами?')

        return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Эх! В этот раз без интрижек:(')

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # REQUEST_KWARGS={
    # 'proxy_url': 'socks5h://207.180.238.12:1080',}
    # updater = Updater('972573533:AAEGNRCTQd_x4e6j3W6Z36pa8bNFAKkn7Vg', request_kwargs=REQUEST_KWARGS, use_context=True)
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("id", getId))
    dp.add_handler(CommandHandler("set", setbd))
    dp.add_handler(CommandHandler("del", delete))
    dp.add_handler(CommandHandler("info", getInfo))
    dp.add_handler(CommandHandler("reg", registration))
    # dp.add_handler(MessageHandler(Filters.audio, getAudio))
    dp.add_handler(MessageHandler(Filters.text, echo))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("anon", anon)],

    states={
           	ID: [MessageHandler(Filters.text, anonId)],
           	MESSAGE: [MessageHandler(Filters.text, anonMessage)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
