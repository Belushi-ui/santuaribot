import discord
from discord.ext import commands

class SantuariBot(commands.Bot):
    def __init__(self):
        # Activamos todos los intents necesarios
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Esto sincroniza el comando de barra /setup_santuari con Discord
        await self.tree.sync()
        print("Comandos sincronizados. ¡Santuari está listo para forjarse!")

bot = SantuariBot()

@bot.event
async def on_ready():
    print(f'Conectado en la terminal como {bot.user} 🏛️')

# ==========================================
# 1. AUTO-REACCIONES PARA CÓDIGO Y DIBUJOS
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Si el mensaje trae imágenes/archivos y está en los canales correctos
    if message.attachments:
        if message.channel.name in ["⌨️・tu-código", "🖌️・tus-dibujos"]:
            await message.add_reaction("👍")
            await message.add_reaction("👎")

# ==========================================
# 2. COMANDO DE CONFIGURACIÓN MAESTRA
# ==========================================
@bot.tree.command(name="setup_santuari", description="Construye todo el servidor, roles y canales desde cero.")
@discord.app_commands.default_permissions(administrator=True)
async def setup_santuari(interaction: discord.Interaction):
    # Avisamos a Discord que el proceso va a tardar más de 3 segundos para que no marque error
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    # --- A. CREACIÓN DE ROLES ---
    # Discord los crea de abajo hacia arriba. Al final de la lista quedan los que tienen más poder.
    roles_a_crear = [
        ("Eventos", 0x2b2d31), ("Avisos", 0x2b2d31), ("Chat muerto", 0x2b2d31),
        ("Hombre cis", 0x2b2d31), ("Mujer cis", 0x2b2d31), ("Transgénero", 0x2b2d31), ("No binarie", 0x2b2d31), ("Otro género", 0x2b2d31),
        ("she/her", 0x2b2d31), ("he/him", 0x2b2d31), ("they/them", 0x2b2d31), ("Otros pronombres", 0x2b2d31),
        ("Gay", 0x2b2d31), ("Lesbiana", 0x2b2d31), ("Bisexual", 0x2b2d31), ("Asexual", 0x2b2d31), ("Arromántico", 0x2b2d31), ("Otra sexualidad", 0x2b2d31),
        ("14-17", 0x2b2d31), ("18-25", 0x2b2d31), ("25+", 0x2b2d31),
        ("Norteamérica", 0x2b2d31), ("Sudamérica", 0x2b2d31), ("Europa", 0x2b2d31), ("Asia", 0x2b2d31),
        ("🎸Arte y filosofía", 0x2b2d31), ("🐉 Rol n Roll", 0x2b2d31), ("🐧Linux & Coding", 0x2b2d31),
        ("Color 10", 0x00BBF9), ("Color 9", 0xFEE440), ("Color 8", 0xF15BB5), ("Color 7", 0x00F5D4), 
        ("Color 6", 0xFF9ED2), ("Color 5", 0x6A4C93), ("Color 4", 0x1982C4), ("Color 3", 0x8AC926), 
        ("Color 2", 0xFFCA3A), ("Color 1", 0xFF595E),
        ("⛓️ Presos políticos", 0x101010), ("Aspirantes", 0xFF8C00), ("Ciudadano", 0x2E8B57), 
        ("Lobby man", 0x800080), ("Ministros", 0x008000), ("Congreso", 0x4169E1), 
        ("Canciller", 0xDC143C), ("Presidente", 0xFFD700)
    ]
    
    creados = {}
    for nombre, color_hex in roles_a_crear:
        # Se crean los roles con sus colores exactos
        rol = await guild.create_role(name=nombre, color=discord.Color(color_hex), reason="Setup Santuari")
        creados[nombre] = rol

    everyone = guild.default_role

    # --- B. CREACIÓN DE CANALES Y CATEGORÍAS ---
    
    # 🏛️ Cancillería
    cat_cancilleria = await guild.create_category("🏛️ Cancillería")
    
    # Permisos para que nadie hable en reglas excepto la Canciller y el Bot
    overwrites_reglas = {
        everyone: discord.PermissionOverwrite(send_messages=False, view_channel=True),
        creados["Canciller"]: discord.PermissionOverwrite(send_messages=True)
    }
    canal_reglas = await cat_cancilleria.create_text_channel("📜・reglas", overwrites=overwrites_reglas)
    await cat_cancilleria.create_text_channel("📖・el-diario-de-la-canciller")
    await cat_cancilleria.create_text_channel("🎫・tickets")
    await cat_cancilleria.create_text_channel("🎨・autoroles")
    
    # 💬 Offtopic
    cat_offtopic = await guild.create_category("💬 Offtopic")
    await cat_offtopic.create_text_channel("👋・presentacion")
    await cat_offtopic.create_text_channel("💬・chat-offtopic")
    await cat_offtopic.create_text_channel("🖼️・media-offtopic")
    await cat_offtopic.create_text_channel("📸・selfies")
    await cat_offtopic.create_text_channel("🫂・venting")
    await cat_offtopic.create_text_channel("😂・memes-offtopic")
    await cat_offtopic.create_text_channel("🪙・economia")

    # 🔊 VC Offtopic
    cat_vc_offtopic = await guild.create_category("🔊 VC Offtopic")
    await cat_vc_offtopic.create_voice_channel("🎮 VC Gaming")
    await cat_vc_offtopic.create_voice_channel("🗣️ VC Charla")
    for i in range(1, 4): await cat_vc_offtopic.create_voice_channel(f"👥 VC Duo {i}", user_limit=2)
    for i in range(1, 3): await cat_vc_offtopic.create_voice_channel(f"👨‍👩‍👦 VC Trio {i}", user_limit=3)

    # 💻 Linux & Coding (Categoría bloqueada con rol)
    overwrites_linux = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        creados["🐧Linux & Coding"]: discord.PermissionOverwrite(view_channel=True)
    }
    cat_linux = await guild.create_category("💻 Linux & Coding", overwrites=overwrites_linux)
    await cat_linux.create_text_channel("🐧・linux-general")
    await cat_linux.create_text_channel("🖼️・linux-media")
    await cat_linux.create_text_channel("🖥️・linux-setup")
    await cat_linux.create_text_channel("😂・linux-coding-memes")
    await cat_linux.create_text_channel("⌨️・tu-código")
    await cat_linux.create_text_channel("🤝・proyectos-comunitarios")

    # 🛠️ VC Asistencia técnica
    cat_vc_asis = await guild.create_category("🛠️ VC Asistencia", overwrites=overwrites_linux)
    for i in range(1, 6): await cat_vc_asis.create_voice_channel(f"🔧 Asistencia {i}")

    # 🐉 Rol n Roll (Categoría bloqueada con rol)
    overwrites_rol = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        creados["🐉 Rol n Roll"]: discord.PermissionOverwrite(view_channel=True)
    }
    cat_rol = await guild.create_category("🐉 Rol n Roll", overwrites=overwrites_rol)
    canal_reglas_rol = await cat_rol.create_text_channel("📜・reglas-rol-n-roll", overwrites=overwrites_reglas)
    await cat_rol.create_text_channel("🎭・presenta-tu-personaje")
    await cat_rol.create_text_channel("🎲・general-rol-n-roll")
    await cat_rol.create_text_channel("🖼️・media-rol-n-roll")
    await cat_rol.create_text_channel("📅・organiza-tu-party")
    await cat_rol.create_text_channel("😂・memes-rol-n-roll")
    await cat_rol.create_text_channel("📚・otros-juegos-de-rol")

    # 🎙️ VC Rol n Roll
    cat_vc_rol = await guild.create_category("🎙️ VC Rol n Roll", overwrites=overwrites_rol)
    for i in range(1, 11): await cat_vc_rol.create_voice_channel(f"🪵 Mesa {i}", user_limit=5)

    # 🎨 Arte y Filosofía (Categoría bloqueada con rol)
    overwrites_arte = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        creados["🎸Arte y filosofía"]: discord.PermissionOverwrite(view_channel=True)
    }
    cat_arte = await guild.create_category("🎨 Arte y Filosofía", overwrites=overwrites_arte)
    await cat_arte.create_text_channel("🎸・general-arte")
    await cat_arte.create_text_channel("🖼️・media-arte")
    await cat_arte.create_text_channel("😂・memes-arte")
    await cat_arte.create_text_channel("📚・tu-biblioteca")
    await cat_arte.create_text_channel("🖌️・tus-dibujos")
    await cat_arte.create_text_channel("🎵・musica")

    # 🎧 VC Arte y filosofía
    cat_vc_arte = await guild.create_category("🎧 VC Arte y filosofía", overwrites=overwrites_arte)
    for i in range(1, 4): await cat_vc_arte.create_voice_channel(f"🎵 Música 3p - {i}", user_limit=3)
    for i in range(1, 3): await cat_vc_arte.create_voice_channel(f"🎵 Música 5p - {i}", user_limit=5)
    for i in range(1, 5): await cat_vc_arte.create_voice_channel(f"🎵 Música 2p - {i}", user_limit=2)
    for i in range(1, 6): await cat_vc_arte.create_voice_channel(f"📖 Lectura 10p - {i}", user_limit=10)
    for i in range(1, 4): await cat_vc_arte.create_voice_channel(f"📖 Lectura 2p - {i}", user_limit=2)

    # --- C. INYECCIÓN DE REGLAS EN EMBEDS ---
    
    embed_reglas = discord.Embed(
        title="🏛️ Constitución de Santuari",
        color=0x1982C4, # Color Azul Zafiro
        description=(
            "**¡Bienvenid@ a la Nación de Santuari!** 🏛️\n"
            "Para mantener la paz y evitar que te enviemos a los **Presos Políticos**, lee nuestra constitución:\n\n"
            "**1. Respeto Total (Cero Tolerancia):** Santuari es un espacio LGBTQ+ friendly. Cualquier comentario de odio, transfobia, homofobia, racismo o acoso resulta en exilio inmediato.\n\n"
            "**2. El Humor es Legal, pero sé inteligente:** El *shitposting*, el sarcasmo y las bromas son bienvenidos en la sección de Offtopic. Pero recuerda: la comedia tiene un límite cuando cruza al acoso personal. Lee la habitación.\n\n"
            "**3. Uso Correcto de Canales:** Los memes van en memes, el código en código. Respeta las secciones de nicho. Prohibido subir contenido +18 o gore bajo ninguna circunstancia.\n\n"
            "**4. El Congreso y los Ministerios:** Las decisiones del *staff* son para mantener el orden. El Lobby man, los Ministros y la Canciller tienen la última palabra.\n\n"
            "**5. Sistema de Tickets:** Si tienes un problema real, abre un ticket. Aunque este servidor sea un caos divertido, **los tickets se toman con absoluta seriedad**. Falsificar o abusar de los tickets es un delito federal."
        )
    )
    await canal_reglas.send(embed=embed_reglas)

    embed_rol_reglas = discord.Embed(
        title="🐉 Leyes de la Taberna (Rol n Roll)",
        color=0xFF595E, # Color Rojo Carmesí
        description=(
            "**1. La Regla de Oro del Consentimiento:** Absolutamente cero romance, incomodidad o dinámicas PvP si el otro jugador no está 100% de acuerdo fuera de personaje (OOC). Si fuerzas situaciones extrañas, tu personaje será devorado por un Tarrasque y tú baneado de la sección.\n\n"
            "**2. La Palabra del DM es Ley:** El Dungeon Master tiene la última palabra sobre las reglas. Si el DM prohíbe una raza rota o impone un nivel, se acata sin discutir.\n\n"
            "**3. Compromiso con la Party:** Si vas a armar una mesa o unirte a una, sé puntual. Avisa si no vas a llegar; no dejes a tus compañeros tirados en la mazmorra.\n\n"
            "**4. Separa Jugador de Personaje:** Lo que pasa en el rol, se queda en el rol. Si mi pícaro le roba a tu paladín, no te enojes conmigo en el canal general."
        )
    )
    await canal_reglas_rol.send(embed=embed_rol_reglas)

    # Finalizar el comando
    await interaction.followup.send("¡El Imperio de Santuari ha sido forjado con éxito! 🏛️✨ Todos los canales, roles y reglas están listos.")

# ¡Pon tu token aquí abajo!
bot.run("MTUxODEzMzM3MjA2MzMxODE2Nw.GVPhGm.JDaB4RjnYNZ_Pv8KJkrv3axIfsYy2aMavNMdU8")
