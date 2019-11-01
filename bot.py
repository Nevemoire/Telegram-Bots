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

MESSAGE, TOTAL, DICE = range(3)


members = 'creator, administrator, member'
memberslist = members.split(', ')


conn = psycopg2.connect(dbname = 'd19olitilh6q1s', user = 'oukggnzlpirgzh', password = 'a4e84b7de4257e36cecc14b60bb0ff570f7ce52d5d24b1c7eb275c96f403af36', host = 'ec2-79-125-23-20.eu-west-1.compute.amazonaws.com')
cursor = conn.cursor()

bot_link = 'telegram.me/royalcasinobot'
bot_username = '@royalcasinobot'
channel_username = '@rylcasino'


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
@run_async
def start(update, context):
	"""Send a message when the command /start is issued."""
	ids = update.message.from_user.id
	fullname = update.message.from_user.full_name
	usern = update.message.from_user.username
	username = usern.lower()
	cursor.execute('select balance from userz where id = %s', (ids,))
	balance = cursor.fetchone()
	error = "None"	
	if error not in str(balance):
		pass
	elif (error in str(fullname) or error in str(username)):
		update.message.reply_text('''Приветствуем тебя в нашем клубе!

Запомни, первое правило клуба - веселись. Больше никаких правил ;)''')
		update.message.reply_text('''<b>Ты у нас впервые?</b>
Чтобы иметь возможность играть у нас, поля _Name_ и _Username_ не должны быть пустыми.
Исправь ситуацию и напиши мне /reg :)

Продолжая использовать бота ты автоматически <a href="https://telegra.ph/Polzovatelskoe-soglashenie-10-22-2">соглашаешься</a> с нашими условиями и подтверждаешь что тебе есть 18 лет.''', parse_mode='HTML')
	else:
		update.message.reply_text('''Приветствуем тебя в нашем клубе!

Запомни, первое правило клуба - веселись. Больше никаких правил ;)''')
		registration_Query = "INSERT INTO userz (id, fullname, username, balance) VALUES (%s, %s, %s, 0)"
		cursor.execute(registration_Query, (ids, fullname, username,))
		conn.commit()
		update.message.reply_text('<b>Ты у нас впервые?</b>\nТвой профиль успешно создан, для справки введи /info ;)\n\nПродолжая использовать бота ты автоматически <a href="https://telegra.ph/Polzovatelskoe-soglashenie-10-22-2">соглашаешься</a> с нашими условиями и подтверждаешь что тебе есть 18 лет.', parse_mode='HTML')
	try:
		user_says = context.args[0]
		invoker = update.message.from_user.id
		error = 'None'
		cursor.execute('SELECT refferrer FROM userz WHERE id = %s', (invoker,))
		promo_used = cursor.fetchone()
		cursor.execute('SELECT id FROM userz')
		totalb = cursor.fetchall()
		if user_says not in str(totalb):
			update.message.reply_text('Такого промокода не существует.')
		elif user_says in str(invoker):
			update.message.reply_text('Свой промокод использовать нельзя!')
		elif error not in str(promo_used):
			update.message.reply_text('Упси, промокод можно использовать только 1 раз.')
		else:
			cursor.execute('UPDATE userz SET reffs = reffs + 1, balance = balance + 20 WHERE id = %s', (user_says,))
			cursor.execute('UPDATE userz SET balance = balance + 100, refferrer = %s WHERE id = %s', (user_says, invoker,))
			update.message.reply_text('Промокод принят. (+100 монет тебе и +20 владельцу промокода)')
			conn.commit()
	except:
		pass


@run_async
def deposit(update, context):
	if update.message.chat_id == -1001441511504:
		update.message.reply_text('Недоступно в этом чате.')
	else:
		update.message.reply_text('Чтобы пополнить баланс, отправь любую сумму пользователю <code>Nevermore</code> через сайт mdk.is.\n<b>Обязательно</b> прикрепи свой <code>ID</code> (число ниже) к донату, иначе сумма будет считаться пожертвованием.', disable_web_page_preview=True, parse_mode='HTML')
		update.message.reply_text(f'<code>{update.message.from_user.id}</code>', parse_mode='HTML')


