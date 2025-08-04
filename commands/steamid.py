import discord
from discord import app_commands
import httpx
import re

STEAM_API_KEY = "E6B3CE692625C45E7F188478FFA4CA4B"

def steamid32_to_steamid64(steamid32):
    # STEAM_X:Y:Z → steamid64
    parts = steamid32.split(":")
    if len(parts) == 3:
        Y = int(parts[1])
        Z = int(parts[2])
        return str(76561197960265728 + Z * 2 + Y)
    return None

def steamid3_to_steamid64(steamid3):
    # [U:1:XXXXXX] → steamid64
    match = re.match(r"\[U:1:(\d+)\]", steamid3)
    if match:
        account_id = int(match.group(1))
        return str(account_id + 76561197960265728)
    return None

def extract_steamid(input_str):
    # Quita espacios y normaliza
    input_str = input_str.strip()
    # URL de perfil
    match = re.search(r"steamcommunity\.com/(id|profiles)/([^/]+)", input_str)
    if match:
        tipo, valor = match.groups()
        if tipo == "profiles" and valor.isdigit() and len(valor) == 17:
            return valor
        else:
            return valor  # vanity
    # SteamID64
    if input_str.isdigit() and len(input_str) == 17:
        return input_str
    # SteamID32
    match = re.match(r"STEAM_[0-5]:[01]:\d+", input_str)
    if match:
        steamid64 = steamid32_to_steamid64(input_str)
        if steamid64:
            return steamid64
    # SteamID3
    match = re.match(r"\[U:1:\d+\]", input_str)
    if match:
        steamid64 = steamid3_to_steamid64(input_str)
        if steamid64:
            return steamid64
    # Vanity
    if re.match(r"^[a-zA-Z0-9_-]{2,32}$", input_str):
        return input_str
    return input_str

async def resolve_vanity(client, vanity):
    url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={vanity}"
    resp = await client.get(url)
    data = resp.json()
    if data["response"].get("success") == 1:
        return data["response"].get("steamid")
    return None

async def get_player_summary(client, steamid):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid}"
    resp = await client.get(url)
    data = resp.json()
    players = data.get("response", {}).get("players", [])
    return players[0] if players else None

@app_commands.command(name="steamid", description="Obtiene información de Steam de un usuario por URL o ID")
@app_commands.describe(usuario="URL de perfil de Steam, SteamID64, SteamID32, SteamID3 o vanity")
async def steamid_command(interaction: discord.Interaction, usuario: str):
    await interaction.response.defer()
    async with httpx.AsyncClient(timeout=10) as client:
        steamid = extract_steamid(usuario)
        # Si no es un steamid64, intenta resolverlo como vanity
        if not (steamid.isdigit() and len(steamid) == 17):
            resolved = await resolve_vanity(client, steamid)
            if not resolved:
                await interaction.followup.send("𝐍𝐨 𝐬𝐞 𝐩𝐮𝐝𝐨 𝐫𝐞𝐬𝐨𝐥𝐯𝐞𝐫 𝐞𝐥 SteamID.")
                return
            steamid = resolved

        player = await get_player_summary(client, steamid)
        if not player:
            await interaction.followup.send("𝐍𝐨 𝐬𝐞 𝐞𝐧𝐜𝐨𝐧𝐭𝐫𝐨́ 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐜𝐢𝐨́𝐧 𝐩𝐚𝐫𝐚 𝐞𝐬𝐞 𝐮𝐬𝐮𝐚𝐫𝐢𝐨.")
            return

        estado = {
            0: "Desconectado",
            1: "Conectado",
            2: "Ocupado",
            3: "Ausente",
            4: "Quiere intercambiar",
            5: "Quiere jugar",
            6: "Usando Steam desde móvil"
        }.get(player.get("personastate", 0), "Desconocido")

        embed = discord.Embed(
            title=player.get("personaname", "Sin nombre"),
            url=player.get("profileurl", ""),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=player.get("avatarfull", ""))
        embed.add_field(name="𝐒𝐭𝐞𝐚𝐦𝐈𝐃𝟔𝟒", value=player.get("steamid", "N/A"), inline=False)
        embed.add_field(name="𝐄𝐬𝐭𝐚𝐝𝐨", value=estado, inline=True)
        embed.add_field(name="𝐏𝐚𝐢́𝐬", value=player.get("loccountrycode", "Desconocido"), inline=True)
        embed.add_field(name="𝐔𝐬𝐚𝐫𝐢𝐨 𝐒𝐭𝐞𝐚𝐦", value=player.get("personaname", "N/A"), inline=False)
        embed.add_field(name="𝐏𝐞𝐫𝐟𝐢𝐥", value=f"[Ver perfil]({player.get('profileurl', '')})", inline=False)
        await interaction.followup.send(embed=embed)
