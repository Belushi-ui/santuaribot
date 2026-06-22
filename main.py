import discord
from discord import app_commands
import os
import random
import datetime
import motor.motor_asyncio
import certifi

# =========================================================================
# ⚙️ CONFIGURACIÓN IMPERIAL
# =========================================================================
ID_SERVIDOR = 1517885569231749240        
ID_CANCILLER = 1518298260479938783       
ID_ROL_AUTOROL = 1518298254767427855     
ID_CANAL_STARBOARD = 1518298279715017016 
ID_BOT_BUMP = 302050872383242240         

ID_ROL_CONGRESISTA = 1518298258382913748 

ROLES_INMUNES = [
    ID_ROL_CONGRESISTA,
    1518298257581936861, # Moderador
    1518298253181845685  # Élite
]

# 🎖️ DICCIONARIO DE ROLES POR NIVEL (Tipografía Doble Strike)
ROLES_NIVEL = {
    5: "🟢 ℕ𝕚𝕧𝕖𝕝 𝟛: ℝ𝕖𝕤𝕚𝕕𝕖𝕟𝕥𝕖",   # Se busca por nombre dinámico en el gremio
    10: "🟢 ℕ𝕚𝕧𝕖𝕝 𝟙𝟘: 𝕀𝕟𝕤𝕡𝕖𝕔𝕥𝕠𝕣",
    20: "🟢 ℕ𝕚𝕧𝕖𝕝 𝟚𝟘: 𝔹𝕦𝕣𝕠𝕔𝕣𝕒𝕥𝕒",
    30: "🟢 ℕ𝕚𝕧𝕖𝕝 𝟛𝟘: 𝕆𝕗𝕚𝕔𝕚𝕟𝕚𝕤𝕥𝕒",
    40: "🟢 ℕ𝕚𝕧𝕖𝕝 𝟜𝟘: 𝕍𝕠𝕫 ℂ𝕚𝕧𝕚𝕔𝕒",
    50: "🟢 ℕ𝕚𝕧𝕖𝕝 𝟛𝟘: ℂ𝕚𝕦𝕕𝕒𝕕𝕒𝕟𝕠 𝔼𝕛𝕖𝕞𝕡𝕝𝕒𝕣",
    100: "🏆 ℕ𝕚𝕧𝕖𝕝 𝟙𝟘𝟘: ℍ𝕖𝕣𝕠𝕖"
}

