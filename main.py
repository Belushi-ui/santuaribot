import discord
from discord import app_commands
import os
import random
import motor.motor_asyncio

# =========================================================================
# ⚙️ CONFIGURACIÓN IMPERIAL
# =========================================================================
# 1. El ID de los Congresistas (para darles más probabilidad de monedas)
ID_ROL_CONGRESISTA = 1518298258382913748 

# 2. Los IDs de los roles que son INMUNES a la automoderación
ROLES_INMUNES = [
    ID_ROL_CONGRESISTA,
    1518298257581936861, # Reemplaza con el ID del rol Moderador
    1518298253181845685  # Reemplaza con el ID del rol Élite
]

class SantuariBot(discord.Client):
    def __init__(self):
        # Activamos los intents necesarios para leer mensajes y ver miembros
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = None # Aquí vivirá nuestra base de datos

    async def setup_hook(self):
        # Conexión a la Bóveda de MongoDB Atlas
        mongo_uri = os.environ.get("MONGO_URI")
        if mongo_uri:
            cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            self.db = cluster["SantuariDB"] 
            print("💾 Bóveda de MongoDB conectada exitosamente.")
        else:
            print("⚠️ ADVERTENCIA: No se encontró la MONGO_URI en las variables de entorno.")

        # Sincronizar comandos de barra
        await self.tree.sync()
        print("🏛️ Comandos sincronizados. ¡Santuari está listo para forjar historia!")

bot = SantuariBot()

# =========================================================================
# 🛡️ EVENTOS PRINCIPALES (Motor Base y Automoderación)
# =========================================================================

@bot.event
async def on_message(message):
    # Ignorar a otros bots y a sí mismo
    if message.author.bot:
        return

    # 1. AUTOMODERACIÓN CON INMUNIDAD DIPLOMÁTICA
    es_inmune = (
        message.author.id == message.guild.owner_id or # Tú (la Canciller) eres intocable
        message.author.guild_permissions.administrator or # Administradores generales
        any(rol.id in ROLES_INMUNES for rol in message.author.roles) # Roles VIP de la lista
    )

    if not es_inmune:
        palabras_prohibidas = ["spamlink.com", "insulto1", "insulto2"] # Edita tus palabras aquí
        if any(palabra in message.content.lower() for palabra in palabras_prohibidas):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, ese vocabulario o enlace no está permitido en el Imperio.", delete_after=5)
            except discord.errors.Forbidden:
                pass
            return # Detiene el código para que el infractor no gane XP ni monedas

    # Verificar que la base de datos esté activa antes de procesar XP
    if bot.db is None:
        return

    coleccion_usuarios = bot.db["usuarios"]

    # 2. BUSCAR O CREAR USUARIO EN LA BÓVEDA
    datos_usuario = await coleccion_usuarios.find_one({"_id": message.author.id})
    if not datos_usuario:
        datos_usuario = {"_id": message.author.id, "xp": 0, "nivel": 1, "monedas": 0, "likes": 0}
        await coleccion_usuarios.insert_one(datos_usuario)

    # 3. SISTEMA DE EXPERIENCIA Y NIVELES
    xp_ganada = random.randint(15, 25)
    nueva_xp = datos_usuario.get("xp", 0) + xp_ganada
    xp_necesaria = datos_usuario.get("nivel", 1) * 100 
    nuevo_nivel = datos_usuario.get("nivel", 1)

    if nueva_xp >= xp_necesaria:
        nuevo_nivel += 1
        nueva_xp -= xp_necesaria
        await message.channel.send(f"🎖️ ¡Gloria al Imperio! {message.author.mention} ha subido al nivel **{nuevo_nivel}**.")

    # 4. SISTEMA DE PROBABILIDAD DE MONEDAS
    probabilidad = 0.05 # Probabilidad base: 5%
    
    # Bono imperial: Si es congresista, sube al 15%
    es_congresista = any(rol.id == ID_ROL_CONGRESISTA for rol in message.author.roles)
    if es_congresista:
        probabilidad = 0.15

    nuevas_monedas = datos_usuario.get("monedas", 0)
    if random.random() < probabilidad:
        monedas_encontradas = random.randint(1, 5)
        nuevas_monedas += monedas_encontradas
        await message.add_reaction("🪙") 

    # 5. ACTUALIZAR EXPEDIENTE
    await coleccion_usuarios.update_one(
        {"_id": message.author.id},
        {"$set": {"xp": nueva_xp, "nivel": nuevo_nivel, "monedas": nuevas_monedas}}
    )

# =========================================================================
# 💰 COMANDOS DE PERFIL Y REPUTACIÓN
# =========================================================================

@bot.tree.command(name="perfil", description="Mira tu nivel, monedas y likes en el Imperio.")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario_objetivo = usuario or interaction.user
    
    if bot.db is None:
        await interaction.response.send_message("❌ La bóveda está desconectada en este momento.", ephemeral=True)
        return

    datos = await bot.db["usuarios"].find_one({"_id": usuario_objetivo.id})
    if not datos:
        await interaction.response.send_message(f"📜 {usuario_objetivo.display_name} aún no tiene registros en el Imperio.")
        return

    embed = discord.Embed(title=f"Perfil Imperial de {usuario_objetivo.display_name}", color=discord.Color.gold())
    embed.add_field(name="🎖️ Nivel", value=str(datos.get("nivel", 1)), inline=True)
    embed.add_field(name="✨ XP", value=str(datos.get("xp", 0)), inline=True)
    embed.add_field(name="🪙 Monedas", value=str(datos.get("monedas", 0)), inline=True)
    embed.add_field(name="❤️ Likes", value=str(datos.get("likes", 0)), inline=True)
    embed.set_thumbnail(url=usuario_objetivo.display_avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="like", description="Dale un like a otro ciudadano del Imperio.")
