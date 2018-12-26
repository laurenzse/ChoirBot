import datetime

from src.language.phrases import formulate
from src.state import choir_status

reminder_before = datetime.timedelta(minutes=15)


def update(bot, job):
    chat_id = choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID)

    inform_about_absences(bot, chat_id)

    inform_about_reminders(bot, chat_id)

    inform_about_gig(bot, chat_id)


def inform_about_absences(bot, chat_id):
    absences = choir_status.absences_at_date(choir_status.next_rehearsal_date(datetime.date.today()))
    if not absences:
        bot.send_message(chat_id=chat_id,
                         text=formulate('niemand-fehlt'))
    else:
        bot.send_message(chat_id=chat_id,
                         text=formulate('jemand-fehlt'))
        bot.send_message(chat_id=chat_id,
                         text=generate_absence_list(absences))


def inform_about_reminders(bot, chat_id):
    reminders = choir_status.get_reminders()
    if reminders:
        bot.send_message(chat_id=chat_id,
                         text="Mir wurde gesagt, dass ich an gewisse Sachen erinnern soll.")
        bot.send_message(chat_id=chat_id,
                         text=generate_reminders_list(reminders))
    choir_status.clear_reminders()


def inform_about_gig(bot, chat_id):
    if choir_status.get_gig():
        weeks_until_gig = choir_status.rehearsals_until_gig()
        gig = choir_status.get_gig()

        if weeks_until_gig == 1:
            bot.send_message(chat_id=chat_id,
                             text="Noch eine Probe bis zum Auftritt {}!".format(gig['name']))
        elif weeks_until_gig >= 1:
            bot.send_message(chat_id=chat_id,
                             text="Bis zum Auftritt {} noch {} Proben!".format(gig['name'], weeks_until_gig))


def generate_absence_list(absences):
    return '- ' + '\n- '.join(map(lambda member: member.first_name, absences))


def generate_reminders_list(reminders):
    return '- ' + '\n- '.join(map(lambda member_reminder: '{}: \"{}\"'.format(member_reminder[0].first_name,
                                                                              member_reminder[1]),
                                  reminders))


def update_datetime():
    now_after_reminder = datetime.datetime.now() + reminder_before
    reminder_datetime = choir_status.next_rehearsal_datetime(now_after_reminder) - reminder_before
    return reminder_datetime
    # return datetime.datetime.now() + datetime.timedelta(seconds=20)
