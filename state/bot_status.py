import logging
import os

from utils.group_members import GroupMemberWatcher
from utils.message_watcher import MessageWatcher
from utils.friendly_chatting_strategy import FriendlyChattingStrategy
from state import choir_status

SINGERS = "members.txt"
BOT_TOKEN_FILE = 'bot_token.txt'

DATA_PATH = "working_data/"

SINGER_WATCHER_FILE = DATA_PATH + "known_singers.pckl"
ALL_MEMBERS_FILE = DATA_PATH + "known_members.pckl"
LAST_SEEN = DATA_PATH + "last_seen.pckl"

service_handler_group = 0

logger = logging.getLogger(__name__)
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def next_service_handler_group():
    global service_handler_group
    service_handler_group -= 1
    return service_handler_group


def configuration_exists(file_name):
    return os.path.exists(file_name)


with open(BOT_TOKEN_FILE, 'r') as file:
    bot_token = file.read().replace('\n', '')

singer_watcher = GroupMemberWatcher(group_chat_id=None, handler_group=next_service_handler_group())
if configuration_exists(SINGER_WATCHER_FILE):
    singer_watcher.load_members(SINGER_WATCHER_FILE)
singer_watcher.import_basic_members(SINGERS)

all_members_watcher = GroupMemberWatcher(group_chat_id=None, handler_group=next_service_handler_group())
if configuration_exists(ALL_MEMBERS_FILE):
    all_members_watcher.load_members(ALL_MEMBERS_FILE)

all_messages_watcher = MessageWatcher(group_chat_id=None, handler_group=next_service_handler_group())

friendly_chatting_strategy = FriendlyChattingStrategy(all_members_watcher, all_messages_watcher)
if configuration_exists(LAST_SEEN):
    friendly_chatting_strategy.load_last_seen(LAST_SEEN)


def save_configuration():
    singer_watcher.save_members(SINGER_WATCHER_FILE)
    all_members_watcher.save_members(ALL_MEMBERS_FILE)
    friendly_chatting_strategy.save_last_seen(LAST_SEEN)
    choir_status.save_data()
