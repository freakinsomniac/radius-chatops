from disnake.ext import commands
import disnake
import os
from database.db import fetch

GUILD_ID = os.getenv("GUILD_ID")
GUILD_IDS = [int(GUILD_ID)] if GUILD_ID else []


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="users",
        description="Lihat semua user radius",
        default_guild_ids=GUILD_IDS
    )
    async def users(self, inter: disnake.ApplicationCommandInteraction):
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


def setup(bot):
    bot.add_cog(Users(bot))