@run_async
def withdraw(update, context):
	if update.message.chat_id == -1001441511504:
		update.message.reply_text('Недоступно в этом чате.')
	else:
		update.message.reply_text('Вывод будет доступен чуть позже.')


@run_async
def registration(update, context):
	ids = update.message.from_user.id
	fullname = update.message.from_user.full_name
	usern = update.message.from_user.username
	username = usern.lower()
	# balance_Query = 
	id_Query = 'select balance from userz where id = %s'
	cursor.execute(id_Query, (ids,))
	balance = cursor.fetchone()
	error = "None"	
	if error not in str(balance):
		update.message.reply_text('<b>Ошибка!</b> Регистрироваться можно только один раз!', parse_mode='HTML')
	elif (error in str(fullname) or error in str(username)):
		update.message.reply_text('<b>Ошибка!</b> <code>Name</code> или <code>Username</code> имеют пустое значение.', parse_mode='HTML')
	else:
		registration_Query = "INSERT INTO userz (id, fullname, username, balance) VALUES (%s, %s, %s, 0)"
		cursor.execute(registration_Query, (ids, fullname, username,))
		conn.commit()
		update.message.reply_text('Регистрация пройдена успешно.')


@run_async
def getInfo(update, context):
	try:
		usrid = update.message.from_user.id
		cursor.execute('SELECT id FROM userz')
		all_users = cursor.fetchall()
		try:
			target = update.message.reply_to_message.from_user.id
			if '/info' in update.message.reply_to_message.text:
				pass
			elif str(target) in str(all_users):
				target_info_Query = "select username, balance from userz where id = %s"
				cursor.execute(target_info_Query, (target,))
				target_info = cursor.fetchall()
				for row in target_info:
					update.message.reply_text(f'@{row[0]}, 💰: <code>{row[1]}</code>', parse_mode="HTML")

					return

			else:
				update.message.reply_text('Ошибка! Этого пользователя нет в нашей базе данных.')

				return

		except:
			pass

		user_info_Query = "select username, balance from userz where id = %s"

		cursor.execute(user_info_Query, (usrid,))
		info = cursor.fetchall()
		for row in info:
			update.message.reply_text(f'@{row[0]}, 💰: <code>{row[1]}</code>', parse_mode="HTML")
	except:
		update.message.reply_text('Произошла ошибка. Попробуй чуть позже.')


