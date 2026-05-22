import logging
import disnake
from disnake.ext import commands
from database.db import fetch, execute
from utils.embeds import success_embed, error_embed, info_embed, warning_embed
from utils.autocomplete import username_autocomplete, groupname_autocomplete
from utils.exceptions import DuplicateUser, UserNotFound, DatabaseError

logger = logging.getLogger(__name__)


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="users",
        description="Lihat semua user radius"
    )
    async def users(self, inter):
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

    @commands.slash_command(
        name="adduser",
        description="Tambah user radius baru"
    )
    async def adduser(self, inter, username: str, password: str, group: str = commands.Param(default=None, autocomplete=groupname_autocomplete)):
        await inter.response.defer()
        username = username.strip()
        
        try:
            exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
            if exists:
                raise DuplicateUser(f"User `{username}` sudah terdaftar di database")
            
            await execute(
                "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)",
                (username, "Cleartext-Password", ":=", password)
            )
            logger.info(f"User '{username}' berhasil ditambahkan")
            
            try:
                await execute(
                    "INSERT INTO userinfo (username, creationdate, creationby, enableportallogin) VALUES (%s, NOW(), %s, %s)",
                    (username, "discord-bot", 0)
                )
            except:
                pass
            
            fields = [("Username", f"`{username}`", True)]
            if group:
                try:
                    await execute(
                        "INSERT INTO radusergroup (username, groupname) VALUES (%s, %s)",
                        (username, group)
                    )
                    fields.append(("Group", f"`{group}`", True))
                    logger.info(f"User '{username}' ditambahkan ke group '{group}'")
                except DatabaseError as e:
                    logger.error(f"Gagal menambah group: {e}")
                    embed = warning_embed("⚠️ User Dibuat, Group Gagal", "User berhasil dibuat tapi gagal menambah ke group")
                    await inter.followup.send(embed=embed)
                    return
            
            embed = success_embed("✅ User Berhasil Ditambahkan", fields=fields)
            await inter.followup.send(embed=embed)
            
        except DuplicateUser as e:
            logger.warning(f"Duplicate user attempt: {username}")
            embed = warning_embed("⚠️ User Sudah Ada", str(e))
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat adduser: {e}")
            embed = error_embed("❌ Gagal Menambah User", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat adduser: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="deluser",
        description="Hapus user radius"
    )
    async def deluser(self, inter, username: str = commands.Param(autocomplete=username_autocomplete)):
        await inter.response.defer()
        
        try:
            exists = await fetch("SELECT 1 FROM radcheck WHERE username=%s LIMIT 1", (username,))
            if not exists:
                raise UserNotFound(f"User `{username}` tidak ada di database")
            
            await execute("DELETE FROM radcheck WHERE username=%s", (username,))
            await execute("DELETE FROM radusergroup WHERE username=%s", (username,))
            logger.info(f"User '{username}' berhasil dihapus")
            
            embed = success_embed("✅ User Berhasil Dihapus", f"User `{username}` telah dihapus dari database.")
            await inter.followup.send(embed=embed)
            
        except UserNotFound as e:
            logger.warning(f"Delete non-existent user: {username}")
            embed = error_embed("❌ User Tidak Ditemukan", str(e))
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat deluser: {e}")
            embed = error_embed("❌ Gagal Menghapus User", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat deluser: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="changepass",
        description="Ubah password user radius"
    )
    async def changepass(self, inter, username: str = commands.Param(autocomplete=username_autocomplete), new_password: str = None):
        await inter.response.defer()
        
        try:
            rows = await fetch("SELECT id FROM radcheck WHERE username=%s AND attribute=%s", (username, "Cleartext-Password"))
            if not rows:
                raise UserNotFound(f"User `{username}` atau password attribute tidak ditemukan")
            
            await execute(
                "UPDATE radcheck SET value=%s WHERE username=%s AND attribute=%s",
                (new_password, username, "Cleartext-Password")
            )
            logger.info(f"Password untuk user '{username}' berhasil diubah")
            
            embed = success_embed("✅ Password Berhasil Diubah", f"Password untuk user `{username}` telah diperbarui.")
            await inter.followup.send(embed=embed)
            
        except UserNotFound as e:
            logger.warning(f"User not found: {username}")
            embed = error_embed("❌ User Tidak Ditemukan", str(e))
            await inter.followup.send(embed=embed)
            
        except DatabaseError as e:
            logger.error(f"Database error saat changepass: {e}")
            embed = error_embed("❌ Gagal Mengubah Password", "Terjadi kesalahan pada database")
            await inter.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"Unexpected error saat changepass: {e}")
            embed = error_embed("❌ Error", "Terjadi error yang tidak terduga")
            await inter.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(UserCommands(bot))
