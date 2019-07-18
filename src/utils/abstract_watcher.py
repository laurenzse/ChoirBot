from telegram.ext import MessageHandler, Filters


class AbstractWatcher:

    def __init__(self, group_chat_id=None, handler_group=-1):
        self.handler = MessageHandler(Filters.all, self.check_interaction)
        self.dispatcher = None
        self.group_chat_id = group_chat_id
        self.handler_group = handler_group

    def check_interaction(self, bot, update):
        # ignore interaction from irrelevant chats
        if self.group_chat_id and update.effective_chat.id != self.group_chat_id:
            return

        self.interaction(bot, update)

    def interaction(self, bot, update):
        raise NotImplementedError()

    def set_dispatcher(self, dispatcher):
        if self.dispatcher is not None:
            self.dispatcher.remove_handler(self.handler, group=self.handler_group)

        self.dispatcher = dispatcher
        self.dispatcher.add_handler(self.handler, group=self.handler_group)