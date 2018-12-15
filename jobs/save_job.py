import datetime
from state import choir_status
from random import randint
from language.phrases import formulate

MINUTE_INTERVAL = 60  # save every hour


def write_nonsense(bot, job):
    # bot.send_message(chat_id=state.choir_status.chat_id,
    #                  text=formulate('abwesenheit-nicht-gesagt'))
    bot.send_message(chat_id=choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID),
                     text=formulate('schwachsinn'))


def next_nonsense_time():
    time = datetime.datetime.now() + datetime.timedelta(minutes=MINUTE_INTERVAL)
    return time
    # return datetime.datetime.now() + datetime.timedelta(seconds=2)
