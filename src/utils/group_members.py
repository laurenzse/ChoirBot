import csv
import pickle
from telegram import User

from src.utils.abstract_watcher import AbstractWatcher

HANDLER_GROUP_START = -1


class GroupMemberWatcher(AbstractWatcher):

    def __init__(self, *args, **kwargs):
        super(GroupMemberWatcher, self).__init__(*args, **kwargs)

        self.telegram_user_list = []
        self.basic_member_list = []

    def members(self):
        converted_users = list(map(lambda user: BasicGroupMember.from_telegram_user(user), self.telegram_user_list))
        return converted_users + self.basic_member_list

    def interaction(self, bot, update):
        # check author of message
        user = update.effective_user
        self.telegram_user_encountered(bot, user)

        # check whether someone has been added or left a group
        message = update.message

        new_members = message.new_chat_members
        if new_members:
            for new_user in new_members:
                self.telegram_user_encountered(bot, new_user)

        left_member = message.left_chat_member
        if left_member is not None and self.user_known(bot, left_member):
            self.remove_user(left_member)

    def telegram_user_encountered(self, bot, user):
        # check whether we know this user and either add them or update their details
        if not self.telegram_user_known(bot, user):
            self.add_telegram_user(bot, user)
        else:
            self.update_telegram_user_details(user)

    def telegram_user_known(self, bot, user):
        # check whether we know the telegram details of this user
        if user.id == bot.id:
            return True
        return self.telegram_user_index(user) != -1

    def basic_member_known(self, user):
        # check whether we know this user (basic member or telegram user) as a basic member
        return user in self.basic_member_list

    def user_known(self, bot, user):
        return self.telegram_user_known(bot, user) or self.basic_member_known(user)

    def remove_user(self, user):
        if self.basic_member_known(user):
            self.remove_basic_member(user)

        if self.telegram_user_known(self, user):
            self.remove_telegram_user(user)

    def update_telegram_user_details(self, user):
        # update user details, e.g. name oder username

        user_index = self.telegram_user_index(user)

        if user_index == -1:
            raise ValueError

        self.telegram_user_list[user_index] = user

    def telegram_user_index(self, user):
        user_index = -1
        for index, telegram_user in enumerate(self.telegram_user_list):
            if telegram_user.id == user.id:
                user_index = index
        return user_index

    def remove_telegram_user(self, user):
        user_index = self.telegram_user_index(user)

        if user_index == -1:
            raise ValueError

        self.telegram_user_list.pop(user_index)

    def add_telegram_user(self, bot, user):
        if self.basic_member_known(user):
            self.remove_basic_member(user)

        if not self.telegram_user_known(bot, user):
            self.telegram_user_list.append(user)

    def add_basic_member(self, member):
        if self.basic_member_known(member):
            # if we know of this member, no need to add them again
            return

        self.basic_member_list.append(member)

    def remove_basic_member(self, member):
        self.basic_member_list.remove(member)

    def import_basic_members(self, file_name):
        with open(file_name) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                name = row[0]
                username = row[1]
                basic_member = BasicGroupMember(name=name, username=username)
                self.add_basic_member(basic_member)

    def save_members(self, file_name):
        with open(file_name, "wb") as fp:
            telegram_users_as_members = list(map(lambda telegram_user:
                                                 BasicGroupMember.from_telegram_user(telegram_user),
                                                 self.telegram_user_list))

            pickle_data = self.basic_member_list + telegram_users_as_members

            pickle.dump(pickle_data, fp)  # Pickling everything as members, as we can't pickle telegram users

    def load_members(self, file_name):
        with open(file_name, "rb") as fp:  # Unpickling
            self.basic_member_list = pickle.load(fp)


class BasicGroupMember(object):
    # Users for which only the name and (optionally) the username and id is known.
    # The bot is not able to produce any interaction with such a user,
    # but knows that they exist within a group.

    def __init__(self, name='', username='', first_name='', user_id=-1):
        if name == '' and username == '' and user_id == -1:
            raise ValueError("BasicGroupMember must be initialized with at least name, username or user_id")

        self.full_name = name
        self.first_name = name if first_name == '' else first_name
        self.username = username
        self.id = user_id

    @staticmethod
    def from_telegram_user(user):
        return BasicGroupMember(name=user.full_name, username=user.username, first_name=user.first_name, user_id=user.id)

    @staticmethod
    def create_from_existing(user):
        """Convenience method to allow handling BasicGroupMembers as well as converting Telegram users"""
        if isinstance(user, BasicGroupMember):
            return user
        if isinstance(user, User):
            return BasicGroupMember.from_telegram_user(user)

    def __hash__(self):
        return hash((self.full_name, self.username, self.id))

    def __eq__(self, other):
        """Compare group members to telegram users or to other members with unknown ids """
        if isinstance(other, BasicGroupMember):
            # first try to compare ids, since they are most reliable for equality
            if self.id != -1 and other.id != -1:
                return self.id == other.id
            if self.username != '' and other.id != '':
                return self.username == other.username
            return self.full_name == other.full_name

        if isinstance(other, User):
            return self == BasicGroupMember.from_telegram_user(other)

        return NotImplemented

    def __str__(self):
        return 'member {} with id {}'.format(self.full_name, self.id)


