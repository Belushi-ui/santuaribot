async def setup_hook(self):
    mongo_uri = os.environ.get("MONGO_URI")
    if mongo_uri:
        # ... tu conexión a Mongo ...
        pass

    #  LIMPIEZA DE COMANDOS (solo si está activado)
    if os.environ.get("LIMPIAR_COMANDOS") == "true":
        print(" Limpiando comandos globales...")
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        print(" Comandos limpios.")

Sincronizar comandos normalmente,
    self.tree.copy_global_to(guild=MY_GUILD)
    await self.tree.sync(guild=MY_GUILD)
    print(" Comandos sincronizados.")