@run_async
def tos(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('<a href="https://telegra.ph/Polzovatelskoe-soglashenie-10-22-2">Пользовательское соглашение</a> <b>Royal Casino</b>', parse_mode='HTML')


@run_async
def getPromo(update, context):
	if update.message.chat_id == -1001441511504:
		update.message.reply_text('Недоступно в этом чате.')
	else:
		ids = update.message.from_user.id
		cursor.execute('SELECT reffs FROM userz where id = %s', (ids,))
		reffs = cursor.fetchone()
		cursor.execute('SELECT refferrer FROM userz where id = %s', (ids,))
		ref = cursor.fetchone()
		update.message.reply_text(f'Исп. промокод: {ref[0]}\nКол-во реффералов: {reffs[0]}\n\nСсылка для приглашения:\nhttps://t.me/RoyalCasinoBot?start={ids}')


@run_async
def coinflip(update, context):
	if update.message.chat_id == -1001441511504:
		update.message.reply_text('Недоступно в этом чате.')

		return ConversationHandler.END
	else:
		context.user_data['game'] = 'coinflip'
		inv_user_id = update.message.from_user.id
		user_balance = "select balance from userz where id = %s"
		cursor.execute(user_balance, (inv_user_id,))
		balance = cursor.fetchone()
		context.user_data['message'] = update.message.reply_text(f'<code>Coinflip</code> 🌕\n\nВведи сумму ставки.\nТвой баланс: <b>{balance[0]}</b> монет\n\n(<b>min</b>: <code>100</code>, <b>max</b>: <code>100000</code>)\nОтмена - /cancel', parse_mode='HTML')
		context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

		return TOTAL


# @run_async
# def roulette(update, context):
# 	context.user_data['game'] = 'roulette'
# 	inv_user_id = update.message.from_user.id
# 	user_balance = "select balance from userz where id = %s"
# 	cursor.execute(user_balance, (inv_user_id,))
# 	balance = cursor.fetchone()
# 	context.user_data['message'] = update.message.reply_text(f'Roulette 🎰\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')
# 	context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

# 	return TOTAL
@run_async
def roulette(update, context):
	update.message.reply_text('Рулетка пока в разработке, но ты можешь сыграть в Dice 🎲 (/dice) или Coinflip 🌕 (/coinflip).')

	return ConversationHandler.END


@run_async
def dice(update, context):
	if update.message.chat_id == -1001441511504:
		update.message.reply_text('Недоступно в этом чате.')

		return ConversationHandler.END
	else:
		try:
			context.user_data['game'] = 'dice'
			inv_user_id = update.message.from_user.id
			user_balance = "select balance from userz where id = %s"
			cursor.execute(user_balance, (inv_user_id,))
			balance = cursor.fetchone()
			# update.message.reply_text(f'Dice 🎲\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')
			context.user_data['message'] = update.message.reply_text(f'<code>Dice</code> 🎲\n\nВведи сумму ставки.\nТвой баланс: <b>{balance[0]}</b> монет\n\n(<b>min</b>: <code>100</code>, <b>max</b>: <code>100000</code>)\nОтмена - /cancel', parse_mode='HTML')
			context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

			return DICE
		except:
			update.message.reply_text('Произошла ошибка.')

			return ConversationHandler.END


@run_async
def dice_start(update, context):
	context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	game = context.user_data['game']
	message = context.user_data['message']
	total = update.message.text
	inv_user_id = update.message.from_user.id
	user_balance = "select balance from userz where id = %s"
	cursor.execute(user_balance, (inv_user_id,))
	balance = cursor.fetchone()
	try:
		summ = int(total)
	except:
		try:
			context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Жаль, но мы не принимаем ничего, кроме монет.\nДа, натурой тоже не принимаем :(\n\nСоздать игру заново - /dice')

			return ConversationHandler.END
		except:

			return

	if summ < 100:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Так не пойдёт, возвращайся в другой раз.')

		return ConversationHandler.END
	elif summ > 100000:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Превышен лимит, может как-нибудь в другой раз ;)')

		return ConversationHandler.END
	elif summ > int(balance[0]):
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Недостаточно монет.')

		return ConversationHandler.END
	elif (summ >= 100) and (summ <= 100000) and game == 'dice':
		keyboard = [[InlineKeyboardButton('2x', callback_data=f'2x {inv_user_id} {summ} dice'),
					 InlineKeyboardButton('3x', callback_data=f'3x {inv_user_id} {summ} dice'),
					 InlineKeyboardButton('5x', callback_data=f'5x {inv_user_id} {summ} dice'),
					 InlineKeyboardButton('10x', callback_data=f'10x {inv_user_id} {summ} dice'),
					 InlineKeyboardButton('50x', callback_data=f'50x {inv_user_id} {summ} dice')],
					[InlineKeyboardButton('Правила игры 🎲', callback_data=f'rules_dice {inv_user_id} {summ}'),
					 InlineKeyboardButton('Диапазоны 🎲', callback_data=f'int_dice {inv_user_id} {summ}')]]
		koefs = InlineKeyboardMarkup(keyboard)
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Теперь выбери коэффициент умножения 👇', reply_markup=koefs)
		cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (summ, inv_user_id,))
		conn.commit()

		return ConversationHandler.END
	else:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='<code>Error 404</code>. Как ты вообще это сделялъ? :/\nСкинь скрин сюда: @daaetoya и получи вознаграждение <b>1000</b> монет.', parse_mode='HTML')

		return ConversationHandler.END
	


