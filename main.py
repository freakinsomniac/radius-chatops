import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from database.db import init_db, close_db, fetch

load_dotenv()

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

@bot.slash_command(
    name="ping",
    description="Test ping bot"
)
async def ping(inter):
    await inter.response.send_message("Pong!")

GUILD_ID = os.getenv("GUILD_ID")
g_id = int(GUILD_ID) if GUILD_ID else None

if g_id:
    @bot.slash_command(
        name="users",
        description="Lihat semua user radius",
        default_guild_ids=[g_id]
    )
    async def users(inter):
        await inter.response.defer()
        query = "SELECT DISTINCT username FROM radcheck ORDER BY username;"
        try:
            rows = await fetch(query)
        except Exception as e:
            await inter.followup.send(f"Error saat mengambil data: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ada user.")
            return

        result = "\n".join(f"- {r['username']}" for r in rows)
        await inter.followup.send(f"📡 Daftar User Radius:\n\n{result}")

bot.run(os.getenv("DISCORD_TOKEN"))
