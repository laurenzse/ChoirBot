from bisect import bisect
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (CommandHandler, CallbackQueryHandler)

from state import choir_status, bot_status
from utils.group_members import BasicGroupMember
from language.phrases import PersonalPhrases

START = 'wunschlied'
keyboard = [[InlineKeyboardButton("Danke!", callback_data='wish_confirm'),
             InlineKeyboardButton("Nicht da", callback_data='wish_next')],
            [InlineKeyboardButton("Abbrechen", callback_data='wish_cancel')]]
reply_markup = InlineKeyboardMarkup(keyboard)


def wish_song(bot, update, user_data, chat_data):
    # the current next wishing member which is being presented to the user
    current_next_wish = next_wish_member(choir_status.get_choir_attribute(choir_status.LAST_WISH))
    chat_data['current_next_wish'] = current_next_wish

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    sent_message = update.message.reply_text(pp.formulate('wunschlied').format(next_wish_string(current_next_wish)),
                                             reply_markup=reply_markup,
                                             parse_mode=ParseMode.MARKDOWN)

    # save the id of the last sent message to prevent editing data with older messages
    chat_data['last_sent_message_id'] = sent_message.message_id


def handle_callback(bot, update, user_data, chat_data):
    current_next_wish = chat_data['current_next_wish']

    query = update.callback_query

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    # if a user tries to answer to a message older than the last one sent, dismiss them
    if query.message.message_id != chat_data['last_sent_message_id']:
        query.edit_message_reply_markup(reply_markup=None)
        query.edit_message_text(text=pp.formulate('illegal-action'))
        return

    if query.data == 'wish_next':
        complain_to_member(bot, current_next_wish)

        current_next_wish = next_wish_member(current_next_wish)
        chat_data['current_next_wish'] = current_next_wish
        answer = pp.formulate('folgereaktion') + ' ' + \
                 pp.formulate('wahl').format(next_wish_string(current_next_wish))
        query.edit_message_text(text=answer, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    elif query.data == 'wish_confirm':
        query.edit_message_reply_markup(reply_markup=None)
        set_current_wish_member(current_next_wish)
        bot.send_message(query.message.chat_id, pp.formulate('gern-geschehen'))

    elif query.data == 'wish_cancel':
        query.edit_message_reply_markup(reply_markup=None)
        bot.send_message(query.message.chat_id, pp.formulate('abbrechen'))


def complain_to_member(bot, member):
    pp = PersonalPhrases(member)
    if member.id != -1:
        bot.send_message(member.id, pp.formulate('abwesenheit-nicht-gesagt'))


def next_wish_string(member):
    return member.first_name


def set_current_wish_member(user):
    current_member = BasicGroupMember.create_from_existing(user)
    choir_status.set_choir_attribute(choir_status.LAST_WISH, current_member)


def next_wish_member(last_wish):
    members = bot_status.singer_watcher.members()
    absences = choir_status.absences_at_date(choir_status.next_rehearsal_date(datetime.date.today()))

    attending_members = [member for member in members if member not in absences]

    sorted_members = sorted(attending_members, key=lambda member: member.full_name.lower())

    next_index = next_member_index(last_wish, sorted_members)
    return sorted_members[next_index]


def next_member_index(current_member, sorted_members):
    try:
        index = sorted_members.index(current_member)
    except ValueError:
        # member does not exist (anymore), search previous one according to name
        all_member_names = list(map(lambda member: member.full_name.lower(), sorted_members))
        index = bisect(all_member_names, current_member.full_name.lower()) - 1 % len(all_member_names)

    return (index + 1) % len(sorted_members)


def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler(START, wish_song, pass_user_data=True, pass_chat_data=True))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback,
                                                pattern='^(^wish_confirm$|^wish_next$|^wish_cancel$)',
                                                pass_user_data=True,
                                                pass_chat_data=True))