@run_async
def Total(update, context):
	game = context.user_data['game']
	message = context.user_data['message']
	context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
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
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Жаль, но мы не принимаем ничего, кроме монет.\nДа, натурой тоже не принимаем :(\n\nВведи <b>целое</b> число.\nОтмена - /cancel', parse_mode='HTML')

		return TOTAL

	if summ < 100:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Так не пойдёт, возвращайся в другой раз.')

		return ConversationHandler.END
	elif summ > 100000:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Превышен лимит, может как-нибудь в другой раз ;)')

		return ConversationHandler.END
	elif summ > int(balance[0]):
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Недостаточно монет.')

		return ConversationHandler.END
	elif (summ >= 100) and (summ <= 100000) and game == 'coinflip':
		try:
			keyboard = [[InlineKeyboardButton('Присоединиться к игре 🤠', callback_data=f'coinflip {inv_user_id} {summ}')],
						[InlineKeyboardButton('Открыть диалог с ботом 👾', url=bot_link)]]
			reply_markup = InlineKeyboardMarkup(keyboard)
			context.bot.send_message(chat_id=channel_username, text=f'<code>Coinflip</code> 🌕\n\n<b>Создатель</b>: {invoker} (@{inv_user})\n<b>Ставка</b>: {summ} монет', parse_mode='HTML', reply_markup=reply_markup)
			context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=f'Дуэль успешно создана.\nНе забудь вступить в канал, где мы публикуем все игры: {channel_username}')
			cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (summ, inv_user_id,))
			conn.commit()
			context.user_data['participants'] = 0
			
			return ConversationHandler.END
		except:
			context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Ошибка :/')

			return ConversationHandler.END
	elif (summ >= 100) and (summ <= 100000) and game == 'roulette':
		keyboard = [[InlineKeyboardButton('Присоединиться к игре 🤠', callback_data=f'roulette {inv_user_id} {summ}')],
					[InlineKeyboardButton('Открыть диалог с ботом 👾', url=bot_link)]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=channel_username, text=f'<code>Roulette</code> 🎰\n\n<b>Создатель</b>: {invoker} (@{inv_user})\n<b>Ставка</b>: {summ} монет', parse_mode='HTML', reply_markup=reply_markup)
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Игра создана, ожидай противника.')
		context.user_data['participants'] = 1
		cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (summ, inv_user_id,))
		conn.commit()
		
		return ConversationHandler.END
	else:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='<code>Error 404</code>. Как ты вообще это сделялъ? :/\nСкинь скрин сюда: @daaetoya и получи вознаграждение <b>1000</b> монет.', parse_mode='HTML')

		return ConversationHandler.END


