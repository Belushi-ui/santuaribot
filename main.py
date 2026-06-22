# =========================================================================
# 🌌 SETUP FASE 1 — ESTRUCTURA DEL SERVIDOR (Mass Effect / Dragon Age)
# =========================================================================
# QUÉ HACE ESTE BOT:
#   Expone un único comando slash /setup, ejecutable SOLO por el usuario
#   con ID_DUEÑO, que:
#   1. Borra TODOS los roles del servidor (excepto @everyone).
#   2. Borra los canales que estén DENTRO de una categoría (no toca canales
#      sueltos que no pertenezcan a ninguna categoría).
#   3. Borra también las categorías mismas.
#   4. Crea todos los roles nuevos (jerarquía, niveles, colores, autoroles).
#   5. Crea todas las categorías y canales nuevos, con permisos de acceso
#      por sección.
#   6. Al final, imprime en consola (logs de Railway) todos los IDs en
#      formato "<ID> ---- Nombre", listos para copiar.
#
# CÓMO SE USA:
#   - Despliega este bot en Railway (o donde sea) de forma normal.
#   - Cuando esté listo (online), ejecuta /setup desde Discord.
#   - Solo el usuario con ID_DUEÑO puede ejecutarlo; cualquier otro
#     recibe un rechazo silencioso (ephemeral) sin que pase nada.
#   - Requiere la variable de entorno DISCORD_TOKEN.
#   - El bot necesita permiso de Administrador (lo pediste así a propósito).
#   - Una vez ejecutado y confirmado que todo salió bien, puedes borrar
#     este código y archivarlo localmente (según tu plan de fases).
#
# ⚠️ ADVERTENCIA: /setup ES DESTRUCTIVO E IRREVERSIBLE.
#   No hay segunda confirmación dentro de Discord — al ejecutar el comando,
#   el borrado empieza de inmediato. Asegúrate de estar listo antes de
#   presionar enter en el comando.
# =========================================================================

import discord
from discord import app_commands
import os
import sys
import json

ID_SERVIDOR = 1518737565967192294  # Cambia esto si corresponde a otro server
ID_DUEÑO = 1360882776706125874     # Único usuario autorizado para ejecutar /setup

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
MY_GUILD = discord.Object(id=ID_SERVIDOR)

# =========================================================================
# 🎨 DEFINICIÓN DE TIPOGRAFÍA DOBLE-STRIKE
# =========================================================================
# Mapeo de caracteres normales a su versión doble-strike (𝕯𝖔𝖚𝖻𝖑𝖊-𝖘𝖙𝖗𝖎𝖐𝖊)
# Se usa SOLO para: roles de jerarquía especial y roles de nivel.
_DOBLE_STRIKE = {
    'A':'𝔸','B':'𝔹','C':'ℂ','D':'𝔻','E':'𝔼','F':'𝔽','G':'𝔾','H':'ℍ','I':'𝕀',
    'J':'𝕁','K':'𝕂','L':'𝕃','M':'𝕄','N':'ℕ','O':'𝕆','P':'ℙ','Q':'ℚ','R':'ℝ',
    'S':'𝕊','T':'𝕋','U':'𝕌','V':'𝕍','W':'𝕎','X':'𝕏','Y':'𝕐','Z':'ℤ',
    'a':'𝕒','b':'𝕓','c':'𝕔','d':'𝕕','e':'𝕖','f':'𝕗','g':'𝕘','h':'𝕙','i':'𝕚',
    'j':'𝕛','k':'𝕜','l':'𝕝','m':'𝕞','n':'𝕟','o':'𝕠','p':'𝕡','q':'𝕢','r':'𝕣',
    's':'𝕤','t':'𝕥','u':'𝕦','v':'𝕧','w':'𝕨','x':'𝕩','y':'𝕪','z':'𝕫',
    '0':'𝟘','1':'𝟙','2':'𝟚','3':'𝟛','4':'𝟜','5':'𝟝','6':'𝟞','7':'𝟟','8':'𝟠','9':'𝟡',
}

