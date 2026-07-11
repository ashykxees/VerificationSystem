# Verification System

A Discord bot that posts a verification embed with a single button on startup. When a member clicks the button, it:

- Adds a configured role (e.g. a verified/member role)
- Removes a configured role (e.g. an unverified role)
- Replies with an ephemeral message prompting the user to visit `https://verified.ashy.enterprises`

## Invite the Bot

A bot cannot join a server by itself. It must be invited with an OAuth2 URL.

1. Go to your Discord application at https://discord.com/developers/applications.
2. Open **OAuth2 > URL Generator**.
3. Select the scopes:
   - `bot`
   - `applications.commands`
4. Select the permissions:
   - `Manage Roles`
   - `Send Messages`
   - `Read Messages/View Channels`
   - `Use Slash Commands`
5. Copy the generated URL and open it in a browser to add the bot to your server.

The bot's highest role must be above the roles it manages.

## Local Setup

1. Create a Discord application and bot at https://discord.com/developers/applications.
2. Copy `.env.example` to `.env` and fill in the values:
   - `DISCORD_BOT_TOKEN` — your bot token
   - `ADD_ROLE_ID` — the role ID to add on verification
   - `REMOVE_ROLE_ID` — the role ID to remove on verification
   - `VERIFICATION_CHANNEL_ID` — the channel ID where the bot will post the verification embed
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

The bot will post the verification embed in the configured channel as soon as it connects.

## Deploy to Railway

1. Push your code to GitHub.
2. In the Railway dashboard, create a new project and deploy from this repository.
3. In the **Variables** tab, add the environment variables:
   - `DISCORD_BOT_TOKEN`
   - `ADD_ROLE_ID`
   - `REMOVE_ROLE_ID`
   - `VERIFICATION_CHANNEL_ID`
4. The `Procfile` already tells Railway to run the bot as a worker with `python bot.py`.
5. Invite the bot to your server before starting Railway, and make sure the bot has access to the `VERIFICATION_CHANNEL_ID` channel.

## Bot Permissions

The bot needs the following permissions:

- Send Messages
- Read Messages/View Channels
- Manage Roles (so it can add/remove the configured roles)
- Use Slash Commands

The bot's highest role must be above the roles it manages.

## Security

Never commit your `.env` file or bot token. If `DISCORD_BOT_TOKEN` was ever committed to git, reset it in the Discord Developer Portal immediately.
