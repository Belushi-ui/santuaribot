# =========================================================================
# 🌌 SANTUARI CORE — MOTOR PRINCIPAL DEL IMPERIO (Fase 2)
# =========================================================================
# SISTEMAS INTEGRADOS:
# - MongoDB (motor asíncrono) para persistencia total.
# - Niveles Exponenciales y auto-asignación de roles de Nivel (10, 20...).
# - Economía (🪙), Top, Perfil, Donar, Robar.
# - Tienda y Objetos (Amuleto de la Suerte, Mutes, Emojis).
# - Casino (Ruleta y Blackjack interactivo).
# - Moderación (Kick, Ban, Timeout, Warn) y Starboard.
# - Eventos aleatorios de "Lluvia de Monedas".
# =========================================================================

import discord
from discord import app_commands
from discord.ext import tasks
import motor.motor_asyncio
import os
import sys
import random
import time
import asyncio
from datetime import timedelta

# --- CONFIGURACIÓN DE IDs ---
ID_SERVIDOR = 1517885569231749240
ID_DUEÑO = 1360882776706125874
ID_CANAL_STARBOARD = 1518814340919328858
ID_CANAL_MODLOGS = 1518762621937909862 # Asegúrate de que sea tu canal de logs
PRECIO_MUTE = 2000
PRECIO_AMULETO = 1000
PRECIO_EMOJI = 5000
PRECIO_STICKER = 5000

class SantuariBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.cooldowns_xp = {}

    async def setup_hook(self):
        # Conexión a MongoDB
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            print("❌ ERROR: No se encontró MONGO_URI.")
            sys.exit(1)
            
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.mongo_client.santuari
        self.users = self.db.usuarios
        self.starboard = self.db.starboard
        
        guild = discord.Object(id=ID_SERVIDOR)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("🏛️ Santuari Core cargado. Base de datos conectada y comandos sincronizados.")

client = SantuariBot()

# =========================================================================
# 🗄️ FUNCIONES DE BASE DE DATOS Y LÓGICA CORE
# =========================================================================

async def get_user_data(user_id: int):
    data = await client.users.find_one({"_id": user_id})
    if not data:
        data = {
            "_id": user_id,
            "xp": 0, "nivel": 1,
            "monedas": 0,
            "mutes_comprados": 0, "mutes_usados_hoy": 0,
            "amuleto": False
        }
        await client.users.insert_one(data)
    return data

async def update_user(user_id: int, query: dict):
    await client.users.update_one({"_id": user_id}, query, upsert=True)

def calcular_xp_requerida(nivel: int):
    # Fórmula Exponencial: 100 * (nivel ^ 1.5)
    return int(100 * (nivel ** 1.5))

# =========================================================================
# 🎲 SISTEMA DE BLACKJACK (UI)
# =========================================================================

def carta_aleatoria():
    cartas = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] # 11 es As
    return random.choice(cartas)

def puntaje_mano(mano):
    total = sum(mano)
    ases = mano.count(11)
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total

class BlackjackView(discord.ui.View):
    def __init__(self, jugador, apuesta, data_jugador):
        super().__init__(timeout=60)
        self.jugador = jugador
        self.apuesta = apuesta
        self.data_jugador = data_jugador
        self.mano_jugador = [carta_aleatoria(), carta_aleatoria()]
        self.mano_dealer = [carta_aleatoria(), carta_aleatoria()]

    async def actualizar_embed(self, interaction: discord.Interaction, finalizado=False):
        pts_jugador = puntaje_mano(self.mano_jugador)
        pts_dealer = puntaje_mano(self.mano_dealer)
        
        embed = discord.Embed(title="🃏 Blackjack", color=0x2E86C1)
        embed.add_field(name=f"Tu mano ({pts_jugador})", value=f"{self.mano_jugador}", inline=False)
        
        if finalizado:
            embed.add_field(name=f"Mano del Croupier ({pts_dealer})", value=f"{self.mano_dealer}", inline=False)
            
            ganancia = 0
            amuleto_usado = False
            
            if pts_jugador > 21:
                if self.data_jugador.get("amuleto"):
                    embed.description = "💥 Te pasaste de 21, pero tu **Amuleto de la Suerte** se rompió protegiendo tu apuesta."
                    amuleto_usado = True
                else:
                    embed.description = "💥 Te pasaste de 21. Perdiste 🪙 **" + str(self.apuesta) + "**."
                    await update_user(self.jugador.id, {"$inc": {"monedas": -self.apuesta}})
            elif pts_dealer > 21 or pts_jugador > pts_dealer:
                ganancia = self.apuesta
                embed.description = f"🎉 ¡Ganaste! Recibes 🪙 **{ganancia}**."
                await update_user(self.jugador.id, {"$inc": {"monedas": ganancia}})
            elif pts_jugador == pts_dealer:
                embed.description = "🤝 Empate. Recuperas tu apuesta."
            else:
                if self.data_jugador.get("amuleto"):
                    embed.description = "El Croupier gana, pero tu **Amuleto de la Suerte** absorbe la pérdida."
                    amuleto_usado = True
                else:
                    embed.description = f"💸 El Croupier gana. Perdiste 🪙 **{self.apuesta}**."
                    await update_user(self.jugador.id, {"$inc": {"monedas": -self.apuesta}})
            
            if amuleto_usado:
                await update_user(self.jugador.id, {"$set": {"amuleto": False}})
                
        else:
            embed.add_field(name="Mano del Croupier", value=f"[{self.mano_dealer[0]}, ?]", inline=False)

        await interaction.response.edit_message(embed=embed, view=None if finalizado else self)

    @discord.ui.button(label="Pedir Carta (Hit)", style=discord.ButtonStyle.primary, custom_id="hit")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.jugador: return
        self.mano_jugador.append(carta_aleatoria())
        if puntaje_mano(self.mano_jugador) > 21:
            await self.actualizar_embed(interaction, finalizado=True)
        else:
            await self.actualizar_embed(interaction)

    @discord.ui.button(label="Plantarse (Stand)", style=discord.ButtonStyle.danger, custom_id="stand")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.jugador: return
        while puntaje_mano(self.mano_dealer) < 17:
            self.mano_dealer.append(carta_aleatoria())
        await self.actualizar_embed(interaction, finalizado=True)

