"""
Discord Verification Bot

Sends an embed with a Verify button. When a member clicks the button:
- Adds the configured verified role
- Removes the configured unverified role
- Sends an ephemeral message with the verification website link
"""

import os
import logging

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("verification_bot")

# Configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADD_ROLE_ID = int(os.getenv("ADD_ROLE_ID", "0"))
REMOVE_ROLE_ID = int(os.getenv("REMOVE_ROLE_ID", "0"))
VERIFICATION_URL = "https://verified.ashy.enterprises"

GUILD_ID = os.getenv("GUILD_ID")
GUILD = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None

intents = discord.Intents.default()
# The bot only uses slash commands and button interactions, so the
# privileged Server Members intent is not required.


class VerificationBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Re-register the persistent view so buttons keep working after restart
        self.add_view(VerifyView())

        if GUILD:
            self.tree.copy_global_to(guild=GUILD)

        try:
            await self.tree.sync()
        except discord.Forbidden:
            logger.error(
                "Failed to sync slash commands. Make sure the bot has been added "
                "to the GUILD_ID server (if set) and has the required permissions."
            )
        except discord.HTTPException as exc:
            logger.error("Failed to sync slash commands: %s", exc)


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.green,
        custom_id="verification_bot:verify_button",
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "This button can only be used inside a server.", ephemeral=True
            )
            return

        member = interaction.user
        add_role = interaction.guild.get_role(ADD_ROLE_ID)
        remove_role = interaction.guild.get_role(REMOVE_ROLE_ID)

        try:
            if add_role and add_role not in member.roles:
                await member.add_roles(add_role, reason="Verification bot")

            if remove_role and remove_role in member.roles:
                await member.remove_roles(remove_role, reason="Verification bot")

            await interaction.response.send_message(
                "Visit the following website to become verified and gain access to the rest of the server:\n"
                f"<{VERIFICATION_URL}>",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to update your roles. Please contact a server administrator.",
                ephemeral=True,
            )
        except discord.HTTPException as exc:
            logger.exception("Failed to update roles for %s: %s", member, exc)
            await interaction.response.send_message(
                "Something went wrong while updating your roles. Please try again later.",
                ephemeral=True,
            )


client = VerificationBot()


@client.tree.command(
    name="setup_verification",
    description="Post the verification message in this channel.",
)
@app_commands.checks.has_permissions(manage_guild=True)
async def setup_verification(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Server Verification",
        description=(
            "Click the button below to verify yourself and gain access to the rest of the server.\n\n"
            f"You will need to visit: {VERIFICATION_URL}"
        ),
        color=discord.Color.green(),
    )
    embed.set_footer(text="Verification System")

    await interaction.response.send_message(
        "Verification message sent below.",
        ephemeral=True,
    )

    if isinstance(interaction.channel, discord.TextChannel):
        await interaction.channel.send(embed=embed, view=VerifyView())


@client.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", client.user, client.user.id)


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is not set. Please check your .env file.")
    client.run(BOT_TOKEN)
