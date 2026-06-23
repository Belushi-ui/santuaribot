# =========================================================================
# 🔧 AJUSTAR — REFUERZO DE PERMISOS POST-SETUP
# =========================================================================
# QUÉ HACE ESTE BOT:
#   Expone un único comando slash /ajustar, ejecutable SOLO por el usuario
#   con ID_DUEÑO, que:
#
#   1. Blinda los canales de "Información del Servidor" (bienvenidas,
#      reglas, guía-del-servidor): nadie puede crear hilos, hacer
#      @here/@everyone, ni añadir reacciones — solo el bot puede reaccionar.
#   2. Aplica el mismo blindaje (sin hilos, sin @here/@everyone, sin
#      reacciones de usuarios) a: presentación, reglas-de-mesa,
#      presentación-de-personajes, y a cualquier canal de autoroles.
#   3. En los canales de votación (votar-códigos, votar-dibujos): sin
#      hilos, sin @here/@everyone, PERO SÍ permite reacciones (para votar).
#   4. Bloquea la creación de hilos en TODOS los canales de texto del
#      servidor (incluyendo los "generales" de cada sección).
#   5. Restringe el acceso a #selfies a partir de Nivel 10 (acumulativo:
#      Nivel 20, 30... 100 también pueden, ya que en Discord los roles de
#      nivel superior no incluyen automáticamente el permiso del inferior,
#      así que se otorga el view_channel a TODOS los roles de nivel >= 10).
#   6. #memes se deja con acceso libre para "Habitante" (sin restricción
#      de nivel), revirtiendo cualquier restricción previa si la hubiera.
#   7. Pone mentionable=False en TODOS los roles de autorol (género,
#      región, sexualidad, pronombres, nichos, edad, ocupación, colores),
#      para que nadie pueda hacer @rol y que resuelva como ping real.
#
# CÓMO SE USA:
#   - Este comando busca canales y roles POR NOMBRE (no por ID fijo), así
#     que funciona sin importar el servidor mientras los nombres coincidan
#     con los que generó /setup. Si renombraste algo manualmente después
#     del setup, ese canal/rol específico no se va a encontrar y se
#     reportará en el resumen final, sin detener el resto del proceso.
#   - Se puede ejecutar varias veces sin problema (es idempotente): solo
#     vuelve a aplicar los mismos permisos, no duplica nada.
#
# ⚠️ NOTA: A diferencia de /setup, este comando NO es destructivo — solo
#   ajusta permisos y la propiedad "mentionable" de roles. No borra nada.
# =========================================================================

import discord
from discord import app_commands
import os
import sys

ID_SERVIDOR = 1517885569231749240  # Cambia esto si corresponde a otro server
ID_DUEÑO = 1360882776706125874     # Único usuario autorizado para ejecutar /ajustar

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
MY_GUILD = discord.Object(id=ID_SERVIDOR)


# =========================================================================
# 📋 CLASIFICACIÓN DE CANALES POR NIVEL DE RESTRICCIÓN
# =========================================================================

# Canales TOTALMENTE BLINDADOS: sin hilos, sin @here/@everyone, sin
# reacciones de usuarios (solo el bot puede reaccionar).
CANALES_BLINDADOS = [
    "👋 bienvenidas",
    "📖 reglas",
    "🗺️ guía-del-servidor",
    "🙋 presentación",
    "📜 reglas-de-mesa",
    "🧙 presentación-de-personajes",
]

# Canales de VOTACIÓN: sin hilos, sin @here/@everyone, PERO SÍ reacciones.
CANALES_VOTACION = [
    "🗳️ votar-códigos",
    "🗳️ votar-dibujos",
]

# Canal con acceso libre (sin restricción de nivel), por si se quiere
# revertir una restricción previa.
CANAL_LIBRE_NIVEL = "😂 memes"

# Canal que requiere Nivel 10 o superior para ver/escribir.
CANAL_NIVEL_10 = "📸 selfies"
NIVEL_MINIMO_REQUERIDO = 10

# Todos los niveles definidos en el setup (debe coincidir con setup_fase1.py)
TODOS_LOS_NIVELES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Roles de autorol que deben quedar con mentionable=False
ROLES_GENERO = ["Hombre", "Mujer", "Transgénero", "No binarie", "Otro género"]
ROLES_REGION = ["Norteamérica", "Sudamérica", "Europa", "Asia"]
ROLES_SEXUALIDAD = ["Heterosexual", "Lesbiana", "Bisexual", "Gay", "Asexual", "Alosexual", "Arromántico", "Otra sexualidad"]
ROLES_PRONOMBRES = ["She/Her", "He/Him", "They/Them", "Otros pronombres"]
ROLES_NICHO = ["Linux & Coding", "Arte y Filosofía", "Rol n Roll"]
ROLES_EDAD = ["14-17", "18-25", "26+"]
ROLES_OCUPACION = ["Artista", "Programador", "Dungeon Master", "Seudo Filósofo", "Politólogo"]
ROLES_COLOR = ["Carmesí", "Ámbar", "Dorado", "Esmeralda", "Zafiro", "Amatista", "Rosa", "Marfil", "Obsidiana", "Celeste"]

