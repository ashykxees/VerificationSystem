# Verification System

A Discord bot that sends a verification embed with a single button. When a member clicks the button, it:

- Adds a configured role (e.g. a verified/member role)
- Removes a configured role (e.g. an unverified role)
- Replies with an ephemeral message prompting the user to visit `https://verified.ashy.enterprises`

## Setup

1. Create a Discord application and bot at https://discord.com/developers/applications.
2. Enable the `Server Members` intent in the bot settings.
3. Copy `.env.example` to `.env` and fill in the values:
   - `DISCORD_BOT_TOKEN` — your bot token
   - `ADD_ROLE_ID` — the role ID to add on verification
   - `REMOVE_ROLE_ID` — the role ID to remove on verification
   - `GUILD_ID` — optional, for faster slash-command sync
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

An admin or anyone with `Manage Server` permission can run:

```
/setup_verification
```

This posts the verification embed to the current channel. Members click the green **Verify** button to receive the configured role changes and the verification prompt.

## Bot Permissions

The bot needs the following permissions:

- Send Messages
- Read Messages/View Channels
- Manage Roles (so it can add/remove the configured roles)
- Use Slash Commands

The bot's highest role must be above the roles it manages.