@run_async
def button(update, context):
	try:
		cursor.execute('SELECT id FROM userz')
		all_users = cursor.fetchall()
	except:
		query.answer('Ошибка! Повтори через несколько секунд.', show_alert=True)

		return
	keyboard = [[InlineKeyboardButton('Создать свою игру', url=bot_link)]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	query = update.callback_query
	betinfo = query.data.split()
	cursor.execute('SELECT username FROM userz WHERE id = %s', (betinfo[1],))
	participant1 = cursor.fetchone()
	cursor.execute('SELECT username, balance FROM userz WHERE id = %s', (query.from_user.id,))
	participant2 = cursor.fetchone()
	betsumm = betinfo[2]
	betssumm = int(betsumm)
	total = int(betsumm)*1.9
	number = random.randint(0, 1000)

	if str(query.from_user.id) not in str(all_users):
		query.answer(f'Ошибка!\n\nСперва нужно зарегистрироваться.\n\nДля регистрации напиши: /reg', show_alert=True)
	elif ('coinflip' in query.data) and (betinfo[1] in str(query.from_user.id)):
		query.answer('Нельзя участвовать в своей же игре.', show_alert=True)
	elif ('coinflip' in query.data) and (int(participant2[1]) < int(betsumm)):
		query.answer('Недостаточно монет.\nЧтобы пополнить баланс напиши боту /deposit', show_alert=True)
	elif 'coinflip' in query.data:
		cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (betsumm, query.from_user.id,))
		cf_participants = [participant1[0], participant2[0]]
		winner = random.choice(cf_participants)
		if int(total) >= 9500:
			try:
				context.bot.send_message(chat_id=-1001441511504, text=f'<b>Поздравляем</b> @{winner}, он(-а) срывает <b>Куш</b> в <code>Coinflip</code>! 👸\n<b>Выигрыш</b>: <code>{int(total)}</code>', parse_mode='HTML')
			except:
				pass
		elif (int(total) >= 5700) and (int(total) < 9500):
			try:
				context.bot.send_message(chat_id=-1001441511504, text=f'<b>Поздравляем</b> @{winner}, он(-а) выигрывает <b>Джекпот</b> в <code>Coinflip</code>! 🏆\n<b>Выигрыш</b>: <code>{int(total)}</code>', parse_mode='HTML')
			except:
				pass
		else:
			pass
		query.edit_message_text(f'<code>Coinflip</code> 🌕\n\n@{participant1[0]} <b>vs</b> @{participant2[0]}\n\n<b>Победитель</b>: @{winner}!\n<b>Выигрыш</b>: <code>{int(total)}</code> монет!', parse_mode='HTML', reply_markup=reply_markup)
		cursor.execute('UPDATE userz SET balance = balance + %s WHERE username = %s', (total, winner,))
		conn.commit()
	elif 'roulette' in query.data:
		query.edit_message_text('Игра в разработке...')
	elif 'dice' in query.data:
		if str(query.from_user.id) in query.data:
			multiplier = query.data.split()
			if 'rules_dice' in query.data:
				query.answer(f'''Правила игры Dice\n\n
1. Игрок указывает ставку и множитель игры.
2. Бот рандомит случайное число от 0 до 100.
3. Если число попадает в диапазон коэффициента (включительно), вы выиграли.''', show_alert=True)
			elif 'int_dice' in query.data:
				query.answer(f'''Диапазоны выигрышей Dice\n\n
x2 - от 575 до 1000,
x3 - от 716 до 1000,
x5 - от 830 до 1000,
x10 - от 915 до 1000,
x50 - от 983 до 1000.''', show_alert=True)
			elif '2x' in query.data and number >= 575:
				query.answer('✅')
				dice_win = int(betsumm)*2
				query.edit_message_text(f'<b>Победа!</b>\n<b>Коэффициент</b>: <code>{multiplier[0]}</code>\n<b>Число</b>: <code>{number}</code>\n<b>Выигрыш</b>: <code>{dice_win}</code> монет!', parse_mode='HTML')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstats SET total = total + %s WHERE multiplier = %s', (dice_win, '2x',))
				cursor.execute('UPDATE dstats SET games = games + 1 WHERE multiplier = %s', ('2x',))
				conn.commit()
			elif '3x' in query.data and number >= 716:
				query.answer('✅')
				dice_win = int(betsumm)*3
				query.edit_message_text(f'<b>Победа!</b>\n<b>Коэффициент</b>: <code>{multiplier[0]}</code>\n<b>Число</b>: <code>{number}</code>\n<b>Выигрыш</b>: <code>{dice_win}</code> монет!', parse_mode='HTML')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstats SET total = total + %s WHERE multiplier = %s', (dice_win, '3x',))
				cursor.execute('UPDATE dstats SET games = games + 1 WHERE multiplier = %s', ('3x',))
				conn.commit()
			elif '5x' in query.data and number >= 830:
				query.answer('✅')
				dice_win = int(betsumm)*5
				query.edit_message_text(f'<b>Победа!</b>\n<b>Коэффициент</b>: <code>{multiplier[0]}</code>\n<b>Число</b>: <code>{number}</code>\n<b>Выигрыш</b>: <code>{dice_win}</code> монет!', parse_mode='HTML')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstats SET total = total + %s WHERE multiplier = %s', (dice_win, '5x',))
				cursor.execute('UPDATE dstats SET games = games + 1 WHERE multiplier = %s', ('5x',))
				conn.commit()
			elif '10x' in query.data and number >= 915:
				query.answer('✅')
				dice_win = int(betsumm)*10
				query.edit_message_text(f'<b>Победа!</b>\n<b>Коэффициент</b>: <code>{multiplier[0]}</code>\n<b>Число</b>: <code>{number}</code>\n<b>Выигрыш</b>: <code>{dice_win}</code> монет!', parse_mode='HTML')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstats SET total = total + %s WHERE multiplier = %s', (dice_win, '10x',))
				cursor.execute('UPDATE dstats SET games = games + 1 WHERE multiplier = %s', ('10x',))
				conn.commit()
				context.bot.send_message(chat_id='@rylcoinmarket', text=f'🏆 {query.from_user.full_name} словил(-а) <code>Джекпот</code>! 🏆\n\n<b>Коэффициент</b>: <code>10X</code>!\n<b>Выигрыш</b>: <code>{dice_win}</code>!', parse_mode='HTML')
			elif '50x' in query.data and number >= 983:
				query.answer('✅')
				dice_win = int(betsumm)*50
				query.edit_message_text(f'<b>Победа!</b>\n<b>Коэффициент</b>: <code>{multiplier[0]}</code>\n<b>Число</b>: <code>{number}</code>\n<b>Выигрыш</b>: <code>{dice_win}</code> монет!', parse_mode='HTML')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstats SET total = total + %s WHERE multiplier = %s', (dice_win, '50x',))
				cursor.execute('UPDATE dstats SET games = games + 1 WHERE multiplier = %s', ('50x',))
				conn.commit()
				context.bot.send_message(chat_id='@rylcoinmarket', text=f'👸 {query.from_user.full_name} сорвал(-а) <b>Куш</b>! 👸\n\n<b>Коэффициент</b>: <code>50X</code>!\n<b>Выигрыш</b>: <code>{dice_win}</code>!', parse_mode='HTML')
			else:
				query.answer('❌')
				query.edit_message_text(f'<b>Проигрыш!</b> В следующий раз повезёт :(\n<b>Коэффициент</b>: <code>{multiplier[0]}</code>\n<b>Число</b>: <code>{number}</code>\n<b>Ставка</b>: <code>{betsumm}</code> монет', parse_mode='HTML')
				cursor.execute(f'UPDATE dstats SET lost = lost - {betsumm} WHERE multiplier = {multiplier[0]}')
				cursor.execute(f'UPDATE dstats SET games = games + 1 WHERE multiplier = {multiplier[0]}')
				conn.commit()
		else:
			query.answer('Ты не можешь участвовать в этой игре! Чтобы создать свою, напиши: /dice', show_alert=True)
	else:
		query.edit_message_text('Ошибка! Попробуй чуть позже.')