# =========================================================================
# 💰 DROPS Y EVENTOS
# =========================================================================

class ReclamarDrop(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="¡Reclamar!", style=discord.ButtonStyle.success, emoji="🪙")
    async def reclamar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await update_user(interaction.user.id, {"$inc": {"monedas": 150}})
        embed = discord.Embed(description=f"🎉 ¡{interaction.user.mention} fue el más rápido y reclamó las **150 🪙**!", color=0xF1C40F)
        await interaction.response.edit_message(embed=embed, view=None)

# =========================================================================
# 📩 EVENTOS DEL SERVIDOR (XP, Drops, Starboard)
# =========================================================================

@client.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild: return

    # 1. DROP ALEATORIO (2% de probabilidad por mensaje)
    if random.random() < 0.02:
        embed = discord.Embed(title="🎁 ¡Lluvia de Monedas!", description="Un cargamento de 🪙 **150 Monedas** ha caído. ¡Sé el primero en reclamarlo!", color=0xF1C40F)
        await message.channel.send(embed=embed, view=ReclamarDrop())

    # 2. SISTEMA DE EXPERIENCIA (Cooldown de 60s)
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
            # Subió de nivel
            nuevo_nivel = nivel_actual + 1
            await update_user(message.author.id, {"$set": {"xp": nueva_xp, "nivel": nuevo_nivel}})
            
            # Revisar si es múltiplo de 10 para auto-rol
            if nuevo_nivel % 10 == 0 and nuevo_nivel <= 100:
                # Busca el rol que contenga "Nivel X" en su nombre (ignorando fuentes raras)
                rol_target = discord.utils.find(lambda r: f"Nivel {nuevo_nivel}" in r.name, message.guild.roles)
                if rol_target:
                    try:
                        await message.author.add_roles(rol_target)
                    except discord.Forbidden:
                        pass
            
            # Anuncio silencioso pero bonito en el chat
            embed_lvl = discord.Embed(description=f"✨ **{message.author.display_name}** ha alcanzado el **Nivel {nuevo_nivel}**.", color=0x57A773)
            await message.channel.send(embed=embed_lvl, delete_after=10)
        else:
            await update_user(message.author.id, {"$set": {"xp": nueva_xp}})

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # STARBOARD SYSTEM
    if payload.emoji.name != "⭐": return
    
    canal = client.get_channel(payload.channel_id)
    mensaje = await canal.fetch_message(payload.message_id)
    
    # Contar estrellas
    reaccion_estrella = discord.utils.get(mensaje.reactions, emoji="⭐")
    if not reaccion_estrella or reaccion_estrella.count < 3: return

    # Buscar en BD
    star_doc = await client.starboard.find_one({"msg_id": mensaje.id})
    canal_starboard = client.get_channel(ID_CANAL_STARBOARD)
    
    embed = discord.Embed(description=mensaje.content, color=0xFFD60A)
    embed.set_author(name=mensaje.author.display_name, icon_url=mensaje.author.display_avatar.url)
    if mensaje.attachments:
        embed.set_image(url=mensaje.attachments[0].url)
    
    contenido_msg = f"⭐ **{reaccion_estrella.count}** | {canal.mention}"

    if star_doc:
        try:
            msg_sb = await canal_starboard.fetch_message(star_doc["sb_msg_id"])
            await msg_sb.edit(content=contenido_msg, embed=embed)
        except: pass
    else:
        msg_sb = await canal_starboard.send(content=contenido_msg, embed=embed)
        await client.starboard.insert_one({"msg_id": mensaje.id, "sb_msg_id": msg_sb.id})

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
    
    progreso = (xp_actual - xp_base) / (xp_req - xp_base)
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
        await interaction.response.send_message("❌ No tienes suficientes monedas.", ephemeral=True)
        return

    if item.value == "amuleto":
        if data.get("amuleto"):
            await interaction.response.send_message("❌ Ya tienes un Amuleto activo.", ephemeral=True)
            return
        await update_user(interaction.user.id, {"$inc": {"monedas": -precio}, "$set": {"amuleto": True}})
        await interaction.response.send_message("✅ Has comprado un **Amuleto de la Suerte**.")
        
    elif item.value == "mute":
        if data.get("mutes_usados_hoy", 0) >= 5:
            await interaction.response.send_message("❌ Has alcanzado el límite diario de compras de mutes (5).", ephemeral=True)
            return
        await update_user(interaction.user.id, {"$inc": {"monedas": -precio, "mutes_comprados": 1, "mutes_usados_hoy": 1}})
        await interaction.response.send_message("✅ Has comprado un **Tóken de Muteo**. Usa `/castigar` para utilizarlo.")
        
    else:
        # Emojis y Stickers avisan al staff
        await update_user(interaction.user.id, {"$inc": {"monedas": -precio}})
        await interaction.response.send_message(f"✅ Has comprado el derecho a un **{item.name}**. Abre un ticket para que el Staff lo suba.")

