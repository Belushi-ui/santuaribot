# =========================================================================
# 🖼️ COMANDO SCRIPT — PUBLICADOR DE EMBEDS ESTÉTICOS Y AUTOROLES
# =========================================================================
# QUÉ HACE ESTE BOT:
#   Expone un único comando slash /embeds, ejecutable SOLO por el dueño.
#   Al activarse, genera e inyecta todos los embeds de reglas, votaciones
#   y los bloques separados de autoroles en sus respectivos canales.
# =========================================================================

import discord
from discord import app_commands
import os
import sys

ID_SERVIDOR = 1517885569231749240  # Tu ID de servidor
ID_DUEÑO = 1360882776706125874     # Tu ID de usuario

# --- CONFIGURACIÓN DE CANALES ---
ID_CANAL_REGLAS = 1518762621937909862
ID_CANAL_REGLAS_MESA = 1518762659875393577
ID_CANAL_VOTAR_CODIGOS = 1518762651134591108
ID_CANAL_VOTAR_DIBUJOS = 1518762681367138436
ID_CANAL_AUTOROLES = 1518804287835345198  # Central de autoroles

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
MY_GUILD = discord.Object(id=ID_SERVIDOR)

# =========================================================================
# 🎨 CONSTRUCTOR DE EMBEDS
# =========================================================================

def generar_embeds():
    embeds_dict = {}

    # 1. Embed de Reglas Generales
    reglas = discord.Embed(
        title="Edictos del Imperio",
        description=(
            "Bienvenido al Imperio. Para mantener el orden entre las estrellas y las eras, "
            "todos los Habitantes deben acatar las siguientes directrices. El desconocimiento de las leyes "
            "no exime de su cumplimiento.\n\n"
            "**1. Respeto Absoluto (Código del Consejo)**\n"
            "Queda estrictamente prohibido el acoso, la discriminación, los discursos de odio o la toxicidad, este es un espacio pro LGBTQIA+, la comedia es legal pero debes aprender a leer la habitacion. "
            "Trata a los demás con la dignidad de un Espectro.\n\n"
            "**2. Contenido Temático y Canales**\n"
            "Mantén las conversaciones en sus secciones correspondientes. No inundes los canales técnicos o de rol "
            "con temas ajenos a ellos.\n\n"
            "**3. Menciones y Pings**\n"
            "No abuses de los pings al staff o a otros usuarios. Las menciones masivas están severamente restringidas.\n\n"
            "**4. Cuentas y Seguridad**\n"
            "Se prohíbe el spam, los enlaces maliciosos, el contenido ilegal o la distribución de software malicioso. "
            "Cualquier intento de sabotaje resultará en un ban irreversible."
        ),
        color=0x9B1C1C # Rojo Inquisidor
    )
    reglas.set_footer(text="Protección Civil — El Imperio vela por ti.")
    embeds_dict["reglas"] = reglas

    # 2. Embed de Reglas de Mesa
    mesa = discord.Embed(
        title="Código de la Taberna",
        description=(
            "Para que las crónicas y campañas fluyan en armonía, tanto los Dungeon Masters como los jugadores "
            "deben respetar el código de juego limpio en nuestras mesas:\n\n"
            "**1. Compromiso y Puntualidad**\n"
            "Si te apuntas a una partida, asiste. Avisa con un mínimo de 24 horas de anticipación si no puedes ir. "
            "El tiempo del DM y de tus compañeros vale oro.\n\n"
            "**2. Respeto a las Decisiones del DM**\n"
            "La palabra del Dungeon Master es la ley final en la mesa. Las disputas sobre reglas se discuten *después* "
            "de la sesión, de forma madura y privada.\n\n"
            "**3. Metajuego y Powergaming**\n"
            "Separa lo que sabes tú como jugador de lo que sabe tu personaje. Juega para contar una historia colectiva, "
            "no para 'ganar' el rol.\n\n"
            "**4. Límites y Seguridad (Líneas y Velos)**\n"
            "Respeta los temas sensibles marcados por la mesa. El rol debe ser un espacio seguro y divertido para todos."
        ),
        color=0x6B4C9A # Morado de El Círculo
    )
    mesa.set_footer(text="Rol & Roll — Que los dados decidan tu destino.")
    embeds_dict["mesa"] = mesa

    # 3. Embed Votar Códigos
    votar_codigos = discord.Embed(
        title="Control de Versiones",
        description=(
            "¡Es hora de elegir el script más eficiente, elegante o ingenioso de la comunidad!\n\n"
            "**¿Cómo votar?**\n"
            "1. Sube tu propuesta o revisa las que están publicadas en el canal correspondiente.\n"
            "2. Utiliza las reacciones habilitadas abajo en cada mensaje para emitir tu voto.\n\n"
            "🏆 *El código ganador recibirá reconocimiento en los logs y estatus especial.*"
        ),
        color=0x3D5A80 # Azul Zafiro / Tecnológico
    )
    votar_codigos.set_footer(text="Compilando el orden del servidor.")
    embeds_dict["votar_codigos"] = votar_codigos

    # 4. Embed Votar Dibujos
    votar_dibujos = discord.Embed(
        title="Galería de Arte",
        description=(
            "El talento del Imperio expuesto ante los ojos de la comunidad. Apoya a nuestros artistas locales:\n\n"
            "**¿Cómo votar?**\n"
            "1. Observa las obras publicadas en esta sección.\n"
            "2. Reacciona con los emojis correspondientes en la publicación que más te inspire.\n\n"
            "✨ *Fomenta la crítica constructiva y apoya el arte sin menospreciar el trabajo de nadie.*"
        ),
        color=0xFFD60A # Dorado
    )
    votar_dibujos.set_footer(text="La cultura es el pilar de nuestra era.")
    embeds_dict["votar_dibujos"] = votar_dibujos

    # --- 5. BLOQUES SEPARADOS DE AUTOROLES ---
    autoroles = []

    gen = discord.Embed(title="🧬 Identidad de Género", description="Selecciona tu identidad para la base de datos del servidor:\n\n• Hombre\n• Mujer\n• Transgénero\n• No binarie\n• Otro género", color=0x95A5A6)
    autoroles.append(gen)

    prn = discord.Embed(title="💬 Pronombres", description="Elige cómo prefieres que se refieran a ti en las interacciones:\n\n• She/Her\n• He/Him\n• They/Them\n• Otros pronombres", color=0x95A5A6)
    autoroles.append(prn)

    reg = discord.Embed(title="🌍 Ubicación Geográfica", description="Dinos desde qué rincón del mundo te conectas al Imperio:\n\n• Norteamérica\n• Sudamérica\n• Europa\n• Asia", color=0x95A5A6)
    autoroles.append(reg)

    sex = discord.Embed(title="🌈 Orientación", description="Define tus roles de orientación si deseas compartirlos con el sector de comunidad:\n\n• Heterosexual\n• Lesbiana\n• Bisexual\n• Gay\n• Asexual\n• Alosexual\n• Arromántico\n• Otra sexualidad", color=0x95A5A6)
    autoroles.append(sex)

    edad = discord.Embed(title="🎂 Grupo de Edad", description="Selecciona tu rango de edad para organizar actividades acordes:\n\n• 14-17\n• 18-25\n• 26+", color=0x95A5A6)
    autoroles.append(edad)

    nichos = discord.Embed(title="⚔️ Sectores de Interés", description="Desbloquea el acceso a las facciones exclusivas del servidor:\n\n• **Linux & Coding**: Entornos Unix, desarrollo y scripts.\n• **Arte y Filosofía**: Espacio cultural, música y debates.\n• **Rol n Roll**: Mesas de rol, manuales y dados.", color=0x95A5A6)
    autoroles.append(nichos)

    ocu = discord.Embed(title="🛠️ Oficios y Especializaciones", description="¿A qué te dedicas dentro o fuera del Imperio?:\n\n• Artista\n• Programador\n• Dungeon Master\n• Seudo Filósofo\n• Politólogo", color=0x95A5A6)
    autoroles.append(ocu)

    colores = discord.Embed(title="🎨 Paleta de Colores", description="Elige el pigmento con el que se mostrará tu nombre en la lista de ciudadanos:\n\n• Carmesí\n• Ámbar\n• Dorado\n• Esmeralda\n• Zafiro\n• Amatista\n• Rosa\n• Marfil\n• Obsidiana\n• Celeste", color=0xF1FAEE)
    autoroles.append(colores)

    embeds_dict["autoroles"] = autoroles
    return embeds_dict

