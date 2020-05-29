
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random
import psycopg2
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, CallbackQueryHandler, ConversationHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

channel = '@nevermorebets'
channel_username = '@theclownfiesta'

memberz = 'creator, administrator, member'
memberslist = memberz.split(', ')

BETSUMM = range(1)

conn = psycopg2.connect(dbname='d19olitilh6q1s', user='oukggnzlpirgzh', password='a4e84b7de4257e36cecc14b60bb0ff570f7ce52d5d24b1c7eb275c96f403af36',
						host='ec2-79-125-23-20.eu-west-1.compute.amazonaws.com')
# conn = psycopg2.connect(dbname=os.environ['dbname'], user=os.environ['user'], password=os.environ['password'],
#						 host=os.environ['host'])

cursor = conn.cursor()


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
	"""Send a message when the command /start is issued."""
	usrid = update.message.from_user.id
	cursor.execute('SELECT id FROM users')
	all_users = cursor.fetchall()
	if str(usrid) in str(all_users):
		try:
			text = context.args[0]
		except:
			return
		if 'ref' in text:
			promo = text.split('ref-')
			error = 'None'
			invoker = update.message.from_user.id
			cursor.execute('SELECT ref_by FROM users WHERE id = %s', (invoker,))
			promo_used = cursor.fetchone()
			cursor.execute('SELECT id FROM users')
			totalb = cursor.fetchall()
			if promo[1] not in str(totalb):
				update.message.reply_text('Такого промокода не существует.')
			elif promo[1] in str(invoker):
				update.message.reply_text('Свой промокод использовать нельзя!')
			elif error not in str(promo_used):
				update.message.reply_text('Промокод уже активирован.')
			else:
				update.message.reply_text(promo[1])
				cursor.execute('UPDATE users SET exp = exp + 1000, ref_by = %s WHERE id = %s', (promo[1], update.message.from_user.id,))
				cursor.execute('UPDATE users SET exp = exp + 100, reffs = reffs + 1 WHERE id = %s', (promo[1],))
				update.message.reply_text('Промокод активирован, вам начислена 1000 монет.')
				conn.commit()

			return ConversationHandler.END
		elif text == 'faq':
			update.message.reply_text('''
<b>1. Как играть?</b>
Ставите на один из трёх доступных коэфициентов, указываете сумму ставки и ждёте результат.
<b>2. Что означают 🎉, 👥, 🏦?</b>
🎉 - Результат игры.
👥 - Сколько всего человек сделало ставку.
🏦 - Общий выигрыш за раунд.
<b>3. Что такое X2, X3 и X6?</b>
Это коэфициенты (множители) игры. Чем больше множитель, тем меньше шанс на его выпадение.
<b>4. Какое число должно выпасть на кубике чтобы я выиграл(-а)?</b>
<b>X2</b>: 2, 4, 6.
<b>X3</b>: 3, 5.
<b>X6</b>: 1.
<b>5. Есть ли какие-нибудь ограничения на ставки?</b>
Да. Для подписчиков @theclownfiesta максимальная ставка - <b>10 000</b> монет, для других - <b>1000</b>.
<b>6. Могу ли я ставить если мне ещё не исполнилось 18 лет?</b>
Да. В ставках на @NevermoreBets используется внутриигровая валюта, которую пользователи получают <a href="https://t.me/nevermorebetsbot?start=deposit">бесплатно</a> или <b>бонусом</b> за материальную поддержку разработчика.
Она не является платёжным средством, не представляет никакой экономической ценности и не может быть поменяна на реальные деньги.

Остались вопросы или есть предложение? Пишите: @daaetoya.
<b>Важно!</b> Если у вас нет уважительной причины, а написать хочется, тогда мы ждём вас в нашем чате: @clownfiestachat.''', parse_mode='HTML')
			return ConversationHandler.END
		elif text == 'deposit':
			update.message.reply_text('''
<b>Несколько способов получить монеты:</b>
1. Пригласить друзей в игру (/promo).
2. Выполнять задания (@clownfiestabot -> /freecoins).
3. Бесплатно, если вы общаетесь и/или играете в игру "Крокодил" в чате, где присутствует @clownfiestabot.
4. Розыгрыши на канале @theclownfiesta.
5. Поддержать разработку бота (/donate), за каждые <b>5</b> руб. вы получите <b>1000</b> монет на свой счёт :)''', parse_mode='HTML')
			return ConversationHandler.END
		elif (text == 'x2') or (text == 'x3') or (text == 'x6'):
			cursor.execute('SELECT bet_mult FROM users WHERE id = %s', (update.message.from_user.id,))
			bet = cursor.fetchone()
			if str(bet[0]) == '0':
				if text == 'x2':
					nums = 'Выигрышные числа: <b>2</b>, <b>4</b>, <b>6</b>.'
				elif text == 'x3':
					nums = 'Выигрышные числа: <b>3</b>, <b>5</b>.'
				elif text == 'x6':
					nums = 'Выигрышное число: <b>1</b>.'
				cursor.execute('SELECT exp FROM users WHERE id = %s', (update.message.from_user.id,))
				bal = cursor.fetchone()
				balance = int(bal[0])
				context.user_data['multiplier'] = int(text[1])
				update.message.reply_text(f'Укажите сумму ставки.\nВаш баланс: <b>{balance}</b> монет.\n\nВ случае выигрыша ваша ставка умножится на <b>{context.user_data["multiplier"]}</b>.\n{nums}\n\nОтменить ставку - /cancel', parse_mode='HTML')

				return BETSUMM
			else:
				update.message.reply_text('Вы уже сделали ставку на этот раунд!')

				return ConversationHandler.END
		else:
			return ConversationHandler.END
	elif str(usrid) not in str(all_users):
		update.message.reply_text('''Кажется, вы присоединились к нам <b>впервые</b>!
Краткая сводка для новичков:

Этот бот работает в паре с @clownfiestabot. Подробнее написано в разделе <a href="https://t.me/nevermorebetsbot?start=faq">ЧаВо</a>, он станет доступен после регистрации (/reg).

Полезные ссылки:
@ClownfiestaBot - Бот, созданный для развлечения пользователей. <b>Работает в чатах!</b>
Кстати, благодаря ему родился я :)
@ClownfiestaChat - Чат для обсуждений ботов и простого общения.
@TheClownfiesta - Канал, где разработчик рассказывает об обновлениях ботов, разных новостях и даже делает розыгрыши.
@NevermoreBets - Канал со ставками.

Добро пожаловать к нам!\nЧтобы зарегистрироваться и начать пользоваться ботом, нажмите: /reg''', parse_mode='HTML')

		return ConversationHandler.END


