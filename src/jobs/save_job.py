import datetime

from src.state.bot_status import save_configuration

MINUTE_INTERVAL = 60  # save every hour


def save(bot, job):
    save_configuration()


def next_save_time():
    time = datetime.datetime.now() + datetime.timedelta(minutes=MINUTE_INTERVAL)
    return time
    # return datetime.datetime.now() + datetime.timedelta(seconds=2)
