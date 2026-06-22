import discord
from discord import app_commands
import os
import random
import motor.motor_asyncio
import certifi  # 🛡️ Mantener importado para romper el bloqueo SSL

# =========================================================================
# ⚙️ CONFIGURACIÓN IMPERIAL (¡LLENA ESTOS DATOS!)
# =========================================================================
ID_SERVIDOR = 1517885569231749240        # ID de tu servidor
ID_CANCILLER = 1518298260479938783       # Tu ID personal de Discord
ID_ROL_AUTOROL = 1518298254767427855     # ID del rol que se da al entrar al servidor
ID_CANAL_STARBOARD = 1518298279715017016 # ID del canal donde irán los mensajes estrella
ID_BOT_BUMP = 302050872383242240         # ID de Disboard

ID_ROL_CONGRESISTA = 1518298258382913748 # ROL VIP para más monedas

ROLES_INMUNES = [
    ID_ROL_CONGRESISTA,
    1518298257581936861, # Moderador
    1518298253181845685  # Élite
]

PALABRAS_PROHIBIDAS = ["spamlink.com", "scam", "insulto_fuerte"]

MY_GUILD = discord.Object(id=ID_SERVIDOR)

class SantuariBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Vital para el autorol
        intents.reactions = True # Vital para el Starboard
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = None

    async def setup_hook(self):
        # Conexión a la Bóveda de MongoDB
        mongo_uri = os.environ.get("MONGO_URI")
        if mongo_uri:
            # 🛡️ PARCHE APLICADO: Forzamos el uso de certifi para evitar fallos de TLS en Railway
            cluster = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_uri,
                tlsCAFile=certifi.where()
            )
            self.db = cluster["SantuariDB"] 
            print("💾 Bóveda de MongoDB connected exitosamente con SSL validado.")
            await self._iniciar_tienda()
        else:
            print("⚠️ ADVERTENCIA: No se encontró la MONGO_URI.")

        # Sincronización INSTANTÁNEA en tu servidor
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("🏛️ Comandos sincronizados al instante en el Imperio.")

    async def _iniciar_tienda(self):
        # Asegura que la tienda empiece con los objetos base
        if self.db is not None:
            tienda = self.db["tienda"]
            if await tienda.count_documents({}) == 0:
                await tienda.insert_many([
                    {"_id": "Emoji Custom", "precio": 200, "descripcion": "Un emoji personalizado a tu elección."},
                    {"_id": "Sticker Custom", "precio": 300, "descripcion": "Un sticker personalizado a tu elección."}
                ])
                print("🛍️ Tienda inicializada con artículos base.")

bot = SantuariBot()

# =========================================================================
# 🛡️ EVENTOS AUTOMÁTICOS
# =========================================================================

@bot.event
async def on_member_join(member):
    # AUTOROL: Da el rol automáticamente cuando alguien entra
    rol = member.guild.get_role(ID_ROL_AUTOROL)
    if rol:
        await member.add_roles(rol)

@bot.event
async def on_raw_reaction_add(payload):
    # STARBOARD: 3 estrellas para destacar
    if str(payload.emoji) != "⭐" or bot.db is None:
        return

    canal = bot.get_channel(payload.channel_id)
    mensaje = await canal.fetch_message(payload.message_id)
    
    if mensaje.author.bot: # Ignorar mensajes de bots
        return

    # Contar estrellas
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
                await starboard_col.insert_one({"_id": mensaje.id}) # Marca como publicado

