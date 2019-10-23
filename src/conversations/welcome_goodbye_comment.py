from telegram.ext import MessageHandler, Filters
from src.language.phrases import formulate, PersonalPhrases
from src.utils.group_members import BasicGroupMember
from lxml import etree
import requests
import re
import random

WELCOME, GOODBYE = range(2)
SAYINGS_URL = {WELCOME: "https://sprueche.woxikon.de/freundschaft", GOODBYE: "https://sprueche.woxikon.de/abschied"}
loaded_sayings = {}


def welcome(bot, update):
    message = update.message
    new_member = message.new_chat_members[0]

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(new_member))

    bot.send_message(chat_id=update.effective_chat.id,
                     text=pp.formulate('willkommen') + " " + random.choice(get_saying(WELCOME)))


def goodbye(bot, update):
    bot.send_message(chat_id=update.effective_chat.id,
                     text=random.choice(get_saying(GOODBYE)))


def get_saying(saying):
    if saying not in loaded_sayings:
        loaded_sayings[saying] = get_sayings_from_url(SAYINGS_URL[saying])
    return loaded_sayings[saying]


def get_sayings_from_url(page):
    html = requests.get(page).text
    tree = etree.HTML(html)
    results = tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/ul/li/div/div/a/text()')

    # first remove all surrounding whitespace with strip(), then remove formatting from remaining string by joining the words with a space
    return [' '.join(result.strip().split()) for result in results]


def add_handlers(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, goodbye))
