import random
from telegram.ext import MessageHandler, Filters

from src.language.phrases import formulate
import src.state.bot_status

REPLY_PROBABILITY = 1/200


def interaction(bot, update):
    if random.random() < REPLY_PROBABILITY:
        update.message.reply_text(formulate('verwirrt'))


def add_handlers(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.group, interaction),
                           group=src.state.bot_status.next_service_handler_group())
