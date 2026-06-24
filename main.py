# =========================================================================
# 🌌 SANTUARI CORE — MOTOR PRINCIPAL DEL IMPERIO (Fase 2 - Versión Final V3.1)
# =========================================================================
# SISTEMAS INTEGRADOS:
# - MongoDB (motor asíncrono) para persistencia total.
# - Niveles Exponenciales y auto-asignación de roles de Nivel (10, 20...).
# - Economía (🪙), Top, Perfil, Donar, Robar, Imprimir Dinero (Owner).
# - Tienda y Objetos (Amuleto de la Suerte, Mutes, Emojis).
# - Casino (Ruleta, Dados encriptados).
# - Moderación (Kick, Ban, Timeout, Warn, Purge) y Starboard (Corregido).
# - Sistema de Autoroles Interactivos y Asignación de Roles por Lotes.
# - Eventos de "Lluvia de Monedas" con Botón Anti-Spam / Anti-Lag.
# =========================================================================

import discord
from discord import app_commands
import motor.motor_asyncio
import os
import sys
import random
import time
import asyncio
import re
import secrets
from datetime import timedelta

# --- CONFIGURACIÓN DE IDs ---
ID_SERVIDOR = 1517885569231749240
ID_DUEÑO = 1360882776706125874
ID_CANAL_STARBOARD = 1518814340919328858
ID_CANAL_MODLOGS = 1518762621937909862 
ID_CANAL_AUTOROLES = 1518804287835345198

PRECIO_MUTE = 2000
PRECIO_AMULETO = 1000
PRECIO_EMOJI = 5000
PRECIO_STICKER = 5000

# Diccionario Global de Emojis -> ID de Rol
ROLES_REACCION = {
    # 🧬 Géneros
    "👨": 1518762591340724374,  # Hombre
    "👩": 1518762591969743016,  # Mujer
    "🏳️‍⚧️": 1518762592917520535,  # Transgénero
    "🟡": 1518762594125615124,  # No binarie
    "❓": 1518762595086106766,  # Otro género
    
    # 📢 Pronombres
    "🔹": 1518762607400587325,  # She/Her
    "🔸": 1518762608159756392,  # He/Him
    "▫️": 1518762608688103627,  # They/Them
    
    # ❤️ Orientación
    "🤍": 1518762598965973012,  # Heterosexual
    "🧡": 1518762599238467727,  # Lesbiana
    "💗": 151876200781975735,   # Bisexual
    "💙": 1518762601587150918,  # Gay
    "🖤": 1518762604250660884,  # Asexual
    "🤎": 1518762604930138295,  # Alorromántico

    # 🌍 Región
    "🦅": 1518762595744481301,  # Norteamérica
    "🌎": 1518762596210053234,  # Sudamérica
    "🌍": 1518762597405560974,  # Europa
    "🌏": 1518762598261063840,  # Asia

    # 📅 Edad
    "🎒": 1518762613171818626,  # 14-17
    "🎓": 1518762613943701564,  # 18-25
    "💼": 1518762614749008003,  # 26+

    # ⚔️ Ocupaciones
    "🎲": 1518762616942628925,  # Dungeon Master
    "📜": 1518762618649575616,  # Politólogo
    "🖌️": 1518762615508045845,  # Artista
    "⌨️": 1518762615801909369,  # Programador
    "📚": 1518762617542414661,  # Seudo Filósofo

    # 🎨 Colores
    "🔴": 1518762581257617602,  # Carmesí
    "🟠": 1518762582578692137,  # Ámbar
    "🟨": 1518762584151560325,  # Dorado
    "🟢": 1518762584931565598,  # Esmeralda
    "🔵": 1518762585720356916,  # Zafiro
    "🟣": 1518762586693304442,  # Amatista
    "🌸": 1518762587741880361,  # Rosa
    "⚪": 1518762588937126068,  # Marfil
    "⚫": 1518762589709013052,  # Obsidiana
    "🧊": 1518762502753710400,  # Celeste

    # 🕯️ Nichos
    "🐧": 1518762610353246290,  # Linux & Coding
    "🐉": 1518762612417101824,  # Rol & Roll
    "🎨": 1518762611427250378,  # Arte y Filosofia
}

class SantuariBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.cooldowns_xp = {}

    async def setup_hook(self):
        print("[LOG] Iniciando conexión con base de datos...")
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            print("❌ [ERROR CORE] No se encontró la variable de entorno MONGO_URI.")
            sys.exit(1)
            
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.mongo_client.santuari
        
        self.db_users = self.db.usuarios
        self.starboard = self.db.starboard
        
        guild = discord.Object(id=ID_SERVIDOR)
        
        # 1. Copiamos los comandos registrados globalmente en el código hacia tu servidor
        self.tree.copy_global_to(guild=guild)
        
        # 2. Sincronizamos el servidor local. Esto sobreescribe la lista vieja y elimina duplicados
        await self.tree.sync(guild=guild)
        
        print("🏛️ [LOG CORE] Santuari Core cargado. ¡Comandos sincronizados de forma limpia y duplicados eliminados!")

client = SantuariBot()

# =========================================================================
# 🗄️ FUNCIONES DE BASE DE DATOS Y LÓGICA CORE
# =========================================================================

async def get_user_data(user_id: int):
    data = await client.db_users.find_one({"_id": user_id})
    if not data:
        print(f"[LOG DB] Creando nuevo perfil de datos para el usuario ID: {user_id}")
        data = {
            "_id": user_id,
            "xp": 0, "nivel": 1,
            "monedas": 0,
            "mutes_comprados": 0, "mutes_usados_hoy": 0,
            "amuleto": False
        }
        await client.db_users.insert_one(data)
    return data

async def update_user(user_id: int, query: dict):
    await client.db_users.update_one({"_id": user_id}, query, upsert=True)

def calcular_xp_requerida(nivel: int):
    return int(100 * (nivel ** 1.5))

# =========================================================================
# 🎰 VISTAS INTERACTIVAS Y SISTEMA ANTI-LAG DE DROPS
# =========================================================================

class ReclamarDrop(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="¡Reclamar!", style=discord.ButtonStyle.success, emoji="🪙", custom_id="claim_drop_btn")
    async def reclamar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.reclamar.disabled = True
        self.stop() 
        
        await update_user(interaction.user.id, {"$inc": {"monedas": 300}})
        print(f"[LOG DROP] {interaction.user} reclamó exitosamente el drop aleatorio de 300 monedas. Botón bloqueado.")
        
        embed = discord.Embed(
            description=f"🎉 ¡{interaction.user.mention} fue el más rápido y reclamó las **300 🪙**!", 
            color=0xF1C40F
        )
        await interaction.response.edit_message(embed=embed, view=None)

# =========================================================================
# 📩 EVENTOS DEL SERVIDOR (Mensajes, XP, Autoroles, Starboard)
# =========================================================================