ROLES_AUTOROL_TODOS = (
    ROLES_GENERO + ROLES_REGION + ROLES_SEXUALIDAD + ROLES_PRONOMBRES +
    ROLES_NICHO + ROLES_EDAD + ROLES_OCUPACION + ROLES_COLOR
)


# =========================================================================
# 🔧 LÓGICA PRINCIPAL
# =========================================================================

def buscar_canal(guild: discord.Guild, nombre: str):
    """Busca un canal de texto por nombre exacto. Devuelve None si no existe."""
    return discord.utils.get(guild.text_channels, name=nombre)


def buscar_rol(guild: discord.Guild, nombre: str):
    """Busca un rol por nombre exacto. Devuelve None si no existe."""
    return discord.utils.get(guild.roles, name=nombre)


async def aplicar_blindaje_total(canal: discord.TextChannel, guild: discord.Guild, reporte: list):
    """Sin hilos, sin @here/@everyone, sin reacciones de usuarios."""
    everyone = guild.default_role
    overwrite = canal.overwrites_for(everyone)
    overwrite.send_messages_in_threads = False
    overwrite.create_public_threads = False
    overwrite.create_private_threads = False
    overwrite.mention_everyone = False
    overwrite.add_reactions = False
    try:
        await canal.set_permissions(everyone, overwrite=overwrite, reason="/ajustar: blindaje total")
        reporte.append(f"   🔒 Blindado por completo: {canal.name}")
    except discord.HTTPException as e:
        reporte.append(f"   ⚠️ Error blindando {canal.name}: {e}")


async def aplicar_blindaje_votacion(canal: discord.TextChannel, guild: discord.Guild, reporte: list):
    """Sin hilos, sin @here/@everyone, PERO sí reacciones (para votar)."""
    everyone = guild.default_role
    overwrite = canal.overwrites_for(everyone)
    overwrite.send_messages_in_threads = False
    overwrite.create_public_threads = False
    overwrite.create_private_threads = False
    overwrite.mention_everyone = False
    overwrite.add_reactions = True  # explícitamente permitido, para votar
    try:
        await canal.set_permissions(everyone, overwrite=overwrite, reason="/ajustar: blindaje de votación")
        reporte.append(f"   🗳️ Blindado (con reacciones habilitadas): {canal.name}")
    except discord.HTTPException as e:
        reporte.append(f"   ⚠️ Error blindando {canal.name}: {e}")


async def bloquear_hilos_generales(canal: discord.TextChannel, guild: discord.Guild, reporte: list):
    """Bloquea solo la creación de hilos, sin tocar reacciones ni menciones."""
    everyone = guild.default_role
    overwrite = canal.overwrites_for(everyone)
    overwrite.send_messages_in_threads = False
    overwrite.create_public_threads = False
    overwrite.create_private_threads = False
    try:
        await canal.set_permissions(everyone, overwrite=overwrite, reason="/ajustar: bloqueo de hilos")
        reporte.append(f"   🧵 Hilos bloqueados: {canal.name}")
    except discord.HTTPException as e:
        reporte.append(f"   ⚠️ Error bloqueando hilos en {canal.name}: {e}")


async def ajustar_acceso_por_nivel(guild: discord.Guild, reporte: list):
    """#selfies requiere Nivel 10+, #memes queda libre para Habitante."""
    everyone = guild.default_role
    rol_habitante = buscar_rol(guild, "Habitante")

    # --- #selfies: requiere Nivel 10 o superior ---
    canal_selfies = buscar_canal(guild, CANAL_NIVEL_10)
    if canal_selfies:
        # Bloquear para @everyone y para Habitante (que no tiene nivel garantizado)
        await canal_selfies.set_permissions(
            everyone, view_channel=False, reason="/ajustar: restricción de nivel"
        )
        if rol_habitante:
            await canal_selfies.set_permissions(
                rol_habitante, view_channel=False, reason="/ajustar: restricción de nivel"
            )
        # Habilitar para cada rol de nivel >= 10
        habilitados = []
        for nivel in TODOS_LOS_NIVELES:
            if nivel >= NIVEL_MINIMO_REQUERIDO:
                rol_nivel = buscar_rol(guild, f"Nivel {nivel}")
                if rol_nivel:
                    await canal_selfies.set_permissions(
                        rol_nivel, view_channel=True, send_messages=True,
                        reason="/ajustar: restricción de nivel"
                    )
                    habilitados.append(str(nivel))
        reporte.append(f"   📸 #selfies restringido a Nivel {NIVEL_MINIMO_REQUERIDO}+ (roles habilitados: {', '.join(habilitados) if habilitados else 'ninguno encontrado'})")
    else:
        reporte.append(f"   ⚠️ No se encontró el canal {CANAL_NIVEL_10}")

    # --- #memes: acceso libre para Habitante, sin restricción de nivel ---
    canal_memes = buscar_canal(guild, CANAL_LIBRE_NIVEL)
    if canal_memes:
        await canal_memes.set_permissions(everyone, view_channel=False, reason="/ajustar: acceso libre")
        if rol_habitante:
            await canal_memes.set_permissions(
                rol_habitante, view_channel=True, send_messages=True,
                reason="/ajustar: acceso libre"
            )
        reporte.append(f"   😂 #memes confirmado con acceso libre (sin restricción de nivel)")
    else:
        reporte.append(f"   ⚠️ No se encontró el canal {CANAL_LIBRE_NIVEL}")


