# Telegram Mute Bot

A simple Telegram bot that allows group administrators to mute and unmute members, manage a whitelist, and view muted users.

## Features

- Mute all members except those on a whitelist
- Unmute/Mute specific users or all users at once
- Add or remove users from the whitelist
- View current whitelist/blacklist

## Commands

- `/togglemute`: Turn on/off mute functionality for the group
- `/unmute @username`: Unmute a specific user
- `/addwhitelist @username`: Add a user to the whitelist
- `/removewhitelist @username`: Remove a user from the whitelist
- `/showwhitelist`: Display the current whitelist
- `/showmuted`: Show all currently muted members

> Note: Only admins can use these commands and the bot needs to be in a group w/ admin privileges

## Setup

1. Clone repo
2. Install the required packages via poetry:
   ```
   poetry shell
   poetry install
   ```
3. Copy `.env.example` to `.env` and replace `'YOUR_BOT_TOKEN'` with your actual Telegram bot token
4. Run the script (ensure your virtual environment is activated):
   ```
   python mod_bot
   ```

## Notes

Default behavior doesn't mute admins and default whitelist is empty (or atleast is defined in main).
This bot stores all data in memory. For persistent storage, consider implementing a db connector, PRs welcome!

## Author

Sambot

## License

[MIT](https://choosealicense.com/licenses/mit/)