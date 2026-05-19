import logging
import disnake
from disnake.ext import commands
from database.db import fetch
from utils.embeds import error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete
from utils.exceptions import UserNotFound, DatabaseError

logger = logging.getLogger(__name__)


class StatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="online",
        description="List currently online users (radacct)"
    )
    async def online(self, inter):
        await inter.response.defer()
        
        try:
            query = "SELECT username, nasipaddress, framedipaddress, acctstarttime FROM radacct WHERE acctstoptime IS NULL ORDER BY username LIMIT 50;"
            rows = await fetch(query)
            
            if not rows:
                raise UserNotFound("Saat ini tidak ada user yang sedang aktif")
            
            result = "\n".join(f"• {r['username']} @ {r.get('nasipaddress') or '-'} ({r.get('framedipaddress') or '-'})" for r in rows)
            embed = info_embed(f"🟢 User Online ({len(rows)})", result)
            logger.info(f"Online users retrieved, count: {len(rows)}")
            
        except UserNotFound as e:
            logger.info(f"No online users found")
            embed = warning_embed("⚠️ Tidak Ada User Online", str(e))
            
        except DatabaseError as e:
            logger.error(f"Database error saat online: {e}")
            embed = error_embed("❌ Gagal Mengambil Data", "Terjadi kesalahan pada database")
            
        except Exception as e:
            logger.exception(f"Unexpected error saat online: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
        
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="userstats",
        description="Show basic session stats for a user (radacct)"
    )
    async def userstats(self, inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        
        try:
            query = "SELECT COUNT(*) AS sessions, COALESCE(SUM(acctinputoctets),0) AS in_bytes, COALESCE(SUM(acctoutputoctets),0) AS out_bytes, MAX(acctstarttime) AS last_login FROM radacct WHERE username=%s"
            rows = await fetch(query, (username,))
            
            if not rows:
                raise UserNotFound(f"Tidak ada data untuk user `{username}`")
            
            r = rows[0]
            in_mb = r['in_bytes'] / (1024 * 1024)
            out_mb = r['out_bytes'] / (1024 * 1024)
            
            fields = [
                ("Sessions", str(r['sessions']), True),
                ("Download", f"{in_mb:.2f} MB", True),
                ("Upload", f"{out_mb:.2f} MB", True),
                ("Last Login", str(r['last_login']), False)
            ]
            embed = info_embed(f"📊 Stats User: {username}", fields=fields)
            logger.info(f"User stats retrieved for '{username}'")
            
        except UserNotFound as e:
            logger.warning(f"User stats not found: {username}")
            embed = error_embed("❌ Data Tidak Ditemukan", str(e))
            
        except DatabaseError as e:
            logger.error(f"Database error saat userstats: {e}")
            embed = error_embed("❌ Gagal Mengambil Stats", "Terjadi kesalahan pada database")
            
        except Exception as e:
            logger.exception(f"Unexpected error saat userstats: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
        
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="lastlogin",
        description="Show last login time for a user (radacct)"
    )
    async def lastlogin(self, inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        
        try:
            query = "SELECT acctstarttime FROM radacct WHERE username=%s ORDER BY acctstarttime DESC LIMIT 1"
            rows = await fetch(query, (username,))
            
            if not rows:
                raise UserNotFound(f"Tidak ada riwayat login untuk user `{username}`")
            
            embed = info_embed(f"🕐 Last Login: {username}", str(rows[0]['acctstarttime']))
            logger.info(f"Last login retrieved for user '{username}'")
            
        except UserNotFound as e:
            logger.warning(f"Last login not found for user: {username}")
            embed = warning_embed("⚠️ Data Tidak Ditemukan", str(e))
            
        except DatabaseError as e:
            logger.error(f"Database error saat lastlogin: {e}")
            embed = error_embed("❌ Gagal Mengambil Data", "Terjadi kesalahan pada database")
            
        except Exception as e:
            logger.exception(f"Unexpected error saat lastlogin: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
        
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="activecount",
        description="Count active sessions (radacct)"
    )
    async def activecount(self, inter):
        await inter.response.defer()
        
        try:
            query = "SELECT COUNT(*) AS active FROM radacct WHERE acctstoptime IS NULL"
            rows = await fetch(query)
            
            if not rows:
                raise DatabaseError("Failed to retrieve active session count")
            
            count = rows[0]['active']
            embed = info_embed(f"🟢 Active Sessions: {count}")
            logger.info(f"Active session count: {count}")
            
        except DatabaseError as e:
            logger.error(f"Database error saat activecount: {e}")
            embed = error_embed("❌ Gagal Menghitung Sessions", "Terjadi kesalahan pada database")
            
        except Exception as e:
            logger.exception(f"Unexpected error saat activecount: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
        
        await inter.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(StatsCommands(bot))
