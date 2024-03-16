# Modelo tabla2 y tabla5 (Reserva)


class Reserva:
    # Debido a un error de inserción se añadió el parámetro de usuario_nombre para relacionarlo
    def __init__(
        self,
        usuario_dni,
        tipo_boleto_nombre,
        tipo_boleto_descuento,
        reservacion_nro,
        usuario_nombre,  # Agregar este atributo
        confirmado=None,
        tarjeta_banco=None,
    ):
        self.usuario_dni = usuario_dni
        self.tipo_boleto_nombre = tipo_boleto_nombre
        self.tipo_boleto_descuento = tipo_boleto_descuento
        self.reservacion_nro = reservacion_nro
        self.usuario_nombre = usuario_nombre  # Inicializarlo aquí
        self.confirmado = confirmado
        self.tarjeta_banco = tarjeta_banco
