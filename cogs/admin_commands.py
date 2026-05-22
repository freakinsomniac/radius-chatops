import os
import sys
import logging
import disnake
from disnake.ext import commands
from utils.embeds import success_embed, error_embed, info_embed, warning_embed

logger = logging.getLogger(__name__)

OWNER_ID = os.getenv("OWNER_ID")
OWNER_ID = int(OWNER_ID) if OWNER_ID else None


async def cog_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    cogs = list(inter.bot.extensions.keys())
    return [c for c in cogs if user_input.lower() in c.lower()][:25]


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_owner(self, inter):
        if OWNER_ID is None:
            return True
        return inter.author.id == OWNER_ID

    @commands.slash_command(
        name="reload",
        description="Reload cog tertentu atau semua cogs (admin only)"
    )
    async def reload(
        self,
        inter,
        cog: str = commands.Param(default=None, autocomplete=cog_autocomplete, description="Nama cog (kosongkan untuk reload semua)")
    ):
        await inter.response.defer(ephemeral=True)

        if not self._is_owner(inter):
            embed = error_embed("❌ Akses Ditolak", "Hanya owner bot yang bisa menggunakan command ini.")
            await inter.followup.send(embed=embed, ephemeral=True)
            return

        if cog:
            try:
                self.bot.reload_extension(cog)
                logger.info(f"Reloaded cog: {cog}")
                embed = success_embed("✅ Cog Reloaded", f"Cog `{cog}` berhasil di-reload.")
            except Exception as e:
                logger.exception(f"Gagal reload cog {cog}: {e}")
                embed = error_embed("❌ Gagal Reload", f"Cog `{cog}`\nError: {e}")
            await inter.followup.send(embed=embed, ephemeral=True)
            return

        results = []
        for ext in list(self.bot.extensions.keys()):
            try:
                self.bot.reload_extension(ext)
                results.append(f"✅ `{ext}`")
            except Exception as e:
                results.append(f"❌ `{ext}` - {e}")
                logger.exception(f"Gagal reload {ext}: {e}")

        embed = info_embed("🔄 Reload All Cogs", "\n".join(results))
        await inter.followup.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="restart",
        description="Restart bot sepenuhnya (admin only)"
    )
    async def restart(self, inter):
        await inter.response.defer(ephemeral=True)

        if not self._is_owner(inter):
            embed = error_embed("❌ Akses Ditolak", "Hanya owner bot yang bisa menggunakan command ini.")
            await inter.followup.send(embed=embed, ephemeral=True)
            return

        embed = warning_embed("🔄 Restarting Bot", "Bot akan restart dalam beberapa detik...")
        await inter.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Bot restart dipicu oleh {inter.author} ({inter.author.id})")

        await self.bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)


def setup(bot):
    bot.add_cog(AdminCommands(bot))