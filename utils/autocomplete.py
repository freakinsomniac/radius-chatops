import re
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
        query = """
            SELECT DISTINCT groupname FROM (
                SELECT groupname FROM radusergroup WHERE groupname LIKE %s
                UNION
                SELECT groupname FROM radgroupreply WHERE groupname LIKE %s
                UNION
                SELECT groupname FROM radgroupcheck WHERE groupname LIKE %s
            ) AS groups ORDER BY groupname LIMIT 25
        """
        search_term = f"{user_input}%"
        rows = await fetch(query, (search_term, search_term, search_term))
        return [r['groupname'] for r in rows] if rows else []
    except Exception:
        return []


async def attribute_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        query = """
            SELECT DISTINCT attribute FROM (
                SELECT attribute FROM radgroupreply WHERE attribute LIKE %s
                UNION
                SELECT attribute FROM radgroupcheck WHERE attribute LIKE %s
                UNION
                SELECT attribute FROM radcheck WHERE attribute LIKE %s
                UNION
                SELECT attribute FROM radreply WHERE attribute LIKE %s
            ) AS attrs ORDER BY attribute LIMIT 25
        """
        search_term = f"{user_input}%"
        rows = await fetch(query, (search_term, search_term, search_term, search_term))
        return [r['attribute'] for r in rows] if rows else []
    except Exception:
        return []


async def operator_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    operators = [":=", "=", "!=", ">", ">=", "<", "<=", "=~", "!~", "=="]
    return [op for op in operators if op.startswith(user_input)]


async def nasname_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        rows = await fetch(
            "SELECT nasname, shortname FROM nas WHERE nasname LIKE %s ORDER BY nasname LIMIT 25",
            (f"%{user_input}%",)
        )
        if not rows:
            return []
        result = []
        for r in rows:
            nasname = r.get('nasname', '')
            shortname = r.get('shortname', '')
            if shortname:
                result.append(f"{nasname} - {shortname}")
            else:
                result.append(nasname)
        return result
    except Exception:
        return []


async def nas_ip_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        if not user_input or user_input.strip() == "":
            rows = await fetch(
                "SELECT DISTINCT nasipaddress FROM radacct WHERE nasipaddress IS NOT NULL ORDER BY nasipaddress LIMIT 25"
            )
        else:
            search_term = f"%{user_input}%"
            rows = await fetch(
                "SELECT DISTINCT nasipaddress FROM radacct WHERE nasipaddress IS NOT NULL AND nasipaddress LIKE %s ORDER BY nasipaddress LIMIT 25",
                (search_term,)
            )
        
        if not rows:
            return []
        
        result = []
        
        nas_map = {}
        try:
            nas_rows = await fetch("SELECT nasname, shortname FROM nas WHERE nasname IS NOT NULL")
            for nas_row in nas_rows:
                nasname = nas_row.get('nasname', '')
                shortname = nas_row.get('shortname', '')
                if nasname and (nasname.count('.') == 3 or '.' in nasname):
                    nas_map[nasname] = shortname or nasname
        except Exception as e:
            print(f"Error fetching NAS records: {e}")
        
        for r in rows:
            ip = r['nasipaddress']
            nas_name = nas_map.get(ip)
            
            if nas_name:
                result.append(f"{ip} - {nas_name}")
            else:
                result.append(ip)
        
        return result
    except Exception as e:
        print(f"Error in nas_ip_autocomplete: {e}")
        return []


async def group_nas_ip_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    groupname = inter.filled_options.get('groupname')
    if not groupname:
        return await nas_ip_autocomplete(inter, user_input)
    
    groupname = groupname.strip()
    try:
        rows = await fetch(
            "SELECT DISTINCT value FROM radgroupcheck WHERE groupname=%s AND attribute=%s AND value LIKE %s ORDER BY value LIMIT 25",
            (groupname, "NAS-IP-Address", f"%{user_input}%")
        )
        if not rows:
            return []
        
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
        
        result = []
        for r in rows:
            ip = r['value']
            nas_name = nas_map.get(ip)
            if nas_name:
                result.append(f"{ip} - {nas_name}")
            else:
                result.append(ip)
        return result
    except Exception:
        return []


async def user_nas_ip_autocomplete(inter: disnake.ApplicationCommandInteraction, user_input: str):
    username = inter.filled_options.get('username')
    if not username:
        return await nas_ip_autocomplete(inter, user_input)
    
    username = username.strip()
    try:
        rows = await fetch(
            "SELECT DISTINCT value FROM radcheck WHERE username=%s AND attribute=%s AND value LIKE %s ORDER BY value LIMIT 25",
            (username, "NAS-IP-Address", f"%{user_input}%")
        )
        if not rows:
            return []
        
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
        
        result = []
        for r in rows:
            ip = r['value']
            nas_name = nas_map.get(ip)
            if nas_name:
                result.append(f"{ip} - {nas_name}")
            else:
                result.append(ip)
        return result
    except Exception:
        return []
