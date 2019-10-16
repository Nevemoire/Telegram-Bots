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
from telegram.ext.dispatcher import run_async
import psycopg2


from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ID, MESSAGE, TOTAL = range(3)


members = 'creator, administrator, member'
memberslist = members.split(', ')


conn = psycopg2.connect(dbname='d3p95g4d436dvm', user='gogkpkgabilgaj', 
                        password='984caca9804921aaba645e063270277f0aca1cf316578740c29104822e91254c', host='ec2-54-228-252-67.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()

bot_link = 'telegram.me/therozbiynukbot'
bot_username = '@therozbiynukbot'
channel_username = '@mdkcasino'


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
@run_async
def start(update, context):
	"""Send a message when the command /start is issued."""
	ids = update.message.from_user.id
	fullname = update.message.from_user.full_name
	usern = update.message.from_user.username
	username = usern.lower()
	# balance_Query = 
	id_Query = 'select "balance" from userz where id = %s'
	cursor.execute(id_Query, (ids,))
	balance = cursor.fetchone()
	error = "None"	
	if error not in str(balance):
		pass
	elif (error in str(fullname) or error in str(username)):
		update.message.reply_text('''Приветствуем тебя в нашем клубе!

Запомни, первое правило клуба - веселись. Больше никаких правил ;)''')
		update.message.reply_text('''*Ты у нас впервые?*
Чтобы иметь возможность играть у нас, поля _Name_ и _Username_ не должны быть пустыми.
Исправь ситуацию и напиши мне /reg :)''', parse_mode='MARKDOWN')
	else:
		update.message.reply_text('''Приветствуем тебя в нашем клубе!

Запомни, первое правило клуба - веселись. Больше никаких правил ;)''')
		registration_Query = "INSERT INTO userz (id, fullname, username, balance) VALUES (%s, %s, %s, 0)"
		cursor.execute(registration_Query, (ids, fullname, username,))
		conn.commit()
		update.message.reply_text('*Ты у нас впервые?*\nТвой профиль успешно создан, для справки введи /info ;)')

	user_says = " ".join(context.args)
	if user_says is not "":
		invoker = update.message.from_user.id
		error = 'None'
		cursor.execute('SELECT refferrer FROM userz WHERE id = %s', (invoker,))
		promo_used = cursor.fetchone()
		cursor.execute('SELECT id FROM userz')
		totalb = cursor.fetchall()
		if user_says not in str(totalb):
			update.message.reply_text('Такого промокода не существует.')
			update.message.reply_text(totalb)
		elif user_says in str(invoker):
			update.message.reply_text('Свой промокод использовать нельзя!')
		elif error not in str(promo_used):
			update.message.reply_text('Упси, промокод можно использовать только 1 раз.')
		else:
			cursor.execute('UPDATE userz SET balance = balance + 20 WHERE id = %s', (user_says,))
			cursor.execute('UPDATE userz SET reffs = reffs + 1, balance = balance + 100, refferrer = %s WHERE id = %s', (user_says, invoker,))
			update.message.reply_text('Промокод принят. (+100 монет тебе и +20 владельцу промокода)')
			conn.commit()
	else:
		pass


def registration(update, context):
	ids = update.message.from_user.id
	fullname = update.message.from_user.full_name
	usern = update.message.from_user.username
	username = usern.lower()
	# balance_Query = 
	id_Query = 'select "balance" from userz where id = %s'
	cursor.execute(id_Query, (ids,))
	balance = cursor.fetchone()
	error = "None"	
	if error not in str(balance):
		update.message.reply_text('*Ошибка!* Регистрироваться можно только один раз!', parse_mode='MARKDOWN')
	elif (error in str(fullname) or error in str(username)):
		update.message.reply_text('*Ошибка!* _Name_ или _Username_ имеют пустое значение.', parse_mode='MARKDOWN')
	else:
		registration_Query = "INSERT INTO userz (id, fullname, username, balance) VALUES (%s, %s, %s, 0)"
		cursor.execute(registration_Query, (ids, fullname, username,))
		conn.commit()
		update.message.reply_text('Регистрация пройдена успешно.')


def getInfo(update, context):
	usrid = update.message.from_user.id
	cursor.execute('SELECT id FROM userz')
	all_users = cursor.fetchall()
	try:
		target = update.message.reply_to_message.from_user.id
		if '/info' in update.message.reply_to_message.text:
			pass
		elif str(target) in str(all_users):
			target_info_Query = "select * from userz where id = %s"
			cursor.execute(target_info_Query, (target,))
			target_info = cursor.fetchall()
			for row in target_info:
				update.message.reply_text(f"""
*Name*: {row[1]}
*Username*: {row[2]}
*Balance*: {row[3]}
*ID*: {row[0]}""", parse_mode="MARKDOWN")

				return

		else:
			update.message.reply_text('Ошибка! Этого пользователя нет в нашей базе данных.')

			return

	except:
		pass

	user_info_Query = "select * from userz where id = %s"

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
    
    
# def echo(update, context):
#     """Send a message when the command /help is issued."""
#     update.message.reply_text('''Искусственный интеллект мне пока что не приделали, поэтому давай общаться понятным языком ;)\nДоступные комманды:

# /coinflip - создать дуэль (1х1)
# /roulette - *в разработке...*    	
# /info - информация по твоему профилю
# /promo - система промокодов
# /help - помощь и другая информация''', parse_mode='MARKDOWN')


def getPromo(update, context):
	ids = update.message.from_user.id
	cursor.execute('SELECT reffs FROM userz where id = %s', (ids,))
	reffs = cursor.fetchone()
	cursor.execute('SELECT refferrer FROM userz where id = %s', (ids,))
	ref = cursor.fetchone()
	update.message.reply_text(f'Твой промокод: {ids}\nИсп. промокод: {ref[0]}\nКол-во реффералов: {reffs[0]}\n\nЧтобы человек активировал твой промокод, ему/ей нужно написать боту:')
	update.message.reply_text(f"/start {ids}")

@run_async  
def getId(update, context):
    ids = update.message.chat.id
    context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
    context.bot.sendMessage(chat_id=update.message.chat.id, text=f'*ID* группы: {ids}\nКопировать без знака "-"!', parse_mode='MARKDOWN')


@run_async
def coinflip(update, context):
	context.user_data['game'] = 'coinflip'
	inv_user_id = update.message.from_user.id
	user_balance = "select balance from userz where id = %s"
	cursor.execute(user_balance, (inv_user_id,))
	balance = cursor.fetchone()
	update.message.reply_text(f'`Coinflip` 🌕\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')

	return TOTAL


@run_async
def roulette(update, context):
	context.user_data['game'] = 'roulette'
	inv_user_id = update.message.from_user.id
	user_balance = "select balance from userz where id = %s"
	cursor.execute(user_balance, (inv_user_id,))
	balance = cursor.fetchone()
	update.message.reply_text(f'`Roulette` 🎰\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')

	return TOTAL


@run_async
def Total(update, context):
	game = context.user_data['game']
	invoker = update.message.from_user.full_name
	inv_user = update.message.from_user.username
	inv_user_id = update.message.from_user.id
	user_balance = "select balance from userz where id = %s"
	cursor.execute(user_balance, (inv_user_id,))
	balance = cursor.fetchone()
	total = update.message.text
	try:
		summ = int(total)
	except:
		update.message.reply_text('Жаль, но мы не принимаем ничего, кроме монет.\nДа, натурой тоже не принимаем :(\n\nВведи *целое* число.\nОтмена - /cancel', parse_mode='MARKDOWN')

		return TOTAL

	if summ < 100:
		update.message.reply_text('Так не пойдёт, возвращайся в другой раз.')

		return ConversationHandler.END
	elif summ > 100000:
		update.message.reply_text('Превышен лимит, может как-нибудь в другой раз ;)')

		return ConversationHandler.END
	elif summ > int(balance[0]):
		update.message.reply_text('Недостаточно монет.')

		return ConversationHandler.END
	elif (summ >= 100) and (summ <= 100000) and game == 'coinflip':
		keyboard = [[InlineKeyboardButton('Присоединиться к игре 🤠', callback_data=f'coinflip {inv_user_id} {summ}')],
					[InlineKeyboardButton('Открыть диалог с ботом 👾', url=bot_link)]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=channel_username, text=f'`Coinflip` 🌕\n\n*Создатель*: {invoker} (@{inv_user})\n*Ставка*: {summ} монет', parse_mode='MARKDOWN', reply_markup=reply_markup)
		update.message.reply_text('Дуэль создана, ожидай противника.')
		
		return ConversationHandler.END
	elif (summ >= 100) and (summ <= 100000) and game == 'roulette':
		keyboard = [[InlineKeyboardButton('Присоединиться к игре 🤠', callback_data=f'roulette {inv_user_id} {summ}')],
					[InlineKeyboardButton('Открыть диалог с ботом 👾', url=bot_link)]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=channel_username, text=f'`Roulette` 🎰\n\n*Создатель*: {invoker} (@{inv_user})\n*Ставка*: {summ} монет\n\n*Участников*: 1/10', parse_mode='MARKDOWN', reply_markup=reply_markup)
		update.message.reply_text('Игра создана, ожидай противников.')
		context.user_data['roulette_bet'] = summ
		context.user_data['roulette_id'] = inv_user_id
		context.user_data['participants'] = 1
		
		return ConversationHandler.END
	else:
		update.message.reply_text('_Error 404_. Как ты вообще это сделялъ? :/\nСкинь скрин сюда: @daaetoya и получи вознаграждение *1000* монет.', parse_mode='MARKDOWN')

		return ConversationHandler.END


@run_async
def button(update, context):
	cursor.execute('SELECT id FROM userz')
	all_users = cursor.fetchall()
	keyboard = [[InlineKeyboardButton('Создать свою игру', url=bot_link)]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	query = update.callback_query
	betinfo = query.data.split()
	cursor.execute('SELECT username FROM userz WHERE id = %s', (betinfo[1],))
	participant1 = cursor.fetchone()
	cursor.execute('SELECT username FROM userz WHERE id = %s', (query.from_user.id,))
	participant2 = cursor.fetchone()
	betsumm = betinfo[2]
	total = int(betsumm)*1.9
	inv_user_id = context.user_data['roulette_id']
	summ = context.user_data['roulette_bet']
	keyboard = [[InlineKeyboardButton('Присоединиться к игре 🤠', callback_data=f'roulette {inv_user_id} {summ}')],
					[InlineKeyboardButton('Открыть диалог с ботом 👾', url=bot_link)]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	if str(query.from_user.id) not in str(all_users):
		query.answer(f'Ошибка!\n\nСперва нужно зарегистрироваться.\n\nРегистрация: {bot_username}', show_alert=True, parse_mode='MARKDOWN')

		return
	elif 'coinflip' in query.data:
		cf_participants = [participant1[0], participant2[0]]
		winner = random.choice(cf_participants)
		query.edit_message_text(f'`Coinflip`\n\n@{participant1[0]} *vs* @{participant2[0]}\n\n*Победитель*: @{winner}!\n*Выигрыш*: `{int(total)}` монет!', parse_mode='MARKDOWN', reply_markup=reply_markup)
	elif 'roulette' in query.data:
		participants = context.user_data['participants']
		if participants < 9:
			participants += 1
			query.edit_message_text(f'*Участников*: {participants}/10', parse_mode='MARKDOWN', reply_markup=reply_markup)
		elif participants == 9:
			query.edit_message_text('Участники собраны, начинаем!')
		else:
			query.edit_message_text('Ошибка! Игра сброшена.')
	else:
		query.edit_message_text('Error')
	

@run_async
def anon(update, context):
    userid = update.message.from_user.id
    member1 = context.bot.get_chat_member(channel_username, userid)
    if member1.status in memberslist:
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
        update.message.reply_text(f'Ненене, так не пойдёт.\nДля начала подпишись на: {channel_username}')
	
        return ConversationHandler.END


@run_async
def anonId(update, context):
    context.user_data['groupid'] = update.message.text
    update.message.reply_text('Отлично, теперь напиши сообщение для отправки.')

    return MESSAGE


@run_async
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


@run_async
def cancel(update, context):
    update.message.reply_text('Эх! В этот раз ничего интересного:(')

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # TOKEN='972573533:AAEcygddWIIEjK7YzEu3PIy5vdlPRUDCASs'
    # REQUEST_KWARGS={
    # 'proxy_url': 'socks5h://188.226.141.211:1080',}
    # updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("promo", getPromo))
    dp.add_handler(CommandHandler("id", getId))
    dp.add_handler(CommandHandler("info", getInfo))
    dp.add_handler(CommandHandler("reg", registration))
    dp.add_handler(CallbackQueryHandler(button))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("anon", anon),
        			  CommandHandler("coinflip", coinflip),
        			  CommandHandler("roulette", roulette)],

    states={
           	ID: [MessageHandler(Filters.text, anonId)],
           	MESSAGE: [MessageHandler(Filters.text, anonMessage)],
           	TOTAL: [MessageHandler(Filters.text, Total)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

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
