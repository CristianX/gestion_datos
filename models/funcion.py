# Modelo para funciones (tabla8)
class Funcion:
    def __init__(
        self,
        ciudad_nombre,
        sala_nro,
        cine_nombre,
        cine_id,
        funcion_cantidad,
        ciudad_provincia=None,
        ciudad_comunidad_autonoma=None,
    ):
        self.ciudad_nombre = ciudad_nombre
        self.sala_nro = sala_nro
        self.cine_nombre = cine_nombre
        self.cine_id = cine_id
        self.funcion_cantidad = funcion_cantidad
        self.ciudad_provincia = ciudad_provincia
        self.ciudad_comunidad_autonoma = ciudad_comunidad_autonoma
