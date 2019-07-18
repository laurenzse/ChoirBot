import re
from telegram import ParseMode
from telegram.ext import (CommandHandler)

from src.utils.group_members import BasicGroupMember
from src.language.phrases import PersonalPhrases

START = 'start'

def respond_start(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    update.message.reply_text(pp.formulate('start'))


def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler(START, respond_start))