def doble_strike(texto: str) -> str:
    """Convierte texto normal a tipografía doble-strike, dejando intactos
    espacios, emojis y símbolos que no estén en el mapeo."""
    return "".join(_DOBLE_STRIKE.get(c, c) for c in texto)


# =========================================================================
# 🎭 DEFINICIÓN DE ROLES
# =========================================================================
# Cada rol: (nombre_final, color_hex, hoist, mentionable)
# El orden en esta lista es el orden de creación. discord.py crea los
# roles de abajo hacia arriba en la jerarquía visual, así que el PRIMERO
# de esta lista queda en la posición MÁS ALTA una vez reordenado al final.

ROLES_JERARQUIA = [
    # (nombre_base, emoji, hex_color)
    ("Andraste",       "💫", 0xF4C430),
    ("Inquisidor",     "🛡️", 0x9B1C1C),
    ("Comandante",     "🤖", 0x1B3A5C),
    ("Espectros",      "👁️", 0xC0C0C0),
    ("Guardas Grises", "⚔️", 0x3A4A5C),
    ("El Círculo",     "🔮", 0x6B4C9A),
]

# Niveles: de 10 en 10 hasta 100
ROLES_NIVEL_DEF = [
    (10,  "🔹"), (20, "🔸"), (30, "🟦"), (40, "🟧"), (50, "🟪"),
    (60,  "🟩"), (70, "💠"), (80, "⭐"), (90, "🌟"), (100, "🏆"),
]

ROL_HABITANTE = "Habitante"  # rol base, sin emoji, tipografía normal

# Colores autorol (sin emoji, tipografía normal)
ROLES_COLOR = [
    ("Carmesí",   0xE63946),
    ("Ámbar",     0xF4A261),
    ("Dorado",    0xFFD60A),
    ("Esmeralda", 0x2A9D8F),
    ("Zafiro",    0x3D5A80),
    ("Amatista",  0x7B2CBF),
    ("Rosa",      0xFF6FB5),
    ("Marfil",    0xF1FAEE),
    ("Obsidiana", 0x22223B),
    ("Celeste",   0x90E0EF),
]

# Autoroles normales (sin emoji, tipografía normal, color gris neutro por defecto)
ROLES_GENERO = ["Hombre", "Mujer", "Transgénero", "No binarie", "Otro género"]
ROLES_REGION = ["Norteamérica", "Sudamérica", "Europa", "Asia"]
ROLES_SEXUALIDAD = ["Heterosexual", "Lesbiana", "Bisexual", "Gay", "Asexual", "Alosexual", "Arromántico", "Otra sexualidad"]
ROLES_PRONOMBRES = ["She/Her", "He/Him", "They/Them", "Otros pronombres"]
ROLES_NICHO = ["Linux & Coding", "Arte y Filosofía", "Rol n Roll"]
ROLES_EDAD = ["14-17", "18-25", "26+"]
ROLES_OCUPACION = ["Artista", "Programador", "Dungeon Master", "Seudo Filósofo", "Politólogo"]


# =========================================================================
# 🧹 PASO 1: LIMPIEZA
# =========================================================================

async def limpiar_servidor(guild: discord.Guild):
    print("\n🧹 Iniciando limpieza del servidor...")

    # --- Borrar canales dentro de categorías (y las categorías mismas) ---
    # Los canales que NO pertenecen a ninguna categoría (category is None)
    # se dejan intactos, tal como se pidió.
    categorias = list(guild.categories)
    for categoria in categorias:
        for canal in list(categoria.channels):
            try:
                await canal.delete(reason="Setup Fase 1: limpieza")
                print(f"   🗑️ Canal borrado: {canal.name}")
            except discord.HTTPException as e:
                print(f"   ⚠️ No se pudo borrar el canal {canal.name}: {e}")
        try:
            await categoria.delete(reason="Setup Fase 1: limpieza")
            print(f"   🗑️ Categoría borrada: {categoria.name}")
        except discord.HTTPException as e:
            print(f"   ⚠️ No se pudo borrar la categoría {categoria.name}: {e}")

    # --- Borrar TODOS los roles (excepto @everyone) ---
    # Incluye roles "managed" creados por este mismo bot en corridas anteriores
    # de setup. NOTA: el rol managed del bot DE DISCORD en sí (el que Discord
    # genera automáticamente para que el bot tenga member object) normalmente
    # no se puede borrar vía API aunque lo intentemos — Discord lo rechaza
    # solo, así que el try/except lo absorbe sin romper el script.
    for rol in list(guild.roles):
        if rol.is_default():
            continue  # @everyone nunca se borra (Discord no lo permite)
        try:
            await rol.delete(reason="Setup Fase 1: limpieza")
            print(f"   🗑️ Rol borrado: {rol.name}")
        except discord.HTTPException as e:
            print(f"   ⚠️ No se pudo borrar el rol {rol.name}: {e}")

    print("✅ Limpieza completada.\n")