@client.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild: return

    if random.random() < 0.03:
        print(f"[LOG EVENTO] Generando drop aleatorio de monedas (3%) en #{message.channel.name}")
        embed = discord.Embed(
            title="🎁 ¡Lluvia de Monedas!", 
            description="Un cargamento de 🪙 **300 Monedas** ha caído del cielo. ¡Sé el primero en presionar el botón!", 
            color=0xF1C40F
        )
        await message.channel.send(embed=embed, view=ReclamarDrop())

    ahora = time.time()
    ultimo_mensaje = client.cooldowns_xp.get(message.author.id, 0)
    
    if ahora - ultimo_mensaje > 60:
        client.cooldowns_xp[message.author.id] = ahora
        xp_ganada = random.randint(15, 25)
        
        user_data = await get_user_data(message.author.id)
        nueva_xp = user_data["xp"] + xp_ganada
        nivel_actual = user_data["nivel"]
        xp_req = calcular_xp_requerida(nivel_actual)

        if nueva_xp >= xp_req:
            nuevo_nivel = nivel_actual + 1
            await update_user(message.author.id, {"$set": {"xp": nueva_xp, "nivel": nuevo_nivel}})
            
            if nuevo_nivel % 10 == 0 and nuevo_nivel <= 100:
                rol_target = discord.utils.find(lambda r: f"Nivel {nuevo_nivel}" in r.name, message.guild.roles)
                if rol_target:
                    try:
                        await message.author.add_roles(rol_target)
                    except discord.Forbidden:
                        print(f"⚠️ [WARN ROLES] No hay permisos para otorgar '{rol_target.name}' a {message.author}")
            
            embed_lvl = discord.Embed(description=f"✨ **{message.author.display_name}** ha alcanzado el **Nivel {nuevo_nivel}**.", color=0x57A773)
            await message.channel.send(embed=embed_lvl, delete_after=10)
        else:
            await update_user(message.author.id, {"$set": {"xp": nueva_xp}})

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return

    if payload.channel_id == ID_CANAL_AUTOROLES:
        guild = client.get_guild(payload.guild_id)
        if not guild: return

        rol_id = ROLES_REACCION.get(payload.emoji.name)
        if rol_id and rol_id != 0:
            rol = guild.get_role(rol_id)
            if rol:
                miembro = guild.get_member(payload.user_id)
                if miembro:
                    try:
                        await miembro.add_roles(rol)
                    except discord.Forbidden:
                        pass
        return 

    if payload.emoji.name == "⭐":
        guild = client.get_guild(payload.guild_id)
        if not guild: return
        
        canal = guild.get_channel(payload.channel_id)
        if not canal: return
        
        try:
            mensaje = await canal.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return 
        
        reaccion_estrella = discord.utils.get(mensaje.reactions, emoji="⭐")
        if not reaccion_estrella or reaccion_estrella.count < 3: return

        star_doc = await client.starboard.find_one({"msg_id": mensaje.id})
        canal_starboard = guild.get_channel(ID_CANAL_STARBOARD)
        if not canal_starboard: return
        
        embed = discord.Embed(description=mensaje.content or "", color=0xFFD60A)
        embed.set_author(name=mensaje.author.display_name, icon_url=mensaje.author.display_avatar.url)
        
        if mensaje.attachments:
            embed.set_image(url=mensaje.attachments[0].url)
        
        contenido_msg = f"⭐ **{reaccion_estrella.count}** | {canal.mention}"

        if star_doc:
            try:
                msg_sb = await canal_starboard.fetch_message(star_doc["sb_msg_id"])
                await msg_sb.edit(content=contenido_msg, embed=embed)
                print(f"[LOG STARBOARD] Mensaje {mensaje.id} actualizado con {reaccion_estrella.count} estrellas.")
            except discord.NotFound:
                msg_sb = await canal_starboard.send(content=contenido_msg, embed=embed)
                await client.starboard.update_one({"msg_id": mensaje.id}, {"$set": {"sb_msg_id": msg_sb.id}})
            except Exception:
                pass
        else:
            msg_sb = await canal_starboard.send(content=contenido_msg, embed=embed)
            await client.starboard.insert_one({"msg_id": mensaje.id, "sb_msg_id": msg_sb.id})
            print(f"[LOG STARBOARD] Nuevo mensaje fijado en Starboard: ID {mensaje.id} de {mensaje.author}")

@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.channel_id == ID_CANAL_AUTOROLES:
        guild = client.get_guild(payload.guild_id)
        if not guild: return

        rol_id = ROLES_REACCION.get(payload.emoji.name)
        if rol_id and rol_id != 0:
            rol = guild.get_role(rol_id)
            if rol:
                miembro = guild.get_member(payload.user_id)
                if miembro:
                    try:
                        await miembro.remove_roles(rol)
                    except discord.Forbidden:
                        pass

# =========================================================================
# 🛍️ COMANDOS DE ECONOMÍA Y DIVERSIÓN
# =========================================================================

