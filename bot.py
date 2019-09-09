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


from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


members = 'creator, administrator, member'
memberslist = members.split(', ')


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


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')
    
    
@run_async  
def getAudio(update, context):
    audio = update.message.audio
    update.message.reply_text(audio.file_id)
    
    
@run_async
def echo(update, context):
    text = update.message.text
    command1 = '!8ball'
    command2 = '!love'
    invoker = update.message.from_user.full_name
    target = text.partition(' ')[2]
    if command1 in update.message.text:
        update.message.reply_text(
            f'Такс.. Розбійник говорит что твои шансы на успех равны: {random.randrange(101)}%')
    elif command2 in update.message.text:
        update.message.reply_text(
            f'Здесь {random.randrange(101)}% совместимости между {invoker} и {target}')
    else:
        pass


@run_async
def inlinequery(update, context):
    """Handle the inline query."""
    userid = update.inline_query.from_user.id
    target = update.inline_query.query
    name = update.inline_query.from_user.full_name
    member = context.bot.get_chat_member('@rozbiynuki', userid)
    if member.status in memberslist:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Їбемо " + update.inline_query.query,
                input_message_content=InputTextMessageContent(
                    message_text=f'{name} {random.choice(actions.action1)} {target} {random.choice(actions.action2)}'))]

        update.inline_query.answer(results)

    else:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Перед трахом підпишися на @razbiynuki",
                input_message_content=InputTextMessageContent(
                    message_text=
                    'Чтобы трахать всё и вся, надо подписаться на наш ламповый канал! Жми: @rozbiynuki'))]

        update.inline_query.answer(results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.audio, getAudio))
    dp.add_handler(MessageHandler(Filters.text, echo))

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
