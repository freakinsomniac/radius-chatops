import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from database.db import init_db, close_db, fetch, execute

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

    @bot.slash_command(
        name="adduser",
        description="Tambah user radius",
        default_guild_ids=[g_id]
    )
    async def adduser(inter, username: str, password: str, group: str = None):
        await inter.response.defer()
        username = username.strip()
        try:
            exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
        except Exception as e:
            await inter.followup.send(f"Error saat mengecek user: {e}")
            return

        if exists:
            await inter.followup.send("User sudah ada.")
            return

        try:
            await execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (username, "Cleartext-Password", ":=", password)
            )
        except Exception as e:
            await inter.followup.send(f"Gagal menambah user: {e}")
            return

        # insert minimal profile data so daloRADIUS UI shows the new user
        try:
            await execute(
                "INSERT INTO userinfo (username, creationdate, creationby, enableportallogin) VALUES (%s, NOW(), %s, %s)",
                (username, "discord-bot", 0)
            )
        except Exception:
            # non-fatal: user was created in radcheck but profile insert failed
            pass

        if group:
            try:
                await execute(
                    "INSERT INTO radusergroup (username, groupname) VALUES (%s, %s)",
                    (username, group)
                )
            except Exception as e:
                await inter.followup.send(f"User dibuat, tetapi gagal menambahkan group: {e}")
                return

        await inter.followup.send(f"User {username} berhasil ditambahkan.")

    @bot.slash_command(
        name="deluser",
        description="Hapus user radius",
        default_guild_ids=[g_id]
    )
    async def deluser(inter, username: str):
        await inter.response.defer()
        try:
            exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
        except Exception as e:
            await inter.followup.send(f"Error saat mengecek user: {e}")
            return

        if not exists:
            await inter.followup.send("User tidak ditemukan.")
            return

        try:
            await execute("DELETE FROM radcheck WHERE username=%s", (username,))
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
        except Exception as e:
            await inter.followup.send(f"Gagal menghapus user: {e}")
            return

        await inter.followup.send(f"User {username} berhasil dihapus.")

    @bot.slash_command(
        name="changepass",
        description="Ubah password user radius",
        default_guild_ids=[g_id]
    )
    async def changepass(inter, username: str, new_password: str):
        await inter.response.defer()
        try:
            rows = await fetch("SELECT id FROM radcheck WHERE username=%s AND attribute=%s", (username, "Cleartext-Password"))
        except Exception as e:
            await inter.followup.send(f"Error saat mengecek user: {e}")
            return

        if not rows:
            await inter.followup.send("User atau attribute password tidak ditemukan.")
            return

        try:
            await execute(
                "UPDATE radcheck SET value=%s WHERE username=%s AND attribute=%s",
                (new_password, username, "Cleartext-Password")
            )
        except Exception as e:
            await inter.followup.send(f"Gagal mengubah password: {e}")
            return

        await inter.followup.send(f"Password untuk {username} berhasil diubah.")

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
            await inter.followup.send(f"Error saat mengambil data online: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ada user online saat ini.")
            return

        result = "\n".join(f"- {r['username']} @ {r.get('nasipaddress') or '-'} ({r.get('framedipaddress') or '-'}) since {r.get('acctstarttime')}" for r in rows)
        await inter.followup.send(f"Online users (max 50):\n{result}")

    @bot.slash_command(
        name="userstats",
        description="Show basic session stats for a user (radacct)",
        default_guild_ids=[g_id]
    )
    async def userstats(inter, username: str):
        await inter.response.defer()
        username = username.strip()
        try:
            query = "SELECT COUNT(*) AS sessions, COALESCE(SUM(acctinputoctets),0) AS in_bytes, COALESCE(SUM(acctoutputoctets),0) AS out_bytes, MAX(acctstarttime) AS last_login FROM radacct WHERE username=%s"
            rows = await fetch(query, (username,))
        except Exception as e:
            await inter.followup.send(f"Error saat mengambil stats: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ditemukan data untuk user tersebut.")
            return

        r = rows[0]
        await inter.followup.send(f"Stats {username}: sessions={r['sessions']}, in={r['in_bytes']} bytes, out={r['out_bytes']} bytes, last_login={r['last_login']}")

    @bot.slash_command(
        name="lastlogin",
        description="Show last login time for a user (radacct)",
        default_guild_ids=[g_id]
    )
    async def lastlogin(inter, username: str):
        await inter.response.defer()
        username = username.strip()
        try:
            query = "SELECT acctstarttime FROM radacct WHERE username=%s ORDER BY acctstarttime DESC LIMIT 1"
            rows = await fetch(query, (username,))
        except Exception as e:
            await inter.followup.send(f"Error saat mengambil last login: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ditemukan last login untuk user tersebut.")
            return

        await inter.followup.send(f"Last login {username}: {rows[0]['acctstarttime']}")

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
            await inter.followup.send(f"Error saat menghitung active sessions: {e}")
            return

        await inter.followup.send(f"Active sessions: {rows[0]['active']}")

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
            await inter.followup.send(f"Error saat mengambil daftar NAS: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ada NAS terdaftar.")
            return

        result = "\n".join(f"- {r['id']}: {r.get('nasname') or '-'} ({r.get('shortname') or '-'}) - {r.get('description') or ''}" for r in rows)
        await inter.followup.send(f"NAS list (max {limit}):\n{result}")

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
            await inter.followup.send(f"Error saat mengambil status NAS: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ada session aktif atau NAS tidak ditemukan.")
            return

        result = "\n".join(f"- {r.get('nasipaddress') or '-'}: {r.get('active')} active" for r in rows)
        await inter.followup.send(f"NAS status:\n{result}")

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
            await inter.followup.send(f"Error saat mengambil user NAS: {e}")
            return

        if not rows:
            await inter.followup.send("Tidak ada user aktif di NAS ini.")
            return

        result = "\n".join(f"- {r['username']} ({r.get('framedipaddress') or '-'}) since {r.get('acctstarttime')}" for r in rows)
        await inter.followup.send(f"Users on {nasip} (max {limit}):\n{result}")

    @bot.slash_command(
        name="setprofile",
        description="Assign a single profile/group to a user (radusergroup)",
        default_guild_ids=[g_id]
    )
    async def setprofile(inter, username: str, groupname: str):
        await inter.response.defer()
        username = username.strip()
        groupname = groupname.strip()
        try:
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
            await execute("INSERT INTO radusergroup (username, groupname) VALUES (%s, %s)", (username, groupname))
        except Exception as e:
            await inter.followup.send(f"Error saat set profile: {e}")
            return

        await inter.followup.send(f"User {username} sekarang di profile {groupname}.")

    @bot.slash_command(
        name="groupadd",
        description="Add a reply attribute to a group (radgroupreply)",
        default_guild_ids=[g_id]
    )
    async def groupadd(inter, groupname: str, attribute: str, op: str, value: str):
        await inter.response.defer()
        groupname = groupname.strip()
        attribute = attribute.strip()
        op = op.strip()
        try:
            await execute("INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES (%s, %s, %s, %s)", (groupname, attribute, op, value))
        except Exception as e:
            await inter.followup.send(f"Gagal menambahkan group reply: {e}")
            return

        await inter.followup.send(f"Group reply ditambahkan ke {groupname}: {attribute} {op} {value}")

    @bot.slash_command(
        name="groupremove",
        description="Remove reply attributes from a group or remove entire group replies",
        default_guild_ids=[g_id]
    )
    async def groupremove(inter, groupname: str, attribute: str = None):
        await inter.response.defer()
        groupname = groupname.strip()
        try:
            if attribute:
                await execute("DELETE FROM radgroupreply WHERE groupname=%s AND attribute=%s", (groupname, attribute))
                await inter.followup.send(f"Removed attribute {attribute} from group {groupname}.")
            else:
                await execute("DELETE FROM radgroupreply WHERE groupname=%s", (groupname,))
                await inter.followup.send(f"Removed all replies for group {groupname}.")
        except Exception as e:
            await inter.followup.send(f"Gagal menghapus group reply: {e}")
            return

bot.run(os.getenv("DISCORD_TOKEN"))
