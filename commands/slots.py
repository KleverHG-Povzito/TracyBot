from discord import app_commands
import discord
from server_utils.query import query_server, parse_server_info

IMAGE_URL = "https://i.imgur.com/Q2ndpHM.jpeg"  # Cambia esta URL por la imagen que desees

@app_commands.command(name="slots", description="Consulta los slots de un servidor por IP:PORT")
@app_commands.describe(ip_port="IP y puerto del servidor en formato ip:port")
async def slots_command(interaction: discord.Interaction, ip_port: str):
    try:
        ip, port = ip_port.split(":")
        port = int(port)
        data, attempts = query_server(ip, port)
        info = parse_server_info(data)
        if info:
            msg = (
                f"𝐒𝐄𝐑𝐕𝐄𝐑: {info['name']} ({ip}:{port})\n"
                f"𝐉𝐔𝐆𝐀𝐃𝐎𝐑𝐄𝐒: {info['players']}/{info['max_players']}\n"
                f"𝐌𝐀𝐏𝐀: {info['map']}\n"
                f"𝐑𝐄𝐈𝐍𝐓𝐄𝐍𝐓𝐎𝐒: {attempts}"
            )
        else:
            msg = f" 𝐍𝐨 𝐬𝐞 𝐩𝐮𝐝𝐨 𝐨𝐛𝐭𝐞𝐧𝐞𝐫 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐜𝐢ó𝐧 𝐝𝐞𝐥 𝐬𝐞𝐫𝐯𝐢𝐝𝐨𝐫. [玄] 𝐑𝐄𝐈𝐍𝐓𝐄𝐍𝐓𝐎𝐒: {attempts}"
    except Exception:
        msg = " 𝐅𝐨𝐫𝐦𝐚𝐭𝐨 𝐢𝐧𝐜𝐨𝐫𝐫𝐞𝐜𝐭𝐨. 𝐔𝐬𝐚 /slots <ip:port>"
    embed = discord.Embed(description=msg)
    embed.set_image(url="IMAGE_URL")
    await interaction.response.send_message(embed=embed)