async def like(interaction: discord.Interaction, usuario: discord.Member):
    if usuario.id == interaction.user.id:
        return await interaction.response.send_message("❌ No puedes darte like a ti mismo.", ephemeral=True)
    if usuario.bot:
        return await interaction.response.send_message("❌ Los bots no coleccionamos likes, solo código.", ephemeral=True)
    if bot.db is None:
        return await interaction.response.send_message("❌ Sin conexión a la bóveda.", ephemeral=True)

    col_usuarios = bot.db["usuarios"]
    
    receptor = await col_usuarios.find_one({"_id": usuario.id})
    if not receptor:
        await col_usuarios.insert_one({"_id": usuario.id, "xp": 0, "nivel": 1, "monedas": 0, "likes": 0})

    await col_usuarios.update_one({"_id": usuario.id}, {"$inc": {"likes": 1}})
    await interaction.response.send_message(f"💖 Le has dado un like a {usuario.mention}. ¡Qué excelente gesto!")

# =========================================================================
# 🛍️ SISTEMA DE TIENDA IMPERIAL
# =========================================================================

@bot.tree.command(name="tienda", description="Mira los objetos disponibles en el Mercado Imperial.")
async def tienda(interaction: discord.Interaction):
    if bot.db is None:
        await interaction.response.send_message("❌ La tienda está cerrada por mantenimiento de la bóveda.", ephemeral=True)
        return

    objetos = await bot.db["tienda"].find().to_list(length=100)
    
    if not objetos:
        await interaction.response.send_message("🕸️ La tienda está vacía por ahora. ¡Vuelve más tarde!")
        return

    embed = discord.Embed(title="🛍️ Mercado del Imperio Santuari", description="Usa `/comprar <nombre_objeto>` para adquirir algo.", color=discord.Color.purple())
    for obj in objetos:
        descripcion = obj.get('descripcion', 'Sin descripción')
        precio = obj.get('precio', 0)
        embed.add_field(name=f"🏷️ {obj['_id']}", value=f"**Costo:** {precio} 🪙\n*{descripcion}*", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="comprar", description="Compra un objeto de la tienda con tus monedas.")
@app_commands.describe(objeto="El nombre exacto del objeto que quieres comprar")
async def comprar(interaction: discord.Interaction, objeto: str):
    if bot.db is None:
        return await interaction.response.send_message("❌ Error de conexión con la bóveda.", ephemeral=True)

    col_usuarios = bot.db["usuarios"]
    col_tienda = bot.db["tienda"]

    item = await col_tienda.find_one({"_id": objeto})
    if not item:
        return await interaction.response.send_message(f"❌ El objeto `{objeto}` no existe en la tienda.", ephemeral=True)

    comprador = await col_usuarios.find_one({"_id": interaction.user.id})
    if not comprador or comprador.get("monedas", 0) < item["precio"]:
        return await interaction.response.send_message("💸 No tienes suficientes monedas para comprar esto.", ephemeral=True)

    await col_usuarios.update_one({"_id": interaction.user.id}, {"$inc": {"monedas": -item["precio"]}})
    await interaction.response.send_message(f"🎉 ¡Felicidades! Has comprado **{objeto}** por {item['precio']} 🪙. Guárdalo bien.")

# =========================================================================
# 👑 COMANDOS DE LA CANCILLER (Solo Administradores)
# =========================================================================

@bot.tree.command(name="tienda_añadir", description="[ADMIN] Añade o actualiza un objeto en la tienda.")
@app_commands.default_permissions(administrator=True)
async def tienda_añadir(interaction: discord.Interaction, nombre: str, precio: int, descripcion: str):
    if bot.db is None:
        return await interaction.response.send_message("❌ Sin conexión.", ephemeral=True)
        
    await bot.db["tienda"].update_one(
        {"_id": nombre},
        {"$set": {"precio": precio, "descripcion": descripcion}},
        upsert=True 
    )
    await interaction.response.send_message(f"✅ Objeto `{nombre}` añadido/actualizado en la tienda por {precio} 🪙.", ephemeral=True)

@bot.tree.command(name="tienda_eliminar", description="[ADMIN] Elimina un objeto de la tienda.")
@app_commands.default_permissions(administrator=True)
async def tienda_eliminar(interaction: discord.Interaction, nombre: str):
    if bot.db is None:
        return await interaction.response.send_message("❌ Sin conexión.", ephemeral=True)

    resultado = await bot.db["tienda"].delete_one({"_id": nombre})
    if resultado.deleted_count > 0:
        await interaction.response.send_message(f"🗑️ Objeto `{nombre}` eliminado de la tienda de forma permanente.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ No se encontró el objeto `{nombre}`.", ephemeral=True)

# =========================================================================
# 🚀 INICIO DEL BOT
# =========================================================================
# TEMPORAL: Cambio para probar conexión
token = os.environ.get("MTUxODEzMzM3MjA2MzMxODE2Nw.Gjg-Iq.UEvsOxKd1L5Zeqf_a2L1mo-YqUYrgINdoD2SjY")
if token:
    bot.run(token)
else:
    print("❌ ERROR CRÍTICO: No se encontró el DISCORD_TOKEN en las variables de entorno.")
    print("❌ ERROR CRÍTICO: No se encontró el DISCORD_TOKEN.")
