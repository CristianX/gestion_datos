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

    # Creación de funciones de actualización de datos
    # Dado que la categoría de la película se encuentra en Tabla1,
    # Tabla6, y SoportePelicula, el método deberá actualizar todas estas tablas
    # para mantener la consistencia de los datos.
    def actualizar_categoria_pelicula(self, nombre_pelicula, nueva_categoria):
        """
        Para actualizar la categoría de una película cuando pelicula_categoria es parte de la clave primaria
        y teniendo en cuenta las limitaciones de Cassandra respecto a la inmutabilidad de las claves primarias,
        se optó por eliminar la fila existente y reinsertarla con la nueva categoría.
        Esto implica manejar cuidadosamente la operación para preservar cualquier otro dato asociado a la película
        que no se deba perder.
        """
        pelicula = self.consultar_pelicula_por_nombre(nombre_pelicula)
        if not pelicula:
            print("Película no encontrada")
            return

        # Luego, elimina la fila existente
        self.session.execute(
            "DELETE FROM Tabla1 WHERE pelicula_nombre = %s", (nombre_pelicula,)
        )

        # Finalmente, reinserta la fila con la nueva categoría
        self.session.execute(
            "INSERT INTO Tabla1 (pelicula_nombre, pelicula_categoria, pelicula_actores) VALUES (%s, %s, %s)",
            (nombre_pelicula, nueva_categoria, pelicula.actores),
        )

        # Realizar la misma operación para Tabla6, usando los atributos directamente
        self.session.execute(
            "DELETE FROM Tabla6 WHERE pelicula_nombre = %s", (nombre_pelicula,)
        )
        self.session.execute(
            "INSERT INTO Tabla6 (pelicula_nombre, pelicula_categoria, pelicula_actores, pelicula_todos_los_publicos) VALUES (%s, %s, %s, %s)",
            (
                nombre_pelicula,
                nueva_categoria,
                pelicula.actores,
                pelicula.todos_los_publicos,
            ),
        )

        # Actualiza también la información en SoportePelicula
        self.session.execute(
            "UPDATE SoportePelicula SET categoria = %s WHERE nombre = %s",
            (nueva_categoria, nombre_pelicula),
        )

        print(
            f"La categoría de la película '{nombre_pelicula}' ha sido actualizada en todas las tablas relevantes."
        )

    # Creación de funciones de borrado de datos
    # Debido a que se necesita borrar el usuario de la tabla7 y soporteusuario se deberá crear
    # un método adicional donde se pueda obtener el dni por nombre
    def obtener_dni_por_nombre(self, nombre_usuario):
        # Intenta obtener el DNI a partir del nombre del usuario de la Tabla7
        query = "SELECT usuario_dni FROM Tabla7 WHERE usuario_nombre = %s"
        rows = self.session.execute(query, (nombre_usuario,))
        for row in rows:
            return row.usuario_dni
        return None

    def borrar_usuario_por_nombre(self, nombre_usuario):
        # Obtener el DNI asociado al nombre del usuario
        dni_usuario = self.obtener_dni_por_nombre(nombre_usuario)

        if dni_usuario:
            # Borrar el usuario de SoporteUsuario
            self.session.execute(
                "DELETE FROM SoporteUsuario WHERE dni = %s", (dni_usuario,)
            )

            # Borrar el usuario de Tabla7
            self.session.execute(
                "DELETE FROM Tabla7 WHERE usuario_nombre = %s", (nombre_usuario,)
            )

            print(f"Usuario '{nombre_usuario}' ha sido borrado de la base de datos.")
        else:
            print(
                f"No se pudo encontrar el DNI para '{nombre_usuario}', no se realizó el borrado."
            )
