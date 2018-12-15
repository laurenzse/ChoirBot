import datetime
from state import choir_status
from random import randint
from language.phrases import formulate

MIN_WAIT_MINUTES = 2 * 60 # 2 hours
MAX_WAIT_MINUTES = 3 * 7 * 24 * 60 # 3 weeks


def write_nonsense(bot, job):
    # bot.send_message(chat_id=state.choir_status.chat_id,
    #                  text=formulate('abwesenheit-nicht-gesagt'))
    bot.send_message(chat_id=choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID),
                     text=formulate('schwachsinn'))


def next_nonsense_time():
    time = datetime.datetime.now() + datetime.timedelta(minutes=randint(MIN_WAIT_MINUTES, MAX_WAIT_MINUTES))
    return time
    # return datetime.datetime.now() + datetime.timedelta(seconds=2)
