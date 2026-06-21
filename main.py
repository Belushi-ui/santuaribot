import discord
from discord.ext import commands
from discord import app_commands
import asyncio

AUTOROLE_MESSAGE_IDS = {}

class SantuariBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("[INFO] Comandos sincronizados. ¡El Nuevo Orden está listo!")

bot = SantuariBot()

@bot.event
async def on_ready():
    print(f'[INFO] Conectado como {bot.user} 🏛️')

# ==========================================
# 1. AUTO-REACCIONES Y STARBOARD
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.attachments and message.channel.name in ["⌨️・tu-código", "🖌️・tus-dibujos"]:
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id: return
    if payload.message_id in AUTOROLE_MESSAGE_IDS:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji_str = str(payload.emoji)
        if emoji_str in AUTOROLE_MESSAGE_IDS[payload.message_id]:
            nombre_rol = AUTOROLE_MESSAGE_IDS[payload.message_id][emoji_str]
            rol = discord.utils.get(guild.roles, name=nombre_rol)
            if rol: await member.add_roles(rol)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in AUTOROLE_MESSAGE_IDS:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji_str = str(payload.emoji)
        if emoji_str in AUTOROLE_MESSAGE_IDS[payload.message_id]:
            nombre_rol = AUTOROLE_MESSAGE_IDS[payload.message_id][emoji_str]
            rol = discord.utils.get(guild.roles, name=nombre_rol)
            if rol: await member.remove_roles(rol)