async def quitar_mentionable_autoroles(guild: discord.Guild, reporte: list):
    """Pone mentionable=False en todos los roles de autorol."""
    encontrados, no_encontrados = 0, []
    for nombre in ROLES_AUTOROL_TODOS:
        rol = buscar_rol(guild, nombre)
        if rol is None:
            no_encontrados.append(nombre)
            continue
        if rol.mentionable:
            try:
                await rol.edit(mentionable=False, reason="/ajustar: bloquear ping de autoroles")
            except discord.HTTPException as e:
                reporte.append(f"   ⚠️ Error al ajustar {nombre}: {e}")
                continue
        encontrados += 1

    reporte.append(f"   🔇 Roles de autorol puestos como no-mencionables: {encontrados}/{len(ROLES_AUTOROL_TODOS)}")
    if no_encontrados:
        reporte.append(f"   ⚠️ No se encontraron estos roles (revisa nombres): {', '.join(no_encontrados)}")


# =========================================================================
# 🏁 COMANDO PRINCIPAL
# =========================================================================

@client.event
async def on_ready():
    print(f"🔌 Conectado como {client.user}")
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    print("🔧 Comando /ajustar sincronizado. Esperando ejecución manual desde Discord...")


@tree.command(name="ajustar", description="[SOLO DUEÑO] Refuerza permisos de canales y bloquea menciones de autoroles.")
async def ajustar(interaction: discord.Interaction):
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
        "🔧 **Ajustando permisos...** Esto puede tomar un momento. Revisa la consola/logs "
        "de Railway para ver el detalle completo.",
        ephemeral=True
    )

    reporte = []
    print(f"\n🔧 /ajustar ejecutado por {interaction.user} (ID: {interaction.user.id})\n")

    # --- 1. Canales totalmente blindados ---
    print("🔒 Aplicando blindaje total...")
    for nombre in CANALES_BLINDADOS:
        canal = buscar_canal(guild, nombre)
        if canal:
            await aplicar_blindaje_total(canal, guild, reporte)
        else:
            reporte.append(f"   ⚠️ No se encontró el canal: {nombre}")

    # --- 2. Canales de votación (blindados pero con reacciones) ---
    print("🗳️ Aplicando blindaje de votación...")
    for nombre in CANALES_VOTACION:
        canal = buscar_canal(guild, nombre)
        if canal:
            await aplicar_blindaje_votacion(canal, guild, reporte)
        else:
            reporte.append(f"   ⚠️ No se encontró el canal: {nombre}")

    # --- 3. Bloquear hilos en TODOS los demás canales de texto ---
    print("🧵 Bloqueando hilos en el resto de canales...")
    nombres_ya_procesados = set(CANALES_BLINDADOS + CANALES_VOTACION)
    for canal in guild.text_channels:
        if canal.name in nombres_ya_procesados:
            continue  # ya se les aplicó una política más estricta arriba
        await bloquear_hilos_generales(canal, guild, reporte)

    # --- 4. Acceso por nivel (#selfies y #memes) ---
    print("📊 Ajustando acceso por nivel...")
    await ajustar_acceso_por_nivel(guild, reporte)

    # --- 5. Mentionable=False en autoroles ---
    print("🔇 Bloqueando menciones de autoroles...")
    await quitar_mentionable_autoroles(guild, reporte)

    # --- Reporte final en consola ---
    print("\n" + "=" * 60)
    print("🎉 /ajustar COMPLETADO — RESUMEN")
    print("=" * 60)
    for linea in reporte:
        print(linea)
    print("=" * 60 + "\n")

    try:
        await interaction.followup.send(
            "✅ **Ajustes completados.** Revisa los logs de Railway para ver el resumen "
            "detallado de qué se aplicó y si algo no se encontró.",
            ephemeral=True
        )
    except discord.HTTPException:
        pass


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR CRÍTICO: No se encontró DISCORD_TOKEN.")
        sys.exit(1)
    client.run(token)


if __name__ == "__main__":
    main()
