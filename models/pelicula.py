# Modelo tabla1 y tabla6


class Pelicula:
    def __init__(self, nombre, categoria, actores, todos_los_publicos=None):
        self.nombre = nombre
        self.categoria = categoria
        self.actores = actores
        self.todos_los_publicos = todos_los_publicos
