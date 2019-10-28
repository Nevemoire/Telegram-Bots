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


conn = psycopg2.connect(dbname='d3p95g4d436dvm', user='gogkpkgabilgaj', 
                        password='984caca9804921aaba645e063270277f0aca1cf316578740c29104822e91254c', host='ec2-54-228-252-67.eu-west-1.compute.amazonaws.com')
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
	cursor.execute('select "balance" from userz where id = %s', (ids,))
	balance = cursor.fetchone()
	error = "None"	
	if error not in str(balance):
		pass
	elif (error in str(fullname) or error in str(username)):
		update.message.reply_text('''Приветствуем тебя в нашем клубе!

Запомни, первое правило клуба - веселись. Больше никаких правил ;)''')
		update.message.reply_text('''*Ты у нас впервые?*
Чтобы иметь возможность играть у нас, поля _Name_ и _Username_ не должны быть пустыми.
Исправь ситуацию и напиши мне /reg :)

Продолжая использовать бота ты автоматически [соглашаешься](https://telegra.ph/Polzovatelskoe-soglashenie-10-22-2) с нашими условиями и подтверждаешь что тебе есть 18 лет..''', parse_mode='MARKDOWN')
	else:
		update.message.reply_text('''Приветствуем тебя в нашем клубе!

Запомни, первое правило клуба - веселись. Больше никаких правил ;)''')
		registration_Query = "INSERT INTO userz (id, fullname, username, balance) VALUES (%s, %s, %s, 0)"
		cursor.execute(registration_Query, (ids, fullname, username,))
		conn.commit()
		update.message.reply_text('*Ты у нас впервые?*\nТвой профиль успешно создан, для справки введи /info ;)\n\nПродолжая использовать бота ты автоматически [соглашаешься](https://telegra.ph/Polzovatelskoe-soglashenie-10-22-2) с нашими условиями и подтверждаешь что тебе есть 18 лет.', parse_mode='MARKDOWN')
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
	update.message.reply_text('Чтобы пополнить баланс, отправь любую сумму пользователю `Nevermore` через сайт mdk.is.\n*Обязательно* прикрепи свой `ID` (число ниже) к донату, иначе сумма будет считаться пожертвованием.', disable_web_page_preview=True, parse_mode='MARKDOWN')
	update.message.reply_text(f'`{update.message.from_user.id}`', parse_mode='MARKDOWN')


@run_async
def withdraw(update, context):
	update.message.reply_text('Вывод будет доступен чуть позже.')


@run_async
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
				target_info_Query = "select * from userz where id = %s"
				cursor.execute(target_info_Query, (target,))
				target_info = cursor.fetchall()
				for row in target_info:
					update.message.reply_text(f'Name: {row[1]}\nUsername: {row[2]}\nBalance: {row[3]}\nID: {row[0]}')

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
			update.message.reply_text(f'Name: {row[1]}\nUsername: {row[2]}\nBalance: {row[3]}\nID: {row[0]}')
	except:
		update.message.reply_text('Произошла ошибка. Попробуй чуть позже.')