# =========================================================================
# 🎭 PASO 2: CREACIÓN DE ROLES
# =========================================================================

async def crear_roles(guild: discord.Guild):
    print("🎭 Creando roles...")
    ids_roles = {}  # nombre_legible -> objeto discord.Role

    # --- Jerarquía especial: emoji + tipografía doble-strike + color único ---
    for nombre_base, emoji, color in ROLES_JERARQUIA:
        nombre_final = f"{emoji} {doble_strike(nombre_base)}"
        rol = await guild.create_role(
            name=nombre_final,
            color=discord.Color(color),
            hoist=True,
            mentionable=True,
            reason="Setup Fase 1: jerarquía"
        )
        ids_roles[nombre_base] = rol
        print(f"   ✅ {nombre_final}")

    # --- Niveles: emoji + tipografía doble-strike, color verde estándar ---
    for nivel, emoji in ROLES_NIVEL_DEF:
        nombre_base = f"Nivel {nivel}"
        nombre_final = f"{emoji} {doble_strike(nombre_base)}"
        rol = await guild.create_role(
            name=nombre_final,
            color=discord.Color(0x57A773),
            hoist=False,
            mentionable=False,
            reason="Setup Fase 1: niveles"
        )
        ids_roles[f"Nivel {nivel}"] = rol
        print(f"   ✅ {nombre_final}")

    # --- Rol base Habitante: sin emoji, tipografía normal ---
    rol_habitante = await guild.create_role(
        name=ROL_HABITANTE,
        color=discord.Color(0x95A5A6),
        hoist=False,
        mentionable=False,
        reason="Setup Fase 1: rol base"
    )
    ids_roles[ROL_HABITANTE] = rol_habitante
    print(f"   ✅ {ROL_HABITANTE}")

    # --- Colores autorol: sin emoji, tipografía normal ---
    for nombre, color in ROLES_COLOR:
        rol = await guild.create_role(
            name=nombre,
            color=discord.Color(color),
            hoist=False,
            mentionable=False,
            reason="Setup Fase 1: colores"
        )
        ids_roles[nombre] = rol
        print(f"   ✅ {nombre}")

    # --- Autoroles normales: sin emoji, tipografía normal, sin color especial ---
    grupos_autorol = (
        ROLES_GENERO + ROLES_REGION + ROLES_SEXUALIDAD +
        ROLES_PRONOMBRES + ROLES_NICHO + ROLES_EDAD + ROLES_OCUPACION
    )
    for nombre in grupos_autorol:
        rol = await guild.create_role(
            name=nombre,
            color=discord.Color.default(),
            hoist=False,
            mentionable=False,
            reason="Setup Fase 1: autoroles"
        )
        ids_roles[nombre] = rol
        print(f"   ✅ {nombre}")

    print("✅ Todos los roles fueron creados.\n")
    return ids_roles


# =========================================================================
# 📂 PASO 3: CREACIÓN DE CANALES
# =========================================================================

