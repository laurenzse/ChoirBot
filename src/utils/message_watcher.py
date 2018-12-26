from collections import deque

from src.utils.abstract_watcher import AbstractWatcher

BUFFER_LENGTH = 50

message_queue = deque(maxlen=BUFFER_LENGTH)


class MessageWatcher(AbstractWatcher):

    def __init__(self, *args, **kwargs):
        super(MessageWatcher, self).__init__(*args, **kwargs)

        self.message_queue = deque(maxlen=BUFFER_LENGTH)

    def interaction(self, bot, update):
        self.message_queue.append(update.message)

    def recent_messages(self):
        return list(self.message_queue)