@client.tree.command(name="perfil", description="Muestra tu nivel y balance financiero.")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    target = usuario or interaction.user
    data = await get_user_data(target.id)
    
    xp_actual = data["xp"]
    nivel = data["nivel"]
    xp_req = calcular_xp_requerida(nivel)
    xp_base = calcular_xp_requerida(nivel - 1) if nivel > 1 else 0
    
    progreso = (xp_actual - xp_base) / (xp_req - xp_base) if xp_req > xp_base else 0
    bar_len = 10
    lleno = int(progreso * bar_len)
    barra = "🟩" * lleno + "⬛" * (bar_len - lleno)

    embed = discord.Embed(title=f"Perfil de {target.display_name}", color=0x9B1C1C)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="✨ Nivel", value=f"**{nivel}**", inline=True)
    embed.add_field(name="🪙 Bóveda", value=f"**{data['monedas']}** Monedas", inline=True)
    embed.add_field(name="📊 Experiencia", value=f"{barra}\n({xp_actual}/{xp_req} XP)", inline=False)
    
    inventario = []
    if data.get("amuleto"): inventario.append("🍀 Amuleto de la Suerte (Activo)")
    if data.get("mutes_comprados", 0) > 0: inventario.append(f"🔇 Tóken de Muteo ({data['mutes_comprados']})")
    
    if inventario:
        embed.add_field(name="🎒 Inventario", value="\n".join(inventario), inline=False)

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="tienda", description="Abre la tienda del Imperio.")
async def tienda(interaction: discord.Interaction):
    embed = discord.Embed(title="🏪 Mercado del Imperio", description="Utiliza `/comprar <item>` para adquirir mercancía.", color=0xF4A261)
    embed.add_field(name="🍀 Amuleto de la Suerte", value=f"🪙 {PRECIO_AMULETO}\nTe protege de perder una apuesta.", inline=False)
    embed.add_field(name="🔇 Silenciador (Tóken)", value=f"🪙 {PRECIO_MUTE}\nTe permite mutear a alguien 5 min (Max 5/día).", inline=False)
    embed.add_field(name="🎨 Emoji Custom", value=f"🪙 {PRECIO_EMOJI}\nDerecho a subir un emoji al server.", inline=False)
    embed.add_field(name="🖼️ Sticker Custom", value=f"🪙 {PRECIO_STICKER}\nDerecho a subir un sticker al server.", inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="comprar", description="Compra un objeto de la tienda.")
@app_commands.choices(item=[
    app_commands.Choice(name="Amuleto de la Suerte", value="amuleto"),
    app_commands.Choice(name="Tóken de Muteo", value="mute"),
    app_commands.Choice(name="Emoji Custom", value="emoji"),
    app_commands.Choice(name="Sticker Custom", value="sticker"),
])
async def comprar(interaction: discord.Interaction, item: app_commands.Choice[str]):
    data = await get_user_data(interaction.user.id)
    precios = {"amuleto": PRECIO_AMULETO, "mute": PRECIO_MUTE, "emoji": PRECIO_EMOJI, "sticker": PRECIO_STICKER}
    precio = precios[item.value]
    
    if data["monedas"] < precio:
        return await interaction.response.send_message("❌ No tienes suficientes monedas.", ephemeral=True)

    if item.value == "amuleto":
        if data.get("amuleto"):
            return await interaction.response.send_message("❌ Ya tienes un Amuleto activo.", ephemeral=True)
        await update_user(interaction.user.id, {"$inc": {"monedas": -precio}, "$set": {"amuleto": True}})
        await interaction.response.send_message("✅ Has comprado un **Amuleto de la Suerte**.")
        
    elif item.value == "mute":
        if data.get("mutes_usados_hoy", 0) >= 5:
            return await interaction.response.send_message("❌ Has alcanzado el límite diario (5).", ephemeral=True)
        await update_user(interaction.user.id, {"$inc": {"monedas": -precio, "mutes_comprados": 1, "mutes_usados_hoy": 1}})
        await interaction.response.send_message("✅ Has comprado un **Tóken de Muteo**. Usa `/castigar` para utilizarlo.")
        
    else:
        await update_user(interaction.user.id, {"$inc": {"monedas": -precio}})
        await interaction.response.send_message(f"✅ Has comprado el derecho a un **{item.name}**. Abre un ticket para reclamarlo al Staff.")

