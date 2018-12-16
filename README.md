# Choir Chat Bot

This Telegram choir chat bot supports any choir within their Telegram group chat.

## Features
- **Manage absences**: Choir members can enter their absences and the bot will gather all registered absences before a rehearsal. Absences can either be only for the next rehearsal or a longer duration.
- **Create reminders**: Choir members can enter a text reminder and the bot will remind the choir before the next rehearsal of it.
- **Wish song**: Is your choir practicing wish songs at the end of each rehearsal? This bot can tell you who is next for wishing. A member list is updated according to the group chat.

## Commands

At this time, this bot only supports the German language.

- **/abwesend** to create and manage absences. Only callable in private chats.
- **/wunschlied** to bring up the wish song iterator.
- **/erinnern** to create and manage reminders.
- **/admin** to manage the bot's configuration. This command is only available to admins (see below) and allows direct access to the configuration - handle with care.


## Setup
1. **Clone git repository.**

``` 
git clone https://gitlab.com/Laurenz/choir-chat-bot.git 
```

2. **Install dependencies. Note that this is a python3 project.**

``` 
pip install python-telegram-bot bidict jsonpickle 
```

3. **Add the bot token file.**

```
touch bot_token.txt
echo "YOUR_TOKEN_HERE" >> bot_token.txt 
```

Check out the [Telegram bot introduction](https://core.telegram.org/bots) to see how to request a bot token. To make this bot work best, you need to **disable privacy mode** of this bot's token. This allows the bot to update it's member list automatically based on the acitivty happening in your group chat. No messages are shared outside of the bot's domain.

4.  **Add a `members.txt` file and optionally add all current members in your choir's group chat.**

``` 
touch members.txt 
```

Telegram's API does not allow disclose the members present in a group chat. The bot will therefore work based on the user activity it sees within the group chat and update it's list accordingly. If your group chat already contains members, you can add these members manually in the `members.txt` file. See `members_sample.txt` for the format expected.

4. **Start the bot to create config files.**
``` 
python3 main.py
```

5. **Stop the bot and edit `choir_status.json`**

- Add someone or multiple people as an admin. Admins can configure the bot while it is running through the `/admin` command. Find the `"admins"` field in the json file and add the user ids. Use the `@userinfobot` to find out your own user id.
- Enter the chat id of your choir's group chat. This id is stored in the `"choir_chat_id"` field in the json file. When the bot is running, admins can also see every id of the chats the bot is participating in.

6. **Start the bot - you're ready to go!**
