import telegram.bot as bot


class HookedBot(bot.Bot):

    def __init__(self, chatting_strategy, *args, **kwargs):
        super(HookedBot, self).__init__(*args, **kwargs)

        self.chatting_strategy = chatting_strategy

    def send_message(self, *args, bypass_hook=False, **kwargs):
        if not bypass_hook:
            self.chatting_strategy.will_send_message(self, *args, **kwargs)

        result = super().send_message(*args, **kwargs)

        if not bypass_hook:
            self.chatting_strategy.has_sent_message(self, *args, **kwargs)

        return result
