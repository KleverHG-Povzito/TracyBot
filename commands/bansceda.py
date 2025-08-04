import discord
from discord import app_commands
import httpx
from bs4 import BeautifulSoup

IMAGE_URL = "https://i.imgur.com/Q2ndpHM.jpeg"  # Usa la misma imagen que en steamid

@app_commands.command(name="ceda", description="Consulta los bans de cedapug.com por SteamID64")
@app_commands.describe(steamid="SteamID64 del usuario")
async def bansceda_command(interaction: discord.Interaction, steamid: str):
    await interaction.response.defer()
    url = f"https://cedapug.com/bans?SteamId={steamid}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
        if response.status_code != 200:
            await interaction.followup.send("No se pudo acceder a la página de CEDA.")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        ban_lines = soup.find_all("div", class_="ban-line")
        if not ban_lines:
            await interaction.followup.send("No se encontraron registros de bans para ese SteamID.")
            return

        ultimos_bans = ban_lines[:3]
        mensajes = []
        for ban in ultimos_bans:
            name = ban.find("div", class_="ban-name")
            steamid_div = ban.find("div", class_="ban-steamid")
            ban_times = ban.find_all("div", class_="ban-time")
            start = ban_times[0] if len(ban_times) > 0 else None
            end = ban_times[1] if len(ban_times) > 1 else None
            reason = ban.find("div", class_="ban-reason")
            banned_by = ban.find_all("div", class_="ban-steamid")[1] if len(ban.find_all("div", class_="ban-steamid")) > 1 else None

            msg = []
            if name:
                msg.append(f"**Nombre:** {name.find_all('div')[1].text.strip()}")
            if steamid_div:
                msg.append(f"**SteamId:** {steamid_div.find_all('div')[1].text.strip()}")
            if start:
                msg.append(f"**Inicio:** {start.find_all('div')[1].text.strip()}")
            if end:
                msg.append(f"**Fin:** {end.find_all('div')[1].text.strip()}")
            if reason:
                msg.append(f"**Razón:** {reason.find_all('div')[1].text.strip()}")
            if banned_by:
                msg.append(f"**Baneado por:** {banned_by.find_all('div')[1].text.strip()}")
            mensajes.append("\n".join(msg))

        texto_final = "\n____________________________________\n".join(mensajes)
        if not texto_final:
            texto_final = "No se encontraron registros de bans para ese SteamID."
        if len(texto_final) > 1990:
            texto_final = texto_final[:1990] + "\n..."

        embed = discord.Embed(
            title=f"Bans de CEDA para SteamID {steamid}",
            description=texto_final,
            color=discord.Color.red()
        )
        embed.set_image(url=IMAGE_URL)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Ocurrió un error: {e}")