async def crear_canales(guild: discord.Guild, roles: dict):
    print("📂 Creando categorías y canales...")
    ids_canales = {}

    everyone = guild.default_role
    rol_habitante = roles[ROL_HABITANTE]
    rol_linux = roles["Linux & Coding"]
    rol_rol = roles["Rol n Roll"]
    rol_arte = roles["Arte y Filosofía"]
    rol_espectros = roles["Espectros"]
    rol_andraste = roles["Andraste"]
    rol_inquisidor = roles["Inquisidor"]
    rol_guardas = roles["Guardas Grises"]
    rol_circulo = roles["El Círculo"]

    staff_roles = [rol_andraste, rol_inquisidor, rol_guardas, rol_circulo]

    async def nueva_categoria(nombre, overwrites=None):
        cat = await guild.create_category(nombre, overwrites=overwrites or {}, reason="Setup Fase 1")
        ids_canales[nombre] = cat.id
        print(f"   📁 Categoría: {nombre}")
        return cat

    async def nuevo_texto(categoria, nombre, topic=None, overwrites=None):
        canal = await categoria.create_text_channel(
            nombre, topic=topic, overwrites=overwrites or {}, reason="Setup Fase 1"
        )
        ids_canales[nombre] = canal.id
        print(f"      💬 {nombre}")
        return canal

    async def nuevo_voz(categoria, nombre, user_limit=0, overwrites=None):
        canal = await categoria.create_voice_channel(
            nombre, user_limit=user_limit, overwrites=overwrites or {}, reason="Setup Fase 1"
        )
        ids_canales[nombre] = canal.id
        print(f"      🔊 {nombre} (límite: {user_limit or 'sin límite'})")
        return canal

    # Overwrite estándar: solo "Habitante" y superiores pueden ver; @everyone no.
    base_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        rol_habitante: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
    }

    def overwrites_con_rol(rol_extra, ver_para_habitante=False):
        """Genera overwrites donde SOLO rol_extra (+ staff) puede ver el canal."""
        ow = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            rol_extra: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
        }
        for sr in staff_roles:
            ow[sr] = discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True)
        return ow

    # ---------------------------------------------------------------
    # 1. Información del Servidor (visible para todos, incluso sin rol)
    # ---------------------------------------------------------------
    info_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False),
    }
    cat_info = await nueva_categoria("📜 Información del Servidor", info_overwrites)
    await nuevo_texto(cat_info, "👋 bienvenidas", "Bienvenido al Imperio. Aquí empieza tu historia.")
    await nuevo_texto(cat_info, "📖 reglas", "Las leyes que rigen este mundo.")
    await nuevo_texto(cat_info, "🎫 tickets", "Contacta al staff de forma privada.",
                       overwrites={everyone: discord.PermissionOverwrite(view_channel=True, send_messages=True)})
    await nuevo_texto(cat_info, "🗺️ guía-del-servidor", "Todo lo que necesitas saber para empezar.")

    # ---------------------------------------------------------------
    # 2. Offtopic (rol Habitante)
    # ---------------------------------------------------------------
    cat_offtopic = await nueva_categoria("🌍 Offtopic", base_overwrites)
    await nuevo_texto(cat_offtopic, "💬 chat-offtopic", "Habla de lo que sea.")
    await nuevo_texto(cat_offtopic, "🙋 presentación", "Cuéntanos quién eres.")
    await nuevo_texto(cat_offtopic, "🎬 media", "Comparte videos e imágenes.")
    await nuevo_texto(cat_offtopic, "😂 memes", "El humor del Imperio.")
    await nuevo_texto(cat_offtopic, "📸 selfies", "Muestra tu rostro al mundo.")

    # ---------------------------------------------------------------
    # 3. VC Offtopic (rol Habitante)
    # ---------------------------------------------------------------
    cat_vc_offtopic = await nueva_categoria("🔊 VC Offtopic", base_overwrites)
    await nuevo_voz(cat_vc_offtopic, "🔊 VC General", user_limit=0)
    for i in range(1, 4):
        await nuevo_voz(cat_vc_offtopic, f"👥 VC Duo {i}", user_limit=2)
    for i in range(1, 5):
        await nuevo_voz(cat_vc_offtopic, f"👥 VC Trío {i}", user_limit=3)
    for i in range(1, 3):
        await nuevo_voz(cat_vc_offtopic, f"👥 VC Grupo {i}", user_limit=5)

    # ---------------------------------------------------------------
    # 4. Linux & Coding (rol Linux & Coding) + VC Mantenimiento dentro
    # ---------------------------------------------------------------
    cat_linux = await nueva_categoria("💻 Linux & Coding", overwrites_con_rol(rol_linux))
    await nuevo_texto(cat_linux, "🐧 linux-general", "Discusión general sobre Linux.")
    await nuevo_texto(cat_linux, "🖼️ linux-media", "Capturas, fotos, recursos visuales.")
    await nuevo_texto(cat_linux, "⚙️ linux-setup", "Muestra tu setup, dotfiles, rice.")
    await nuevo_texto(cat_linux, "😂 linux-coding-memes", "Humor de programador.")
    await nuevo_texto(cat_linux, "📝 tu-código", "Comparte tu código.")
    await nuevo_texto(cat_linux, "🗳️ votar-códigos", "Vota el mejor código de la semana.")
    for i in range(1, 6):
        await nuevo_voz(cat_linux, f"🛠️ Ayuda Técnica {i}", user_limit=0)

    # ---------------------------------------------------------------
    # 5. Rol & Roll (rol Rol n Roll)
    # ---------------------------------------------------------------
    cat_rol = await nueva_categoria("🎲 Rol & Roll", overwrites_con_rol(rol_rol))
    await nuevo_texto(cat_rol, "📜 reglas-de-mesa", "Normas para las partidas.")
    await nuevo_texto(cat_rol, "🧙 presentación-de-personajes", "Presenta a tu personaje.")
    await nuevo_texto(cat_rol, "🎲 general-rol-n-roll", "Charla general de rol.")
    await nuevo_texto(cat_rol, "🖼️ media-rol-n-roll", "Imágenes y recursos de rol.")
    await nuevo_texto(cat_rol, "🗂️ organizar-party", "Busca grupo para tu próxima partida.")
    await nuevo_texto(cat_rol, "😂 memes-rol", "Humor de mesa.")
    await nuevo_texto(cat_rol, "🃏 otros-juegos-de-rol", "Otros sistemas y juegos de rol.")

    # ---------------------------------------------------------------
    # 6. VC Rol & Roll (rol Rol n Roll)
    # ---------------------------------------------------------------
    cat_vc_rol = await nueva_categoria("🔊 VC Rol & Roll", overwrites_con_rol(rol_rol))
    for i in range(1, 6):
        await nuevo_voz(cat_vc_rol, f"🎲 Mesa {i}", user_limit=5)

    # ---------------------------------------------------------------
    # 7. Arte y Cultura (rol Arte y Filosofía)
    # ---------------------------------------------------------------
    cat_arte = await nueva_categoria("🎨 Arte y Cultura", overwrites_con_rol(rol_arte))
    await nuevo_texto(cat_arte, "🎨 general-arte-y-cultura", "Charla general de arte y filosofía.")
    await nuevo_texto(cat_arte, "🎵 música", "Comparte y discute música.")
    await nuevo_texto(cat_arte, "🖼️ media-arte-y-cultura", "Imágenes y recursos culturales.")
    await nuevo_texto(cat_arte, "😂 memes-arte-y-cultura", "Humor artístico.")
    await nuevo_texto(cat_arte, "📚 tu-biblioteca", "Recomendaciones y reseñas.")
    await nuevo_texto(cat_arte, "🖌️ tus-dibujos", "Comparte tus dibujos.")
    await nuevo_texto(cat_arte, "🗳️ votar-dibujos", "Vota el mejor dibujo de la semana.")

    # ---------------------------------------------------------------
    # 8. VIP Espectros (rol Espectros) — categoría propia, antes de Moderación
    # ---------------------------------------------------------------
    cat_vip = await nueva_categoria("👁️ VIP Espectros", overwrites_con_rol(rol_espectros))
    await nuevo_texto(cat_vip, "🛋️ sala-privada", "Solo para Espectros.")

    # ---------------------------------------------------------------
    # 9. Moderación (solo staff)
    # ---------------------------------------------------------------
    mod_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
    }
    for sr in staff_roles:
        mod_overwrites[sr] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    cat_mod = await nueva_categoria("🛡️ Moderación", mod_overwrites)
    await nuevo_texto(cat_mod, "📋 mod-logs", "Registro automático de acciones de moderación.")
    await nuevo_texto(cat_mod, "🚨 reportes", "Reportes de usuarios.")
    await nuevo_texto(cat_mod, "🗣️ chat-staff", "Discusión interna del staff.")
    await nuevo_texto(cat_mod, "⚖️ sanciones", "Registro de warns, mutes y bans.")

    print("✅ Todos los canales fueron creados.\n")
    return ids_canales