def dstats(update, context):
	cursor.execute('SELECT games, total, lost FROM dstats')
	info = cursor.fetchall()
	cursor.execute('SELECT SUM(games), SUM(total), SUM(lost) FROM dstats')
	results = cursor.fetchall()
	for stats in info:
# 		update.message.reply_text(f'''Статистика по играм:
# 2x: {stats[0]} <b>{stats[5]}</b> (<code>{stats[10]}</code>)
# 3x: {stats[1]} <b>{stats[6]}</b> (<code>{stats[11]}</code>)
# 5x: {stats[2]} <b>{stats[7]}</b> (<code>{stats[12]}</code>)
# 10x: {stats[3]} <b>{stats[8]}</b> (<code>{stats[13]}</code>)
# 50x: {stats[4]} <b>{stats[9]}</b> (<code>{stats[14]}</code>)''', parse_mode='HTML')
		update.message.reply_text(f'''Статистика по играм:
2x: {stats[0, 0]} <b>{stats[0, 1]}</b> (<code>{stats[0, 2]}</code>)
3x: {stats[1, 0]} <b>{stats[1, 1]}</b> (<code>{stats[1, 2]}</code>)
5x: {stats[2, 0]} <b>{stats[2, 1]}</b> (<code>{stats[2, 2]}</code>)
10x: {stats[3, 0]} <b>{stats[3, 1]}</b> (<code>{stats[3, 2]}</code>)
50x: {stats[4, 0]} <b>{stats[4, 1]}</b> (<code>{stats[4, 2]}</code>)''', parse_mode='HTML')
		update.message.reply_text(stats)
	for res in results:
		update.message.reply_text(f'Итог: {res[0]} <b>{res[1]}</b> (<code>{res[2]}</code>)', parse_mode='HTML')
	

@run_async
def anon(update, context):
	if update.message.chat_id == -1001441511504:
		update.message.reply_text('Недоступно в этом чате.')

		return ConversationHandler.END
	else:
	    cursor.execute('SELECT id FROM userz')
	    all_users = cursor.fetchall()
	    userid = update.message.from_user.id
	    if str(userid) in str(all_users):
	        member1 = context.bot.get_chat_member(channel_username, userid)
	        if member1.status in memberslist:
	    	    context.user_data['message'] = update.message.reply_text('Наконец что-то интересненькое ;)\n\nНапиши сюда сообщение для отправки. <b>Стоимость</b>: <code>100</code> монет.\n/cancel - чтобы отменить.', parse_mode='HTML')
	    	    context.user_data['user'] = update.message.from_user.full_name

	    	    return MESSAGE
	        else:
	            update.message.reply_text(f'Ненене, так не пойдёт.\nДля начала подпишись на: {channel_username}')
		
	            return ConversationHandler.END
	    else:
	        update.message.reply_text('Сперва зарегистрируйся (/reg)')
		
	        return ConversationHandler.END


