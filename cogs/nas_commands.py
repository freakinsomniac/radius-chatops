import os
import logging
import disnake
from disnake.ext import commands
from database.db import fetch, execute
from utils.embeds import success_embed, error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete, nas_ip_autocomplete, nasname_autocomplete
from utils.exceptions import UserNotFound, DatabaseError

logger = logging.getLogger(__name__)

NAS_TYPE_CHOICES = {
    "other": "other",
    "mikrotik": "mikrotik",
    "cisco": "cisco",
}


class NasCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="naslist",
        description="List configured NAS devices"
    )
    async def naslist(self, inter, limit: int = 50):
        await inter.response.defer()
        limit = max(1, min(200, int(limit)))
        try:
            query = f"SELECT id, nasname, shortname, description FROM nas ORDER BY id LIMIT {limit};"
            rows = await fetch(query)
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil daftar NAS: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada NAS", "Tidak ada NAS terdaftar di database.")
            await inter.followup.send(embed=embed)
            return

        result = "\n".join(f"• **{r['id']}** - {r.get('nasname') or '-'} ({r.get('shortname') or '-'})" for r in rows)
        embed = info_embed(f"🖥️ NAS List (Limit: {limit})", result)
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="nasusers",
        description="List users currently connected to a NAS"
    )
    async def nasusers(self, inter, nasip: str, limit: int = 100):
        await inter.response.defer()
        limit = max(1, min(500, int(limit)))
        try:
            query = f"SELECT username, framedipaddress, acctstarttime FROM radacct WHERE nasipaddress=%s AND acctstoptime IS NULL ORDER BY acctstarttime DESC LIMIT {limit}"
            rows = await fetch(query, (nasip,))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil user NAS: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada User", f"Tidak ada user aktif di NAS `{nasip}`.")
            await inter.followup.send(embed=embed)
            return

        result = "\n".join(f"• {r['username']} ({r.get('framedipaddress') or '-'})" for r in rows)
        embed = info_embed(f"👥 Users on {nasip} (Max {limit})", result)
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="addnasip",
        description="Tambah NAS IP Address restriction untuk user"
    )
    async def addnasip(
        self,
        inter,
        username: str = commands.Param(autocomplete=username_autocomplete),
        nas_ip: str = commands.Param(name="nas_ip", autocomplete=nas_ip_autocomplete, description="Pilih NAS dari autocomplete atau ketik IP langsung")
    ):
        await inter.response.defer()
        username = username.strip()
        
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
            user_exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
            if not user_exists:
                raise UserNotFound(f"User `{username}` tidak ada di database")

            existing = await fetch(
                "SELECT 1 FROM radcheck WHERE username=%s AND attribute=%s AND value=%s LIMIT 1",
                (username, "NAS-IP-Address", ip_address)
            )
            if existing:
                embed = warning_embed("⚠️ Sudah Ada", f"User `{username}` sudah memiliki akses ke NAS `{ip_address}`")
                await inter.followup.send(embed=embed)
                return

            await execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (username, "NAS-IP-Address", "==", ip_address)
            )
            logger.info(f"NAS IP '{ip_address}' ditambahkan untuk user '{username}'")
            
        except UserNotFound as e:
            logger.warning(f"User not found: {username}")
            embed = error_embed("❌ User Tidak Ditemukan", str(e))
            await inter.followup.send(embed=embed)
            return
            
        except DatabaseError as e:
            logger.error(f"Database error saat addnasip: {e}")
            embed = error_embed("❌ Gagal Menambah NAS IP", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            return
            
        except Exception as e:
            logger.exception(f"Unexpected error saat addnasip: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)
            return

        fields = [
            ("Username", f"`{username}`", True),
            ("NAS IP", f"`{ip_address}`", True),
            ("Operator", "`==`", True)
        ]
        embed = success_embed("✅ NAS IP Berhasil Ditambahkan", fields=fields)
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="removenasip",
        description="Hapus NAS IP Address restriction dari user"
    )
    async def removenasip(
        self,
        inter,
        username: str = commands.Param(autocomplete=username_autocomplete),
        nas_ip: str = commands.Param(name="nas_ip", autocomplete=nas_ip_autocomplete, description="Pilih NAS dari autocomplete atau ketik IP langsung")
    ):
        await inter.response.defer()
        username = username.strip()
        
        if " - " in nas_ip:
            ip_address = nas_ip.split(" - ")[0].strip()
        else:
            ip_address = nas_ip.strip()

        try:
            existing = await fetch(
                "SELECT 1 FROM radcheck WHERE username=%s AND attribute=%s AND value=%s LIMIT 1",
                (username, "NAS-IP-Address", ip_address)
            )
            if not existing:
                raise UserNotFound(f"User `{username}` tidak memiliki akses ke NAS `{ip_address}`")

            await execute(
                "DELETE FROM radcheck WHERE username=%s AND attribute=%s AND value=%s",
                (username, "NAS-IP-Address", ip_address)
            )
            logger.info(f"NAS IP '{ip_address}' dihapus untuk user '{username}'")
            
        except UserNotFound as e:
            logger.warning(f"NAS IP not found for user: {username}")
            embed = error_embed("❌ Tidak Ditemukan", str(e))
            await inter.followup.send(embed=embed)
            return
            
        except DatabaseError as e:
            logger.error(f"Database error saat removenasip: {e}")
            embed = error_embed("❌ Gagal Menghapus NAS IP", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            return
            
        except Exception as e:
            logger.exception(f"Unexpected error saat removenasip: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)
            return

        embed = success_embed("✅ NAS IP Berhasil Dihapus", f"User `{username}` tidak lagi memiliki akses ke NAS `{ip_address}`.")
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="listnasip",
        description="Lihat semua NAS IP yang bisa diakses user"
    )
    async def listnasip(self, inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()

        try:
            rows = await fetch(
                "SELECT value FROM radcheck WHERE username=%s AND attribute=%s ORDER BY value",
                (username, "NAS-IP-Address")
            )
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil NAS IP: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada Restriction", f"User `{username}` tidak memiliki NAS IP restriction (akses ke semua NAS).")
            await inter.followup.send(embed=embed)
            return

        nas_map = {}
        try:
            nas_rows = await fetch("SELECT nasname, shortname FROM nas WHERE nasname IS NOT NULL")
            for nas_row in nas_rows:
                nasname = nas_row.get('nasname', '')
                shortname = nas_row.get('shortname', '')
                if nasname and (nasname.count('.') == 3 or '.' in nasname):
                    nas_map[nasname] = shortname or nasname
        except Exception:
            pass

        result_lines = []
        for r in rows:
            ip = r['value']
            nas_name = nas_map.get(ip)
            if nas_name:
                result_lines.append(f"• `{ip}` - **{nas_name}**")
            else:
                result_lines.append(f"• `{ip}`")

        result = "\n".join(result_lines)
        embed = info_embed(f"🖥️ NAS IP Access: {username}", result)
        await inter.followup.send(embed=embed)


    @commands.slash_command(
        name="addnas",
        description="Tambah NAS device baru ke database"
    )
    async def addnas(
        self,
        inter,
        nasname: str = commands.Param(name="nas_ip_host", description="NAS IP/Host"),
        secret: str = commands.Param(name="nas_secret", description="NAS Secret"),
        type: str = commands.Param(name="nas_type", choices=NAS_TYPE_CHOICES, description="NAS Type"),
        shortname: str = commands.Param(name="nas_shortname", description="NAS Shortname")
    ):
        await inter.response.defer()
        nasname = nasname.strip()
        shortname = shortname.strip()

        try:
            existing = await fetch("SELECT 1 FROM nas WHERE nasname=%s LIMIT 1", (nasname,))
            if existing:
                embed = warning_embed("⚠️ NAS Sudah Ada", f"NAS dengan nasname `{nasname}` sudah terdaftar.")
                await inter.followup.send(embed=embed)
                return

            await execute(
                "INSERT INTO nas (nasname, shortname, type, ports, secret, description) VALUES (%s, %s, %s, %s, %s, %s)",
                (nasname, shortname, type, 0, secret, "")
            )
            logger.info(f"NAS '{nasname}' ({shortname}) berhasil ditambahkan")
        except Exception as e:
            logger.exception(f"Gagal menambah NAS: {e}")
            embed = error_embed("❌ Gagal Menambah NAS", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        fields = [
            ("NAS Name", f"`{nasname}`", True),
            ("Shortname", f"`{shortname}`", True),
            ("Type", f"`{type}`", True),
            ("Ports", "`0`", True),
            ("Description", "-", False)
        ]
        embed = success_embed("✅ NAS Berhasil Ditambahkan", fields=fields)
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="delnas",
        description="Hapus NAS device dari database"
    )
    async def delnas(
        self,
        inter,
        nasname: str = commands.Param(autocomplete=nasname_autocomplete, description="NAS yang akan dihapus")
    ):
        await inter.response.defer()
        nasname = nasname.strip()

        if " - " in nasname:
            nasname = nasname.split(" - ")[0].strip()

        try:
            existing = await fetch("SELECT id, nasname, shortname FROM nas WHERE nasname=%s LIMIT 1", (nasname,))
            if not existing:
                embed = error_embed("❌ NAS Tidak Ditemukan", f"NAS dengan nasname `{nasname}` tidak ada di database.")
                await inter.followup.send(embed=embed)
                return

            await execute("DELETE FROM nas WHERE nasname=%s", (nasname,))
            logger.info(f"NAS '{nasname}' berhasil dihapus")
        except Exception as e:
            logger.exception(f"Gagal menghapus NAS: {e}")
            embed = error_embed("❌ Gagal Menghapus NAS", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        nas_info = existing[0]
        fields = [
            ("NAS Name", f"`{nas_info.get('nasname')}`", True),
            ("Shortname", f"`{nas_info.get('shortname') or '-'}`", True)
        ]
        embed = success_embed("✅ NAS Berhasil Dihapus", fields=fields)
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="viewnas",
        description="Lihat detail NAS atau daftar singkat semua NAS"
    )
    async def viewnas(self, inter, nas: str = commands.Param(autocomplete=nasname_autocomplete, description="Pilih NAS (opsional)")):
        await inter.response.defer()
        try:
            if nas:
                if " - " in nas:
                    nas = nas.split(" - ")[0].strip()
                rows = await fetch("SELECT id, nasname, shortname, type, ports, secret, description FROM nas WHERE nasname=%s LIMIT 1", (nas,))
                if not rows:
                    embed = error_embed("❌ NAS Tidak Ditemukan", f"NAS `{nas}` tidak ada di database.")
                    await inter.followup.send(embed=embed)
                    return

                r = rows[0]
                fields = [
                    ("ID", f"`{r.get('id')}`", True),
                    ("NAS Name", f"`{r.get('nasname') or '-'}`", True),
                    ("Shortname", f"`{r.get('shortname') or '-'}`", True),
                    ("Type", f"`{r.get('type') or '-'}`", True),
                    ("Ports", f"`{r.get('ports') or '-'}`", True),
                    ("Secret", f"`{r.get('secret') or '-'}`", False),
                    ("Description", f"{r.get('description') or '-'}", False),
                ]
                embed = info_embed(f"🖥️ NAS Detail: {r.get('nasname')}", fields=fields)
                await inter.followup.send(embed=embed)
                return

            # no specific NAS provided -> list brief
            rows = await fetch("SELECT id, nasname, shortname, type FROM nas ORDER BY id LIMIT 200")
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil data NAS: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada NAS", "Tidak ada NAS terdaftar di database.")
            await inter.followup.send(embed=embed)
            return

        result = "\n".join(f"• **{r['id']}** - {r.get('nasname') or '-'} ({r.get('shortname') or '-'}) — `{r.get('type') or '-'}`" for r in rows)
        embed = info_embed("🖥️ NAS List", result)
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="editnas",
        description="Edit field NAS yang sudah ada (hanya field yang diberikan akan diupdate)"
    )
    async def editnas(
        self,
        inter,
        nas: str = commands.Param(autocomplete=nasname_autocomplete, description="Pilih NAS yang akan diubah"),
        secret: str = None,
        type: str = commands.Param(default=None, choices=NAS_TYPE_CHOICES, description="Ubah tipe NAS (opsional)"),
        shortname: str = None,
        ports: int = None,
        description: str = None
    ):
        await inter.response.defer()
        nas_input = nas.strip()
        if " - " in nas_input:
            nas_input = nas_input.split(" - ")[0].strip()

        try:
            existing = await fetch("SELECT id FROM nas WHERE nasname=%s LIMIT 1", (nas_input,))
            if not existing:
                embed = error_embed("❌ NAS Tidak Ditemukan", f"NAS `{nas_input}` tidak ada di database.")
                await inter.followup.send(embed=embed)
                return

            updates = {}
            params = []
            if secret is not None:
                updates['secret'] = secret
            if type is not None:
                updates['type'] = type
            if shortname is not None:
                updates['shortname'] = shortname
            if ports is not None:
                try:
                    ports = int(ports)
                    updates['ports'] = ports
                except Exception:
                    embed = error_embed("❌ Format Ports Tidak Valid", "Field `ports` harus berupa angka.")
                    await inter.followup.send(embed=embed)
                    return
            if description is not None:
                updates['description'] = description

            if not updates:
                embed = warning_embed("⚠️ Tidak Ada Perubahan", "Tidak ada field yang diberikan untuk diupdate.")
                await inter.followup.send(embed=embed)
                return

            set_clause = ", ".join(f"{k}=%s" for k in updates.keys())
            params = list(updates.values()) + [nas_input]
            sql = f"UPDATE nas SET {set_clause} WHERE nasname=%s"
            await execute(sql, tuple(params))
            logger.info(f"NAS '{nas_input}' diupdate: {list(updates.keys())}")
        except Exception as e:
            logger.exception(f"Gagal mengupdate NAS: {e}")
            embed = error_embed("❌ Gagal Mengupdate NAS", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        fields = [(k.capitalize(), f"`{v}`", True) for k, v in updates.items()]
        embed = success_embed("✅ NAS Berhasil Diupdate", fields=fields)
        await inter.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(NasCommands(bot))
