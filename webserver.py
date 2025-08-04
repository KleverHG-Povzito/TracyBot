from flask import Flask
import threading
import os
import asyncio
import sys

# Importa tu bot de Discord desde tu archivo bot.py
# Asegúrate de que 'bot.py' esté en el mismo directorio o en una ruta accesible
from bot import bot as discord_bot_client

app = Flask(__name__)

# Variable para saber si el bot de Discord ya está corriendo
discord_bot_running = False

@app.route('/')
def home():
    """Ruta principal para la verificación de estado del servicio."""
    global discord_bot_running
    if discord_bot_running:
        return "Discord Bot is running and Flask server is active!", 200
    else:
        return "Flask server is active, attempting to start Discord Bot...", 200

def run_flask_app():
    """Inicia la aplicación Flask."""
    port = int(os.environ.get('PORT', 8080)) # Render asigna el puerto en la variable de entorno PORT
    app.run(host='0.0.0.0', port=port)

def run_discord_bot():
    """Inicia el bot de Discord en un bucle de eventos asíncrono."""
    global discord_bot_running
    try:
        # Aquí es donde realmente ejecutas tu bot de Discord.
        # discord_bot_client ya es la instancia de tu bot.
        discord_bot_client.run(os.getenv('DISCORD_TOKEN'))
        discord_bot_running = True # Marca que el bot se inició correctamente
    except Exception as e:
        print(f"Error al iniciar el bot de Discord: {e}", file=sys.stderr)
        discord_bot_running = False

if __name__ == '__main__':
    # Inicia la aplicación Flask en un hilo separado
    # Esto permite que el hilo principal se use para el bot de Discord
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True # Esto asegura que el hilo de Flask se cierre si el programa principal se cierra
    flask_thread.start()

    # Inicia el bot de Discord directamente en el hilo principal
    run_discord_bot()