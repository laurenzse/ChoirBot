#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
from telegram.ext import (Updater)
from telegram.utils.request import Request

from src.conversations import absence_conv, wish_song_conv, confused_comment, remind_conv, admin_conv, mechanical_turk, \
    help_conv, gig_conv
from src.jobs import pre_rehearsal_update, post_rehearsal_update, nonsense_update, save_job
from src.state import choir_status
from src.state.bot_status import singer_watcher, all_members_watcher, all_messages_watcher, logger, \
    friendly_chatting_strategy, bot_token, save_configuration
from src.utils.hooked_bot import HookedBot
from src.conversations import thank_you_comment
from src import utils


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create request object manually since we also create a custom bot object
    request = Request(con_pool_size=8)

    # Create the Updater and pass it the bot's token.
    # The friendly chatting strategy greets users when it begins talking to them
    bot = HookedBot(friendly_chatting_strategy, bot_token, request=request)
    updater = Updater(bot=bot)

    # Send startup message to admins
    send_startup_message(bot)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set dispatchers for all watchers so we know the persons the bot is talking to and the messages it gets send
    singer_watcher.set_dispatcher(dp)
    all_members_watcher.set_dispatcher(dp)
    all_messages_watcher.set_dispatcher(dp)

    # Serious conversations
    wish_song_conv.add_handlers(dp)
    absence_conv.add_handlers(dp)
    remind_conv.add_handlers(dp)
    admin_conv.add_handlers(dp)
    help_conv.add_handlers(dp)
    gig_conv.add_handlers(dp)

    # Fun conversations
    confused_comment.add_handlers(dp)
    thank_you_comment.add_handlers(dp)
    mechanical_turk.add_handlers(dp)

    utils.message_jobs.job_queue = updater.job_queue
    utils.message_jobs.add_job('PRE_REHEARSAL_UPDATE',
                                   pre_rehearsal_update.update,
                                   pre_rehearsal_update.update_datetime)
    utils.message_jobs.add_job('POST_REHEARSAL_UPDATE',
                                   post_rehearsal_update.update,
                                   post_rehearsal_update.update_datetime)
    utils.message_jobs.add_job('SAVE_JOB',
                                   save_job.save,
                                   save_job.next_save_time)
    utils.message_jobs.add_job('NONSENSE',
                                   nonsense_update.write_nonsense,
                                   nonsense_update.next_nonsense_time)
    utils.message_jobs.check_message_jobs()

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # React to a stop event by saving the data
    signal.signal(signal.SIGINT, signal_handler)

    # Save the current configuration to create config files if not existing
    save_configuration()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



def send_startup_message(bot):
    admins = choir_status.choir_attributes[choir_status.ADMINS]

    for admin_id in admins:
        bot.send_message(admin_id, "Der Bot wurde soeben gestartet.")


def signal_handler(sig, frame):
    print('Stopping...')
    save_configuration()


if __name__ == '__main__':
    main()
