import datetime
import random
from telegram import ParseMode

from src.language.phrases import formulate
from src.state import choir_status
from src.jobs import pre_rehearsal_update
POST_PROBABILTY = 0.2

reminder_after = datetime.timedelta(minutes=choir_status.get_choir_attribute(choir_status.REHEARSAL_DURATION) * 0.75)


def update(bot, job):
    pre_rehearsal_update.posted_update_message_id = None
    if random.random() < POST_PROBABILTY:
        bot.send_message(chat_id=choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID),
                         text=formulate('nach-der-probe'),
                         disable_notification=True,
                         parse_mode=ParseMode.MARKDOWN)


def update_datetime():
    now_before_reminder = datetime.datetime.now() - reminder_after
    reminder_datetime = choir_status.next_rehearsal_datetime(now_before_reminder) + reminder_after
    return reminder_datetime
    # return datetime.datetime.now() + datetime.timedelta(seconds=10)
