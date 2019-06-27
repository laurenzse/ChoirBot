import datetime

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, RegexHandler, Filters

from src.language.phrases import PersonalPhrases
from src.state import choir_status
from src.utils.group_members import BasicGroupMember
import src.datepicker.telegramcalendar as telegramcalendar
from src.jobs import pre_rehearsal_update

ABSENT_REGEX_FILE = 'src/language/absent_regex.txt'

START = 'abwesend'
SELECTION, SELECT_START, SELECT_END, CONFIRM = range(4)

new_absence_keyboard = [['Nur nächstes Mal', 'Längerer Zeitraum'], ['Abbrechen']]
existing_absence_keyboard = [['Fehle nur nächstes Mal', 'Zeitraum ändern', 'Fehle doch nicht'], ['Abbrechen']]
confirm_keyboard = [['Ja', 'Nein']]

CONVERSATION_TIMEOUT = 60 * 5 # after 5 minutes of inactivity, the conversation gets discarded


def register_absence(bot, update):
    return start_absence_registration(update.message, update.effective_user)


def absence_recognized(bot, update):
    if update.effective_chat.id != update.message.from_user.id:
        original_message = bot.forward_message(update.message.from_user.id, update.effective_chat.id, update.message.message_id)
    else:
        original_message = update.message

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(original_message.from_user))

    bot.send_message(update.message.from_user.id,
                     pp.formulate('abwesend-erkannt'),
                     reply_to_message_id=original_message.message_id)

    return start_absence_registration(original_message, update.effective_user)


def start_absence_registration(message, user):
    existing_absence = choir_status.get_absence_of_user(user)
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(user))
    if existing_absence:
        start_date, end_date = existing_absence
        message.reply_text((pp.formulate('abwesenheit-bereits-vermerkt') +
                                   " " + pp.formulate('was-machen')).format(start_date.strftime("%d.%m."),
                                                                            end_date.strftime("%d.%m.")),
                                  reply_markup=ReplyKeyboardMarkup(existing_absence_keyboard, one_time_keyboard=True),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        message.reply_text(pp.formulate('nächstes-mal-oder-länger'),
                                  reply_markup=ReplyKeyboardMarkup(new_absence_keyboard, one_time_keyboard=True))
    return SELECTION


def save_absence_once(bot, update):
    next_rehearsal = choir_status.next_rehearsal_date(datetime.date.today())
    # day_after = next_rehearsal + datetime.timedelta(1)

    choir_status.remove_absence_of_user(update.effective_user)  # first try to remove an existing absence
    choir_status.add_absence(update.effective_user, next_rehearsal, next_rehearsal)
    pre_rehearsal_update.refresh_posted_update(bot)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('etwas-gemerkt'))

    return ConversationHandler.END


def delete_existing_absence(bot, update):
    choir_status.remove_absence_of_user(update.effective_user)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('doch-da'))
    pre_rehearsal_update.refresh_posted_update(bot)

    return ConversationHandler.END


def ask_duration_start(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('ab-wann-abwesend'),
                              reply_markup=telegramcalendar.create_calendar())

    return SELECT_START


def ask_duration_end(bot, update, user_data):
    selected, start_date = telegramcalendar.process_calendar_selection(bot, update)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    query = update.callback_query

    if selected:
        user_data['absence_conv_start'] = start_date
        bot.send_message(query.message.chat_id, pp.formulate('bis-wann-abwesend'),
                         reply_markup=telegramcalendar.create_calendar())
        return SELECT_END

    return SELECT_START


def confirm_duration(bot, update, user_data):
    selected, end_date = telegramcalendar.process_calendar_selection(bot, update)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    query = update.callback_query

    if selected:
        if end_date.date() < datetime.date.today():
            bot.send_message(query.message.chat_id,
                             pp.formulate('zeitraum-bereits-vorbei') + " " + pp.formulate('ab-wann-abwesend'),
                             reply_markup=telegramcalendar.create_calendar())
            return SELECT_START

        start_date = user_data['absence_conv_start']

        if end_date < start_date:
            bot.send_message(query.message.chat_id,
                             pp.formulate('ende-vor-start') + " " + pp.formulate('ab-wann-abwesend'),
                             reply_markup=telegramcalendar.create_calendar())
            return SELECT_START

        user_data['absence_conv_end'] = end_date
        bot.send_message(query.message.chat_id,
                         pp.formulate('zeitraum-bestätigen').format(start_date.strftime("%d.%m."), end_date.strftime("%d.%m.")),
                         reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True),
                         parse_mode=ParseMode.MARKDOWN)
        return CONFIRM

    return SELECT_END


def save_absence_duration(bot, update, user_data):
    start_date = user_data['absence_conv_start'].date()
    end_date = user_data['absence_conv_end'].date()

    choir_status.remove_absence_of_user(update.effective_user)  # first try to remove an existing absence
    choir_status.add_absence(update.effective_user, start_date, end_date)
    pre_rehearsal_update.refresh_posted_update(bot)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('etwas-gemerkt'))

    return ConversationHandler.END


def cancel(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('abbrechen'))

    return ConversationHandler.END


def add_handlers(dispatcher):
    new_abs_regexes = ['^{}'.format(item) for sublist in new_absence_keyboard for item in sublist]
    existing_abs_regexes = ['^{}'.format(item) for sublist in existing_absence_keyboard for item in sublist]
    confirm_regexes = ['^{}'.format(item) for sublist in confirm_keyboard for item in sublist]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START, register_absence, filters=Filters.private),
                      CommandHandler(START, absence_recognized, filters=~ Filters.private),
                      RegexHandler(absent_regex(), absence_recognized)],
        states={
            SELECTION: [RegexHandler(new_abs_regexes[0], save_absence_once),
                        RegexHandler(new_abs_regexes[1], ask_duration_start),
                        RegexHandler(new_abs_regexes[2], cancel),
                        RegexHandler(existing_abs_regexes[0], save_absence_once),
                        RegexHandler(existing_abs_regexes[1], ask_duration_start),
                        RegexHandler(existing_abs_regexes[2], delete_existing_absence),
                        RegexHandler(existing_abs_regexes[3], cancel)],
            SELECT_START: [CallbackQueryHandler(ask_duration_end, pass_user_data=True)],
            SELECT_END: [CallbackQueryHandler(confirm_duration, pass_user_data=True)],
            CONFIRM: [RegexHandler(confirm_regexes[0], save_absence_duration, pass_user_data=True),
                      RegexHandler(confirm_regexes[1], ask_duration_start)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
        per_chat=False,     # ignore the chat, so we can transfer a conversation to a private chat
        per_user=True,
    )

    dispatcher.add_handler(conv_handler)


def absent_regex():
    with open(ABSENT_REGEX_FILE, 'r') as file:
        data = file.read().replace('\n', '')
    return data