@client.tree.command(name="gamble", description="Apuesta tus monedas.")
@app_commands.choices(juego=[
    app_commands.Choice(name="Ruleta (50/50)", value="ruleta"),
    app_commands.Choice(name="Blackjack", value="blackjack")
])
async def gamble(interaction: discord.Interaction, juego: app_commands.Choice[str], apuesta: int):
    if apuesta <= 0:
        await interaction.response.send_message("❌ Apuesta inválida.", ephemeral=True)
        return
        
    data = await get_user_data(interaction.user.id)
    if data["monedas"] < apuesta:
        await interaction.response.send_message("❌ No tienes suficientes monedas.", ephemeral=True)
        return

    if juego.value == "ruleta":
        ganar = random.choice([True, False])
        if ganar:
            await update_user(interaction.user.id, {"$inc": {"monedas": apuesta}})
            await interaction.response.send_message(f"🎰 ¡La ruleta giró y GANASTE! Recibes 🪙 **{apuesta}**.")
        else:
            if data.get("amuleto"):
                await update_user(interaction.user.id, {"$set": {"amuleto": False}})
                await interaction.response.send_message("🎰 La ruleta giró y perdiste... ¡Pero tu **Amuleto de la Suerte** se rompió y salvó tus monedas!")
            else:
                await update_user(interaction.user.id, {"$inc": {"monedas": -apuesta}})
                await interaction.response.send_message(f"🎰 La ruleta giró y PERDISTE. Se te han restado 🪙 **{apuesta}**.")
                
    elif juego.value == "blackjack":
        vista = BlackjackView(interaction.user, apuesta, data)
        await vista.actualizar_embed(interaction)

@client.tree.command(name="robar", description="Intenta robar monedas a otro usuario (40% éxito).")
async def robar(interaction: discord.Interaction, victima: discord.Member):
    if victima.bot or victima == interaction.user:
        await interaction.response.send_message("❌ Objetivo inválido.", ephemeral=True)
        return
        
    data_ladron = await get_user_data(interaction.user.id)
    data_victima = await get_user_data(victima.id)
    
    if data_ladron["monedas"] < 500:
        await interaction.response.send_message("❌ Necesitas al menos 500 monedas de fondo para asumir la multa si fallas.", ephemeral=True)
        return
    if data_victima["monedas"] < 100:
        await interaction.response.send_message("❌ Esa persona es demasiado pobre para robarle.", ephemeral=True)
        return
        
    if random.random() < 0.40: # 40% éxito
        botin = int(data_victima["monedas"] * 0.15) # Roba 15%
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
    if victima.bot or victima.guild_permissions.administrator:
        await interaction.response.send_message("❌ No puedes mutear a esa entidad.", ephemeral=True)
        return
        
    data = await get_user_data(interaction.user.id)
    if data.get("mutes_comprados", 0) <= 0:
        await interaction.response.send_message("❌ No tienes Tókens de Muteo. Cómpralos en la `/tienda`.", ephemeral=True)
        return
        
    duracion = discord.utils.utcnow() + timedelta(minutes=5)
    try:
        await victima.timeout(duracion, reason=f"Mute comprado por {interaction.user.display_name}")
        await update_user(interaction.user.id, {"$inc": {"mutes_comprados": -1}})
        await interaction.response.send_message(f"💸 Has gastado un tóken. {victima.mention} ha sido silenciado por 5 minutos.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ El bot no tiene permisos suficientes para mutear a esta persona.", ephemeral=True)

# =========================================================================
# 🏁 ARRANQUE DE MOTOR
# =========================================================================

if __name__ == "__main__":
    client.run(os.environ["DISCORD_TOKEN"])
