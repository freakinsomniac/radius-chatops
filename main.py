import os
import disnake
from disnake.ext import commands
from disnake.ext.commands import CommandSyncFlags
from dotenv import load_dotenv
from database.db import init_db, close_db
import logging
import asyncio

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GUILD_ID = os.getenv("GUILD_ID")
GUILD_IDS = [int(GUILD_ID)] if GUILD_ID else None

command_sync_flags = CommandSyncFlags.default()

bot = commands.InteractionBot(
    test_guilds=GUILD_IDS,
    sync_commands_debug=True
)

@bot.event
async def on_ready():
    print(f"Bot online sebagai {bot.user}")
    print("Guild IDs:", [g.id for g in bot.guilds])
    cmds = [c for c in bot.application_commands]
    print("Registered application commands (count=", len(cmds), "):")
    for c in cmds:
        try:
            gids = getattr(c, "guild_ids", None)
            if gids is None and bot.test_guilds:
                gids = tuple(bot.test_guilds)
        except Exception:
            gids = None
        print("-", c.name, "guild_ids=", gids)
    
    print("Force syncing application commands to Discord...")
    try:
        await bot._prepare_application_commands()
        await bot._sync_application_commands()
        print("[SUCCESS] Force sync completed successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to force sync commands: {e}")



async def load_cogs():
    cogs_to_load = [
        'cogs.user_commands',
        'cogs.nas_commands',
        'cogs.group_commands',
        'cogs.stats_commands',
        'cogs.attribute_commands',
        'cogs.admin_commands',
    ]
    
    for cog in cogs_to_load:
        try:
            bot.load_extension(cog)
            logger.info(f"[SUCCESS] Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to load cog {cog}: {e}")


@bot.slash_command(name="ping", description="Test ping bot")
async def ping(inter):
    await inter.response.send_message("Pong! 🏓")


if __name__ == "__main__":
    async def main():
        await load_cogs()
        await init_db()
        try:
            await bot.start(os.getenv("DISCORD_TOKEN"))
        finally:
            logger.info("Closing database connection...")
            await close_db()
            logger.info("Database connection closed")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown received (Ctrl+C)")