@run_async
def tos(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('[Пользовательское соглашение](https://telegra.ph/Polzovatelskoe-soglashenie-10-22-2) *Royal Casino*', parse_mode='MARKDOWN')


@run_async
def getPromo(update, context):
	ids = update.message.from_user.id
	cursor.execute('SELECT reffs FROM userz where id = %s', (ids,))
	reffs = cursor.fetchone()
	cursor.execute('SELECT refferrer FROM userz where id = %s', (ids,))
	ref = cursor.fetchone()
	update.message.reply_text(f'Исп. промокод: {ref[0]}\nКол-во реффералов: {reffs[0]}\n\nСсылка для приглашения:\nhttps://t.me/RoyalCasinoBot?start={ids}')


@run_async
def coinflip(update, context):
	context.user_data['game'] = 'coinflip'
	inv_user_id = update.message.from_user.id
	user_balance = "select balance from userz where id = %s"
	cursor.execute(user_balance, (inv_user_id,))
	balance = cursor.fetchone()
	context.user_data['message'] = update.message.reply_text(f'`Coinflip` 🌕\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')
	context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

	return TOTAL


# @run_async
# def roulette(update, context):
# 	context.user_data['game'] = 'roulette'
# 	inv_user_id = update.message.from_user.id
# 	user_balance = "select balance from userz where id = %s"
# 	cursor.execute(user_balance, (inv_user_id,))
# 	balance = cursor.fetchone()
# 	context.user_data['message'] = update.message.reply_text(f'`Roulette` 🎰\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')
# 	context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

# 	return TOTAL
@run_async
def roulette(update, context):
	update.message.reply_text('Рулетка пока в разработке, но ты можешь сыграть в Dice 🎲 (/dice) или Coinflip 🌕 (/coinflip).')

	return ConversationHandler.END


@run_async
def dice(update, context):
	try:
		context.user_data['game'] = 'dice'
		inv_user_id = update.message.from_user.id
		user_balance = "select balance from userz where id = %s"
		cursor.execute(user_balance, (inv_user_id,))
		balance = cursor.fetchone()
		# update.message.reply_text(f'`Dice` 🎲\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')
		context.user_data['message'] = update.message.reply_text(f'`Dice` 🎲\n\nВведи сумму ставки.\nТвой баланс: *{balance[0]}* монет\n\n(*min*: 100, *max*: 100000)\nОтмена - /cancel', parse_mode='MARKDOWN')
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
			context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Жаль, но мы не принимаем ничего, кроме монет.\nДа, натурой тоже не принимаем :(\n\nСоздать игру заново - /dice', parse_mode='MARKDOWN')

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
					[InlineKeyboardButton('Правила игры🎲', callback_data=f'rules_dice {inv_user_id} {summ}'),
					 InlineKeyboardButton('Диапазоны 🎲', callback_data=f'int_dice {inv_user_id} {summ}')]]
		koefs = InlineKeyboardMarkup(keyboard)
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Теперь выбери коэффициент умножения 👇', reply_markup=koefs)
		cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (summ, inv_user_id,))
		conn.commit()

		return ConversationHandler.END
	else:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='_Error 404_. Как ты вообще это сделялъ? :/\nСкинь скрин сюда: @daaetoya и получи вознаграждение *1000* монет.', parse_mode='MARKDOWN')

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
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Жаль, но мы не принимаем ничего, кроме монет.\nДа, натурой тоже не принимаем :(\n\nВведи *целое* число.\nОтмена - /cancel', parse_mode='MARKDOWN')

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
			context.bot.send_message(chat_id=channel_username, text=f'`Coinflip` 🌕\n\n*Создатель*: {invoker} (@{inv_user})\n*Ставка*: {summ} монет', parse_mode='MARKDOWN', reply_markup=reply_markup)
			context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=f'Дуэль успешно создана.\nНе забудь вступить в канал, где мы публикуем все игры: {channel_username}')
			cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (summ, inv_user_id,))
			conn.commit()
			
			return ConversationHandler.END
		except:
			context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Ошибка :/')

			return ConversationHandler.END
	elif (summ >= 100) and (summ <= 100000) and game == 'roulette':
		keyboard = [[InlineKeyboardButton('Присоединиться к игре 🤠', callback_data=f'roulette {inv_user_id} {summ}')],
					[InlineKeyboardButton('Открыть диалог с ботом 👾', url=bot_link)]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=channel_username, text=f'`Roulette` 🎰\n\n*Создатель*: {invoker} (@{inv_user})\n*Ставка*: {summ} монет', parse_mode='MARKDOWN', reply_markup=reply_markup)
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='Игра создана, ожидай противника.')
		context.user_data['participants'] = 1
		cursor.execute('UPDATE userz SET balance = balance - %s WHERE id = %s', (summ, inv_user_id,))
		conn.commit()
		
		return ConversationHandler.END
	else:
		context.user_data['message'] = context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='_Error 404_. Как ты вообще это сделялъ? :/\nСкинь скрин сюда: @daaetoya и получи вознаграждение *1000* монет.', parse_mode='MARKDOWN')

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
	number = random.randint(0, 100)

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
		query.edit_message_text(f'`Coinflip` 🌕\n\n@{participant1[0]} *vs* @{participant2[0]}\n\n*Победитель*: @{winner}!\n*Выигрыш*: `{int(total)}` монет!', parse_mode='MARKDOWN', reply_markup=reply_markup)
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
x2 - от 55 до 100,
x3 - от 70 до 100,
x5 - от 82 до 100,
x10 - от 91 до 100,
x50 - от 98 до 100.''', show_alert=True)
			elif '2x' in query.data and number >= 55:
				query.answer('✅')
				dice_win = int(betsumm)*2
				query.edit_message_text(f'*Победа!*\n*Коэффициент*: `{multiplier[0]}`\n*Число*: `{number}`\n*Выигрыш*: `{dice_win}` монет!', parse_mode='MARKDOWN')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstatstest SET total2x = total2x + %s', (dice_win,))
				cursor.execute('UPDATE dstatstest SET games2x = games2x + 1')
				conn.commit()
			elif '3x' in query.data and number >= 70:
				query.answer('✅')
				dice_win = int(betsumm)*3
				query.edit_message_text(f'*Победа!*\n*Коэффициент*: `{multiplier[0]}`\n*Число*: `{number}`\n*Выигрыш*: `{dice_win}` монет!', parse_mode='MARKDOWN')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstatstest SET total3x = total3x + %s', (dice_win,))
				cursor.execute('UPDATE dstatstest SET games3x = games3x + 1')
				conn.commit()
			elif '5x' in query.data and number >= 82:
				query.answer('✅')
				dice_win = int(betsumm)*5
				query.edit_message_text(f'*Победа!*\n*Коэффициент*: `{multiplier[0]}`\n*Число*: `{number}`\n*Выигрыш*: `{dice_win}` монет!', parse_mode='MARKDOWN')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstatstest SET total5x = total5x + %s', (dice_win,))
				cursor.execute('UPDATE dstatstest SET games5x = games5x + 1')
				conn.commit()
			elif '10x' in query.data and number >= 91:
				query.answer('✅')
				dice_win = int(betsumm)*10
				query.edit_message_text(f'*Победа!*\n*Коэффициент*: `{multiplier[0]}`\n*Число*: `{number}`\n*Выигрыш*: `{dice_win}` монет!', parse_mode='MARKDOWN')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstatstest total10x = total10x + %s', (dice_win,))
				cursor.execute('UPDATE dstatstest SET games10x = games10x + 1')
				conn.commit()
			elif '50x' in query.data and number >= 98:
				query.answer('✅')
				dice_win = int(betsumm)*50
				query.edit_message_text(f'*Победа!*\n*Коэффициент*: `{multiplier[0]}`\n*Число*: `{number}`\n*Выигрыш*: `{dice_win}` монет!', parse_mode='MARKDOWN')
				cursor.execute('UPDATE userz SET balance = balance + %s WHERE id = %s', (dice_win, query.from_user.id,))
				cursor.execute('UPDATE dstatstest total50x = total50x + %s', (dice_win,))
				cursor.execute('UPDATE dstatstest SET games50x = games50x + 1')
				conn.commit()
			else:
				query.answer('❌')
				query.edit_message_text(f'*Проигрыш!* В следующий раз повезёт :(\n*Коэффициент*: `{multiplier[0]}`\n*Число*: `{number}`\n*Ставка*: `{betsumm}` монет', parse_mode='MARKDOWN')
				lostgame = f'lost{multiplier[0]}'
				game = f'games{multiplier[0]}'
				tstring = f'{lostgame} = {lostgame} - {betsumm}'
				cursor.execute(f'UPDATE dstatstest SET {tstring}')
				string = f'{game} = {game} + 1'
				cursor.execute(f'UPDATE dstatstest SET {string}')
				conn.commit()
		else:
			query.answer('Ты не можешь участвовать в этой игре! Чтобы создать свою, напиши: /dice', show_alert=True)
	else:
		query.edit_message_text('Ошибка! Попробуй чуть позже.')


def dstats(update, context):
	cursor.execute('SELECT * FROM dstatstest')
	results = cursor.fetchall()
	for stats in results:
		update.message.reply_text(f'Статистика по играм:\n2x: {stats[0]} *{stats[5]}* (`{stats[10]}`)\n3x: {stats[1]} *{stats[6]}* (`{stats[11]}`)\n5x: {stats[2]} *{stats[7]}* (`{stats[12]}`)\n10x: {stats[3]} *{stats[8]}* (`{stats[13]}`)\n50x: {stats[4]} *{stats[9]}* (`{stats[14]}`)', parse_mode='MARKDOWN')
	

@run_async
def anon(update, context):
    userid = update.message.from_user.id
    member1 = context.bot.get_chat_member(channel_username, userid)
    if member1.status in memberslist:
    	context.user_data['message'] = update.message.reply_text('Наконец что-то интересненькое ;)\n\nНапиши сюда сообщение для отправки. *Стоимость*: `100` монет.\n/cancel - чтобы отменить.',parse_mode='MARKDOWN')
    	context.user_data['user'] = update.message.from_user.full_name

    	return MESSAGE
    else:
        update.message.reply_text(f'Ненене, так не пойдёт.\nДля начала подпишись на: {channel_username}')
	
        return ConversationHandler.END


@run_async
def anonMessage(update, context):
    user = context.user_data['user']
    message = update.message.text
    try:
        context.bot.sendMessage(chat_id=-1001441511504, text=f'*Какой-то анон написал(-а):*\n{message}', parse_mode='MARKDOWN')
        context.bot.sendMessage(chat_id=391206263, text=f'*{user} написал(-а):*\n{message}', parse_mode='MARKDOWN')

        return ConversationHandler.END
    except:
        update.message.reply_text(f'Что-то пошло не так :(\nТы точно удалил(-а) знак "-" перед числами?')

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
				context.bot.send_message(chat_id='@rylcoinmarket', text=f'`[Deposit]`\nПользователь @{args[1]} внёс {args[2]} монет на свой счёт.', parse_mode='MARKDOWN')
			except:
				update.message.reply_text('Error add')
		elif '!remove' in update.message.text:
			if balance[0] >= int(args[2]):
				try:
					cursor.execute('UPDATE userz SET balance = balance - %s WHERE username = %s', (args[2], args[1],))
					conn.commit()
					context.bot.send_message(chat_id='@rylcoinmarket', text=f'`[Withdraw]`\nПользователь @{args[1]} вывел {args[2]} монет.', parse_mode='MARKDOWN')
				except:
					update.message.reply_text('Error remove')
			else:
				update.message.reply_text('Недостаточно монет.')
		else:
			pass
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
    updater = Updater(os.environ['token'], use_context=True)

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