# 🎭 DICCIONARIOS DE CONFIGURACIÓN DE AUTOROLES (Tipografía Doble Strike)
DICCIONARIO_AUTOROLES = {
    "Regiones": {"🦅": "🦅 ℕ𝕠𝕣𝕥𝕖𝕒𝕞𝕖𝕣𝕚𝕔𝕒", "🦙": "🦙 𝕊𝕦𝕕𝕒𝕞𝕖𝕣𝕚𝕔𝕒", "🏰": "🏰 𝔼𝕦𝕣𝕠𝕡𝕒", "🐉": "🐉 𝔸𝕤𝕚𝕒"},
    "Edades": {"🎒": "🎒 𝟙𝟜-𝟙𝟟", "🎓": "🎓 𝟙𝟠-𝟚𝟝", "🍷": "🍷 𝟚𝟝+"},
    "Generos": {"♂️": "♂️ ℍ𝕠𝕞𝕓𝕣𝕖 𝕔𝕚𝕤", "♀️": "♀️ 𝕄𝕦𝕛𝕖𝕣 𝕔𝕚𝕤", "🏳️‍⚧️": "🏳️‍⚧️ 𝕋𝕣𝕒𝕟𝕤𝕘𝕖𝕟𝕖𝕣𝕠", "👽": "👽 ℕ𝕠 𝕓𝕚𝕟𝕒𝕣𝕚𝕖", "🌀": "🌀 𝕆𝕥𝕣𝕠 𝕘𝕖𝕟𝕖𝕣𝕠"},
    "Pronombres": {"📖": "📖 𝕤𝕙𝕖/𝕙𝕖𝕣", "📘": "📘 𝕙𝕖/𝕙𝕚𝕞", "📗": "📗 𝕥𝕙𝕖𝪪/𝕥𝕙𝕖𝕞", "📔": "📔 𝕆𝕥𝕣ос 𝕡𝕣𝕠𝕟𝕠𝕞𝕓𝕣𝕖𝕤"},
    "Sexualidades": {"🌈": "🌈 𝔾𝕒𝕪", "🌸": "🌸 𝕃𝕖𝕤𝕓𝕚𝕒𝕟𝕒", "💜": "💜 𝔹𝕚𝕤𝕖𝕩𝕦𝕒𝕝", "🖤": "🖤 𝔸𝕤𝕖𝕩𝕦𝕒𝕝", "🤍": "🤍 𝔸𝕣𝕣𝕠𝕞𝕒𝕟𝕥𝕚𝕔𝕠", "✨": "✨ 𝕆𝕥𝕣𝕒 𝕤𝕖𝕩𝕦𝕒𝕝𝕚𝕕𝕒𝕕"},
    "Nichos": {"🎸": "🎸 𝔸𝕣𝕥𝕖 𝕪 𝔽𝕚𝕝𝕠𝕤𝕠𝕗𝕚𝕒", "🎲": "🎲 ℝ𝕠𝕝 𝕟 ℝ𝕠𝕝𝕝", "🐧": "🐧 𝕃𝕚𝕟𝕦𝕩 & ℂ𝕠𝕕𝕚𝕟𝕘"},
    "Colores": {"🔴": "🔴 ℂ𝕠𝕝𝕠𝕣 𝟙", "🟠": "🟠 ℂ𝕠𝕝𝕠𝕣 𝟚", "🟡": "🟡 ℂ𝕠𝕝𝕠𝕣 𝟛", "🟢": "🟢 ℂ𝕠𝕝𝕠𝕣 𝟜", "🔵": "🔵 ℂ𝕠𝕝𝕠𝕣 𝟝", "🟣": "🟣 ℂ𝕠𝕝𝕠𝕣 𝟞", "🟤": "🟤 ℂ𝕠𝕝𝕠𝕣 𝟟", "⚫": "⚫ ℂ𝕠𝕝𝕠𝕣 𝟠", "🤍": "🤍 ℂ𝕠𝕝𝕠𝕣 𝟡", "💖": "💖 ℂ𝕠𝕝𝕠𝕣 𝟙𝟘"}
}

MY_GUILD = discord.Object(id=ID_SERVIDOR)

class SantuariBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        intents.reactions = True 
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = None

    async def setup_hook(self):
        mongo_uri = os.environ.get("MONGO_URI")
        if mongo_uri:
            cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, tlsCAFile=certifi.where())
            self.db = cluster["SantuariDB"] 
            print("💾 Bóveda de MongoDB conectada exitosamente con SSL validado.")
            await self._iniciar_tienda()
        else:
            print("⚠️ ADVERTENCIA: No se encontró la MONGO_URI.")

        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("🏛️ Comandos sincronizados al instante en el Imperio.")

    async def _iniciar_tienda(self):
        if self.db is not None:
            # 🧹 PURGA TOTAL DE USUARIOS SOLICITADA - RESET COMPLETO A 0
            await self.db["usuarios"].drop()
            print("🧹 Base de datos de usuarios completamente destruida y reiniciada a 0.")

            tienda = self.db["tienda"]
            if await tienda.count_documents({}) == 0:
                await tienda.insert_many([
                    {"_id": "Emoji Custom", "precio": 200, "descripcion": "Un emoji personalizado a tu elección."},
                    {"_id": "Sticker Custom", "precio": 300, "descripcion": "Un sticker personalizado a tu elección."}
                ])
                print("🛍️ Tienda inicializada con artículos base.")

bot = SantuariBot()

# =========================================================================
# 🎭 EVENTOS Y COMPROBACIONES DE REACCIONES CRUDAS
# =========================================================================