@bot.event
async def on_message(message):
    if bot.db is None:
        return

    # RECOMPENSA POR BUMP (Disboard)
    if message.author.id == ID_BOT_BUMP and message.interaction:
        usuario_bump = message.interaction.user
        if "Bump done!" in message.embeds[0].description or "Bump efectuado" in message.embeds[0].description:
            recompensa = 50 # Monedas por el bump
            await bot.db["usuarios"].update_one(
                {"_id": usuario_bump.id}, 
                {"$inc": {"monedas": recompensa}}, 
                upsert=True
            )
            await message.channel.send(f"📢 ¡Gracias por hacer Bump, {usuario_bump.mention}! Has recibido **{recompensa} 🪙**.")
        return

    if message.author.bot:
        return

    # 1. MODERACIÓN Y FILTRO
    es_inmune = (
        message.author.id == message.guild.owner_id or 
        message.author.guild_permissions.administrator or 
        any(rol.id in ROLES_INMUNES for rol in message.author.roles)
    )

    if not es_inmune:
        if any(palabra in message.content.lower() for palabra in PALABRAS_PROHIBIDAS):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, cuidado con lo que hablas. Eso no está permitido.", delete_after=5)
            except discord.errors.Forbidden:
                pass
            return 

    # 2. ECONOMÍA BASE (XP y Monedas aleatorias)
    coleccion_usuarios = bot.db["usuarios"]
    datos_usuario = await coleccion_usuarios.find_one({"_id": message.author.id})
    if not datos_usuario:
        datos_usuario = {"_id": message.author.id, "xp": 0, "nivel": 1, "monedas": 0, "likes": 0}

    xp_ganada = random.randint(15, 25)
    nueva_xp = datos_usuario.get("xp", 0) + xp_ganada
    nuevo_nivel = datos_usuario.get("nivel", 1)
    xp_necesaria = nuevo_nivel * 100 

    if nueva_xp >= xp_necesaria:
        nuevo_nivel += 1
        nueva_xp -= xp_necesaria
        await message.channel.send(f"🎖️ ¡{message.author.mention} ascendió al nivel **{nuevo_nivel}**!")

    # Probabilidad de encontrar moneda
    probabilidad = 0.15 if any(rol.id == ID_ROL_CONGRESISTA for rol in message.author.roles) else 0.05
    nuevas_monedas = datos_usuario.get("monedas", 0)
    
    if random.random() < probabilidad:
        nuevas_monedas += random.randint(1, 5)
        await message.add_reaction("🪙") 

    await coleccion_usuarios.update_one(
        {"_id": message.author.id},
        {"$set": {"xp": nueva_xp, "nivel": nuevo_nivel, "monedas": nuevas_monedas}},
        upsert=True
    )

# =========================================================================
# 💰 COMANDOS GLOBALES
# =========================================================================

@bot.tree.command(name="perfil", description="Mira tu estatus en el Imperio.")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    if bot.db is None: return await interaction.response.send_message("❌ Bóveda cerrada.", ephemeral=True)
    usuario_obj = usuario or interaction.user
    datos = await bot.db["usuarios"].find_one({"_id": usuario_obj.id})
    if not datos: return await interaction.response.send_message(f"📜 {usuario_obj.display_name} no tiene expediente.")

    embed = discord.Embed(title=f"Perfil de {usuario_obj.display_name}", color=discord.Color.gold())
    embed.add_field(name="🎖️ Nivel", value=str(datos.get("nivel", 1)))
    embed.add_field(name="🪙 Monedas", value=str(datos.get("monedas", 0)))
    embed.add_field(name="❤️ Likes", value=str(datos.get("likes", 0)))
    embed.set_thumbnail(url=usuario_obj.display_avatar.url)
    await interaction.response.send_message(embed=embed)

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

    # Restar monedas
    await bot.db["usuarios"].update_one({"_id": interaction.user.id}, {"$inc": {"monedas": -item["precio"]}})
    
    # Mensaje de éxito y PING a la Canciller
    await interaction.response.send_message(f"🎉 **{interaction.user.display_name}** compró `{objeto}`.")
    await interaction.channel.send(f"🔔 <@{ID_CANCILLER}>, debes gestionar la entrega de `{objeto}` para {interaction.user.mention}.")

# =========================================================================
# 👑 COMANDOS DE ADMINISTRACIÓN
# =========================================================================

@bot.tree.command(name="tienda_añadir", description="[ADMIN] Añade/Actualiza la tienda.")
@app_commands.default_permissions(administrator=True)
async def tienda_añadir(interaction: discord.Interaction, nombre: str, precio: int, descripcion: str):
    if bot.db is None: return await interaction.response.send_message("❌ Sin conexión.", ephemeral=True)
    await bot.db["tienda"].update_one({"_id": nombre}, {"$set": {"precio": precio, "descripcion": descripcion}}, upsert=True)
    await interaction.response.send_message(f"✅ Objeto `{nombre}` guardado por {precio} 🪙.", ephemeral=True)

@bot.tree.command(name="tienda_eliminar", description="[ADMIN] Quita un objeto.")
@app_commands.default_permissions(administrator=True)
async def tienda_eliminar(interaction: discord.Interaction, nombre: str):
    if bot.db is None: return await interaction.response.send_message("❌ Sin conexión.", ephemeral=True)
    await bot.db["tienda"].delete_one({"_id": nombre})
    await interaction.response.send_message(f"🗑️ `{nombre}` eliminado.", ephemeral=True)

# =========================================================================
# 🚀 EJECUCIÓN (CON SEGURIDAD)
# =========================================================================
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERROR CRÍTICO: No se encontró el DISCORD_TOKEN.")
