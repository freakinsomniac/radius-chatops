import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from database.db import init_db, close_db
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = commands.InteractionBot()

@bot.event
async def on_ready():
    print(f"Bot online sebagai {bot.user}")
    print("Guild IDs:", [g.id for g in bot.guilds])
    await init_db()
    cmds = [c for c in bot.application_commands]
    print("Registered application commands (count=", len(cmds), "):")
    for c in cmds:
        try:
            gids = getattr(c, "default_guild_ids", None)
        except Exception:
            gids = None
        print("-", c.name, "guild_ids=", gids)


async def load_cogs():
    GUILD_ID = os.getenv("GUILD_ID")
    g_id = int(GUILD_ID) if GUILD_ID else None
    
    cogs_to_load = [
        'cogs.user_commands',
        'cogs.nas_commands',
        'cogs.group_commands',
        'cogs.stats_commands',
        'cogs.attribute_commands',
    ]
    
    for cog in cogs_to_load:
        try:
            bot.load_extension(cog)
            logger.info(f"✅ Loaded cog: {cog}")
            
            if g_id:
                cog_name = cog.split('.')[-1]
                if cog_name in bot.cogs:
                    cog_instance = bot.cogs[cog_name]
                    for command in bot.pending_application_commands:
                        if hasattr(command, 'cog') and command.cog == cog_instance:
                            command.default_guild_ids = [g_id]
        except Exception as e:
            logger.error(f"❌ Failed to load cog {cog}: {e}")


@bot.slash_command(
    name="ping",
    description="Test ping bot"
)
async def ping(inter):
    await inter.response.send_message("Pong! 🏓")

GUILD_ID = os.getenv("GUILD_ID")
g_id = int(GUILD_ID) if GUILD_ID else None


if __name__ == "__main__":
    import asyncio
    
    async def main():
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))
    
    asyncio.run(main())