@bot.event
async def on_member_join(member):
    rol = member.guild.get_role(ID_ROL_AUTOROL)
    if rol:
        await member.add_roles(rol)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id or bot.db is None:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild: return
    member = guild.get_member(payload.user_id)
    if not member: return

    emoji_str = str(payload.emoji)

    # 🚪 SECCIÓN A: Auto-roles Persistentes desde MongoDB Atlas
    autorole_data = await bot.db["autoroles_mensajes"].find_one({"_id": payload.message_id})
    if autorole_data:
        mapeo = autorole_data.get("mapeo", {})
        if emoji_str in mapeo:
            nombre_rol = mapeo[emoji_str]
            rol = discord.utils.get(guild.roles, name=nombre_rol)
            if rol:
                await member.add_roles(rol)
        return

    # ⭐ SECCIÓN B: Sistema General de Starboard
    if emoji_str == "⭐":
        canal = bot.get_channel(payload.channel_id)
        mensaje = await canal.fetch_message(payload.message_id)
        if mensaje.author.bot: 
            return

        reaccion = discord.utils.get(mensaje.reactions, emoji="⭐")
        if reaccion and reaccion.count >= 3:
            starboard_col = bot.db["starboard"]
            ya_publicado = await starboard_col.find_one({"_id": mensaje.id})
            
            if not ya_publicado:
                canal_starboard = bot.get_channel(ID_CANAL_STARBOARD)
                if canal_starboard:
                    embed = discord.Embed(description=mensaje.content, color=discord.Color.gold())
                    embed.set_author(name=mensaje.author.display_name, icon_url=mensaje.author.display_avatar.url)
                    embed.add_field(name="Enlace", value=f"[Ir al mensaje]({mensaje.jump_url})")
                    if mensaje.attachments:
                        embed.set_image(url=mensaje.attachments[0].url)
                    await canal_starboard.send(content=f"⭐ **{reaccion.count}** en {canal.mention}", embed=embed)
                    await starboard_col.insert_one({"_id": mensaje.id})

@bot.event
async def on_raw_reaction_remove(payload):
    if bot.db is None: return
    
    guild = bot.get_guild(payload.guild_id)
    if not guild: return
    member = guild.get_member(payload.user_id)
    if not member: return

    emoji_str = str(payload.emoji)

    # Remover roles si remueven la reacción en los paneles guardados
    autorole_data = await bot.db["autoroles_mensajes"].find_one({"_id": payload.message_id})
    if autorole_data:
        mapeo = autorole_data.get("mapeo", {})
        if emoji_str in mapeo:
            nombre_rol = mapeo[emoji_str]
            rol = discord.utils.get(guild.roles, name=nombre_rol)
            if rol:
                await member.remove_roles(rol)

# =========================================================================
# 📈 SISTEMA RPG DE CHAT Y MONEDAS (BLINDADO CONTRA DMs)
# =========================================================================

@bot.event
async def on_message(message):
    # Ignorar DMs y mensajes de otros autómatas
    if message.guild is None or message.author.bot:
        return

    if bot.db is None:
        return

    # RECOMPENSA POR BUMP (Disboard)
    if message.author.id == ID_BOT_BUMP and message.interaction:
        usuario_bump = message.interaction.user
        if "Bump done!" in message.embeds[0].description or "Bump efectuado" in message.embeds[0].description:
            recompensa = 50
            await bot.db["usuarios"].update_one({"_id": usuario_bump.id}, {"$inc": {"monedas": recompensa}}, upsert=True)
            await message.channel.send(f"📢 ¡Gracias por hacer Bump, {usuario_bump.mention}! Has recibido **{recompensa} 🪙**.")
        return

    miembro = message.author
    coleccion_usuarios = bot.db["usuarios"]
    datos_usuario = await coleccion_usuarios.find_one({"_id": miembro.id})
    
    if not datos_usuario:
        datos_usuario = {"_id": miembro.id, "xp": 0, "nivel": 1, "monedas": 0}

    nuevo_nivel = datos_usuario.get("nivel", 1)
    
    if nuevo_nivel >= 100:
        return

    # Ritmo de ganancia de XP equilibrado
    xp_ganada = random.randint(10, 20)
    nueva_xp = datos_usuario.get("xp", 0) + xp_ganada

    # Curva matemática exponencial: Lenta tras nivel 5
    if nuevo_nivel < 5:
        xp_necesaria = nuevo_nivel * 120
    else:
        xp_necesaria = int((nuevo_nivel ** 2.2) * 45)

    if nueva_xp >= xp_necesaria:
        nuevo_nivel += 1
        nueva_xp -= xp_necesaria
        await message.channel.send(f"🎖️ ¡{miembro.mention} ascendió al nivel **{nuevo_nivel}**!")

        # Otorgar rangos honoríficos dinámicos basados en el nombre
        if nuevo_nivel in ROLES_NIVEL:
            nombre_rol = ROLES_NIVEL[nuevo_nivel]
            rol_a_dar = discord.utils.get(message.guild.roles, name=nombre_rol)
            if rol_a_dar:
                await miembro.add_roles(rol_a_dar)
                await message.channel.send(f"⚔️ ¡Se le ha otorgado el rango honorífico **{rol_a_dar.name}** a {miembro.mention}!")

    # Probabilidad de recolección de monedas
    es_congresista = any(rol.id == ID_ROL_CONGRESISTA for rol in miembro.roles) if hasattr(miembro, 'roles') else False
    probabilidad = 0.15 if es_congresista else 0.05
    nuevas_monedas = datos_usuario.get("monedas", 0)
    
    if random.random() < probabilidad:
        nuevas_monedas += random.randint(1, 5)
        await message.add_reaction("🪙") 

    await coleccion_usuarios.update_one(
        {"_id": miembro.id},
        {"$set": {"xp": nueva_xp, "nivel": nuevo_nivel, "monedas": nuevas_monedas}},
        upsert=True
    )

