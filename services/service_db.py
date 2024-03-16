from config.bdd import get_session
from models.usuario import Usuario
from models.pelicula import Pelicula


class DBService:
    def __init__(self):
        self.session = get_session()

    # Creación de métodos destinados a consultar la información de tablas soporte
    def consultar_usuario_por_dni(self, dni):
        query = "SELECT * FROM SoporteUsuario WHERE dni = %s"
        row = self.session.execute(query, (dni,)).one()
        if row:
            return Usuario(dni=row.dni, nombre=row.nombre, tlfs=row.tlfs)
        return None

    def consultar_pelicula_por_nombre(self, nombre):
        query = "SELECT * FROM SoportePelicula WHERE nombre = %s"
        row = self.session.execute(query, (nombre,)).one()
        if row:
            return Pelicula(
                nombre=row.nombre,
                categoria=row.categoria,
                actores=row.actores,
                todos_los_publicos=row.todos_los_publicos,
            )
        return None

    # Creación de métodos de inserción de datos

    def insertar_usuario(self, usuario):
        # Inserción en Tabla7 (usuario_nombre, usuario_dni, usuario_tlfs)
        self.session.execute(
            "INSERT INTO Tabla7 (usuario_nombre, usuario_dni, usuario_tlfs) VALUES (%s, %s, %s)",
            (usuario.nombre, usuario.dni, usuario.tlfs),
        )

        # Inserción en SoporteUsuario (dni, nombre, tlfs)
        # Asegúrate de que los parámetros estén en el orden correcto según el esquema de SoporteUsuario
        self.session.execute(
            "INSERT INTO SoporteUsuario (dni, nombre, tlfs) VALUES (%s, %s, %s)",
            (
                usuario.dni,
                usuario.nombre,
                usuario.tlfs,
            ),  # Corrección aquí: primero dni, luego nombre
        )

    def insertar_pelicula(self, pelicula):
        # Primera inserción para Tabla1, que no incluye todos_los_publicos
        self.session.execute(
            "INSERT INTO Tabla1 (pelicula_nombre, pelicula_categoria, pelicula_actores) VALUES (%s, %s, %s)",
            (pelicula.nombre, pelicula.categoria, pelicula.actores),
        )

        # Inserción para Tabla6 y SoportePelicula, que sí incluyen todos_los_publicos
        queries = [
            "INSERT INTO Tabla6 (pelicula_nombre, pelicula_categoria, pelicula_actores, pelicula_todos_los_publicos) VALUES (%s, %s, %s, %s)",
            "INSERT INTO SoportePelicula (nombre, categoria, actores, todos_los_publicos) VALUES (%s, %s, %s, %s)",
        ]
        for query in queries:
            self.session.execute(
                query,
                (
                    pelicula.nombre,
                    pelicula.categoria,
                    pelicula.actores,
                    pelicula.todos_los_publicos,
                ),
            )

    # Definición básica de insertado Reserva-Compra
    def insertar_reserva_compra(self, reserva):
        # Insertar en Tabla2 (información de reserva)
        query_tabla2 = """
        INSERT INTO Tabla2 (usuario_dni, tipo_boleto_nombre, tipo_boleto_descuento, reservacion_nro, usuario_nombre) 
        VALUES (%s, %s, %s, %s, %s)
        """
        self.session.execute(
            query_tabla2,
            (
                reserva.usuario_dni,
                reserva.tipo_boleto_nombre,
                reserva.tipo_boleto_descuento,
                reserva.reservacion_nro,
                reserva.usuario_nombre,  # Asume que este valor se proporciona o se obtiene de otra manera
            ),
        )

        # Insertar en Tabla5 si aplica (información de compra con tarjeta)
        if reserva.confirmado is not None and reserva.tarjeta_banco is not None:
            query_tabla5 = """
            INSERT INTO Tabla5 (reservacion_confirmado, tarjeta_banco, reservacion_nro) 
            VALUES (%s, %s, %s)
            """
            self.session.execute(
                query_tabla5,
                (
                    reserva.confirmado,
                    reserva.tarjeta_banco,
                    reserva.reservacion_nro,
                ),
            )

    def insertar_cine_con_salas(self, cine, salas):
        """
        Inserta un cine y sus salas asociadas, demostrando la relación "Posee".
        :param cine: Instancia de Cine.
        :param salas: Lista de instancias de Sala.
        """
        # Insertar cine
        query_cine = """
        INSERT INTO Cine (cine_nombre, cine_id) VALUES (%s, %s)
        """
        self.session.execute(query_cine, (cine.nombre, cine.cine_id))

        # Insertar salas asociadas al cine
        for sala in salas:
            query_sala = """
            INSERT INTO Tabla3 (sala_nro, sala_capacidad, cine_nombre, cine_id) VALUES (%s, %s, %s, %s)
            """
            self.session.execute(
                query_sala, (sala.nro, sala.capacidad, cine.nombre, cine.cine_id)
            )

    # Relación posee
    def insertar_sala_en_cine(self, cine_nombre, cine_id, sala_nro, sala_capacidad):
        """
        Inserta una sala y la asocia con un cine específico.

        :param cine_nombre: Nombre del cine al que pertenece la sala.
        :param cine_id: Identificador único del cine.
        :param sala_nro: Número de la sala dentro del cine.
        :param sala_capacidad: Capacidad máxima de espectadores de la sala.
        """
        query = """
        INSERT INTO Tabla3 (sala_nro, sala_capacidad, cine_nombre, cine_id) 
        VALUES (%s, %s, %s, %s)
        """
        self.session.execute(query, (sala_nro, sala_capacidad, cine_nombre, cine_id))
