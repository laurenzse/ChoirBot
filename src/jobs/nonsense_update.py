import datetime
from random import randint

from src.language.phrases import formulate
from src.state import choir_status

MIN_WAIT_MINUTES = 2 * 7 * 24 * 60 # 2 weeks
MAX_WAIT_MINUTES = 9 * 7 * 24 * 60 # 9 weeks


def write_nonsense(bot, job):
    # bot.send_message(chat_id=state.choir_status.chat_id,
    #                  text=formulate('abwesenheit-nicht-gesagt'))
    bot.send_message(chat_id=choir_status.get_choir_attribute(choir_status.CHOIR_CHAT_ID),
                     text=formulate('schwachsinn'))


def next_nonsense_time():
    time = datetime.datetime.now() + datetime.timedelta(minutes=randint(MIN_WAIT_MINUTES, MAX_WAIT_MINUTES))
    return time
    # return datetime.datetime.now() + datetime.timedelta(seconds=2)
