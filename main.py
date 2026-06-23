# =========================================================================
# 🌟 COMANDO SCRIPT — PUBLICADOR EXCLUSIVO PARA STARBOARD
# =========================================================================
# QUÉ HACE ESTE BOT:
#   Expone el comando slash /embeds (solo para ti). Al ejecutarlo,
#   publica el embed informativo del Starboard en el canal correspondiente.
# =========================================================================

import discord
from discord import app_commands
import os
import sys

ID_SERVIDOR = 1517885569231749240  # Tu ID de servidor
ID_DUEÑO = 1360882776706125874     # Tu ID de usuario

# --- CONFIGURACIÓN DE CANAL ---
ID_CANAL_STARBOARD = 1518814340919328858  # Canal de Starboard

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
MY_GUILD = discord.Object(id=ID_SERVIDOR)

# =========================================================================
# 🎨 CONSTRUCTOR DEL EMBED DE STARBOARD
# =========================================================================

def generar_embed_starboard():
    embed = discord.Embed(
        title="⭐ EL SALÓN DE LA FAMA — STARBOARD",
        description=(
            "Este canal inmortaliza los mejores momentos, memes, códigos o aportes "
            "de la comunidad. Es un espacio curado puramente por ustedes.\n\n"
            "**¿Cómo destacar un mensaje aquí?**\n"
            "1. Encuentra un mensaje que valga la pena guardar en el servidor.\n"
            "2. Reacciona a ese mensaje con el emoji de la estrella: ⭐.\n\n"
            "**📌 Regla de Oro:**\n"
            "Se necesitan un mínimo de **3 estrellas (⭐)** para que el mensaje "
            "sea archivado automáticamente en este canal por el bot.\n\n"
            "*¡Apoya el contenido de tus compañeros y ayuda a construir la memoria del Imperio!*"
        ),
        color=0xFFD60A # Dorado Estrella brillante
    )
    embed.set_footer(text="Starboard — Curación de contenido comunitaria.")
    return embed

# =========================================================================
# ⚙️ EVENTOS Y COMANDO SLASHS
# =========================================================================

@client.event
async def on_ready():
    print(f"🔌 Conectado como {client.user}")
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    print("🏛️ Comando /embeds (Starboard) listo para ejecución manual.")

@tree.command(name="embeds", description="[SOLO DUEÑO] Envía el embed informativo al canal de Starboard.")
async def enviar_embeds(interaction: discord.Interaction):
    # Restricción de seguridad
    if interaction.user.id != ID_DUEÑO:
        await interaction.response.send_message("❌ No tienes autorización para usar esto.", ephemeral=True)
        return

    await interaction.response.send_message("⏳ Publicando interfaz de Starboard...", ephemeral=True)
    
    embed_starboard = generar_embed_starboard()
    
    ch_starboard = client.get_channel(ID_CANAL_STARBOARD)
    if ch_starboard:
        await ch_starboard.send(embed=embed_starboard
