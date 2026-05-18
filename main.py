import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from database.db import init_db, close_db, fetch, execute
from utils.embeds import success_embed, error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete, groupname_autocomplete, attribute_autocomplete, operator_autocomplete, nas_ip_autocomplete

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
    await inter.response.send_message("Pong! 🏓")

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
            embed = error_embed("❌ Error", f"Gagal mengambil data: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada Data", "Tidak ada user di database.")
            await inter.followup.send(embed=embed)
            return

        users_list = [r['username'] for r in rows]
        chunk_size = 50
        chunks = [users_list[i:i + chunk_size] for i in range(0, len(users_list), chunk_size)]
        
        for idx, chunk in enumerate(chunks):
            result = "\n".join(f"• {u}" for u in chunk)
            embed = info_embed(
                f"📡 Daftar User Radius (Halaman {idx + 1}/{len(chunks)})",
                f"Total: {len(users_list)} user\n\n{result}"
            )
            await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="adduser",
        description="Tambah user radius baru",
        default_guild_ids=[g_id]
    )
    async def adduser(inter, username: str, password: str, group: str = commands.Param(default=None, autocomplete=groupname_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        try:
            exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengecek user: {e}")
            await inter.followup.send(embed=embed)
            return

        if exists:
            embed = warning_embed("⚠️ User Sudah Ada", f"User `{username}` sudah terdaftar di database.")
            await inter.followup.send(embed=embed)
            return

        try:
            await execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (username, "Cleartext-Password", ":=", password)
            )
        except Exception as e:
            embed = error_embed("❌ Gagal Menambah User", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        try:
            await execute(
                "INSERT INTO userinfo (username, creationdate, creationby, enableportallogin) VALUES (%s, NOW(), %s, %s)",
                (username, "discord-bot", 0)
            )
        except Exception:
            pass

        if group:
            try:
                await execute(
                    "INSERT INTO radusergroup (username, groupname) VALUES (%s, %s)",
                    (username, group)
                )
                fields = [("Username", f"`{username}`", True), ("Group", f"`{group}`", True)]
            except Exception as e:
                embed = warning_embed("⚠️ User Dibuat, Group Gagal", f"User berhasil dibuat tapi gagal menambah group: {e}")
                await inter.followup.send(embed=embed)
                return
        else:
            fields = [("Username", f"`{username}`", True)]

        embed = success_embed("✅ User Berhasil Ditambahkan", fields=fields)
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="deluser",
        description="Hapus user radius",
        default_guild_ids=[g_id]
    )
    async def deluser(inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        try:
            exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengecek user: {e}")
            await inter.followup.send(embed=embed)
            return

        if not exists:
            embed = error_embed("❌ User Tidak Ditemukan", f"User `{username}` tidak ada di database.")
            await inter.followup.send(embed=embed)
            return

        try:
            await execute("DELETE FROM radcheck WHERE username=%s", (username,))
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
        except Exception as e:
            embed = error_embed("❌ Gagal Menghapus User", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        embed = success_embed("✅ User Berhasil Dihapus", f"User `{username}` telah dihapus dari database.")
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="changepass",
        description="Ubah password user radius",
        default_guild_ids=[g_id]
    )
    async def changepass(inter, username: str = commands.Param(autocomplete=username_autocomplete), new_password: str = None):
        await inter.response.defer()
        try:
            rows = await fetch("SELECT id FROM radcheck WHERE username=%s AND attribute=%s", (username, "Cleartext-Password"))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengecek user: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = error_embed("❌ User Tidak Ditemukan", f"User `{username}` atau attribute password tidak ditemukan.")
            await inter.followup.send(embed=embed)
            return

        try:
            await execute(
                "UPDATE radcheck SET value=%s WHERE username=%s AND attribute=%s",
                (new_password, username, "Cleartext-Password")
            )
        except Exception as e:
            embed = error_embed("❌ Gagal Mengubah Password", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        embed = success_embed("✅ Password Berhasil Diubah", f"Password untuk user `{username}` telah diperbarui.")
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="online",
        description="List currently online users (radacct)",
        default_guild_ids=[g_id]
    )
    async def online(inter):
        await inter.response.defer()
        try:
            query = "SELECT username, nasipaddress, framedipaddress, acctstarttime FROM radacct WHERE acctstoptime IS NULL ORDER BY username LIMIT 50;"
            rows = await fetch(query)
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil data online: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada User Online", "Saat ini tidak ada user yang sedang aktif.")
            await inter.followup.send(embed=embed)
            return

        result = "\n".join(f"• {r['username']} @ {r.get('nasipaddress') or '-'} ({r.get('framedipaddress') or '-'})" for r in rows)
        embed = info_embed(
            f"🟢 User Online ({len(rows)})",
            result
        )
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="userstats",
        description="Show basic session stats for a user (radacct)",
        default_guild_ids=[g_id]
    )
    async def userstats(inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        try:
            query = "SELECT COUNT(*) AS sessions, COALESCE(SUM(acctinputoctets),0) AS in_bytes, COALESCE(SUM(acctoutputoctets),0) AS out_bytes, MAX(acctstarttime) AS last_login FROM radacct WHERE username=%s"
            rows = await fetch(query, (username,))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil stats: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = error_embed("❌ Data Tidak Ditemukan", f"Tidak ada data untuk user `{username}`.")
            await inter.followup.send(embed=embed)
            return

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
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="lastlogin",
        description="Show last login time for a user (radacct)",
        default_guild_ids=[g_id]
    )
    async def lastlogin(inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        try:
            query = "SELECT acctstarttime FROM radacct WHERE username=%s ORDER BY acctstarttime DESC LIMIT 1"
            rows = await fetch(query, (username,))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil last login: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Data Tidak Ditemukan", f"Tidak ada riwayat login untuk user `{username}`.")
            await inter.followup.send(embed=embed)
            return

        embed = info_embed(f"🕐 Last Login: {username}", str(rows[0]['acctstarttime']))
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="activecount",
        description="Count active sessions (radacct)",
        default_guild_ids=[g_id]
    )
    async def activecount(inter):
        await inter.response.defer()
        try:
            query = "SELECT COUNT(*) AS active FROM radacct WHERE acctstoptime IS NULL"
            rows = await fetch(query)
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal menghitung active sessions: {e}")
            await inter.followup.send(embed=embed)
            return

        count = rows[0]['active']
        embed = info_embed(f"🟢 Active Sessions: {count}")
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="naslist",
        description="List configured NAS devices",
        default_guild_ids=[g_id]
    )
    async def naslist(inter, limit: int = 50):
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

    @bot.slash_command(
        name="nasstatus",
        description="Show active session count per NAS or for a specific NAS",
        default_guild_ids=[g_id]
    )
    async def nasstatus(inter, nasip: str = None):
        await inter.response.defer()
        try:
            if nasip:
                rows = await fetch("SELECT nasipaddress, COUNT(*) AS active FROM radacct WHERE acctstoptime IS NULL AND nasipaddress=%s GROUP BY nasipaddress", (nasip,))
            else:
                rows = await fetch("SELECT nasipaddress, COUNT(*) AS active FROM radacct WHERE acctstoptime IS NULL GROUP BY nasipaddress")
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil status NAS: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada Session", "Tidak ada session aktif atau NAS tidak ditemukan.")
            await inter.followup.send(embed=embed)
            return

        result = "\n".join(f"• {r.get('nasipaddress') or '-'}: **{r.get('active')}** active" for r in rows)
        embed = info_embed("🖥️ NAS Status", result)
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="nasusers",
        description="List users currently connected to a NAS",
        default_guild_ids=[g_id]
    )
    async def nasusers(inter, nasip: str, limit: int = 100):
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

    @bot.slash_command(
        name="setprofile",
        description="Assign a single profile/group to a user (radusergroup)",
        default_guild_ids=[g_id]
    )
    async def setprofile(inter, username: str = commands.Param(autocomplete=username_autocomplete), groupname: str = commands.Param(autocomplete=groupname_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        groupname = groupname.strip()
        try:
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
            await execute("INSERT INTO radusergroup (username, groupname) VALUES (%s, %s)", (username, groupname))
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal set profile: {e}")
            await inter.followup.send(embed=embed)
            return

        fields = [("Username", f"`{username}`", True), ("Profile", f"`{groupname}`", True)]
        embed = success_embed("✅ Profile Berhasil Diubah", fields=fields)
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="groupadd",
        description="Add a reply attribute to a group (radgroupreply)",
        default_guild_ids=[g_id]
    )
    async def groupadd(inter, groupname: str = commands.Param(autocomplete=groupname_autocomplete), attribute: str = commands.Param(autocomplete=attribute_autocomplete), op: str = commands.Param(autocomplete=operator_autocomplete), value: str = None):
        await inter.response.defer()
        groupname = groupname.strip()
        attribute = attribute.strip()
        op = op.strip()
        try:
            await execute("INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES (%s, %s, %s, %s)", (groupname, attribute, op, value))
        except Exception as e:
            embed = error_embed("❌ Gagal Menambah Group Reply", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        fields = [("Group", f"`{groupname}`", True), ("Attribute", f"`{attribute}`", True), ("Operator", f"`{op}`", True), ("Value", f"`{value}`", True)]
        embed = success_embed("✅ Group Reply Berhasil Ditambahkan", fields=fields)
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="groupremove",
        description="Remove reply attributes from a group or remove entire group replies",
        default_guild_ids=[g_id]
    )
    async def groupremove(inter, groupname: str = commands.Param(autocomplete=groupname_autocomplete), attribute: str = commands.Param(default=None, autocomplete=attribute_autocomplete)):
        await inter.response.defer()
        groupname = groupname.strip()
        try:
            if attribute:
                await execute("DELETE FROM radgroupreply WHERE groupname=%s AND attribute=%s", (groupname, attribute))
                embed = success_embed("✅ Attribute Berhasil Dihapus", f"Attribute `{attribute}` dihapus dari group `{groupname}`.")
            else:
                await execute("DELETE FROM radgroupreply WHERE groupname=%s", (groupname,))
                embed = success_embed("✅ Group Reply Berhasil Dihapus", f"Semua reply untuk group `{groupname}` telah dihapus.")
        except Exception as e:
            embed = error_embed("❌ Gagal Menghapus Group Reply", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="checkattributes",
        description="Lihat semua attributes dari seorang user",
        default_guild_ids=[g_id]
    )
    async def checkattributes(inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        
        try:
            rows = await fetch(
                "SELECT attribute, op, value FROM radcheck WHERE username=%s ORDER BY attribute",
                (username,)
            )
        except Exception as e:
            embed = error_embed("❌ Error", f"Gagal mengambil attributes: {e}")
            await inter.followup.send(embed=embed)
            return

        if not rows:
            embed = warning_embed("⚠️ Tidak Ada Attributes", f"User `{username}` tidak memiliki attributes.")
            await inter.followup.send(embed=embed)
            return

        result = "\n".join(f"• **{r['attribute']}** `{r['op']}` `{r['value']}`" for r in rows)
        embed = info_embed(f"📋 Check Attributes: {username}", result)
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="addnasip",
        description="Tambah NAS IP Address restriction untuk user",
        default_guild_ids=[g_id]
    )
    async def addnasip(
        inter,
        username: str = commands.Param(autocomplete=username_autocomplete),
        nas_ip: str = commands.Param(name="nas_ip", autocomplete=nas_ip_autocomplete, description="Format: IP - ShortName (NasName)")
    ):
        await inter.response.defer()
        username = username.strip()
        
        ip_address = nas_ip.split(" - ")[0].strip() if " - " in nas_ip else nas_ip.strip()
        
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
                embed = error_embed("❌ User Tidak Ditemukan", f"User `{username}` tidak ada di database.")
                await inter.followup.send(embed=embed)
                return

            existing = await fetch(
                "SELECT 1 FROM radcheck WHERE username=%s AND attribute=%s AND value=%s LIMIT 1",
                (username, "NAS-IP-Address", ip_address)
            )
            if existing:
                embed = warning_embed("⚠️ Sudah Ada", f"User `{username}` sudah memiliki akses ke NAS `{ip_address}`.")
                await inter.followup.send(embed=embed)
                return

            await execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (username, "NAS-IP-Address", "==", ip_address)
            )
        except Exception as e:
            embed = error_embed("❌ Gagal Menambah NAS IP", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        fields = [
            ("Username", f"`{username}`", True),
            ("NAS IP", f"`{ip_address}`", True),
            ("Operator", "`==`", True)
        ]
        embed = success_embed("✅ NAS IP Berhasil Ditambahkan", fields=fields)
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="removenasip",
        description="Hapus NAS IP Address restriction dari user",
        default_guild_ids=[g_id]
    )
    async def removenasip(
        inter,
        username: str = commands.Param(autocomplete=username_autocomplete),
        nas_ip: str = commands.Param(name="nas_ip", description="IP Address yang ingin dihapus")
    ):
        await inter.response.defer()
        username = username.strip()
        nas_ip = nas_ip.strip()

        ip_address = nas_ip.split(" - ")[0].strip() if " - " in nas_ip else nas_ip.strip()

        try:
            existing = await fetch(
                "SELECT 1 FROM radcheck WHERE username=%s AND attribute=%s AND value=%s LIMIT 1",
                (username, "NAS-IP-Address", ip_address)
            )
            if not existing:
                embed = error_embed("❌ Tidak Ditemukan", f"User `{username}` tidak memiliki akses ke NAS `{ip_address}`.")
                await inter.followup.send(embed=embed)
                return

            await execute(
                "DELETE FROM radcheck WHERE username=%s AND attribute=%s AND value=%s",
                (username, "NAS-IP-Address", ip_address)
            )
        except Exception as e:
            embed = error_embed("❌ Gagal Menghapus NAS IP", f"Error: {e}")
            await inter.followup.send(embed=embed)
            return

        embed = success_embed("✅ NAS IP Berhasil Dihapus", f"User `{username}` tidak lagi memiliki akses ke NAS `{ip_address}`.")
        await inter.followup.send(embed=embed)

    @bot.slash_command(
        name="listnasip",
        description="Lihat semua NAS IP yang bisa diakses user",
        default_guild_ids=[g_id]
    )
    async def listnasip(inter, username: str = commands.Param(autocomplete=username_autocomplete)):
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

        nas_info = {}
        try:
            nas_rows = await fetch("SELECT nasipaddress, shortname, nasname FROM nas")
            nas_info = {r['nasipaddress']: r for r in nas_rows}
        except Exception:
            pass

        result_lines = []
        for r in rows:
            ip = r['value']
            if ip in nas_info:
                info = nas_info[ip]
                result_lines.append(f"• `{ip}` - **{info.get('shortname', 'N/A')}** ({info.get('nasname', 'N/A')})")
            else:
                result_lines.append(f"• `{ip}`")

        result = "\n".join(result_lines)
        embed = info_embed(f"🖥️ NAS IP Access: {username}", result)
        await inter.followup.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
