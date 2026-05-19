import logging
import disnake
from disnake.ext import commands
from database.db import fetch, execute
from utils.embeds import success_embed, error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete, groupname_autocomplete, attribute_autocomplete, operator_autocomplete
from utils.exceptions import UserNotFound, DatabaseError

logger = logging.getLogger(__name__)


class GroupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="setprofile",
        description="Assign a single profile/group to a user (radusergroup)"
    )
    async def setprofile(self, inter, username: str = commands.Param(autocomplete=username_autocomplete), groupname: str = commands.Param(autocomplete=groupname_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        groupname = groupname.strip()
        
        try:
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
            await execute("INSERT INTO radusergroup (username, groupname) VALUES (%s, %s)", (username, groupname))
            logger.info(f"User '{username}' diassign ke group '{groupname}'")
            
            fields = [("Username", f"`{username}`", True), ("Profile", f"`{groupname}`", True)]
            embed = success_embed("✅ Profile Berhasil Diubah", fields=fields)
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat setprofile: {e}")
            embed = error_embed("❌ Gagal Set Profile", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat setprofile: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="groupadd",
        description="Add a reply attribute to a group (radgroupreply)"
    )
    async def groupadd(self, inter, groupname: str = commands.Param(autocomplete=groupname_autocomplete), attribute: str = commands.Param(autocomplete=attribute_autocomplete), op: str = commands.Param(autocomplete=operator_autocomplete), value: str = None):
        await inter.response.defer()
        groupname = groupname.strip()
        attribute = attribute.strip()
        op = op.strip()
        
        try:
            await execute("INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES (%s, %s, %s, %s)", (groupname, attribute, op, value))
            logger.info(f"Attribute '{attribute}' ditambahkan ke group '{groupname}'")
            
            fields = [("Group", f"`{groupname}`", True), ("Attribute", f"`{attribute}`", True), ("Operator", f"`{op}`", True), ("Value", f"`{value}`", True)]
            embed = success_embed("✅ Group Reply Berhasil Ditambahkan", fields=fields)
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat groupadd: {e}")
            embed = error_embed("❌ Gagal Menambah Group Reply", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat groupadd: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="groupremove",
        description="Remove reply attributes from a group or remove entire group replies"
    )
    async def groupremove(self, inter, groupname: str = commands.Param(autocomplete=groupname_autocomplete), attribute: str = commands.Param(default=None, autocomplete=attribute_autocomplete)):
        await inter.response.defer()
        groupname = groupname.strip()
        
        try:
            if attribute:
                await execute("DELETE FROM radgroupreply WHERE groupname=%s AND attribute=%s", (groupname, attribute))
                logger.info(f"Attribute '{attribute}' dihapus dari group '{groupname}'")
                embed = success_embed("✅ Attribute Berhasil Dihapus", f"Attribute `{attribute}` dihapus dari group `{groupname}`.")
            else:
                await execute("DELETE FROM radgroupreply WHERE groupname=%s", (groupname,))
                logger.info(f"Semua attributes dihapus dari group '{groupname}'")
                embed = success_embed("✅ Group Reply Berhasil Dihapus", f"Semua reply untuk group `{groupname}` telah dihapus.")
                
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat groupremove: {e}")
            embed = error_embed("❌ Gagal Menghapus Group Reply", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat groupremove: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(GroupCommands(bot))
