# Modelo relación cine y sala (tabla3)
class Sala:
    def __init__(self, nro, capacidad, cine_nombre=None):
        self.nro = nro
        self.capacidad = capacidad
        self.cine_nombre = cine_nombre
