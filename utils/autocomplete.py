from disnake.ext import commands
import disnake
from database.db import fetch


async def username_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        rows = await fetch("SELECT DISTINCT username FROM radcheck WHERE username LIKE %s ORDER BY username LIMIT 25", (f"{user_input}%",))
        return [r['username'] for r in rows] if rows else []
    except Exception:
        return []


async def groupname_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        rows = await fetch("SELECT DISTINCT groupname FROM radusergroup WHERE groupname LIKE %s ORDER BY groupname LIMIT 25", (f"{user_input}%",))
        return [r['groupname'] for r in rows] if rows else []
    except Exception:
        return []


async def attribute_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        rows = await fetch("SELECT DISTINCT attribute FROM radgroupreply WHERE attribute LIKE %s ORDER BY attribute LIMIT 25", (f"{user_input}%",))
        return [r['attribute'] for r in rows] if rows else []
    except Exception:
        return []


async def operator_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    operators = [":=", "=", "!=", ">", ">=", "<", "<=", "=~", "!~", "=="]
    return [op for op in operators if op.startswith(user_input)]