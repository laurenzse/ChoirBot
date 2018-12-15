from telegram.ext import MessageHandler, Filters
import random
import state.bot_status
from language.phrases import formulate

REPLY_PROBABILITY = 1/200


def interaction(bot, update):
    if random.random() < REPLY_PROBABILITY:
        update.message.reply_text(formulate('verwirrt'))


def add_handlers(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.group, interaction),
                           group=state.bot_status.next_service_handler_group())
