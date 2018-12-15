import datetime
from state import choir_status
from language.phrases import formulate

reminder_after = datetime.timedelta(minutes=choir_status.get_choir_attribute(choir_status.REHEARSAL_DURATION) * 0.75)


def update(bot, job):
    bot.send_message(chat_id=choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID),
                     text="/wunschlied verwenden um die Person fürs nächste Wunschlied zu bestimmen, /erinnern verwenden um Erinnerungen für die nächste Probe zu erstellen.",
                     disable_notification=True)


def update_datetime():
    now_before_reminder = datetime.datetime.now() - reminder_after
    reminder_datetime = choir_status.next_rehearsal_datetime(now_before_reminder) + reminder_after
    return reminder_datetime
    # return datetime.datetime.now() + datetime.timedelta(seconds=10)