@run_async
def anonMessage(update, context):
    user = context.user_data['user']
    message = update.message.text
    cursor.execute('SELECT balance FROM userz WHERE id = %s', (update.message.from_user.id,))
    balance = cursor.fetchone()
    if int(balance[0]) >= 100:
        cursor.execute('UPDATE userz SET balance = balance - 100 WHERE id = %s', (update.message.from_user.id,))
        conn.commit()
        context.bot.sendMessage(chat_id=-1001441511504, text=f'<b>Какой-то анон написал(-а)</b>:\n{message}', parse_mode='HTML')
        context.bot.sendMessage(chat_id=391206263, text=f'<b>{user} написал(-а)</b>:\n{message}', parse_mode='HTML')

        return ConversationHandler.END
    else:
        update.message.reply_text(f'Недостаточно монет, возвращайся в другой раз.')

        return ConversationHandler.END


@run_async
def cancel(update, context):
	message = context.user_data['message']
	context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Эх! В этот раз ничего интересного:(')
	context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

	return ConversationHandler.END


def echo(update, context):
	if ('!add' in update.message.text) or ('!remove' in update.message.text):
		message = update.message.text
		args = message.split()
		cursor.execute('SELECT balance FROM userz WHERE username = %s', (args[1],))
		balance = cursor.fetchone()
		cursor.execute('SELECT username FROM userz')
		all_users = cursor.fetchall()
		if args[1] not in str(all_users):
			update.message.reply_text('Такого пользователя не существует.')
		elif '!add' in update.message.text:
			try:
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE username = %s', (args[2], args[1],))
				conn.commit()
				context.bot.send_message(chat_id='@rylcoinmarket', text=f'<code>[Deposit]</code>\nПользователь @{args[1]} внёс {args[2]} монет на свой счёт.', parse_mode='HTML')
			except:
				update.message.reply_text('Error add')
		elif '!remove' in update.message.text:
			if balance[0] >= int(args[2]):
				try:
					cursor.execute('UPDATE userz SET balance = balance - %s WHERE username = %s', (args[2], args[1],))
					conn.commit()
					context.bot.send_message(chat_id='@rylcoinmarket', text=f'<code>[Withdraw]</code>\nПользователь @{args[1]} вывел {args[2]} монет.', parse_mode='HTML')
				except:
					update.message.reply_text('Error remove')
			else:
				update.message.reply_text('Недостаточно монет.')
		else:
			pass
	elif ('!drefresh' in update.message.text):
		cursor.execute('UPDATE dstats SET games, total, lost VALUES (0, 0, 0)')
		conn.commit()
	else:
		pass


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # TOKEN='683044036:AAGM___X_lK52LDR1SmiTCOvcjdHRh2cYkY'
    # updater = Updater('683044036:AAGM___X_lK52LDR1SmiTCOvcjdHRh2cYkY', use_context=True)
    updater = Updater(os.environ['token'], request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(CommandHandler("tos", tos))
    dp.add_handler(CommandHandler("dstats", dstats))
    dp.add_handler(CommandHandler("deposit", deposit))
    dp.add_handler(CommandHandler("withdraw", withdraw))
    dp.add_handler(CommandHandler("promo", getPromo))
    dp.add_handler(CommandHandler("info", getInfo))
    dp.add_handler(CommandHandler("reg", registration))
    dp.add_handler(CallbackQueryHandler(button))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("anon", anon),
        			  CommandHandler("coinflip", coinflip),
        			  CommandHandler("roulette", roulette),
        			  CommandHandler("dice", dice)],

    states={
           	MESSAGE: [MessageHandler(Filters.text, anonMessage)],
           	TOTAL: [MessageHandler(Filters.text, Total)],
           	DICE: [MessageHandler(Filters.text | Filters.group, dice_start)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text & Filters.user(username="@daaetoya"), echo))

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
