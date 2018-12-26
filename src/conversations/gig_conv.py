import datetime
from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import Filters, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, \
    RegexHandler

from src.language.phrases import PersonalPhrases
from src.state import choir_status
from src.utils.group_members import BasicGroupMember
from src.datepicker import telegramcalendar

START = 'auftritt'
ENTERING_NAME, ENTERING_DATE, GIG_EXISTING, CONFIRM = range(4)
gig_operations_keyboard = [['Auftritt ändern', 'Auftritt entfernen', 'Abbrechen']]
confirm_keyboard = [['Ja', 'Nein']]

MAX_NAME_LENGTH = 140

CONVERSATION_TIMEOUT = 60 * 5  # after 5 minutes of inactivity, the conversation gets discarded


def ask_user(bot, update):
    existing_gig = choir_status.get_gig()
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    if existing_gig:
        gig_date = existing_gig['date']
        gig_name = existing_gig['name']
        update.message.reply_text((pp.formulate('auftritt-schon-vorhanden') +
                                   " " + pp.formulate('was-machen')).format(gig_name,
                                                                            gig_date.strftime("%d.%m.")),
                                  reply_markup=ReplyKeyboardMarkup(gig_operations_keyboard, one_time_keyboard=True),
                                  parse_mode=ParseMode.MARKDOWN)

        return GIG_EXISTING
    else:
        return create_gig(bot, update)


def create_gig(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('wie-ist-auftritt-name'))
    return ENTERING_NAME


def name_entered(bot, update, user_data):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    gig_name = update.message.text

    if len(gig_name) > MAX_NAME_LENGTH:
        update.message.reply_text('Fass dich kürzer, dieser Name ist ein bisschen zu lang für meinen Geschmack.')
        return ENTERING_NAME
    elif '\"' in gig_name:
        update.message.reply_text('In deinem Namen ist das böse Zeichen \" enthalten, bitte entfern das mal...')
        return ENTERING_NAME
    else:
        user_data['gig_name'] = gig_name

        update.message.reply_text(pp.formulate('wann-ist-auftritt'),
                                  reply_markup=telegramcalendar.create_calendar())
        return ENTERING_DATE


def confirm_gig(bot, update, user_data):
    selected, gig_datetime = telegramcalendar.process_calendar_selection(bot, update)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    query = update.callback_query

    if selected:
        gig_date = gig_datetime.date()
        today = datetime.date.today()
        if today > gig_date:
            bot.send_message(query.message.chat_id,
                             pp.formulate('zeitraum-bereits-vorbei') + " " + pp.formulate('wann-ist-auftritt'),
                             reply_markup=telegramcalendar.create_calendar())
            return ENTERING_DATE

        name = user_data['gig_name']
        user_data['gig_date'] = gig_date

        bot.send_message(query.message.chat_id,
                         pp.formulate('auftritt-bestätigen').format(name, gig_date.strftime("%d.%m.")),
                         reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True),
                         parse_mode=ParseMode.MARKDOWN)
        return CONFIRM

    return ENTERING_DATE


def save_gig(bot, update, user_data):
    gig_name = user_data['gig_name']
    gig_date = user_data['gig_date']

    choir_status.set_gig(gig_date, gig_name)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('etwas-gemerkt'))

    return ConversationHandler.END


def cancel(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('abbrechen'))

    return ConversationHandler.END


def remove_gig(bot, update):
    choir_status.remove_gig()

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('auftritt-gelöscht'))

    return ConversationHandler.END


def add_handlers(dispatcher):
    gig_operations_regexes = ['^{}'.format(item) for sublist in gig_operations_keyboard for item in sublist]
    confirm_regexes = ['^{}'.format(item) for sublist in confirm_keyboard for item in sublist]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START, ask_user)],
        states={
            ENTERING_NAME: [MessageHandler(Filters.text, name_entered, pass_user_data=True)],
            ENTERING_DATE: [CallbackQueryHandler(confirm_gig, pass_user_data=True)],
            CONFIRM: [RegexHandler(confirm_regexes[0], save_gig, pass_user_data=True),
                      RegexHandler(confirm_regexes[1], create_gig)],
            GIG_EXISTING: [RegexHandler(gig_operations_regexes[0], create_gig),
                           RegexHandler(gig_operations_regexes[1], remove_gig),
                           RegexHandler(gig_operations_regexes[2], cancel)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT
    )

    dispatcher.add_handler(conv_handler)

