import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# Diccionario global para guardar los IDs de los mensajes de autoroles
AUTOROLE_MESSAGE_IDS = {}

class SantuariBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("[INFO] Comandos sincronizados. ¡Santuari está listo para forjarse!")

bot = SantuariBot()

@bot.event
async def on_ready():
    print('------------------------------------------------')
    print(f'[INFO] Conectado en la terminal como {bot.user} 🏛️')
    print('------------------------------------------------')

# ==========================================
# 1. SISTEMA AUTOMÁTICO DE FRONTERAS (Ingreso)
# ==========================================
@bot.event
async def on_member_join(member):
    guild = member.guild
    rol_ciudadano = discord.utils.get(guild.roles, name="Ciudadano")
    rol_recien = discord.utils.get(guild.roles, name="Recién Arribados") # Creado manual abajo
    
    roles_a_dar = []
    if rol_ciudadano: roles_a_dar.append(rol_ciudadano)
    if rol_recien: roles_a_dar.append(rol_recien)
    
    if roles_a_dar:
        await member.add_roles(*roles_a_dar)

# ==========================================
# 2. AUTO-REACCIONES Y STARBOARD (4 Estrellas)
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Auto-reacciones para código y arte
    if message.attachments:
        if message.channel.name in ["⌨️・tu-código", "🖌️・tus-dibujos"]:
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    # --- LÓGICA DE STARBOARD ---
    if str(payload.emoji) == "⭐":
        channel = bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        reaction = discord.utils.get(message.reactions, emoji="⭐")
        if reaction and reaction.count >= 4:
            guild = bot.get_guild(payload.guild_id)
            starboard_channel = discord.utils.get(guild.text_channels, name="⭐・starboard")
            
            if starboard_channel:
                async for msg in starboard_channel.history(limit=50):
                    if msg.embeds and f"ID: {message.id}" in msg.embeds[0].footer.text:
                        return
                
                embed = discord.Embed(description=message.content, color=discord.Color.gold(), timestamp=message.created_at)
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                embed.add_field(name="Origen", value=f"[Ir al mensaje]({message.jump_url})")
                embed.set_footer(text=f"⭐ {reaction.count} | ID: {message.id}")
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)
                await starboard_channel.send(embed=embed)

    # --- LÓGICA DE AUTOROLES ---
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
# 3. COMANDO DE REESTRUCTURACIÓN IMPERIAL
# ==========================================
@bot.tree.command(name="setup_santuari", description="Purga total y reconstrucción del Imperio de Santuari.")
@discord.app_commands.default_permissions(administrator=True)
async def setup_santuari(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    guild = interaction.guild

    await interaction.followup.send("⚠️ **Iniciando protocolo de purga y reconstrucción masiva. Discord puede tardar un par de minutos, por favor espera...** ⚙️")

    # --- A. PURGA DE CANALES VIEJOS ---
    nombres_categorias = ["🏛️ Cancillería", "💬 Offtopic", "🔊 VC Offtopic", "💻 Linux & Coding", "🛠️ VC Asistencia", "🐉 Rol n Roll", "🎙️ VC Rol n Roll", "🎨 Arte y Filosofía", "🎧 VC Arte y filosofía", "👁️ Congreso VIP", "📁 Logs & Brigada"]
    for cat in guild.categories:
        if cat.name in nombres_categorias:
            for ch in cat.channels: await ch.delete()
            await cat.delete()

    # --- B. CREACIÓN DE ROLES (De menor a mayor jerarquía) ---
    roles_base = [
        ("Recién Arribados", 0x808080), # Gris base
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
        ("⛓️ Presos políticos", 0x101010)
    ]
    
    nombres_niveles = {
        5: ("Nivel 5: Residente Oficial", 0x00FA9A),
        10: ("Nivel 10: Inspector de Distrito", 0x00FA9A),
        20: ("Nivel 20: Burócrata Menor", 0x00FA9A),
        30: ("Nivel 30: Oficinista del Régimen", 0x00FA9A),
        40: ("Nivel 40: Voz Cívica", 0x00FA9A),
        50: ("Nivel 50: Ciudadano Ejemplar", 0x00FA9A),
        60: ("Nivel 60: Comisionado", 0x00FA9A),
        70: ("Nivel 70: Supervisor Cívico", 0x00FA9A),
        80: ("Nivel 80: Ideólogo", 0x00FA9A),
        90: ("Nivel 90: Asesor del Congreso", 0x00FA9A),
        100: ("Nivel 100: Héroe de Santuari", 0x00FA9A)
    }

    roles_gobierno = [
        ("Aspirantes", 0xFF8C00), ("Ciudadano", 0x2E8B57), 
        ("Lobby man", 0x800080), ("Ministros", 0x008000), ("Congreso", 0x4169E1), 
        ("Presidente", 0xFFD700), ("Canciller", 0xDC143C)
    ]

    creados = {}
    
    # 1. Crear roles base y estéticos
    for nombre, color_hex in roles_base:
        if not discord.utils.get(guild.roles, name=nombre):
            rol = await guild.create_role(name=nombre, color=discord.Color(color_hex))
            creados[nombre] = rol
        else: creados[nombre] = discord.utils.get(guild.roles, name=nombre)

    # 2. Crear roles de Nivel
    for lvl, (nombre, color_hex) in nombres_niveles.items():
        if not discord.utils.get(guild.roles, name=nombre):
            rol = await guild.create_role(name=nombre, color=discord.Color(color_hex))
            creados[nombre] = rol
        else: creados[nombre] = discord.utils.get(guild.roles, name=nombre)

    # 3. Crear roles de Gobierno con Permisos
    for nombre, color_hex in roles_gobierno:
        perms = discord.Permissions.none()
        if nombre == "Canciller": perms.update(administrator=True, manage_nicknames=True)
        elif nombre in ["Presidente", "Ministros"]: perms.update(manage_messages=True, moderate_members=True, view_audit_log=True)
        elif nombre == "Aspirantes": perms.update(manage_messages=True)
        
        if not discord.utils.get(guild.roles, name=nombre):
            rol = await guild.create_role(name=nombre, color=discord.Color(color_hex), permissions=perms, hoist=True)
            creados[nombre] = rol
        else: creados[nombre] = discord.utils.get(guild.roles, name=nombre)

    everyone = guild.default_role

    # --- C. CREACIÓN DE CANALES Y CATEGORÍAS ---
    
    # 1. 🏛️ Cancillería (Nadie escribe, excepto Canciller/Bot)
    ow_cancilleria = {
        everyone: discord.PermissionOverwrite(send_messages=False, view_channel=True),
        creados["Canciller"]: discord.PermissionOverwrite(send_messages=True),
        creados["Presidente"]: discord.PermissionOverwrite(send_messages=True)
    }
    cat_cancilleria = await guild.create_category("🏛️ Cancillería")
    canal_reglas = await cat_cancilleria.create_text_channel("📜・reglas", overwrites=ow_cancilleria)
    await cat_cancilleria.create_text_channel("📖・el-diario-de-la-canciller", overwrites=ow_cancilleria)
    await cat_cancilleria.create_text_channel("🎫・tickets")
    canal_autoroles = await cat_cancilleria.create_text_channel("🎨・autoroles", overwrites=ow_cancilleria)
    
    # 2. 💬 Offtopic (Con restricciones por nivel)
    ow_general = {
        everyone: discord.PermissionOverwrite(view_channel=True),
        creados["Ciudadano"]: discord.PermissionOverwrite(attach_files=False, embed_links=False),
        creados[nombres_niveles[5][0]]: discord.PermissionOverwrite(attach_files=True, embed_links=True),
        creados["⛓️ Presos políticos"]: discord.PermissionOverwrite(view_channel=False)
    }
    ow_nivel5 = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        creados[nombres_niveles[5][0]]: discord.PermissionOverwrite(view_channel=True),
        creados["Canciller"]: discord.PermissionOverwrite(view_channel=True)
    }
    
    cat_offtopic = await guild.create_category("💬 Offtopic", overwrites=ow_general)
    await cat_offtopic.create_text_channel("👋・presentacion")
    await cat_offtopic.create_text_channel("💬・chat-offtopic")
    await cat_offtopic.create_text_channel("🖼️・media-offtopic")
    await cat_offtopic.create_text_channel("🫂・venting")
    await cat_offtopic.create_text_channel("🪙・economia")
    await cat_offtopic.create_text_channel("⭐・starboard", overwrites=ow_cancilleria) # Solo lectura
    
    await cat_offtopic.create_text_channel("📸・selfies", overwrites=ow_nivel5)
    await cat_offtopic.create_text_channel("😂・memes-offtopic", overwrites=ow_nivel5)

    # 3. 🔊 VC Offtopic
    cat_vc_offtopic = await guild.create_category("🔊 VC Offtopic")
    await cat_vc_offtopic.create_voice_channel("🎮 VC Gaming")
    await cat_vc_offtopic.create_voice_channel("🗣️ VC Charla")
    for i in range(1, 4): await cat_vc_offtopic.create_voice_channel(f"👥 VC Duo {i}", user_limit=2)
    for i in range(1, 3): await cat_vc_offtopic.create_voice_channel(f"👨‍👩‍👦 VC Trio {i}", user_limit=3)

    # 4. Nichos (Linux, Rol, Arte) Bloqueados con Rol
    ow_linux = {everyone: discord.PermissionOverwrite(view_channel=False), creados["🐧Linux & Coding"]: discord.PermissionOverwrite(view_channel=True)}
    cat_linux = await guild.create_category("💻 Linux & Coding", overwrites=ow_linux)
    for ch in ["🐧・linux-general", "🖼️・linux-media", "🖥️・linux-setup", "😂・linux-coding-memes", "⌨️・tu-código", "🤝・proyectos-comunitarios"]: await cat_linux.create_text_channel(ch)
    
    cat_vc_asis = await guild.create_category("🛠️ VC Asistencia", overwrites=ow_linux)
    for i in range(1, 6): await cat_vc_asis.create_voice_channel(f"🔧 Asistencia {i}")

    ow_rol = {everyone: discord.PermissionOverwrite(view_channel=False), creados["🐉 Rol n Roll"]: discord.PermissionOverwrite(view_channel=True)}
    cat_rol = await guild.create_category("🐉 Rol n Roll", overwrites=ow_rol)
    canal_reglas_rol = await cat_rol.create_text_channel("📜・reglas-rol-n-roll", overwrites=ow_cancilleria)
    for ch in ["🎭・presenta-tu-personaje", "🎲・general-rol-n-roll", "🖼️・media-rol-n-roll", "📅・organiza-tu-party", "😂・memes-rol-n-roll", "📚・otros-juegos-de-rol"]: await cat_rol.create_text_channel(ch)
    
    cat_vc_rol = await guild.create_category("🎙️ VC Rol n Roll", overwrites=ow_rol)
    for i in range(1, 11): await cat_vc_rol.create_voice_channel(f"🪵 Mesa {i}", user_limit=5)

    ow_arte = {everyone: discord.PermissionOverwrite(view_channel=False), creados["🎸Arte y filosofía"]: discord.PermissionOverwrite(view_channel=True)}
    cat_arte = await guild.create_category("🎨 Arte y Filosofía", overwrites=ow_arte)
    for ch in ["🎸・general-arte", "🖼️・media-arte", "😂・memes-arte", "📚・tu-biblioteca", "🖌️・tus-dibujos", "🎵・musica"]: await cat_arte.create_text_channel(ch)
    
    cat_vc_arte = await guild.create_category("🎧 VC Arte y filosofía", overwrites=ow_arte)
    for i in range(1, 4): await cat_vc_arte.create_voice_channel(f"🎵 Música 3p - {i}", user_limit=3)

    # 5. ZONAS CLASIFICADAS (Congreso VIP y Logs)
    ow_congreso = {everyone: discord.PermissionOverwrite(view_channel=False), creados["Congreso"]: discord.PermissionOverwrite(view_channel=True), creados["Canciller"]: discord.PermissionOverwrite(view_channel=True)}
    cat_congreso = await guild.create_category("👁️ Congreso VIP", overwrites=ow_congreso)
    await cat_congreso.create_text_channel("🍷・sala-del-congreso")
    await cat_congreso.create_voice_channel("👑 Junta Ministerial")

    ow_logs = {everyone: discord.PermissionOverwrite(view_channel=False), creados["Aspirantes"]: discord.PermissionOverwrite(view_channel=True), creados["Ministros"]: discord.PermissionOverwrite(view_channel=True), creados["Canciller"]: discord.PermissionOverwrite(view_channel=True)}
    cat_logs = await guild.create_category("📁 Logs & Brigada", overwrites=ow_logs)
    await cat_logs.create_text_channel("🗄️・auditoria-y-logs")

    # --- D. INYECCIÓN DE REGLAS (Igual a tu código) ---
    embed_reglas = discord.Embed(title="🏛️ Constitución de Santuari", color=0x1982C4, description="**1. Respeto Total (Cero Tolerancia):** Santuari es un espacio LGBTQ+ friendly. Cualquier comentario de odio, transfobia, homofobia, racismo o acoso resulta en exilio inmediato.\n\n**2. El Humor es Legal, pero sé inteligente:** El shitposting, el sarcasmo y las bromas son bienvenidos en Offtopic. Pero la comedia tiene un límite cuando cruza al acoso personal.\n\n**3. Uso Correcto de Canales:** Los memes van en memes, el código en código. Prohibido subir contenido +18 o gore.\n\n**4. El Congreso y los Ministerios:** El Lobby man, los Ministros y la Canciller tienen la última palabra.\n\n**5. Sistema de Tickets:** Falsificar o abusar de los tickets es un delito federal.")
    await canal_reglas.send(embed=embed_reglas)
    
    embed_rol_reglas = discord.Embed(title="🐉 Leyes de la Taberna (Rol n Roll)", color=0xFF595E, description="**1. Regla del Consentimiento:** Cero romance o dinámicas PvP si el otro jugador no está 100% de acuerdo OOC.\n**2. La Palabra del DM es Ley.**\n**3. Compromiso con la Party:** Sé puntual.\n**4. Separa Jugador de Personaje.**")
    await canal_reglas_rol.send(embed=embed_rol_reglas)

    # --- E. EMBEDS DE AUTOROLES Y GOBIERNO ---
    global AUTOROLE_MESSAGE_IDS

    # Embed 1: Explicación del Gobierno y Niveles
    embed_gov = discord.Embed(title="🏛️ Estructura del Régimen y Beneficios Cívicos", color=0xDC143C, description="Conoce el orden jerárquico de nuestra Nación. Tu comportamiento dicta tu ascenso o tu caída a los sótanos de la prisión.")
    embed_gov.add_field(name="👑 Altas Esferas (Moderación y Control)", value="**Canciller & Presidente:** Dueños absolutos. Modifican apodos y leyes.\n**Congreso:** Élite inmune a la auto-moderación. Tienen canales ocultos.\n**Ministros:** Moderadores con capacidad de banear.\n**Aspirantes:** Moderadores en prueba, vigilan el chat.", inline=False)
    embed_gov.add_field(name="📜 Sistema de Niveles Cívicos", value="Al chatear ganarás XP. Subir de nivel otorga beneficios:\n\n🟢 **Nivel 5:** Desbloquea el acceso para ver y postear en `#📸・selfies` y `#😂・memes-offtopic`. Permite enviar imágenes en chat general.\n🔵 **Niveles 10 al 100:** Roles cosméticos exclusivos que demuestran tu estatus de oficinista a Héroe Nacional.", inline=False)
    embed_gov.add_field(name="⛓️ Presos Políticos", value="Ciudadanos exiliados. Pierden acceso a todos los canales excepto a su celda.", inline=False)
    await canal_autoroles.send(embed=embed_gov)

    # Embed 2: Colores
    embed_col = discord.Embed(title="🎨 Ministerio de Identidad: Colores", color=0x2b2d31, description="Reacciona para obtener el color de tu nombre en el chat.")
    msg_col = await canal_autoroles.send(embed=embed_col)
    dic_col = {"🔴": "Color 1", "🟠": "Color 2", "🟡": "Color 3", "🟢": "Color 4", "🔵": "Color 5", "🟣": "Color 6", "🟤": "Color 7", "⚫": "Color 8", "⚪": "Color 9", "💖": "Color 10"}
    for emoji in dic_col.keys(): await msg_col.add_reaction(emoji)
    AUTOROLE_MESSAGE_IDS[msg_col.id] = dic_col

    # Embed 3: Géneros y Pronombres
    embed_gen = discord.Embed(title="⚧️ Ministerio de Identidad: Género y Pronombres", color=0x2b2d31, description="Selecciona tu clasificación demográfica.")
    msg_gen = await canal_autoroles.send(embed=embed_gen)
    dic_gen = {"👨": "Hombre cis", "👩": "Mujer cis", "🏳️‍⚧️": "Transgénero", "👽": "No binarie", "📖": "he/him", "📗": "she/her", "📘": "they/them"}
    for emoji in dic_gen.keys(): await msg_gen.add_reaction(emoji)
    AUTOROLE_MESSAGE_IDS[msg_gen.id] = dic_gen

    # Embed 4: Nichos
    embed_nichos = discord.Embed(title="📚 Clasificación de Intereses", color=0x2b2d31, description="Desbloquea las categorías secretas del servidor.")
    embed_nichos.add_field(name="Opciones", value="🐧 ➔ Linux & Coding\n🐉 ➔ Rol n Roll\n🎸 ➔ Arte y Filosofía")
    msg_nichos = await canal_autoroles.send(embed=embed_nichos)
    dic_nichos = {"🐧": "🐧Linux & Coding", "🐉": "🐉 Rol n Roll", "🎸": "🎸Arte y filosofía"}
    for emoji in dic_nichos.keys(): await msg_nichos.add_reaction(emoji)
    AUTOROLE_MESSAGE_IDS[msg_nichos.id] = dic_nichos

    await interaction.followup.send("🏛️✨ **¡SANTUARI HA SIDO FORJADO COMPLETAMENTE!** Todos los canales, roles, candados VIP y autoroles están operativos.")

bot.run("MTUxODEzMzM3MjA2MzMxODE2Nw.GVPhGm.JDaB4RjnYNZ_Pv8KJkrv3axIfsYy2aMavNMdU8")