# =========================================================================
# 💰 COMANDOS ECONÓMICOS INTERACTIVOS
# =========================================================================

@bot.tree.command(name="perfil", description="Mira tu estatus en el Imperio.")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    if bot.db is None: return await interaction.response.send_message("❌ Bóveda cerrada.", ephemeral=True)
    usuario_obj = usuario or interaction.user
    datos = await bot.db["usuarios"].find_one({"_id": usuario_obj.id})
    if not datos: return await interaction.response.send_message(f"📜 {usuario_obj.display_name} no tiene expediente asignado.")

    embed = discord.Embed(title=f"Perfil de {usuario_obj.display_name}", color=discord.Color.gold())
    embed.add_field(name="🎖️ Nivel", value=str(datos.get("nivel", 1)))
    embed.add_field(name="🪙 Billetera", value=f"{datos.get('monedas', 0)} 🪙")
    embed.set_thumbnail(url=usuario_obj.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dar", description="Transfiere monedas de tu saldo a otro ciudadano.")
async def dar(interaction: discord.Interaction, objetivo: discord.Member, cantidad: int):
    if bot.db is None: return await interaction.response.send_message("❌ Bóveda cerrada.", ephemeral=True)
    if cantidad <= 0: return await interaction.response.send_message("❌ Cantidad inválida.", ephemeral=True)
    if objetivo.id == interaction.user.id: return await interaction.response.send_message("❌ No puedes darte dinero a ti mismo.", ephemeral=True)

    remitente = await bot.db["usuarios"].find_one({"_id": interaction.user.id})
    if not remitente or remitente.get("monedas", 0) < cantidad:
        return await interaction.response.send_message("💸 No posees suficientes fondos.", ephemeral=True)

    await bot.db["usuarios"].update_one({"_id": interaction.user.id}, {"$inc": {"monedas": -cantidad}})
    await bot.db["usuarios"].update_one({"_id": objetivo.id}, {"$inc": {"monedas": cantidad}}, upsert=True)
    await interaction.response.send_message(f"🤝 {interaction.user.mention} le ha transferido **{cantidad} 🪙** a {objetivo.mention}.")

@bot.tree.command(name="robar", description="Intenta saquear la billetera de otro usuario (Riesgo alto).")
async def robar(interaction: discord.Interaction, objetivo: discord.Member):
    if bot.db is None: return await interaction.response.send_message("❌ Bóveda cerrada.", ephemeral=True)
    if objetivo.id == interaction.user.id: return await interaction.response.send_message("❌ No puedes robarte a ti mismo.", ephemeral=True)
    if objetivo.bot: return await interaction.response.send_message("❌ No puedes robarle a un autómata.", ephemeral=True)

    victima_data = await bot.db["usuarios"].find_one({"_id": objetivo.id})
    if not victima_data or victima_data.get("monedas", 0) < 10:
        return await interaction.response.send_message("💸 La víctima está en la miseria, no vale la pena el riesgo.", ephemeral=True)

    ladron_data = await bot.db["usuarios"].find_one({"_id": interaction.user.id})
    multa = random.randint(15, 30)

    if not ladron_data or ladron_data.get("monedas", 0) < multa:
        return await interaction.response.send_message(f"🚨 No tienes suficiente capital para pagar la fianza si fallas (Mínimo: {multa} 🪙).", ephemeral=True)

    # 🎲 Éxito del 40%
    if random.random() < 0.40:
        porcentaje_robado = random.uniform(0.10, 0.35)
        botin = int(victima_data.get("monedas", 0) * porcentaje_robado)
        if botin < 1: botin = 1

        await bot.db["usuarios"].update_one({"_id": objetivo.id}, {"$inc": {"monedas": -botin}})
        await bot.db["usuarios"].update_one({"_id": interaction.user.id}, {"$inc": {"monedas": botin}})
        await interaction.response.send_message(f"🥷 ¡ÉXITO! {interaction.user.mention} asaltó a {objetivo.mention} en un callejón y huyó con **{botin} 🪙**.")
    else:
        await bot.db["usuarios"].update_one({"_id": interaction.user.id}, {"$inc": {"monedas": -multa}})
        await bot.db["usuarios"].update_one({"_id": objetivo.id}, {"$inc": {"monedas": multa}})
        await interaction.response.send_message(f"🚨 ¡FRACASO! Descubrieron a {interaction.user.mention} robando a {objetivo.mention}. Pagó una fianza forzada de **{multa} 🪙**.")

# =========================================================================
# 🛡️ COMANDOS DE MODERACIÓN IMPERIAL
# =========================================================================

@bot.tree.command(name="mute", description="Silencia temporalmente a un infractor mediante aislamiento.")
@app_commands.default_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, infractor: discord.Member, minutos: int, motivo: str = "Infracción de las leyes imperiales."):
    duracion = datetime.timedelta(minutes=minutos)
    
    try:
        embed_dm = discord.Embed(title="⚠️ Has sido aislado temporalmente", color=discord.Color.orange())
        embed_dm.add_field(name="Servidor", value=interaction.guild.name)
        embed_dm.add_field(name="Duración", value=f"{minutos} minutos")
        embed_dm.add_field(name="Motivo", value=motivo)
        await infractor.send(embed=embed_dm)
    except:
        pass 

    await infractor.timeout(duracion, reason=motivo)
    await interaction.response.send_message(f"🤫 **{infractor.display_name}** ha sido aislado por {minutos} minutos. Motivo: {motivo}")

