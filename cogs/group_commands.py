import logging
import re
import disnake
from disnake.ext import commands
from database.db import fetch, execute
from utils.embeds import success_embed, error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete, groupname_autocomplete, attribute_autocomplete, operator_autocomplete, nas_ip_autocomplete, group_nas_ip_autocomplete
from utils.exceptions import UserNotFound, DatabaseError

logger = logging.getLogger(__name__)


def _parse_nas_ips(regex_val):
    if not regex_val:
        return []
    match = re.match(r"^\^\((.*)\)\$$", regex_val)
    if match:
        return [p.replace(r"\.", ".") for p in match.group(1).split('|')]
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", regex_val):
        return [regex_val]
    return []


def _build_nas_regex(ips):
    unique_ips = sorted(list(set(ips)))
    escaped_ips = [ip.replace(".", r"\.") for ip in unique_ips]
    return f"^({('|').join(escaped_ips)})$"


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

    @commands.slash_command(
        name="groupnasadd",
        description="Add a NAS IP restriction to a group (adds individual check row)"
    )
    async def groupnasadd(
        self,
        inter,
        groupname: str = commands.Param(autocomplete=groupname_autocomplete),
        nas_ip: str = commands.Param(autocomplete=nas_ip_autocomplete, description="Pilih atau ketik IP NAS yang akan ditambahkan")
    ):
        await inter.response.defer()
        groupname = groupname.strip()
        
        if " - " in nas_ip:
            ip_address = nas_ip.split(" - ")[0].strip()
        else:
            ip_address = nas_ip.strip()
            
        parts = ip_address.split(".")
        if len(parts) != 4:
            embed = error_embed("❌ Format IP Tidak Valid", f"IP `{ip_address}` tidak valid. Gunakan format: 192.168.1.1")
            await inter.followup.send(embed=embed)
            return
        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError()
        except (ValueError, TypeError):
            embed = error_embed("❌ Format IP Tidak Valid", f"IP `{ip_address}` tidak valid. Gunakan format: 192.168.1.1")
            await inter.followup.send(embed=embed)
            return

        try:
            existing = await fetch(
                "SELECT 1 FROM radgroupcheck WHERE groupname=%s AND attribute=%s AND value=%s LIMIT 1",
                (groupname, "NAS-IP-Address", ip_address)
            )
            
            if existing:
                embed = warning_embed("⚠️ Sudah Ada", f"Group `{groupname}` sudah memiliki batasan untuk NAS IP `{ip_address}`.")
                await inter.followup.send(embed=embed)
                return
            
            await execute(
                "INSERT INTO radgroupcheck (groupname, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (groupname, "NAS-IP-Address", "==", ip_address)
            )
            logger.info(f"Created group '{groupname}' NAS IP restriction row: added '{ip_address}'")
            
            ip_rows = await fetch(
                "SELECT value FROM radgroupcheck WHERE groupname=%s AND attribute=%s ORDER BY value",
                (groupname, "NAS-IP-Address")
            )
            ips = [r['value'] for r in ip_rows]
            
            allowed_list = "\n".join(f"• `{ip}`" for ip in ips)
            fields = [
                ("Group Name", f"`{groupname}`", True),
                ("Added IP", f"`{ip_address}`", True),
                ("All Allowed NAS IPs", allowed_list, False)
            ]
            embed = success_embed("✅ NAS IP Berhasil Ditambahkan ke Group", fields=fields)
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat groupnasadd: {e}")
            embed = error_embed("❌ Gagal Menambahkan NAS ke Group", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat groupnasadd: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="groupnasremove",
        description="Remove a NAS IP restriction from a group"
    )
    async def groupnasremove(
        self,
        inter,
        groupname: str = commands.Param(autocomplete=groupname_autocomplete),
        nas_ip: str = commands.Param(autocomplete=group_nas_ip_autocomplete, description="Pilih IP NAS yang ingin dihapus")
    ):
        await inter.response.defer()
        groupname = groupname.strip()
        
        if " - " in nas_ip:
            ip_address = nas_ip.split(" - ")[0].strip()
        else:
            ip_address = nas_ip.strip()

        try:
            existing = await fetch(
                "SELECT id FROM radgroupcheck WHERE groupname=%s AND attribute=%s AND value=%s LIMIT 1",
                (groupname, "NAS-IP-Address", ip_address)
            )
            
            if not existing:
                embed = warning_embed("⚠️ Tidak Ditemukan", f"IP `{ip_address}` tidak ditemukan dalam pembatasan group `{groupname}`.")
                await inter.followup.send(embed=embed)
                return
            
            row_id = existing[0]['id']
            await execute("DELETE FROM radgroupcheck WHERE id=%s", (row_id,))
            logger.info(f"Removed NAS IP restriction '{ip_address}' for group '{groupname}'")
            
            ip_rows = await fetch(
                "SELECT value FROM radgroupcheck WHERE groupname=%s AND attribute=%s ORDER BY value",
                (groupname, "NAS-IP-Address")
            )
            ips = [r['value'] for r in ip_rows]
            
            if not ips:
                embed = success_embed("✅ NAS IP Berhasil Dihapus", f"Semua pembatasan NAS IP untuk group `{groupname}` telah dihapus (akses tidak dibatasi).")
            else:
                allowed_list = "\n".join(f"• `{ip}`" for ip in ips)
                fields = [
                    ("Group Name", f"`{groupname}`", True),
                    ("Removed IP", f"`{ip_address}`", True),
                    ("Remaining Allowed NAS IPs", allowed_list, False)
                ]
                embed = success_embed("✅ NAS IP Berhasil Dihapus dari Group", fields=fields)
            
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat groupnasremove: {e}")
            embed = error_embed("❌ Gagal Menghapus NAS dari Group", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat groupnasremove: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="creategroup",
        description="Create a new group with a default placeholder configuration"
    )
    async def creategroup(self, inter, groupname: str):
        await inter.response.defer()
        groupname = groupname.strip()
        
        try:
            exists_reply = await fetch("SELECT 1 FROM radgroupreply WHERE groupname=%s LIMIT 1", (groupname,))
            exists_check = await fetch("SELECT 1 FROM radgroupcheck WHERE groupname=%s LIMIT 1", (groupname,))
            
            if exists_reply or exists_check:
                embed = warning_embed("⚠️ Group Sudah Ada", f"Group `{groupname}` sudah terdaftar di database.")
                await inter.followup.send(embed=embed)
                return
            
            await execute(
                "INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (groupname, "Session-Timeout", ":=", "0")
            )
            logger.info(f"Group '{groupname}' created with default Session-Timeout placeholder")
            
            embed = success_embed("✅ Group Berhasil Dibuat", f"Group `{groupname}` telah dibuat dengan konfigurasi default (unlimited session timeout).")
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat creategroup: {e}")
            embed = error_embed("❌ Gagal Membuat Group", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat creategroup: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="deletegroup",
        description="Delete a group and all its check/reply attributes and user mappings"
    )
    async def deletegroup(self, inter, groupname: str = commands.Param(autocomplete=groupname_autocomplete)):
        await inter.response.defer()
        groupname = groupname.strip()
        
        try:
            exists_reply = await fetch("SELECT 1 FROM radgroupreply WHERE groupname=%s LIMIT 1", (groupname,))
            exists_check = await fetch("SELECT 1 FROM radgroupcheck WHERE groupname=%s LIMIT 1", (groupname,))
            exists_user = await fetch("SELECT 1 FROM radusergroup WHERE groupname=%s LIMIT 1", (groupname,))
            
            if not exists_reply and not exists_check and not exists_user:
                embed = error_embed("❌ Group Tidak Ditemukan", f"Group `{groupname}` tidak ada di database.")
                await inter.followup.send(embed=embed)
                return
            
            await execute("DELETE FROM radgroupreply WHERE groupname=%s", (groupname,))
            await execute("DELETE FROM radgroupcheck WHERE groupname=%s", (groupname,))
            await execute("DELETE FROM radusergroup WHERE groupname=%s", (groupname,))
            
            logger.info(f"Group '{groupname}' and all its attributes and mappings were deleted")
            
            embed = success_embed("✅ Group Berhasil Dihapus", f"Group `{groupname}` beserta seluruh atribut dan pemetaan usernya telah dihapus dari database.")
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat deletegroup: {e}")
            embed = error_embed("❌ Gagal Menghapus Group", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat deletegroup: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="removeprofile",
        description="Remove profile/group assignment from a user (leaving them without any group)"
    )
    async def removeprofile(self, inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        
        try:
            rows = await fetch("SELECT groupname FROM radusergroup WHERE username=%s LIMIT 1", (username,))
            if not rows:
                embed = warning_embed("⚠️ Tidak Berubah", f"User `{username}` saat ini tidak memiliki profile/group.")
                await inter.followup.send(embed=embed)
                return
            
            groupname = rows[0]['groupname']
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
            logger.info(f"User '{username}' removed from group '{groupname}'")
            
            embed = success_embed("✅ Profile Berhasil Dicopot", f"User `{username}` telah dikeluarkan dari group `{groupname}` dan sekarang tidak memiliki group.")
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat removeprofile: {e}")
            embed = error_embed("❌ Gagal Mencopot Profile", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat removeprofile: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="groupinfo",
        description="Lihat detail informasi, konfigurasi, dan jumlah user di suatu group"
    )
    async def groupinfo(self, inter, groupname: str = commands.Param(autocomplete=groupname_autocomplete)):
        await inter.response.defer()
        groupname = groupname.strip()
        
        try:
            exists_reply = await fetch("SELECT 1 FROM radgroupreply WHERE groupname=%s LIMIT 1", (groupname,))
            exists_check = await fetch("SELECT 1 FROM radgroupcheck WHERE groupname=%s LIMIT 1", (groupname,))
            exists_user = await fetch("SELECT 1 FROM radusergroup WHERE groupname=%s LIMIT 1", (groupname,))
            
            if not exists_reply and not exists_check and not exists_user:
                embed = error_embed("❌ Group Tidak Ditemukan", f"Group `{groupname}` tidak terdaftar di database.")
                await inter.followup.send(embed=embed)
                return
            
            user_count_row = await fetch("SELECT COUNT(*) AS count FROM radusergroup WHERE groupname=%s", (groupname,))
            user_count = user_count_row[0]['count'] if user_count_row else 0
            
            check_rows = await fetch("SELECT attribute, op, value FROM radgroupcheck WHERE groupname=%s ORDER BY attribute", (groupname,))
            reply_rows = await fetch("SELECT attribute, op, value FROM radgroupreply WHERE groupname=%s ORDER BY attribute", (groupname,))
            
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
                
            allowed_nas_ips = []
            other_checks = []
            
            for r in check_rows:
                attr = r['attribute']
                op = r['op']
                val = r['value']
                
                if attr == "NAS-IP-Address":
                    ips = _parse_nas_ips(val)
                    for ip in ips:
                        nas_name = nas_map.get(ip)
                        if nas_name:
                            allowed_nas_ips.append(f"• `{ip}` - **{nas_name}**")
                        else:
                            allowed_nas_ips.append(f"• `{ip}`")
                else:
                    other_checks.append(f"• **{attr}** `{op}` `{val}`")
            
            fields = [
                ("👥 Jumlah User", f"`{user_count} user`", True)
            ]
            
            if allowed_nas_ips:
                fields.append(("🖥️ Allowed NAS IPs", "\n".join(allowed_nas_ips), False))
            else:
                fields.append(("🖥️ Allowed NAS IPs", "*Akses ke semua NAS (Tidak Dibatasi)*", False))
                
            if other_checks:
                fields.append(("📋 Check Attributes (Syarat)", "\n".join(other_checks), False))
                
            if reply_rows:
                reply_list = [f"• **{r['attribute']}** `{r['op']}` `{r['value']}`" for r in reply_rows]
                fields.append(("⚙️ Reply Attributes (Layanan)", "\n".join(reply_list), False))
            else:
                fields.append(("⚙️ Reply Attributes (Layanan)", "*Tidak ada reply attributes*", False))
                
            embed = info_embed(f"🖥️ Group Info: {groupname}", fields=fields)
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat groupinfo: {e}")
            embed = error_embed("❌ Gagal Mengambil Data Group", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat groupinfo: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(GroupCommands(bot))
