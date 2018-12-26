from telegram.ext import MessageHandler, Filters
from src.language.phrases import PersonalPhrases
from src.utils.group_members import BasicGroupMember
import src.state.bot_status

THANK_YOU = ['dank']


def interaction(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    text = update.message.text.lower()
    if any(s in text for s in THANK_YOU):
        update.message.reply_text(pp.formulate('gern-geschehen'))


def add_handlers(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.private, interaction),
                           group=src.state.bot_status.next_service_handler_group())