@client.tree.command(name="gamble", description="Prueba tu suerte en los juegos de azar del Imperio.")
@app_commands.choices(juego=[
    app_commands.Choice(name="Ruleta (50/50)", value="ruleta"),
    app_commands.Choice(name="Dados: Mayor que 7 (50/50)", value="dados_mayor"),
    app_commands.Choice(name="Dados: Predecir Número Exacto (Pago 3x)", value="dados_exacto")
])
@app_commands.choices(prediccion_numero=[
    app_commands.Choice(name="1", value=1),
    app_commands.Choice(name="2", value=2),
    app_commands.Choice(name="3", value=3),
    app_commands.Choice(name="4", value=4),
    app_commands.Choice(name="5", value=5),
    app_commands.Choice(name="6", value=6)
])
async def gamble(
    interaction: discord.Interaction, 
    juego: app_commands.Choice[str], 
    apuesta: int, 
    prediccion_numero: app_commands.Choice[int] = None
):
    if apuesta <= 0:
        return await interaction.response.send_message("❌ La apuesta debe ser una cantidad mayor a 0.", ephemeral=True)
        
    data = await get_user_data(interaction.user.id)
    if data["monedas"] < apuesta:
        return await interaction.response.send_message("❌ No cuentas con suficientes monedas in tu bóveda.", ephemeral=True)

    # --- JUEGO 1: RULETA TRADICIONAL ---
    if juego.value == "ruleta":
        if random.choice([True, False]):
            await update_user(interaction.user.id, {"$inc": {"monedas": apuesta}})
            await interaction.response.send_message(f"🎰 ¡La ruleta giró y GANASTE! Recibes 🪙 **{apuesta}**.")
        else:
            if data.get("amuleto"):
                await update_user(interaction.user.id, {"$set": {"amuleto": False}})
                await interaction.response.send_message("🎰 La ruleta giró y perdiste... ¡Pero tu **Amuleto de la Suerte** absorbió el golpe!")
            else:
                await update_user(interaction.user.id, {"$inc": {"monedas": -apuesta}})
                await interaction.response.send_message(f"🎰 La ruleta giró y PERDISTE. Se te han restado 🪙 **{apuesta}**.")

    # --- JUEGO 2: DADOS MAYOR QUE 7 (50/50) ---
    elif juego.value == "dados_mayor":
        dado1 = secrets.choice(range(1, 7))
        dado2 = secrets.choice(range(1, 7))
        suma = dado1 + dado2
        
        embed = discord.Embed(title="🎲 Lanzamiento de Dados (Suma > 7)", color=0x9B59B6)
        embed.add_field(name="Resultado", value=f"🎲 Dado 1: **{dado1}**\n🎲 Dado 2: **{dado2}**\n\n💰 Suma Total: **{suma}**", inline=False)
        
        if suma > 7:
            await update_user(interaction.user.id, {"$inc": {"monedas": apuesta}})
            embed.description = f"🎉 ¡La suma es mayor que 7! Ganaste 🪙 **{apuesta}** monedas."
            embed.color = 0x2ECC71
        else:
            if data.get("amuleto"):
                await update_user(interaction.user.id, {"$set": {"amuleto": False}})
                embed.description = "📉 La suma no superó el 7... ¡Pero tu **Amuleto de la Suerte** se rompió protegiendo tus fondos!"
                embed.color = 0xF1C40F
            else:
                await update_user(interaction.user.id, {"$inc": {"monedas": -apuesta}})
                embed.description = f"💸 La suma es menor o igual a 7. Perdiste 🪙 **{apuesta}** monedas."
                embed.color = 0xE74C3C
                
        await interaction.response.send_message(embed=embed)

    # --- JUEGO 3: DADOS NÚMERO EXACTO (Pago 3x) ---
    elif juego.value == "dados_exacto":
        if not prediccion_numero:
            return await interaction.response.send_message("❌ Para jugar a este modo debes elegir un número del 1 al 6 usando el parámetro opcional `prediccion_numero`.", ephemeral=True)
        
        numero_elegido = prediccion_numero.value
        resultado_dado = random.randint(1, 6)
        
        embed = discord.Embed(title="🎲 Predicción de Dado Único", color=0x34495E)
        embed.add_field(name="Tu predicción", value=f"🎯 Número: **{numero_elegido}**", inline=True)
        embed.add_field(name="Resultado del Dado", value=f"🎲 Cayó en: **{resultado_dado}**", inline=True)
        
        if numero_elegido == resultado_dado:
            ganancia_triple = apuesta * 2
            await update_user(interaction.user.id, {"$inc": {"monedas": ganancia_triple}})
            embed.description = f"🔥 ¡PREDICCIÓN PERFECTA! El destino coincide. Triplicas tu apuesta y ganas 🪙 **{ganancia_triple}** monedas."
            embed.color = 0x2ECC71
        else:
            if data.get("amuleto"):
                await update_user(interaction.user.id, {"$set": {"amuleto": False}})
                embed.description = "❌ Tu predicción falló... ¡Pero tu **Amuleto de la Suerte** evitó que perdieras la inversión!"
                embed.color = 0xF1C40F
            else:
                await update_user(interaction.user.id, {"$inc": {"monedas": -apuesta}})
                embed.description = f"💸 El dado no cooperó. Has perdido 🪙 **{apuesta}** monedas."
                embed.color = 0xE74C3C
                
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="robar", description="Intenta robar monedas a otro usuario (40% éxito).")
async def robar(interaction: discord.Interaction, victima: discord.Member):
    if victima.bot or victima == interaction.user:
        return await interaction.response.send_message("❌ Objetivo inválido.", ephemeral=True)
        
    data_ladron = await get_user_data(interaction.user.id)
    data_victima = await get_user_data(victima.id)
    
    if data_ladron["monedas"] < 500:
        return await interaction.response.send_message("❌ Necesitas al menos 500 monedas de fondo.", ephemeral=True)
    if data_victima["monedas"] < 100:
        return await interaction.response.send_message("❌ Esa persona es demasiado pobre para robarle.", ephemeral=True)

    if random.random() < 0.40:
        botin = int(data_victima["monedas"] * 0.15)
        await update_user(interaction.user.id, {"$inc": {"monedas": botin}})
        await update_user(victima.id, {"$inc": {"monedas": -botin}})
        await interaction.response.send_message(f"🥷 ¡Éxito! Lograste robarle 🪙 **{botin}** a {victima.display_name}.")
    else:
        multa = 500
        await update_user(interaction.user.id, {"$inc": {"monedas": -multa}})
        await interaction.response.send_message(f"🚔 ¡Te han atrapado! Pagas una multa de 🪙 **{multa}**.")

