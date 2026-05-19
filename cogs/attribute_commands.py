import logging
import disnake
from disnake.ext import commands
from database.db import fetch
from utils.embeds import error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete
from utils.exceptions import UserNotFound, DatabaseError

logger = logging.getLogger(__name__)


class AttributeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="checkattributes",
        description="Lihat semua attributes dari seorang user"
    )
    async def checkattributes(self, inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        
        try:
            rows = await fetch(
                "SELECT attribute, op, value FROM radcheck WHERE username=%s ORDER BY attribute",
                (username,)
            )
            
            if not rows:
                raise UserNotFound(f"User `{username}` tidak memiliki attributes")
            
            nas_map = {}
            try:
                nas_rows = await fetch("SELECT nasname, shortname FROM nas WHERE nasname IS NOT NULL")
                for nas_row in nas_rows:
                    nasname = nas_row.get('nasname', '')
                    shortname = nas_row.get('shortname', '')
                    if nasname and (nasname.count('.') == 3 or '.' in nasname):
                        nas_map[nasname] = shortname or nasname
            except Exception as e:
                logger.warning(f"Failed to fetch NAS mapping: {e}")
            
            result_lines = []
            for r in rows:
                attr = r['attribute']
                op = r['op']
                value = r['value']
                
                if attr == "NAS-IP-Address":
                    nas_name = nas_map.get(value)
                    if nas_name:
                        result_lines.append(f"• **{attr}** `{op}` `{value}` - **{nas_name}**")
                    else:
                        result_lines.append(f"• **{attr}** `{op}` `{value}`")
                else:
                    result_lines.append(f"• **{attr}** `{op}` `{value}`")
            
            result = "\n".join(result_lines)
            embed = info_embed(f"📋 Check Attributes: {username}", result)
            logger.info(f"Attributes retrieved for user '{username}'")
            
        except UserNotFound as e:
            logger.warning(f"User not found: {username}")
            embed = warning_embed("⚠️ Tidak Ada Attributes", str(e))
            
        except DatabaseError as e:
            logger.error(f"Database error saat checkattributes: {e}")
            embed = error_embed("❌ Gagal Mengambil Attributes", "Terjadi kesalahan pada database")
            
        except Exception as e:
            logger.exception(f"Unexpected error saat checkattributes: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
        
        await inter.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(AttributeCommands(bot))