# =========================================================================
# 🏁 EJECUCIÓN PRINCIPAL
# =========================================================================

@client.event
async def on_ready():
    print(f"🔌 Conectado como {client.user}")
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    print("🏛️ Comando /setup sincronizado. Esperando ejecución manual desde Discord...")


@tree.command(name="setup", description="[SOLO DUEÑO] Borra y recrea TODA la estructura del servidor. Irreversible.")
async def setup(interaction: discord.Interaction):
    # --- Restricción dura: solo el dueño puede ejecutar esto ---
    if interaction.user.id != ID_DUEÑO:
        await interaction.response.send_message(
            "❌ No tienes autorización para ejecutar este comando.", ephemeral=True
        )
        return

    guild = interaction.guild
    if guild is None or guild.id != ID_SERVIDOR:
        await interaction.response.send_message(
            "❌ Este comando solo puede ejecutarse en el servidor configurado.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        "⚠️ **Iniciando setup destructivo.** Esto va a borrar todos los roles y todos los canales "
        "dentro de categorías, y luego recrear todo de cero. Revisa la consola/logs de Railway "
        "para ver el progreso y los IDs finales.",
        ephemeral=True
    )

    print(f"\n⚠️ /setup ejecutado por {interaction.user} (ID: {interaction.user.id})")
    print(f"Esto va a BORRAR todos los roles y todos los canales dentro de categorías")
    print(f"en '{guild.name}'. Esta acción es IRREVERSIBLE.\n")

    await limpiar_servidor(guild)
    roles = await crear_roles(guild)
    canales = await crear_canales(guild, roles)

    # --- Reordenar jerarquía de roles ---
    print("📊 Reordenando jerarquía de roles...")
    try:
        posiciones = {}
        orden_deseado = (
            [nombre for nombre, _, _ in ROLES_JERARQUIA] +
            [f"Nivel {n}" for n, _ in reversed(ROLES_NIVEL_DEF)] +
            [ROL_HABITANTE]
        )
        posicion_actual = len(guild.roles)
        for nombre in orden_deseado:
            if nombre in roles:
                posiciones[roles[nombre]] = posicion_actual
                posicion_actual -= 1
        await guild.edit_role_positions(positions=posiciones)
        print("✅ Jerarquía reordenada.\n")
    except discord.HTTPException as e:
        print(f"⚠️ No se pudo reordenar automáticamente la jerarquía: {e}")
        print("   Puedes reordenarla manualmente arrastrando los roles en la configuración del servidor.\n")

    # --- IMPRESIÓN FINAL DE IDs (en consola/logs de Railway) ---
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETADO")
    print("=" * 60)

    print("\n📋 IDs de Canales y Categorías:")
    for nombre, id_ in canales.items():
        print(f"{id_} ---- {nombre}")

    print("\n👥 IDs de Roles:")
    for nombre, rol in roles.items():
        print(f"{rol.id} ---- {nombre}")

    print("\n💾 JSON para copiar a un archivo local:")
    datos = {
        "canales": canales,
        "roles": {nombre: rol.id for nombre, rol in roles.items()},
    }
    print(json.dumps(datos, indent=2, ensure_ascii=False))

    try:
        await interaction.followup.send(
            "✅ **Setup completado.** Revisa los logs de Railway para copiar todos los IDs "
            "(canales y roles) en formato `<ID> ---- Nombre`, más el JSON completo.",
            ephemeral=True
        )
    except discord.HTTPException:
        pass  # si el token de interacción ya expiró (proceso muy largo), no pasa nada; ya quedó en logs


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR CRÍTICO: No se encontró DISCORD_TOKEN.")
        sys.exit(1)
    client.run(token)


if __name__ == "__main__":
    main()
