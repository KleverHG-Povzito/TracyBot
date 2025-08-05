from discord import app_commands
import discord
from server_utils.query import query_server, parse_server_info

IMAGE_URL = "https://i.imgur.com/Q2ndpHM.jpeg"

@app_commands.command(name="slots", description="Consulta los slots de un servidor por IP:PORT")
@app_commands.describe(ip_port="IP y puerto del servidor en formato ip:port")
async def slots_command(interaction: discord.Interaction, ip_port: str):
    # Responde de inmediato para evitar el "timeout".
    # Esta es una respuesta temporal que se editará más tarde.
    await interaction.response.defer()

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
    except (ValueError, IndexError):
        msg = " 𝐅𝐨𝐫𝐦𝐚𝐭𝐨 𝐢𝐧𝐜𝐨𝐫𝐫𝐞𝐜𝐭𝐨. 𝐔𝐬𝐚 /slots <ip:port>"
    except Exception as e:
        msg = f" 𝐎𝐜𝐮𝐫𝐫𝐢ó 𝐮𝐧 𝐞𝐫𝐫𝐨𝐫: {e}"

    embed = discord.Embed(description=msg)
    embed.set_image(url=IMAGE_URL) # Asegúrate de que esta URL sea válida
    
    # Usa `followup.send` para enviar la respuesta final después del defer.
    await interaction.followup.send(embed=embed)