# =========================================================================
# ⚙️ EVENTOS Y COMANDO SLASHS
# =========================================================================

@client.event
async def on_ready():
    print(f"🔌 Conectado como {client.user}")
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    print("🏛️ Comando /embeds listo para ejecución manual.")

@tree.command(name="embeds", description="[SOLO DUEÑO] Envía de forma masiva los embeds de diseño y autoroles.")
async def enviar_embeds(interaction: discord.Interaction):
    # Restricción dura de seguridad
    if interaction.user.id != ID_DUEÑO:
        await interaction.response.send_message("❌ No tienes autorización para usar esto.", ephemeral=True)
        return

    await interaction.response.send_message("⏳ Procesando e inyectando interfaces visuales...", ephemeral=True)
    
    data = generar_embeds()
    
    # 1. Reglas
    ch_reglas = client.get_channel(ID_CANAL_REGLAS)
    if ch_reglas: await ch_reglas.send(embed=data["reglas"])

    # 2. Reglas de Mesa
    ch_mesa = client.get_channel(ID_CANAL_REGLAS_MESA)
    if ch_mesa: await ch_mesa.send(embed=data["mesa"])

    # 3. Votar Códigos
    ch_vc = client.get_channel(ID_CANAL_VOTAR_CODIGOS)
    if ch_vc: await ch_vc.send(embed=data["votar_codigos"])

    # 4. Votar Dibujos
    ch_vd = client.get_channel(ID_CANAL_VOTAR_DIBUJOS)
    if ch_vd: await ch_vd.send(embed=data["votar_dibujos"])

    # 5. Autoroles divididos
    ch_auto = client.get_channel(ID_CANAL_AUTOROLES)
    if ch_auto:
        await ch_auto.send("🏛️ **CENTRAL DE ASIGNACIÓN DE IDENTIDAD Y ROLES**\n*Por favor, examina los siguientes módulos informativos de personalización.*")
        for embed_bloque in data["autoroles"]:
            await ch_auto.send(embed=embed_bloque)

    await interaction.followup.send("✅ ¡Todos los embeds estéticos han sido publicados en sus canales!", ephemeral=True)

def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: Falta DISCORD_TOKEN.")
        sys.exit(1)
    client.run(token)

if __name__ == "__main__":
    main()
