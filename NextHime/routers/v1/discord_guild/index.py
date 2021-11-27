from fastapi import APIRouter
from fastapi_versioning import versioned_api_route

from NextHime.main import bot

router = APIRouter(route_class=versioned_api_route(1))


@router.get("/")
async def index() -> dict:
    """Topページ"""
    return {"body": {"type": "text", "text": "Welcome to the API Version 1"}}


@router.get("/guild_info/{server_id}")
async def server_info(server_id: int) -> dict:
    """与えられたサーバーIDからサーバーの基本情報を返します"""
    guild = bot.get_guild(server_id)
    admin_list = []
    for member in guild.members:
        if member.guild_permissions.administrator:
            admin_list.append({
                f"{member}": {
                    "id": f"{member.id}",
                    "name": f"{member.name}"
                }
            })
        print(f"{member} {member.guild_permissions.administrator}")
    return {
        "result": {
            "type": "success",
            "guild": {
                "name": f"{guild.name}",
                "id": f"{guild.id}",
                "owner": {
                    "name": f"{guild.owner.name}",
                    "id": f"{guild.owner.id}"
                },
                "operators": admin_list,
            },
        }
    }