def reg(update, context):
	ids = update.message.from_user.id
	name = update.message.from_user.full_name
	cur_time = int(time.time())
	cursor.execute('SELECT id FROM users')
	members = cursor.fetchall()
	if str(ids) in str(members):
		cursor.execute('UPDATE users SET name = %s, lastmsg = %s WHERE id = %s', (name, cur_time, ids,))
	else:
		registered = time.strftime('%d.%m.%y')
		cursor.execute('INSERT INTO users (id, name, lastmsg, registered) VALUES (%s, %s, %s, %s)', (ids, name, cur_time, registered,))
		update.message.reply_text('Регистрация пройдена успешно!\nПереходите на наш канал: @NevermoreBets')
	conn.commit()


def bet_summ(update, context):
	cursor.execute('SELECT exp FROM users WHERE id = %s', (update.message.from_user.id,))
	bal = cursor.fetchone()
	balance = int(bal[0])
	multiplier = context.user_data['multiplier']
	try:
		bet = int(update.message.text)
		member = context.bot.get_chat_member(channel_username, update.message.from_user.id)
		if member.status in memberslist:
			maxBet = 10000
		else:
			maxBet = 1000
		if bet >= 100 and bet <= balance and bet <= maxBet:
			cursor.execute('UPDATE users SET exp = exp - %s, bet = %s, bet_mult = %s, total_bet = total_bet + %s WHERE id = %s', (bet, bet, multiplier, bet, update.message.from_user.id,))
			conn.commit()
			update.message.reply_text(f'💰: {balance-bet}\n🎲: [<b>X{multiplier}</b>] <b>{bet}</b> монет.\n👾: @NevermoreBets', parse_mode='HTML')
			del context.user_data['multiplier']

			return ConversationHandler.END
		elif bet >= 100 and bet > balance and bet <= maxBet:
			update.message.reply_text(f'Недостаточно монет!\nВаш баланс: <b>{balance}</b> монет.\n\nОтменить ставку - /cancel', parse_mode='HTML')
		elif bet < 100 or bet > maxBet:
			update.message.reply_text('Ошибка! <b>Мин.</b> ставка: <b>100</b> монет, <b>макс.</b> ставка: <b>1000</b> монет.\nДля подписчиков @theclownfiesta <b>макс.</b> ставка: <b>10 000</b> монет.\n\nОтменить ставку - /cancel', parse_mode='HTML')
	except:
		update.message.reply_text('Проверьте, чтобы в вашем сообщении не было лишних символов и попробуйте ещё раз.\n\nОтменить ставку - /cancel')


