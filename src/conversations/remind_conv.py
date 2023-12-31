import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import Filters, CommandHandler, ConversationHandler, MessageHandler, RegexHandler

from src.language.phrases import PersonalPhrases
from src.utils.group_members import BasicGroupMember
from src.state import choir_status

START = 'erinnern'
ENTERING = range(1)
reminder_operations_keyboard = [['Erinnerung löschen', 'Abbrechen']]

MAX_REMINDER_LENGTH = 280

CONVERSATION_TIMEOUT = 60 * 5  # after 5 minutes of inactivity, the conversation gets discarded


def ask_user(bot, update):
    existing_reminder = choir_status.get_reminder_of_user(update.effective_user)
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    if existing_reminder:
        update.message.reply_text(pp.formulate('erinnerung-schon-vorhanden').format(existing_reminder),
                                  reply_markup=ReplyKeyboardMarkup(reminder_operations_keyboard, one_time_keyboard=True))
    else:
        update.message.reply_text(pp.formulate('an-was-erinnern'))

    return ENTERING


def enter_reminder(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    reminder_text = update.message.text

    if len(reminder_text) > MAX_REMINDER_LENGTH:
        update.message.reply_text('Fass dich kürzer, diese Erinnerung ist ein bisschen zu lang für meinen Geschmack.')
        return ENTERING
    elif '\"' in reminder_text:
        update.message.reply_text('In deiner Erinnerung ist das böse Zeichen \" enthalten, bitte entfern das mal...')
        return ENTERING
    else:
        choir_status.remove_reminder_of_user(update.effective_user)  # first try to remove an existing reminder
        next_rehearsal = choir_status.next_rehearsal_datetime(datetime.datetime.now()).date()
        choir_status.add_reminder(update.effective_user, update.message.text, next_rehearsal)

        update.message.reply_text(pp.formulate('etwas-gemerkt'))
        return ConversationHandler.END


def cancel(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('abbrechen'))

    return ConversationHandler.END


def delete_reminder(bot, update):
    choir_status.remove_reminder_of_user(update.effective_user)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('erinnerung-gelöscht'))

    return ConversationHandler.END


def add_handlers(dispatcher):
    operations_regexes = ['^{}'.format(item) for sublist in reminder_operations_keyboard for item in sublist]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START, ask_user)],
        states={
            ENTERING: [RegexHandler(operations_regexes[1], cancel),
                       RegexHandler(operations_regexes[0], delete_reminder),
                       MessageHandler(Filters.text, enter_reminder)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT
    )

    dispatcher.add_handler(conv_handler)

