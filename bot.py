import discord
from discord import app_commands
import os
from commands.slots import slots_command
from commands.vacios import vacios_command
from commands.steamid import steamid_command
from commands.bansceda import bansceda_command

# No necesitamos DISCORD_TOKEN aquí, ya que webserver.py lo obtendrá y pasará a bot.run()
# DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") # <-- Esta línea ya no es necesaria aquí si webserver.py lo pasa

intents = discord.Intents.default()
intents.message_content = True

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Asegúrate de que estos comandos estén definidos en tus archivos
        self.tree.add_command(slots_command)
        self.tree.add_command(vacios_command)
        self.tree.add_command(steamid_command)
        self.tree.add_command(bansceda_command)
        print("🤖 Comandos añadidos al árbol.") # Mensaje para depuración

bot = MyBot() # Instancia global de tu bot

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    try:
        # Solo sincronizamos una vez al iniciar
        synced = await bot.tree.sync() # Sincroniza comandos globales
        print(f"🔄 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

