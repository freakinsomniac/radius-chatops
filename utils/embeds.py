import disnake
from enum import Enum

class ResponseType(Enum):
    SUCCESS = 0x2ecc71
    ERROR = 0xe74c3c
    INFO = 0x3498db
    WARNING = 0xf39c12

def create_embed(title: str, description: str = None, response_type: ResponseType = ResponseType.INFO, fields: list = None):
    embed = disnake.Embed(
        title=title,
        description=description,
        color=response_type.value
    )
    if fields:
        for field in fields:
            name, value, inline = field if len(field) == 3 else (field[0], field[1], False)
            embed.add_field(name=name, value=value, inline=inline)
    return embed

def success_embed(title: str, description: str = None, fields: list = None):
    return create_embed(title, description, ResponseType.SUCCESS, fields)

def error_embed(title: str, description: str = None, fields: list = None):
    return create_embed(title, description, ResponseType.ERROR, fields)

def info_embed(title: str, description: str = None, fields: list = None):
    return create_embed(title, description, ResponseType.INFO, fields)

def warning_embed(title: str, description: str = None, fields: list = None):
    return create_embed(title, description, ResponseType.WARNING, fields)