def cancel(update, context):
	update.message.reply_text('Охрана, отмена 😵\n\nОбязательно возвращайтесь, мы ждём вас! @NevermoreBets')

	return ConversationHandler.END


def donate(update, context):
	update.message.reply_text('Реквизиты для доната:\nСбер: 5469 3800 8674 8745\nЯ.Соберу: yasobe.ru/na/Nevermore\n\nПрикрепите ваш UserID к донату чтобы получить 1000 монет за каждые 5 руб. доната :)')
	update.message.reply_text(f'Ваш UserID: {update.message.from_user.id}')


def promo(update, context):
	update.message.reply_text(f'Ссылка для приглашения:\nhttps://t.me/NevermoreBetsBot?start=ref-{update.message.from_user.id}')


def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('Чтобы сделать ставку перейдите в этот канал: @NevermoreBets.\nЧастые вопросы и ответы на них вы можете посмотреть, нажав на соответствующую кнопку под одним из сообщений на канале.\nЕсть другие вопросы или предложения? Пишите: @daaetoya')


def bot_bets(context):
	try:
		cursor.execute('SELECT COUNT(bet_mult) FROM users WHERE bet_mult > 0')
		bet_num = cursor.fetchone()
		total_bets = int(bet_num[0])
	except:
		total_bets = 0
	job = context.job
	keyboard = [[InlineKeyboardButton("X2", url="t.me/nevermorebetsbot?start=x2"), InlineKeyboardButton("X3", url="t.me/nevermorebetsbot?start=x3"), InlineKeyboardButton("X6", url="t.me/nevermorebetsbot?start=x6")],
				[InlineKeyboardButton("Пополнить 💰", url="t.me/nevermorebetsbot?start=deposit"), InlineKeyboardButton("ЧаВо 👩‍🎓", url="t.me/nevermorebetsbot?start=faq")]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	bets = context.bot.send_dice(chat_id=channel)
	if (bets.dice.value == 2) or (bets.dice.value == 4) or (bets.dice.value == 6):
		multiplier = 'x2'
		mult = 2
	elif (bets.dice.value == 3) or (bets.dice.value == 5):
		multiplier = 'x3'
		mult = 3
	elif bets.dice.value == 1:
		multiplier = 'x6'
		mult = 6
	else:
		context.bot.send_message(chat_id=channel, text='Error')

		return
	cursor.execute('SELECT SUM(bet) FROM users WHERE bet_mult = %s', (mult,))
	bet_total = cursor.fetchone()
	try:
		total_win = int(bet_total[0])
	except:
		total_win = 0
	cursor.execute('UPDATE users SET exp = exp + bet * %s WHERE bet_mult = %s', (mult, mult,))
	cursor.execute('UPDATE users SET bet = 0, bet_mult = 0 WHERE bet_mult > 0')
	conn.commit()
	context.bot.send_message(chat_id=channel, text=f'🎉 {multiplier} | 👥 {total_bets} | 🏦 {total_win*mult}\n\nСделать ставку 👇', reply_markup=reply_markup)
	msg = context.bot.send_message(chat_id=channel, text=f'⌛️: {job.interval} секунд.')
	mID = msg.message_id
	context.job_queue.run_repeating(sec_update, interval=10, first=11, context=mID)
	global t_sec
	global t_range
	t_sec = 95
	t_range = 9


def sec_update(context):
	global t_sec
	global t_range
	job = context.job
	if t_range > 1:
		t_sec = t_sec - 10
		context.bot.edit_message_text(chat_id=channel, message_id=job.context, text=f'⌛️: {t_sec} секунд.')
		t_range = t_range - 1
	elif t_range == 1:
		t_sec = t_sec - 10
		context.bot.delete_message(chat_id=channel, message_id=job.context)
		job.schedule_removal()
	else:
		logger.info('shit')


def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
	"""Start the bot."""
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	updater = Updater("936330141:AAHTjMpi22s603reitWXuQib9mZD-Ht_YV8", use_context=True)
	# updater = Updater(os.environ['token'], use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher
	j = updater.job_queue
	j.run_repeating(bot_bets, interval=95, first=0)

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={ BETSUMM: [MessageHandler((Filters.text&(~(Filters.command))), bet_summ)], },

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("reg", reg))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("donate", donate))
	dp.add_handler(CommandHandler("promo", promo))
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
