"""
Discord Verification Bot

Posts a verification embed with a Verify button on startup. When a member
clicks the button:
- Adds the configured verified role
- Removes the configured unverified role
- Sends an ephemeral message with the verification website link
"""

import os
import logging

import discord
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
VERIFICATION_CHANNEL_ID = int(os.getenv("VERIFICATION_CHANNEL_ID", "0"))
VERIFICATION_URL = "https://verified.ashy.enterprises"

intents = discord.Intents.default()


def verification_embed() -> discord.Embed:
    return discord.Embed(
        title="Server Verification",
        description=(
            "Click the button below to verify yourself and gain access to the rest of the server.\n\n"
            f"You will need to visit: {VERIFICATION_URL}"
        ),
        color=discord.Color.green(),
    ).set_footer(text="Verification System")


class VerificationBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)

    async def setup_hook(self):
        # Re-register the persistent view so buttons keep working after restart
        self.add_view(VerifyView())


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


@client.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", client.user, client.user.id)

    if not VERIFICATION_CHANNEL_ID:
        logger.error("VERIFICATION_CHANNEL_ID is not set.")
        return

    try:
        channel = await client.fetch_channel(VERIFICATION_CHANNEL_ID)
    except discord.NotFound:
        logger.error("Verification channel %s not found.", VERIFICATION_CHANNEL_ID)
        return
    except discord.HTTPException as exc:
        logger.error("Failed to fetch verification channel: %s", exc)
        return

    if not isinstance(channel, discord.TextChannel):
        logger.error("Verification channel %s is not a text channel.", VERIFICATION_CHANNEL_ID)
        return

    await channel.send(embed=verification_embed(), view=VerifyView())
    logger.info("Verification embed posted in %s.", channel)


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is not set. Please check your .env file.")
    client.run(BOT_TOKEN)