# =========================================================================
# 🛡️ MODERACIÓN Y COMANDOS VIP
# =========================================================================

async def registrar_sancion(guild: discord.Guild, titulo: str, color: int, moderador: discord.Member, victima: discord.Member, razon: str):
    canal = guild.get_channel(ID_CANAL_MODLOGS)
    if canal:
        embed = discord.Embed(title=titulo, description=f"**Usuario:** {victima.mention}\n**Moderador:** {moderador.mention}\n**Motivo:** {razon}", color=color)
        await canal.send(embed=embed)

@client.tree.command(name="kick", description="[STAFF] Expulsa a un usuario.")
@app_commands.default_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón especificada."):
    await usuario.kick(reason=razon)
    await registrar_sancion(interaction.guild, "👢 Usuario Expulsado", 0xE67E22, interaction.user, usuario, razon)
    await interaction.response.send_message(f"✅ {usuario.mention} fue expulsado.", ephemeral=True)

@client.tree.command(name="ban", description="[STAFF] Banea a un usuario.")
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón especificada."):
    await usuario.ban(reason=razon)
    await registrar_sancion(interaction.guild, "🔨 Usuario Baneado", 0x992D22, interaction.user, usuario, razon)
    await interaction.response.send_message(f"✅ {usuario.mention} fue baneado.", ephemeral=True)

@client.tree.command(name="mute", description="[STAFF] Aísla a un usuario (Timeout).")
@app_commands.default_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, usuario: discord.Member, minutos: int, razon: str = "Sin razón especificada."):
    duracion = discord.utils.utcnow() + timedelta(minutes=minutos)
    await usuario.timeout(duracion, reason=razon)
    await registrar_sancion(interaction.guild, "🔇 Usuario Muteado", 0xF1C40F, interaction.user, usuario, f"{minutos} min - {razon}")
    await interaction.response.send_message(f"✅ {usuario.mention} muteado por {minutos} minutos.", ephemeral=True)

