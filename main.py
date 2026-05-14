import os

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot = commands.InteractionBot()

@bot.event
async def on_ready():
    print(f"Bot online sebagai {bot.user}")

@bot.slash_command(
    name="ping",
    description="Test ping bot"
)
async def ping(inter):
    await inter.response.send_message(
        "Pong!"
    )

bot.run(
    os.getenv("DISCORD_TOKEN")
)