@bot.tree.command(name="ban", description="Destierra permanentemente a un usuario del Imperio.")
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, infractor: discord.Member, motivo: str = "Traición al Imperio."):
    try:
        embed_dm = discord.Embed(title="🚫 Has sido desterrado", color=discord.Color.red())
        embed_dm.add_field(name="Servidor", value=interaction.guild.name)
        embed_dm.add_field(name="Motivo", value=motivo)
        await infractor.send(embed=embed_dm)
    except:
        pass

    await infractor.ban(reason=motivo)
    await interaction.response.send_message(f"🔨 **{infractor.display_name}** ha sido desterrado permanentemente del servidor. Motivo: {motivo}")

@bot.tree.command(name="purge", description="Purga un número masivo de mensajes del canal.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, cantidad: int):
    if cantidad <= 0 or cantidad > 100:
        return await interaction.response.send_message("❌ La purga debe ser de entre 1 y 100 mensajes simultáneos.", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    eliminados = await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(f"🗑️ Purga completada. Se eliminaron **{len(eliminados)}** mensajes de la historia.", ephemeral=True)

# =========================================================================
# 🎭 PANALES DE REACCIÓN PERSISTENTES CON MONGODB
# =========================================================================

@bot.tree.command(name="desplegar_autoroles", description="[ADMIN] Despliega los paneles de auto-roles por reacción vinculados a MongoDB.")
@app_commands.default_permissions(administrator=True)
async def desplegar_autoroles(interaction: discord.Interaction):
    if bot.db is None: 
        return await interaction.response.send_message("❌ Sin conexión a la Bóveda.", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    canal = interaction.channel
    coleccion_msg = bot.db["autoroles_mensajes"]

    async def generar_bloque(titulo, color, diccionario_mapeo):
        desc = "Reacciona al emoji correspondiente para reclamar tu identidad dentro del Imperio:\n\n"
        for emoji, nombre_rol in diccionario_mapeo.items():
            desc += f"{emoji} ➔ **{nombre_rol}**\n"
        
        embed = discord.Embed(title=titulo, color=color, description=desc)
        msg = await canal.send(embed=embed)
        
        for emoji in diccionario_mapeo.keys():
            await msg.add_reaction(emoji)
        
        await coleccion_msg.update_one(
            {"_id": msg.id},
            {"$set": {"mapeo": diccionario_mapeo}},
            upsert=True
        )

    await generar_bloque("🌎 Ministerio de Fronteras: Tu Región", 0x1982C4, DICCIONARIO_AUTOROLES["Regiones"])
    await generar_bloque("⏳ Ministerio del Tiempo: Tu Edad", 0xFF8C00, DICCIONARIO_AUTOROLES["Edades"])
    await generar_bloque("⚧️ Ministerio de Identidad: Género", 0xFF9ED2, DICCIONARIO_AUTOROLES["Generos"])
    await generar_bloque("🗣️ Ministerio de Identidad: Pronombres", 0x8AC926, DICCIONARIO_AUTOROLES["Pronombres"])
    await generar_bloque("🌈 Ministerio de Identidad: Orientación", 0x6A4C93, DICCIONARIO_AUTOROLES["Sexualidades"])
    await generar_bloque("📚 Clasificación de Intereses", 0x2E8B57, DICCIONARIO_AUTOROLES["Nichos"])
    await generar_bloque("🎨 Paleta del Régimen: Colores", 0xFFD700, DICCIONARIO_AUTOROLES["Colores"])

    await interaction.followup.send("✅ Todos los bloques de auto-roles han sido desplegados y asegurados en MongoDB.", ephemeral=True)

# =========================================================================
# 🛍️ MERCADO IMPERIAL
# =========================================================================

@bot.tree.command(name="tienda", description="Mercado Imperial.")
async def tienda(interaction: discord.Interaction):
    if bot.db is None: return await interaction.response.send_message("❌ Bóveda cerrada.", ephemeral=True)
    objetos = await bot.db["tienda"].find().to_list(length=100)
    embed = discord.Embed(title="🛍️ Tienda de Santuari", description="Usa `/comprar <nombre>`", color=discord.Color.purple())
    for obj in objetos:
        embed.add_field(name=f"🏷️ {obj['_id']}", value=f"**{obj['precio']} 🪙** - {obj['descripcion']}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="comprar", description="Compra un objeto.")
@app_commands.describe(objeto="Nombre exacto del objeto.")
async def comprar(interaction: discord.Interaction, objeto: str):
    if bot.db is None: return await interaction.response.send_message("❌ Bóveda cerrada.", ephemeral=True)
    item = await bot.db["tienda"].find_one({"_id": objeto})
    if not item: return await interaction.response.send_message("❌ Objeto inexistente.", ephemeral=True)

    comprador = await bot.db["usuarios"].find_one({"_id": interaction.user.id})
    if not comprador or comprador.get("monedas", 0) < item["precio"]:
        return await interaction.response.send_message("💸 Monedas insuficientes.", ephemeral=True)

    await bot.db["usuarios"].update_one({"_id": interaction.user.id}, {"$inc": {"monedas": -item["precio"]}})
    await interaction.response.send_message(f"🎉 **{interaction.user.display_name}** compró `{objeto}`.")
    await interaction.channel.send(f"🔔 <@{ID_CANCILLER}>, debes gestionar la entrega de `{objeto}` para {interaction.user.mention}.")

token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERROR CRÍTICO: No se encontró el DISCORD_TOKEN.")