@client.tree.command(name="castigar", description="Gasta un Tóken de Muteo para silenciar a alguien por 5 minutos.")
async def castigar(interaction: discord.Interaction, victima: discord.Member):
    # IDs de los roles VIP a los que se les retira la inmunidad
    ROLES_VULNERABLES = [
        1518762564660498574,
        1518762566501924996,
        1518762567286264020,
        1518762567793905821
    ]
    
    tiene_rol_vulnerable = any(rol.id in ROLES_VULNERABLES for rol in victima.roles)

    # El bot ignorará la inmunidad de administrador si la víctima tiene un rol vulnerable
    if victima.bot or (victima.guild_permissions.administrator and not tiene_rol_vulnerable):
        return await interaction.response.send_message("❌ No puedes mutear a esta entidad.", ephemeral=True)
        
    data = await get_user_data(interaction.user.id)
    if data.get("mutes_comprados", 0) <= 0:
        return await interaction.response.send_message("❌ No tienes Tókens de Muteo.", ephemeral=True)
        
    duracion = discord.utils.utcnow() + timedelta(minutes=5)
    try:
        await victima.timeout(duracion, reason=f"Mute comprado por {interaction.user.display_name}")
        await update_user(interaction.user.id, {"$inc": {"mutes_comprados": -1}})
        await interaction.response.send_message(f"💸 Has gastado un tóken. {victima.mention} ha sido silenciado por 5 minutos. ¡Nadie es intocable!")
    except discord.Forbidden:
        await interaction.response.send_message("❌ El bot no pudo aplicar el mute. Asegúrate de mover el rol de Santuari lo más arriba posible en la lista de jerarquías del servidor.", ephemeral=True)

