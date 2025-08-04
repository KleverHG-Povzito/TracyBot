from discord import app_commands
import discord
from config import SERVIDORES
from server_utils.query import query_server, parse_server_info
from server_utils.filter import vacios
import asyncio

IMAGE_URL = "https://i.imgur.com/Q2ndpHM.jpeg"  # Cambia esto por la URL de la imagen que prefieras

async def get_server_info(s):
    loop = asyncio.get_running_loop()
    data, _ = await loop.run_in_executor(None, query_server, s["ip"], s["port"])
    info = parse_server_info(data)
    if info:
        info["ip"] = s["ip"]
        info["port"] = s["port"]
        return info
    return None

@app_commands.command(name="vacios", description="Muestra los servidores vacíos")
async def vacios_command(interaction: discord.Interaction):
    await interaction.response.defer()
    tasks = [get_server_info(s) for s in SERVIDORES]
    servidores_info = [info for info in await asyncio.gather(*tasks) if info]
    vacios_list = vacios(servidores_info)
    embed = discord.Embed(title="Servidores Vacíos", color=discord.Color.blue())
    embed.set_image(url=IMAGE_URL)
    if vacios_list:
        msg = "\n".join([
            f"𝐒𝐄𝐑𝐕𝐄𝐑 {i+1}: {s['name']} ({s['ip']}:{s['port']}) - 𝐒𝐋𝐎𝐓𝐒: {s['players']}/{s['max_players']}"
            for i, s in enumerate(vacios_list)
        ])
        embed.description = msg
        await interaction.followup.send(embed=embed)
    else:
        embed.description = "𝐍𝐨 𝐡𝐚𝐲 𝐬𝐞𝐫𝐯𝐢𝐝𝐨𝐫𝐞𝐬 𝐯𝐚𝐜í𝐨𝐬."
        await interaction.followup.send(embed=embed)
