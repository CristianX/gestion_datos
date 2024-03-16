# Modelo relación cine y sala (tabla3)
class Cine:
    def __init__(self, nombre, cine_id, salas=[]):
        self.nombre = nombre
        self.cine_id = cine_id
        self.salas = salas  # Lista de instancias de Sala