@client.tree.command(name="purge", description="[STAFF] Elimina una cantidad específica de mensajes.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, cantidad: int):
    if cantidad < 1 or cantidad > 100:
        return await interaction.response.send_message("❌ La cantidad debe estar entre 1 y 100.", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    eliminados = await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(f"🧹 Se han eliminado **{len(eliminados)}** mensajes correctamente.")

# =========================================================================
# ⚙️ COMANDOS EXCLUSIVOS DEL DUEÑO
# =========================================================================

@client.tree.command(name="imprimir_dinero", description="[OWNER] Genera e inyecta monedas de la nada en las arcas de un usuario.")
async def imprimir_dinero(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if interaction.user.id != ID_DUEÑO:
        return await interaction.response.send_message("❌ Comando restringido al soberano del Imperio.", ephemeral=True)
    
    if cantidad <= 0:
        return await interaction.response.send_message("❌ Debes imprimir una cantidad mayor a 0.", ephemeral=True)
        
    await get_user_data(usuario.id)
    await update_user(usuario.id, {"$inc": {"monedas": cantidad}})
    print(f"[LOG ADMIN ECON] {interaction.user} imprimió {cantidad} monedas para {usuario}")
    
    embed = discord.Embed(
        title="🏦 Inyección de Fondos Imperial", 
        description=f"Se han materializado 🪙 **{cantidad}** monedas en la bóveda de {usuario.mention}.", 
        color=0x2ECC71
    )
    embed.set_footer(text="Acción autorizada por el Alto Mando de Santuari.")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="aplicar_autoroles", description="[OWNER] Despliega los embeds de autoroles en el canal configurado.")
async def aplicar_autoroles(interaction: discord.Interaction):
    if interaction.user.id != ID_DUEÑO:
        return await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
    
    if interaction.channel_id != ID_CANAL_AUTOROLES:
        return await interaction.response.send_message(f"❌ Este comando solo se puede usar en <#{ID_CANAL_AUTOROLES}>.", ephemeral=True)

    await interaction.response.send_message("Generando sistema de autoroles expandido...", ephemeral=True)

    secciones = [
        {"embed": discord.Embed(title="🧬 Selecciona tu Género", description="Reacciona al emoji correspondiente para obtener el rol:\n\n👨 Hombre\n👩 Mujer\n🏳️‍⚧️ Transgénero\n🟡 No binarie\n❓ Otro género", color=0x3498DB), "emojis": ["👨", "👩", "🏳️‍⚧️", "🟡", "❓"]},
        {"embed": discord.Embed(title="🔹 Selecciona tus Pronombres", description="Reacciona al emoji correspondiente para obtener tus pronombres:\n\n🔹 She/Her\n🔸 He/Him\n▫️ They/Them", color=0x1ABC9C), "emojis": ["🔹", "🔸", "▫️"]},
        {"embed": discord.Embed(title="❤️ Selecciona tu Orientación", description="Reacciona al emoji correspondiente para obtener el rol:\n\n🤍 Heterosexual\n🧡 Lesbiana\n💗 Bisexual\n💙 Gay\n🖤 Asexual\n🤎 Alosexual", color=0xE74C3C), "emojis": ["🤍", "🧡", "💗", "💙", "🖤", "🤎"]},
        {"embed": discord.Embed(title="🌍 Selecciona tu Región", description="Reacciona al emoji correspondiente para obtener el rol:\n\n🦅 Norteamérica\n🌎 Sudamérica\n🌍 Europa\n🌏 Asia", color=0x2ECC71), "emojis": ["🦅", "🌎", "🌍", "🌏"]},
        {"embed": discord.Embed(title="📅 Selecciona tu Rango de Edad", description="Reacciona al emoji correspondiente para obtener el rol:\n\n🎒 14-17\n🎓 18-25\n💼 26+", color=0xF1C40F), "emojis": ["🎒", "🎓", "💼"]},
        {"embed": discord.Embed(title="🛡️ Selecciona tu Ocupación / Rol del Imperio", description="Reacciona al emoji correspondiente para reclamar tu ocupación:\n\n🎲 Dungeon Master\n📜 Politólogo\n🖌️ Artista\n⌨️ Programador\n📚 Seudo Filósofo", color=0xE67E22), "emojis": ["🎲", "📜", "🖌️", "⌨️", "📚"]},
        {"embed": discord.Embed(title="🎨 Selecciona tu Color", description="Reacciona al emoji correspondiente para obtener el rol:\n\n🔴 Carmesí\n🟠 Ámbar\n🟨 Dorado\n🟢 Esmeralda\n🔵 Zafiro\n🟣 Amatista\n🌸 Rosa\n⚪ Marfil\n⚫ Obsidiana\n🧊 Celeste", color=0x9B59B6), "emojis": ["🔴", "🟠", "🟨", "🟢", "🔵", "🟣", "🌸", "⚪", "⚫", "🧊"]},
        {"embed": discord.Embed(title="🕯️ Selecciona tus Nichos", description="Reacciona al emoji correspondiente para unirte a los nichos del Imperio:\n\n🐧 Linux & Coding\n🐉 Rol & Roll\n🎨 Arte y Filosofía", color=0x7F8C8D), "emojis": ["🐧", "🐉", "🎨"]}
    ]

    for seccion in secciones:
        mensaje = await interaction.channel.send(embed=seccion["embed"])
        for emoji in seccion["emojis"]:
            try:
                await mensaje.add_reaction(emoji)
            except discord.HTTPException:
                pass

@client.tree.command(name="dar_rol_multi", description="[OWNER] Da un rol a varios usuarios (menciónalos o escribe sus IDs).")
async def dar_rol_multi(interaction: discord.Interaction, rol: discord.Role, usuarios: str):
    if interaction.user.id != ID_DUEÑO:
        return await interaction.response.send_message("❌ Comando restringido al dueño del servidor.", ephemeral=True)

    await interaction.response.defer(ephemeral=False)
    ids_encontrados = set(re.findall(r'\d+', usuarios))
    
    if not ids_encontrados:
        return await interaction.followup.send("❌ No se detectó ningún usuario o ID válido en tu texto.")

    asignados = []
    errores = []

    for user_id_str in ids_encontrados:
        try:
            member = interaction.guild.get_member(int(user_id_str))
            if not member:
                member = await interaction.guild.fetch_member(int(user_id_str))
            
            if member and rol not in member.roles:
                await member.add_roles(rol)
                asignados.append(member.display_name)
        except discord.NotFound:
            errores.append(f"ID {user_id_str} (No existe)")
        except discord.Forbidden:
            errores.append(f"ID {user_id_str} (Jerarquía/Permisos)")
        except Exception:
            errores.append(f"ID {user_id_str} (Error inesperado)")

    embed = discord.Embed(title="✅ Asignación Múltiple", color=0x2ECC71)
    embed.add_field(name="Rol Aplicado", value=rol.mention, inline=False)
    embed.add_field(name=f"Asignados con éxito ({len(asignados)})", value=", ".join(asignados) or "Ninguno", inline=False)
    
    if errores:
        embed.add_field(name=f"Errores encontrados ({len(errores)})", value="\n".join(errores)[:1024], inline=False)
    
    await interaction.followup.send(embed=embed)

# =========================================================================
# 🏁 ARRANQUE DE MOTOR
# =========================================================================

if __name__ == "__main__":
    client.run(os.environ["DISCORD_TOKEN"])
