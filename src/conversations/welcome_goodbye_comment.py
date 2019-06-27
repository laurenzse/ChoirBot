from telegram.ext import MessageHandler, Filters
from src.language.phrases import formulate, PersonalPhrases
from src.utils.group_members import BasicGroupMember
from lxml import etree
import requests
import re
import random


def welcome(bot, update):
    message = update.message
    new_member = message.new_chat_members[0]

    pp = PersonalPhrases(BasicGroupMember.from_telegram_user(new_member))
    update.message.reply_text(pp.formulate('willkommen') + " " + random.choice(welcome_sayings))


def goodbye(bot, update):
    update.message.reply_text(random.choice(goodbye_sayings))


def get_sayings(page):
    html = requests.get(page).text
    tree = etree.HTML(html)
    results = tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/ul/li/div/div/a/text()')

    return [re.findall(r'\n\s*(\w.*)\n', result)[0] for result in results]


goodbye_sayings = get_sayings("https://sprueche.woxikon.de/abschied")
welcome_sayings = get_sayings("https://sprueche.woxikon.de/freundschaft")


def add_handlers(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, goodbye))