# ==========================================
# 2. COMANDO DEL APOCALIPSIS Y GÉNESIS
# ==========================================
@bot.tree.command(name="setup_santuari", description="Purga absoluta y reconstrucción tipográfica del Imperio.")
@discord.app_commands.default_permissions(administrator=True)
async def setup_santuari(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    try:
        await interaction.followup.send("⚠️ **Iniciando el Apocalipsis de Santuari. Borrando toda existencia previa...** ⚙️", ephemeral=True)
    except: pass

    # --- A. PURGA TOTAL DE CANALES ---
    nombres_categorias = ["🏛️ Cancillería", "📖 El Manifiesto", "💬 Offtopic", "🔊 VC Offtopic", "💻 Linux & Coding", "🛠️ VC Asistencia", "🐉 Rol n Roll", "🎙️ VC Rol n Roll", "🎨 Arte y Filosofía", "🎧 VC Arte y filosofía", "👁️ Congreso VIP", "📁 Logs & Brigada"]
    for cat in guild.categories:
        if cat.name in nombres_categorias:
            for ch in cat.channels: 
                try: await ch.delete()
                except: pass
            try: await cat.delete()
            except: pass

    # --- B. PURGA TOTAL DE ROLES ---
    for rol in guild.roles:
        # No borrar @everyone, roles de bots o integraciones de Twitch/Patreon
        if rol.name != "@everyone" and not rol.is_bot_managed() and not rol.is_premium_subscriber() and not rol.is_integration():
            try: await rol.delete()
            except: pass

    # --- C. CREACIÓN DE ROLES (Tipografía 𝔻𝕠𝕓𝕝𝕖 𝕊𝕥𝕣𝕚𝕜𝕖 y Emojis) ---
    roles_base = [
        ("🆕 ℝ𝕖𝕔𝕚𝕖𝕟 𝔸𝕣𝕣𝕚𝕓𝕒𝕕𝕠", 0x808080),
        ("📅 𝔼𝕧𝕖𝕟𝕥𝕠𝕤", 0x2b2d31), ("🔔 𝔸𝕧𝕚𝕤𝕠𝕤", 0x2b2d31), ("💀 ℂ𝕙𝕒𝕥 𝕄𝕦𝕖𝕣𝕥𝕠", 0x2b2d31),
        
        # Identidad
        ("♂️ ℍ𝕠𝕞𝕓𝕣𝕖 𝕔𝕚𝕤", 0x2b2d31), ("♀️ 𝕄𝕦𝕛𝕖𝕣 𝕔𝕚𝕤", 0x2b2d31), ("🏳️‍⚧️ 𝕋𝕣𝕒𝕟𝕤𝕘𝕖𝕟𝕖𝕣𝕠", 0x2b2d31), ("👽 ℕ𝕠 𝕓𝕚𝕟𝕒𝕣𝕚𝕖", 0x2b2d31), ("🌀 𝕆𝕥𝕣𝕠 𝕘𝕖𝕟𝕖𝕣𝕠", 0x2b2d31),
        ("📖 𝕤𝕙𝕖/𝕙𝕖𝕣", 0x2b2d31), ("📘 𝕙𝕖/𝕙𝕚𝕞", 0x2b2d31), ("📗 𝕥𝕙𝕖𝕪/𝕥𝕙𝕖𝕞", 0x2b2d31), ("📔 𝕆𝕥𝕣𝕠𝕤 𝕡𝕣𝕠𝕟𝕠𝕞𝕓𝕣𝕖𝕤", 0x2b2d31),
        ("🌈 𝔾𝕒𝕪", 0x2b2d31), ("🌸 𝕃𝕖𝕤𝕓𝕚𝕒𝕟𝕒", 0x2b2d31), ("💜 𝔹𝕚𝕤𝕖𝕩𝕦𝕒𝕝", 0x2b2d31), ("🖤 𝔸𝕤𝕖𝕩𝕦𝕒𝕝", 0x2b2d31), ("🤍 𝔸𝕣𝕣𝕠𝕞𝕒𝕟𝕥𝕚𝕔𝕠", 0x2b2d31), ("✨ 𝕆𝕥𝕣𝕒 𝕤𝕖𝕩𝕦𝕒𝕝𝕚𝕕𝕒𝕕", 0x2b2d31),
        
        # Edades y Regiones
        ("🎒 𝟙𝟜-𝟙𝟟", 0x2b2d31), ("🎓 𝟙𝟠-𝟚𝟝", 0x2b2d31), ("🍷 𝟚𝟝+", 0x2b2d31),
        ("🦅 ℕ𝕠𝕣𝕥𝕖𝕒𝕞𝕖𝕣𝕚𝕔𝕒", 0x2b2d31), ("🦙 𝕊𝕦𝕕𝕒𝕞𝕖𝕣𝕚𝕔𝕒", 0x2b2d31), ("🏰 𝔼𝕦𝕣𝕠𝕡𝕒", 0x2b2d31), ("🐉 𝔸𝕤𝕚𝕒", 0x2b2d31),
        
        # Nichos
        ("🎸 𝔸𝕣𝕥𝕖 𝕪 𝔽𝕚𝕝𝕠𝕤𝕠𝕗𝕚𝕒", 0x2b2d31), ("🎲 ℝ𝕠𝕝 𝕟 ℝ𝕠𝕝𝕝", 0x2b2d31), ("🐧 𝕃𝕚𝕟𝕦𝕩 & ℂ𝕠𝕕𝕚𝕟𝕘", 0x2b2d31),
        
        # Colores Estéticos
        ("💖 ℂ𝕠𝕝𝕠𝕣 𝟙𝟘", 0x00BBF9), ("🤍 ℂ𝕠𝕝𝕠𝕣 𝟡", 0xFEE440), ("⚫ ℂ𝕠𝕝𝕠𝕣 𝟠", 0xF15BB5), ("🟤 ℂ𝕠𝕝𝕠𝕣 𝟟", 0x00F5D4), 
        ("🟣 ℂ𝕠𝕝𝕠𝕣 𝟞", 0xFF9ED2), ("🔵 ℂ𝕠𝕝𝕠𝕣 𝟝", 0x6A4C93), ("🟢 ℂ𝕠𝕝𝕠𝕣 𝟜", 0x1982C4), ("🟡 ℂ𝕠𝕝𝕠𝕣 𝟛", 0x8AC926), 
        ("🟠 ℂ𝕠𝕝𝕠𝕣 𝟚", 0xFFCA3A), ("🔴 ℂ𝕠𝕝𝕠𝕣 𝟙", 0xFF595E),
        
        ("⛓️ ℙ𝕣𝕖𝕤𝕠𝕤 ℙ𝕠𝕝𝕚𝕥𝕚𝕔𝕠𝕤", 0x101010)
    ]
    
    nombres_niveles = {
        5: ("🟢 ℕ𝕚𝕧𝕖𝕝 𝟝: ℝ𝕖𝕤𝕚𝕕𝕖𝕟𝕥𝕖", 0x00FA9A),
        10: ("🟢 ℕ𝕚𝕧𝕖𝕝 𝟙𝟘: 𝕀𝕟𝕤𝕡𝕖𝕔𝕥𝕠𝕣", 0x00FA9A),
        20: ("🟢 ℕ𝕚𝕧𝕖𝕝 𝟚𝟘: 𝔹𝕦𝕣𝕠𝕔𝕣𝕒𝕥𝕒", 0x00FA9A),
        30: ("🟢 ℕ𝕚𝕧𝕖𝕝 𝟛𝟘: 𝕆𝕗𝕚𝕔𝕚𝕟𝕚𝕤𝕥𝕒", 0x00FA9A),
        40: ("🟢 ℕ𝕚𝕧𝕖𝕝 𝟜𝟘: 𝕍𝕠𝕫 ℂ𝕚𝕧𝕚𝕔𝕒", 0x00FA9A),
        50: ("🟢 ℕ𝕚𝕧𝕖𝕝 𝟝𝟘: ℂ𝕚𝕦𝕕𝕒𝕕𝕒𝕟𝕠 𝔼𝕛𝕖𝕞𝕡𝕝𝕒𝕣", 0x00FA9A),
        100: ("🏆 ℕ𝕚𝕧𝕖𝕝 𝟙𝟘𝟘: ℍ𝕖𝕣𝕠𝕖", 0x00FA9A)
    }

    roles_gobierno = [
        ("🛡️ 𝔸𝕤𝕡𝕚𝕣𝕒𝕟𝕥𝕖𝕤", 0xFF8C00), ("🏛️ ℂ𝕚𝕦𝕕𝕒𝕕𝕒𝕟𝕠", 0x2E8B57), 
        ("💼 𝕃𝕠𝕓𝕓𝕪 𝕞𝕒𝕟", 0x800080), ("⚖️ 𝕄𝕚𝕟𝕚𝕤𝕥𝕣𝕠𝕤", 0x008000), ("👁️ ℂ𝕠𝕟𝕘𝕣𝕖𝕤𝕠", 0x4169E1), 
        ("🦅 ℙ𝕣𝕖𝕤𝕚𝕕𝕖𝕟𝕥𝕖", 0xFFD700), ("👑 ℂ𝕒𝕟𝕔𝕚𝕝𝕝𝕖𝕣", 0xDC143C)
    ]

    creados = {}
    for nombre, color_hex in roles_base:
        rol = await guild.create_role(name=nombre, color=discord.Color(color_hex))
        creados[nombre] = rol

    for lvl, (nombre, color_hex) in nombres_niveles.items():
        rol = await guild.create_role(name=nombre, color=discord.Color(color_hex))
        creados[nombre] = rol

    for nombre, color_hex in roles_gobierno:
        perms = discord.Permissions.none()
        if "ℂ𝕒𝕟𝕔𝕚𝕝𝕝𝕖𝕣" in nombre: perms.update(administrator=True, manage_nicknames=True)
        elif "ℙ𝕣𝕖𝕤𝕚𝕕𝕖𝕟𝕥𝕖" in nombre or "𝕄𝕚𝕟𝕚𝕤𝕥𝕣𝕠𝕤" in nombre: perms.update(manage_messages=True, moderate_members=True, view_audit_log=True)
        elif "𝔸𝕤𝕡𝕚𝕣𝕒𝕟𝕥𝕖𝕤" in nombre: perms.update(manage_messages=True)
        
        rol = await guild.create_role(name=nombre, color=discord.Color(color_hex), permissions=perms, hoist=True)
        creados[nombre] = rol

    everyone = guild.default_role

    # --- D. CREACIÓN DE CANALES ---
    # 1. 🏛️ Cancillería
    ow_cancilleria = {
        everyone: discord.PermissionOverwrite(send_messages=False, view_channel=True),
        creados["👑 ℂ𝕒𝕟𝕔𝕚𝕝𝕝𝕖𝕣"]: discord.PermissionOverwrite(send_messages=True),
    }
    cat_cancilleria = await guild.create_category("🏛️ Cancillería")
    canal_reglas = await cat_cancilleria.create_text_channel("📜・la-constitucion", overwrites=ow_cancilleria)
    await cat_cancilleria.create_text_channel("📖・el-diario-de-la-canciller", overwrites=ow_cancilleria)
    await cat_cancilleria.create_text_channel("🎫・tickets")
    canal_autoroles = await cat_cancilleria.create_text_channel("🎨・autoroles", overwrites=ow_cancilleria)

    # 2. 📖 El Manifiesto (Explicación de todo)
    cat_manifiesto = await guild.create_category("📖 El Manifiesto")
    canal_explicacion = await cat_manifiesto.create_text_channel("🗺️・guia-de-santuari", overwrites=ow_cancilleria)

    # 3. 💬 Offtopic
    ow_general = {
        everyone: discord.PermissionOverwrite(view_channel=True),
        creados["🏛️ ℂ𝕚𝕦𝕕𝕒𝕕𝕒𝕟𝕠"]: discord.PermissionOverwrite(attach_files=False, embed_links=False),
        creados[nombres_niveles[5][0]]: discord.PermissionOverwrite(attach_files=True, embed_links=True),
        creados["⛓️ ℙ𝕣𝕖𝕤𝕠𝕤 ℙ𝕠𝕝𝕚𝕥𝕚𝕔𝕠𝕤"]: discord.PermissionOverwrite(view_channel=False)
    }
    ow_nivel5 = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        creados[nombres_niveles[5][0]]: discord.PermissionOverwrite(view_channel=True),
        creados["👑 ℂ𝕒𝕟𝕔𝕚𝕝𝕝𝕖𝕣"]: discord.PermissionOverwrite(view_channel=True)
    }
    
    cat_offtopic = await guild.create_category("💬 Offtopic", overwrites=ow_general)
    for ch in ["👋・presentacion", "💬・chat-offtopic", "🖼️・media-offtopic", "🫂・venting", "🪙・economia"]: await cat_offtopic.create_text_channel(ch)
    await cat_offtopic.create_text_channel("⭐・starboard", overwrites=ow_cancilleria)
    await cat_offtopic.create_text_channel("📸・selfies", overwrites=ow_nivel5)
    await cat_offtopic.create_text_channel("😂・memes-offtopic", overwrites=ow_nivel5)

    cat_vc_offtopic = await guild.create_category("🔊 VC Offtopic")
    await cat_vc_offtopic.create_voice_channel("🎮 VC Gaming")
    await cat_vc_offtopic.create_voice_channel("🗣️ VC Charla")

    # 4. Nichos
    ow_linux = {everyone: discord.PermissionOverwrite(view_channel=False), creados["🐧 𝕃𝕚𝕟𝕦𝕩 & ℂ𝕠𝕕𝕚𝕟𝕘"]: discord.PermissionOverwrite(view_channel=True)}
    cat_linux = await guild.create_category("💻 Linux & Coding", overwrites=ow_linux)
    for ch in ["🐧・linux-general", "🖼️・linux-media", "🖥️・linux-setup", "😂・linux-coding-memes", "⌨️・tu-código"]: await cat_linux.create_text_channel(ch)
    
    ow_rol = {everyone: discord.PermissionOverwrite(view_channel=False), creados["🎲 ℝ𝕠𝕝 𝕟 ℝ𝕠𝕝𝕝"]: discord.PermissionOverwrite(view_channel=True)}
    cat_rol = await guild.create_category("🐉 Rol n Roll", overwrites=ow_rol)
    canal_reglas_rol = await cat_rol.create_text_channel("📜・leyes-de-la-taberna", overwrites=ow_cancilleria)
    for ch in ["🎭・presenta-tu-personaje", "🎲・general-rol", "🖼️・media-rol", "📅・organiza-tu-party", "😂・memes-rol"]: await cat_rol.create_text_channel(ch)
    
    ow_arte = {everyone: discord.PermissionOverwrite(view_channel=False), creados["🎸 𝔸𝕣𝕥𝕖 𝕪 𝔽𝕚𝕝𝕠𝕤𝕠𝕗𝕚𝕒"]: discord.PermissionOverwrite(view_channel=True)}
    cat_arte = await guild.create_category("🎨 Arte y Filosofía", overwrites=ow_arte)
    for ch in ["🎸・general-arte", "🖼️・media-arte", "😂・memes-arte", "📚・tu-biblioteca", "🖌️・tus-dibujos", "🎵・musica"]: await cat_arte.create_text_channel(ch)

    # 5. VIP y Logs
    ow_congreso = {everyone: discord.PermissionOverwrite(view_channel=False), creados["👁️ ℂ𝕠𝕟𝕘𝕣𝕖𝕤𝕠"]: discord.PermissionOverwrite(view_channel=True), creados["👑 ℂ𝕒𝕟𝕔𝕚𝕝𝕝𝕖𝕣"]: discord.PermissionOverwrite(view_channel=True)}
    cat_congreso = await guild.create_category("👁️ Congreso VIP", overwrites=ow_congreso)
    await cat_congreso.create_text_channel("🍷・sala-del-congreso")

    ow_logs = {everyone: discord.PermissionOverwrite(view_channel=False), creados["⚖️ 𝕄𝕚𝕟𝕚𝕤𝕥𝕣𝕠𝕤"]: discord.PermissionOverwrite(view_channel=True), creados["👑 ℂ𝕒𝕟𝕔𝕚𝕝𝕝𝕖𝕣"]: discord.PermissionOverwrite(view_channel=True)}
    cat_logs = await guild.create_category("📁 Logs & Brigada", overwrites=ow_logs)
    canal_auditoria = await cat_logs.create_text_channel("🗄️・auditoria-y-logs")

    # --- E. INYECCIÓN DE REGLAS EXTREMAS ---
    reglas_texto = (
        "**ESTATUTOS ABSOLUTOS DEL IMPERIO DE SANTUARI**\n\n"
        "**ARTÍCULO I: LA SUPREMACÍA DE LA CANCILLER** 👑\n"
        "Santuari **NO es una democracia**. Este proyecto es propiedad intelectual, estructural y absoluta de la Canciller Adeline. Su palabra es ley, su decisión es final, inapelable e indiscutible. Si la Canciller decide alterar una regla, banear a un usuario o reestructurar el servidor, se hará sin derecho a réplica.\n\n"
        "**ARTÍCULO II: ZONA SEGURA (CERO TOLERANCIA)** 🛡️\n"
        "Este es un refugio estrictamente LGBTQ+ Friendly. Cualquier mínimo asomo de homofobia, transfobia, racismo, machismo, odio o acoso directo resultará en exilio inmediato y permanente. Aquí no hay 'segundas oportunidades' para el odio.\n\n"
        "**ARTÍCULO III: EL LÍMITE DE LA COMEDIA** 🎭\n"
        "El *shitposting*, los baits, el humor negro y el sarcasmo son el alma de la zona Offtopic. Eres libre de ser una *jodedora*, PERO la línea se traza en el ataque personal. Aprende a leer la habitación; si tu 'broma' es hostigamiento continuo, conocerás las celdas de los Presos Políticos.\n\n"
        "**ARTÍCULO IV: SEGREGACIÓN DE CONTENIDO** 🗂️\n"
        "Respeta los nichos. Código en código, memes en memes, rol en rol. Queda terminantemente prohibido el contenido NSFW explícito (+18) o Gore en cualquier rincón público del servidor. Romper esto es ban directo de IP visual.\n\n"
        "**ARTÍCULO V: BUROCRACIA Y TICKETS** 🎫\n"
        "El staff (Ministros, Presidente, Aspirantes) actúa bajo la voluntad del Congreso y la Canciller. Faltarles al respeto es un delito federal. Si tienes un problema real, abre un Ticket. Si abres un Ticket para trollear, serás silenciado indefinidamente."
    )
    embed_reglas = discord.Embed(title="📜 LA CONSTITUCIÓN DE SANTUARI", color=0xDC143C, description=reglas_texto)
    embed_reglas.set_footer(text="Dictado y firmado por la Canciller Adeline.")
    await canal_reglas.send(embed=embed_reglas)

    reglas_rol = (
        "**EL CÓDIGO DE SANGRE DE LA TABERNA**\n\n"
        "**1. LA LEY DE HIERRO DEL CONSENTIMIENTO OOC (Out of Character):** 🛑\n"
        "No existe el romance forzado. No existe el PvP (jugador contra jugador) forzado. Si intentas robar, atacar, o iniciar una dinámica romántica/sexual con el personaje de otro jugador SIN que la persona detrás de la pantalla haya aceptado clara y explícitamente, serás vetado del Rol permanentemente.\n\n"
        "**2. LA INFALIBILIDAD DEL DUNGEON MASTER:** 🎲\n"
        "Detrás de la pantalla, el DM es Dios. Si el DM dice que tu hechizo falla, falla. Si el DM prohíbe el uso de manuales homebrew o razas rotas, lo acatas. No se permite detener el flujo del juego para discutir reglas durante 30 minutos.\n\n"
        "**3. JUGADOR ≠ PERSONAJE (Metagaming):** 🎭\n"
        "Si mi Pícaro traiciona a tu Paladín por oro, es rol. No te enojes conmigo en el chat general ni lleves rencores personales al Offtopic. Del mismo modo, tu personaje NO SABE lo que tú sabes; no uses información externa para ganar ventaja en el juego.\n\n"
        "**4. EL JURAMENTO DE LA PARTY:** 🤝\n"
        "D&D y los RPGs son compromisos. Si te inscribes en una campaña, tu deber es asistir. Si faltas sin avisar y dejas a tus compañeros vendidos frente al dragón, el DM tiene derecho a convertir a tu personaje en un NPC sacrificable."
    )
    embed_rol = discord.Embed(title="🐉 LEYES DE LA TABERNA (Rol n Roll)", color=0xFF8C00, description=reglas_rol)
    await canal_reglas_rol.send(embed=embed_rol)

    # --- F. CANAL DE EXPLICACIÓN (MANIFIESTO) ---
    texto_guia = (
        "**BIENVENIDO A SANTUARI: GUÍA DE SUPERVIVENCIA**\n\n"
        "Este servidor es una **meritocracia estética** diseñada por y para su creadora, la **Canciller Adeline**, quien posee la autoridad absoluta sobre cada byte de información aquí dentro. Aquí te explicamos cómo funciona nuestro mundo:\n\n"
        "**¿Cómo gano permisos? (Sistema de XP)** 📈\n"
        "Al entrar eres un *Recién Arribado* con derechos básicos. Conforme interactúes en los canales de texto, subirás de nivel. Al llegar al **Nivel 5**, ganarás el derecho de enviar imágenes y desbloquearás los canales oscuros de `#📸・selfies` y `#😂・memes-offtopic`.\n\n"
        "**Los Ministerios (Roles del Staff):** ⚖️\n"
        "• **Canciller 👑:** Adeline. La creadora. Dueña de la última palabra.\n"
        "• **Presidente 🦅 / Congreso 👁️:** La élite de confianza, inmunes a la moderación.\n"
        "• **Ministros ⚖️:** Moderadores con el dedo en el botón de Ban.\n"
        "• **Aspirantes 🛡️:** En entrenamiento, vigilan que cumplas la Constitución.\n\n"
        "**Canales de Nicho:** 📚\n"
        "Para no saturar el servidor, canales como **Linux, Arte y Rol** están ocultos. Ve al canal de `#🎨・autoroles` y reclama el rol correspondiente para que la categoría aparezca mágicamente en tu barra lateral."
    )
    embed_guia = discord.Embed(title="🗺️ MAPA DEL IMPERIO", color=0x1982C4, description=texto_guia)
    await canal_explicacion.send(embed=embed_guia)

    # --- G. AUTOROLES CON MENCIONES EXACTAS ---
    global AUTOROLE_MESSAGE_IDS

    async def mandar_autorol(titulo, color, diccionario):
        desc = "Reacciona al emoji para obtener tu rol y asignarlo a tu perfil:\n\n"
        for emoji, nombre_rol in diccionario.items():
            rol_obj = creados.get(nombre_rol)
            if rol_obj:
                desc += f"{emoji} ➔ {rol_obj.mention}\n"
        
        embed = discord.Embed(title=titulo, color=color, description=desc)
        msg = await canal_autoroles.send(embed=embed)
        for emoji in diccionario.keys(): await msg.add_reaction(emoji)
        AUTOROLE_MESSAGE_IDS[msg.id] = diccionario

    # 1. Regiones
    await mandar_autorol("🌎 Ministerio de Fronteras: Tu Región", 0x1982C4, {"🦅": "🦅 ℕ𝕠𝕣𝕥𝕖𝕒𝕞𝕖𝕣𝕚𝕔𝕒", "🦙": "🦙 𝕊𝕦𝕕𝕒𝕞𝕖𝕣𝕚𝕔𝕒", "🏰": "🏰 𝔼𝕦𝕣𝕠𝕡𝕒", "🐉": "🐉 𝔸𝕤𝕚𝕒"})
    
    # 2. Edades
    await mandar_autorol("⏳ Ministerio del Tiempo: Tu Edad", 0xFF8C00, {"🎒": "🎒 𝟙𝟜-𝟙𝟟", "🎓": "🎓 𝟙𝟠-𝟚𝟝", "🍷": "🍷 𝟚𝟝+"})
    
    # 3. Género
    await mandar_autorol("⚧️ Ministerio de Identidad: Género", 0xFF9ED2, {"♂️": "♂️ ℍ𝕠𝕞𝕓𝕣𝕖 𝕔𝕚𝕤", "♀️": "♀️ 𝕄𝕦𝕛𝕖𝕣 𝕔𝕚𝕤", "🏳️‍⚧️": "🏳️‍⚧️ 𝕋𝕣𝕒𝕟𝕤𝕘𝕖𝕟𝕖𝕣𝕠", "👽": "👽 ℕ𝕠 𝕓𝕚𝕟𝕒𝕣𝕚𝕖", "🌀": "🌀 𝕆𝕥𝕣𝕠 𝕘𝕖𝕟𝕖𝕣𝕠"})
    
    # 4. Pronombres
    await mandar_autorol("🗣️ Ministerio de Identidad: Pronombres", 0x8AC926, {"📖": "📖 𝕤𝕙𝕖/𝕙𝕖𝕣", "📘": "📘 𝕙𝕖/𝕙𝕚𝕞", "📗": "📗 𝕥𝕙𝕖𝕪/𝕥𝕙𝕖𝕞", "📔": "📔 𝕆𝕥𝕣𝕠𝕤 𝕡𝕣𝕠𝕟𝕠𝕞𝕓𝕣𝕖𝕤"})
    
    # 5. Sexualidad
    await mandar_autorol("🌈 Ministerio de Identidad: Orientación", 0x6A4C93, {"🌈": "🌈 𝔾𝕒𝕪", "🌸": "🌸 𝕃𝕖𝕤𝕓𝕚𝕒𝕟𝕒", "💜": "💜 𝔹𝕚𝕤𝕖𝕩𝕦𝕒𝕝", "🖤": "🖤 𝔸𝕤𝕖𝕩𝕦𝕒𝕝", "🤍": "🤍 𝔸𝕣𝕣𝕠𝕞𝕒𝕟𝕥𝕚𝕔𝕠", "✨": "✨ 𝕆𝕥𝕣𝕒 𝕤𝕖𝕩𝕦𝕒𝕝𝕚𝕕𝕒𝕕"})
    
    # 6. Nichos
    await mandar_autorol("📚 Clasificación de Intereses", 0x2E8B57, {"🎸": "🎸 𝔸𝕣𝕥𝕖 𝕪 𝔽𝕚𝕝𝕠𝕤𝕠𝕗𝕚𝕒", "🎲": "🎲 ℝ𝕠𝕝 𝕟 ℝ𝕠𝕝𝕝", "🐧": "🐧 𝕃𝕚𝕟𝕦𝕩 & ℂ𝕠𝕕𝕚𝕟𝕘"})
    
    # 7. Colores
    await mandar_autorol("🎨 Paleta del Régimen: Colores", 0xFFD700, {"🔴": "🔴 ℂ𝕠𝕝𝕠𝕣 𝟙", "🟠": "🟠 ℂ𝕠𝕝𝕠𝕣 𝟚", "🟡": "🟡 ℂ𝕠𝕝𝕠𝕣 𝟛", "🟢": "🟢 ℂ𝕠𝕝𝕠𝕣 𝟜", "🔵": "🔵 ℂ𝕠𝕝𝕠𝕣 𝟝", "🟣": "🟣 ℂ𝕠𝕝𝕠𝕣 𝟞", "🟤": "🟤 ℂ𝕠𝕝𝕠𝕣 𝟟", "⚫": "⚫ ℂ𝕠𝕝𝕠𝕣 𝟠", "🤍": "🤍 ℂ𝕠𝕝𝕠𝕣 𝟡", "💖": "💖 ℂ𝕠𝕝𝕠𝕣 𝟙𝟘"})

    await canal_auditoria.send("👑✨ **¡SANTUARI HA SIDO FORJADO!** La visión de la Canciller Adeline se ha materializado con éxito. Roles, tipografías y reglas operativas al 100%.")

bot.run("MTUxODEzMzM3MjA2MzMxODE2Nw.GVPhGm.JDaB4RjnYNZ_Pv8KJkrv3axIfsYy2aMavNMdU8")
