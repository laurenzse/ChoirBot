import datetime
import pickle
import random

from src.utils.group_members import BasicGroupMember
from src.language.phrases import PersonalPhrases

SECONDS_FOR_INACTIVITY = 60 * 60 * 3 # 3 hours

NOT_WORKING_PROBABILITY = 1/20
NOT_WORKING_DAY = 6 # sunday


class FriendlyChattingStrategy:

    def __init__(self, member_watcher, message_watcher):
        self.last_interactions = {}
        self.member_watcher = member_watcher
        self.message_watcher = message_watcher

    def will_send_message(self, bot, *args, **kwargs):
        chat_id = args[0] if args else kwargs.get('chat_id')
        reply_to_message_id = kwargs.get('reply_to_message_id')

        maybe_member = BasicGroupMember(user_id=chat_id)
        observed_members = self.member_watcher.members()

        if maybe_member in observed_members:
            observed_member = observed_members[observed_members.index(maybe_member)]
            self.chatting_with_member(bot, chat_id, observed_member, reply_to_message_id)
        elif reply_to_message_id is not None:
            user = self.get_user_by_sent_message_id(reply_to_message_id)
            if user is not None:
                self.chatting_with_member(bot, chat_id, BasicGroupMember.from_telegram_user(user), reply_to_message_id)

    def has_sent_message(self, bot, *args, **kwargs):
        pass

    def get_user_by_sent_message_id(self, sent_message_id):
        recent_messages = self.message_watcher.recent_messages()

        for message in recent_messages:
            if message.message_id == sent_message_id:
                return message.from_user

        return None

    def chatting_with_member(self, bot, chat_id, member, reply_to_message_id):
        if member.id not in self.last_interactions:
            # we have not talked to this member yet
            self.first_time(bot, chat_id, member, reply_to_message_id)
        elif datetime.datetime.now() - self.last_interactions[member.id] \
                > datetime.timedelta(seconds=SECONDS_FOR_INACTIVITY):
            # since we have talked to this member, some time elapsed
            self.talk_again(bot, chat_id, member, reply_to_message_id)

        self.last_interactions[member.id] = datetime.datetime.now()

    @staticmethod
    def first_time(bot, chat_id, member, reply_to_message_id):
        pp = PersonalPhrases(member)

        bot.send_message(chat_id, pp.formulate('zum-ersten-mal'), bypass_hook=True)

    @staticmethod
    def talk_again(bot, chat_id, member, reply_to_message_id):
        pp = PersonalPhrases(member)
        today = datetime.date.today()

        if today.day == NOT_WORKING_DAY and random.random() < NOT_WORKING_PROBABILITY:
            bot.send_message(chat_id, 'Am Sonntag arbeite ich eigentlich nicht, aber für dich tu\' ich\'s trotzdem', bypass_hook=True)
        else:
            bot.send_message(chat_id, pp.formulate('wiedersehen'), bypass_hook=True)

    def save_last_seen(self, file_name):
        with open(file_name, "wb") as fp:  # Pickling
            pickle.dump(self.last_interactions, fp)

    def load_last_seen(self, file_name):
        with open(file_name, "rb") as fp:  # Unpickling
            self.last_interactions = pickle.load(fp)
