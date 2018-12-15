from bidict import bidict
from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, Filters

from state import choir_status, bot_status
from language.phrases import PersonalPhrases
from utils.group_members import BasicGroupMember

START = 'mechanical_turk'
DISCONNECT = 'trennen'
CANCEL = 'cancel'
ENTERING_CHAT_ID, TUNNEL_ACTIVE = range(2)

tunnels = bidict()


def ask_for_chat_id(bot, update):
    if choir_status.is_admin(update.effective_user):
        update.message.reply_text(
            "Ich kann eine Verbindung zu einem beliebigen Chat aufbauen, mit dem ich selbst auch schreiben köπnnte. "
            "Meine eigenen Nachrichten in diesem Chat werde ich dir allerdings nicht übermitteln. ")
        update.effective_chat.send_message("Wie lautet die ID des Chats für den ich einen Tunnel einrichten soll?")
        return ENTERING_CHAT_ID

    return ConversationHandler.END


def chat_id_entered(bot, update):
    id_string = update.message.text

    try:
        chat_id = int(id_string)
    except ValueError:
        update.message.reply_text("Bitte gib eine gültige ID ein.")

        return ENTERING_CHAT_ID

    tunnels[update.effective_chat.id] = chat_id

    update.message.reply_text("Ein Tunnel für diesen Chat ist nun aktiv.")
    update.effective_chat.send_message("Du kannst diese Verbindung jederzeit mit /{} aufheben.".format(DISCONNECT))

    return TUNNEL_ACTIVE


def any_interaction(bot, update):
    origin_id = update.effective_chat.id

    message_text = update.message.text

    if origin_id in tunnels and message_text != '/{}'.format(DISCONNECT) \
            and message_text != '/{}'.format(CANCEL):
        destiny_id = tunnels[origin_id]
        bot.send_message(destiny_id, message_text)

    if origin_id in tunnels.inv:
        destiny_id = tunnels.inv[origin_id]
        bot.send_message(destiny_id, '_{}_'.format(message_text), parse_mode=ParseMode.MARKDOWN)


def disconnect(bot, update):
    origin_id = update.effective_chat.id

    try:
        tunnels.pop(origin_id)
    except ValueError:
        return False

    update.message.reply_text('Die Verbindung wurde getrennt.')

    return True


def done(bot, update):
    if not disconnect(bot, update):
        update.message.reply_text('Ich konnte keine Verbindung finden, die getrennt werden könnte.')

    return ConversationHandler.END


def cancel(bot, update):
    disconnect(bot, update)

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(update.effective_user))
    update.message.reply_text(pp.formulate('abbrechen'))

    return ConversationHandler.END


def add_handlers(dispatcher):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START, ask_for_chat_id)],
        states={
            ENTERING_CHAT_ID: [MessageHandler(Filters.text, chat_id_entered)],
            TUNNEL_ACTIVE: [CommandHandler(DISCONNECT, done)]
        },
        fallbacks=[CommandHandler(CANCEL, cancel)]
    )

    dispatcher.add_handler(MessageHandler(Filters.all, any_interaction),
                           group=bot_status.next_service_handler_group())

    dispatcher.add_handler(conv_handler)
