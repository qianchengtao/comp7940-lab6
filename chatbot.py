# from telegram import Update
# from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
from telegram.ext import *
import configparser
import logging
import redis
from ChatGPT_HKBU import HKBU_ChatGPT
import os

global redis1
def main():
    config = configparser.ConfigParser()
    # config.read('config.ini')
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(os.environ['HOST']),
                         password=(os.environ['PASSWORD']),
                         port=(os.environ['REDISPORT'])

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)


    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
                                     equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    # To start the bot:
    updater.start_polling()
    updater.idle()

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update, context) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update, context) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +
                                  redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def hello_command(update, context) -> None:
    """Send a message when the command /hello is issued."""
    logging.info(context.args[0])
    msg = context.args[0]
    update.message.reply_text('Good day, '+msg+'!')

if __name__ == '__main__':
    main()