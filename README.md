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

``` git clone https://gitlab.com/Laurenz/choir-chat-bot.git ```

2. **Install dependencies. Note that this is a python3 project.**

``` pip install python-telegram-bot bidict jsonpickle ```

3. **Add the bot token file.**

Check out the [Telegram bot introduction](https://core.telegram.org/bots) to see how to request a bot token.

```
touch bot_token.txt
echo "YOUR_TOKEN_HERE" >> bot_token.txt 
```

4. **Start up the bot to create config files.**
``` python3 main.py ```

5. **Stop the bot and edit `choir_status.json`**

- Add someone or multiple people as an admin. Admins can configure the bot while it is running through the `/admin` command. Find the `"admins"` field in the json file and add the user ids. Use the `@userinfobot` to find out your own user id.
- Enter the chat id of your choir's group chat. This id is stored in the `"choir_chat_id"` field in the json file.

6. **Start up the bot - you're ready to go!**
