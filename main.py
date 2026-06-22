import discord
from discord import app_commands
import os

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print("Limpiando comandos globales...")
    tree.clear_commands(guild=None)
    await tree.sync()
    print(" Comandos globales borrados.")
    await client.close()

token = os.environ.get("DISCORD_TOKEN")
client.run(token)
