import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from src.language.phrases import formulate, PersonalPhrases
from src.state import choir_status
from src.utils.group_members import BasicGroupMember

reminder_before = datetime.timedelta(minutes=60)

keyboard = [[InlineKeyboardButton("Meine Anwesenheit ändern", callback_data='change_absence')]]
reply_markup = InlineKeyboardMarkup(keyboard)
last_sent_message_id = None


def update_text():
    texts = [absence_text(), reminder_text(), gig_text()]
    filtered_texts = list(filter(None, texts))
    return '\n\n'.join(filtered_texts)


def absence_text():
    text = ""

    absences = choir_status.absences_at_date(choir_status.next_rehearsal_date(datetime.date.today()))
    if not absences:
        text = formulate('niemand-fehlt')
    else:
        text = formulate('jemand-fehlt') + '\n\n' + generate_absence_list(absences)

    return text


def reminder_text():
    text = ""
    reminders = choir_status.get_reminders()
    if reminders:
        text = "Mir wurde gesagt, dass ich an gewisse Sachen erinnern soll.\n\n" + generate_reminders_list(reminders)
    choir_status.clear_reminders()

    return text


def gig_text():
    text = ""
    if choir_status.get_gig():
        weeks_until_gig = choir_status.rehearsals_until_gig()
        gig = choir_status.get_gig()

        if weeks_until_gig == 1:
            text = "Noch eine Probe bis zum Auftritt {}!".format(gig['name'])
        elif weeks_until_gig >= 1:
            text = "Bis zum Auftritt {} noch {} Proben!".format(gig['name'], weeks_until_gig)

    return text


def generate_absence_list(absences):
    return '- ' + '\n- '.join(map(lambda member: member.first_name, absences))


def generate_reminders_list(reminders):
    return '- ' + '\n- '.join(map(lambda member_reminder: '{}: \"{}\"'.format(member_reminder[0].first_name,
                                                                              member_reminder[1]),
                                  reminders))


def post_update(bot, job):
    global last_sent_message_id
    chat_id = choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID)

    full_update_text = update_text()

    sent_message = bot.send_message(chat_id=chat_id,
                                    text=full_update_text,
                                    reply_markup=reply_markup)

    last_sent_message_id = sent_message.message_id


def handle_absence_switch_callback(bot, update):
    query = update.callback_query

    if query.message.message_id != last_sent_message_id:
        pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
        query.edit_message_reply_markup(reply_markup=None)
        query.edit_message_text(text=pp.formulate('illegal-action'))
        return

    member = BasicGroupMember.from_telegram_user(update.effective_user)

    toggle_absences_for_member(member)

    query.edit_message_text(text=update_text(), reply_markup=reply_markup)


def toggle_absences_for_member(member):
    next_date = choir_status.next_rehearsal_date(datetime.date.today())
    absences = choir_status.absences_at_date(next_date)
    if member in absences:
        choir_status.remove_absence_of_user(member)
    else:
        until_date = next_date + datetime.timedelta(1)
        choir_status.add_absence(member, next_date, until_date)


def add_handlers(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(handle_absence_switch_callback,
                                                pattern='^change_absence$'))

def update_datetime():
    now_after_reminder = datetime.datetime.now() + reminder_before
    reminder_datetime = choir_status.next_rehearsal_datetime(now_after_reminder) - reminder_before
    return reminder_datetime
    # return datetime.datetime.now() + datetime.timedelta(seconds=10)
