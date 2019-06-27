from telegram import ReplyKeyboardMarkup, constants
from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, RegexHandler, Filters

from src.language.phrases import PersonalPhrases
from src.state import choir_status, bot_status
from src.utils.group_members import BasicGroupMember
from src.utils import message_jobs

START = 'admin'
SELECTING, ITEM_SELECTING_FOR_PRINT, ITEM_SELECTING_FOR_CHANGE, CHANGE_ITEM, CONFIRM_RESET, MEMBER_SELECTING = range(6)

possible_operations_keyboard = [['Element ausgeben', 'Element ändern'], ['Verfügbare Elemente ausgeben', 'Alle Elemente zurücksetzen'], ['Mitglieder ausgeben', 'Mitglied entfernen'], ['Zuletzt empfangene Nachrichten'], ['Jobs erneut erstellen'], ['Jetzt speichern'], ['Fertig']]
confirm_keyboard = [['Ja', 'Nein']]

CONVERSATION_TIMEOUT = 60 * 30 # after 30 minutes of inactivity, the conversation gets discarded


def present_selection(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))

    if choir_status.is_admin(update.effective_user):
        update.message.reply_text("Was möchtest du machen?",
                              reply_markup=ReplyKeyboardMarkup(possible_operations_keyboard, one_time_keyboard=True))
        return SELECTING
    else:
        update.message.reply_text(pp.formulate('illegal-action'))
        return ConversationHandler.END


def print_items(bot, update):
    update.message.reply_text(status_item_names_as_string(choir_status.access_attributes()))
    return present_selection(bot, update)


def status_item_names_as_string(status):
    return '\n'.join(list(status.keys()))


def ask_for_item_to_print(bot, update):
    update.message.reply_text('Welches Element soll ausgegeben werden?')
    return ITEM_SELECTING_FOR_PRINT


def print_item(bot, update):
    item_name = update.message.text
    update.message.reply_text(str(choir_status.get_choir_attribute(item_name))[-constants.MAX_MESSAGE_LENGTH:])
    return present_selection(bot, update)


def ask_for_item_change(bot, update):
    update.message.reply_text('Welches Element soll geändert werden?')
    return ITEM_SELECTING_FOR_CHANGE


def ask_for_new_item_content(bot, update, user_data):
    item_name = update.message.text
    user_data['selected_item'] = item_name
    update.message.reply_text('Was soll der neue Inhalt von {} sein?'.format(item_name))
    return CHANGE_ITEM


def perform_change(bot, update, user_data):
    item_name = user_data['selected_item']

    try:
        # we only give admins access, still this could be dangerous
        unevaluated_item = update.message.text
        new_item = eval(unevaluated_item)

        success = choir_status.set_choir_attribute(item_name, new_item)
    except SyntaxError:
        success = False

    if success:
        update.message.reply_text('Das Element wurde entsprechend geändert.')
    else:
        update.message.reply_text('Das Element wurde nicht geändert.')

    return present_selection(bot, update)


def recently_received_message(bot, update):
    messages = bot_status.all_messages_watcher.recent_messages()

    def message_object_summary(message):
        summary = '"{}" from {}, user-id: {}, chat-id: {}, chat-type: {}'.format(message.text,
                                                                                 message.from_user.full_name,
                                                                                 message.from_user.id,
                                                                                 message.chat.id,
                                                                                 message.chat.type)
        return summary

    string_messages = '\n\n'.join(list(map(message_object_summary, messages)))
    update.message.reply_text(string_messages[-constants.MAX_MESSAGE_LENGTH:])

    return present_selection(bot, update)


def recreate_jobs(bot, update):
    message_jobs.delete_all_jobs()
    message_jobs.check_message_jobs()
    update.message.reply_text('Die Jobs wurden erneut erstellt.')

    return present_selection(bot, update)


def confirm_reset(bot, update):
    update.message.reply_text('Möchtest du wirklich alle Attribute zurücksetzen?',
                              reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True))

    return CONFIRM_RESET


def reset_choir_attributes(bot, update):
    choir_status.reset_to_default()
    choir_status.choir_attributes[choir_status.ADMINS] = [update.effective_user.id]
    update.message.reply_text('Alle Attribute wurden zurückgesetzt. '
                              'Zu Verwaltungszwecken wurdest du erneut als Admin eingetragen.')

    return present_selection(bot, update)


def save_configuration(bot, update):
    bot_status.save_configuration()
    update.message.reply_text('Die aktuelle Konfiguration wurde gespeichert.')

    return present_selection(bot, update)


def print_choir_members(bot, update):
    members = bot_status.singer_watcher.members()
    members_strings = [member_description(member) for member in members]
    members_message = '\n\n'.join(members_strings)

    for chunk in chunks(members_message, constants.MAX_MESSAGE_LENGTH):
            update.message.reply_text(chunk)
    return present_selection(bot, update)


def member_description(member):
    return "name: {}\nusername: {}\nuser_id: {}".format(member.full_name, member.username, member.id)


# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def ask_for_member_to_remove(bot, update):
    update.message.reply_text('Welches Mitglied soll entfernt werden?')
    return MEMBER_SELECTING


def remove_member(bot, update):
    user_search = update.message.text

    members = bot_status.singer_watcher.members()
    for member in members:
        if member.full_name == user_search or member.username == user_search or str(member.id) == user_search:
            bot_status.singer_watcher.remove_user(bot, member)
            member_string = member_description(member)
            update.message.reply_text("Folgendes Mitglied wurde entfernt:\n{}".format(member_string))
            return present_selection(bot, update)

    update.message.reply_text("Es konnte kein passendes Mitglied entfernt werden.")
    return present_selection(bot, update)


def done(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('gern-geschehen'))

    return ConversationHandler.END


def cancel(bot, update):
    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('abbrechen'))

    return ConversationHandler.END


def add_handlers(dispatcher):
    operations_regexes = ['^{}'.format(item) for sublist in possible_operations_keyboard for item in sublist]
    confirm_regexes = ['^{}'.format(item) for sublist in confirm_keyboard for item in sublist]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START, present_selection, filters=Filters.private)],
        states={
            SELECTING: [RegexHandler(operations_regexes[0], ask_for_item_to_print),
                        RegexHandler(operations_regexes[1], ask_for_item_change),
                        RegexHandler(operations_regexes[2], print_items),
                        RegexHandler(operations_regexes[3], confirm_reset),
                        RegexHandler(operations_regexes[4], print_choir_members),
                        RegexHandler(operations_regexes[5], ask_for_member_to_remove),
                        RegexHandler(operations_regexes[6], recently_received_message),
                        RegexHandler(operations_regexes[7], recreate_jobs),
                        RegexHandler(operations_regexes[8], save_configuration),
                        RegexHandler(operations_regexes[9], done)],
            ITEM_SELECTING_FOR_CHANGE: [MessageHandler(Filters.text, ask_for_new_item_content, pass_user_data=True)],
            ITEM_SELECTING_FOR_PRINT: [MessageHandler(Filters.text, print_item)],
            MEMBER_SELECTING: [MessageHandler(Filters.text, remove_member)],
            CHANGE_ITEM: [MessageHandler(Filters.text, perform_change, pass_user_data=True)],
            CONFIRM_RESET: [RegexHandler(confirm_regexes[0], reset_choir_attributes),
                            RegexHandler(confirm_regexes[1], present_selection)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT
    )

    dispatcher.add_handler(conv_handler)