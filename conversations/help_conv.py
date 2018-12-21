from telegram import ParseMode
from telegram.ext import (CommandHandler)

from utils.group_members import BasicGroupMember
from language.phrases import PersonalPhrases
import re

COMMANDS_PATTERN = '## Commands.+(?=##)'
HELP_FILE_NAME = 'README.md'
START = 'hilfe'

commands_help = None


def show_help(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    update.message.reply_text(pp.formulate('hilfe'))
    update.message.reply_text(commands_string(HELP_FILE_NAME), parse_mode=ParseMode.MARKDOWN)


def commands_string(file_name):
    global commands_help
    if commands_help:
        return commands_help

    with open(file_name, 'r') as file:
        help_string = file.read()

    matches = re.search(COMMANDS_PATTERN, help_string, re.S)
    commands_help = matches[0]
    return commands_help


def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler(START, show_help))
    dispatcher.add_handler(CommandHandler('/help', show_help))
