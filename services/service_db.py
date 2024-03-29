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
        # En este método no se usa un array de querys ya que el orden de los atributos en Tabla7 y SoporteUsuario son diferentes
        self.session.execute(
            "INSERT INTO Tabla7 (usuario_nombre, usuario_dni, usuario_tlfs) VALUES (%s, %s, %s)",
            (usuario.nombre, usuario.dni, usuario.tlfs),
        )

        # Inserción en SoporteUsuario (dni, nombre, tlfs)
        self.session.execute(
            "INSERT INTO SoporteUsuario (dni, nombre, tlfs) VALUES (%s, %s, %s)",
            (
                usuario.dni,
                usuario.nombre,
                usuario.tlfs,
            ),
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

        # Insertar en Tabla5 información de compra con tarjeta
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

        # Luego, eliminar la fila existente
        self.session.execute(
            "DELETE FROM Tabla1 WHERE pelicula_nombre = %s", (nombre_pelicula,)
        )

        # Finalmente, reinserta la fila con la nueva categoría
        self.session.execute(
            "INSERT INTO Tabla1 (pelicula_nombre, pelicula_categoria, pelicula_actores) VALUES (%s, %s, %s)",
            (nombre_pelicula, nueva_categoria, pelicula.actores),
        )

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

    # Creación de funciones de consulta de información general
    # Realizar una consulta en Cassandra que requiere filtrar los datos de una manera que Cassandra considera
    # potencialmente ineficiente o que podría tener un rendimiento impredecible
    # requiere de una acción llamada ALLOW FILTERING
    # Utilizar ALLOW FILTERING permite realizar estas consultas, pero debe usarse con precaución,
    # ya que puede llevar a operaciones de escaneo completo de la tabla y afectar negativamente el rendimiento.
    # Tabla1: Películas por categoría
    def consultar_peliculas_por_categoria(self, categoria=None):
        if categoria:
            query = """
            SELECT pelicula_nombre, pelicula_categoria, pelicula_actores
            FROM Tabla1
            WHERE pelicula_categoria = %s
            ALLOW FILTERING
            """
            peliculas = self.session.execute(query, (categoria,))
        else:
            query = "SELECT pelicula_nombre, pelicula_categoria, pelicula_actores FROM Tabla1"
            peliculas = self.session.execute(query)
        for pelicula in peliculas:
            print(
                f"Nombre: {pelicula.pelicula_nombre}, Categoría: {pelicula.pelicula_categoria}, Actores: {pelicula.pelicula_actores}"
            )

    # Tabla2: Reservas por usuario y tipo de boleto
    def consultar_reservas_por_dni_tipo_boleto(self, dni, tipo_boleto_nombre=None):
        if tipo_boleto_nombre:
            query = """
            SELECT tipo_boleto_nombre, tipo_boleto_descuento, usuario_dni, reservacion_nro
            FROM Tabla2
            WHERE usuario_dni = %s AND tipo_boleto_nombre = %s
            ALLOW FILTERING
            """
            reservas = self.session.execute(query, (dni, tipo_boleto_nombre))
        else:
            query = """
            SELECT tipo_boleto_nombre, tipo_boleto_descuento, usuario_dni, reservacion_nro
            FROM Tabla2
            WHERE usuario_dni = %s
            ALLOW FILTERING
            """
            reservas = self.session.execute(query, (dni,))
        for reserva in reservas:
            print(
                f"DNI: {reserva.usuario_dni}, Tipo de Boleto: {reserva.tipo_boleto_nombre}, Descuento: {reserva.tipo_boleto_descuento}, Número de Reservación: {reserva.reservacion_nro}"
            )

    # Tabla3: Salas por cine
    def consultar_salas_por_cine(self, cine_nombre):
        query = """
        SELECT sala_nro, sala_capacidad, cine_nombre, cine_id
        FROM Tabla3
        WHERE cine_nombre = %s
        ALLOW FILTERING
        """
        salas = self.session.execute(query, (cine_nombre,))
        for sala in salas:
            print(
                f"Número de Sala: {sala.sala_nro}, Capacidad: {sala.sala_capacidad}, Cine: {sala.cine_nombre}, Cine ID: {sala.cine_id}"
            )

    # Tabla4: Reservas por usuario
    def consultar_reservas_por_usuario(self, usuario_nombre):
        query = "SELECT usuario_nombre, usuario_dni, reservacion_cantidad FROM Tabla4 WHERE usuario_nombre = %s"
        reservas = self.session.execute(query, (usuario_nombre,))
        for reserva in reservas:
            print(
                f"Nombre: {reserva.usuario_nombre}, DNI: {reserva.usuario_dni}, Cantidad de Reservas: {reserva.reservacion_cantidad}"
            )

    # Tabla5: Reservas confirmadas por banco
    def consultar_reservas_por_banco(self, tarjeta_banco, confirmado=True):
        query = "SELECT reservacion_nro, tarjeta_banco, reservacion_confirmado FROM Tabla5 WHERE tarjeta_banco = %s AND reservacion_confirmado = %s"
        reservas = self.session.execute(query, (tarjeta_banco, confirmado))
        for reserva in reservas:
            print(
                f"Número de Reservación: {reserva.reservacion_nro}, Banco: {reserva.tarjeta_banco}, Confirmado: {reserva.reservacion_confirmado}"
            )

    # Tabla6: Películas para todos los públicos
    def consultar_peliculas_todos_publicos(self, todos_los_publicos=True):
        query = """
        SELECT pelicula_nombre, pelicula_categoria, pelicula_actores, pelicula_todos_los_publicos
        FROM Tabla6
        WHERE pelicula_todos_los_publicos = %s
        ALLOW FILTERING
        """
        peliculas = self.session.execute(query, (todos_los_publicos,))
        for pelicula in peliculas:
            print(
                f"Nombre: {pelicula.pelicula_nombre}, Categoría: {pelicula.pelicula_categoria}, Actores: {pelicula.pelicula_actores}, Todos los Públicos: {pelicula.pelicula_todos_los_publicos}"
            )

    # Tabla7: Usuarios por nombre o DNI
    def consultar_usuario_por_nombre_dni(self, valor, buscar_por="nombre"):
        if buscar_por == "nombre":
            query = """
            SELECT usuario_nombre, usuario_dni, usuario_tlfs 
            FROM Tabla7 
            WHERE usuario_nombre = %s 
            ALLOW FILTERING
            """
        else:  # buscar_por == "dni"
            query = """
            SELECT usuario_nombre, usuario_dni, usuario_tlfs 
            FROM Tabla7 
            WHERE usuario_dni = %s 
            ALLOW FILTERING
            """
        usuarios = self.session.execute(query, (valor,))
        for usuario in usuarios:
            print(
                f"Nombre: {usuario.usuario_nombre}, DNI: {usuario.usuario_dni}, Teléfonos: {usuario.usuario_tlfs}"
            )

    # Tabla8: Funciones por ciudad
    def consultar_funciones_por_ciudad(self, ciudad_nombre):
        query = """
        SELECT ciudad_nombre, sala_nro, cine_nombre, cine_id, funcion_cantidad
        FROM Tabla8
        WHERE ciudad_nombre = %s
        ALLOW FILTERING
        """
        funciones = self.session.execute(query, (ciudad_nombre,))
        for funcion in funciones:
            print(
                f"Ciudad: {funcion.ciudad_nombre}, Número de Sala: {funcion.sala_nro}, Cine: {funcion.cine_nombre}, Cine ID: {funcion.cine_id}, Cantidad de Funciones: {funcion.funcion_cantidad}"
            )

    # Extra (Inserción de información en tabla4)
    # Debido a que esta tabla se encarga en rastrear la cantidad de reservas realizadas por cada usuario
    # se requiere de un métodoque incremente el contador de reservascada vez que se realice una nueva reserva
    def incrementar_reservas_usuario(self, usuario_dni):
        # Intenta obtener el nombre del usuario basado en el DNI
        usuario_info = self.consultar_usuario_por_dni(usuario_dni)
        if usuario_info:
            usuario_nombre = usuario_info.nombre
            # Verificar si el usuario ya tiene reservas registradas
            query = "SELECT reservacion_cantidad FROM Tabla4 WHERE usuario_dni = %s AND usuario_nombre = %s"
            result = self.session.execute(query, (usuario_dni, usuario_nombre)).one()

            if result:
                nueva_cantidad = result.reservacion_cantidad + 1
                update_query = "UPDATE Tabla4 SET reservacion_cantidad = %s WHERE usuario_dni = %s AND usuario_nombre = %s"
                self.session.execute(
                    update_query, (nueva_cantidad, usuario_dni, usuario_nombre)
                )
            else:
                # Si el usuario no tiene reservas, insertar una nueva fila con cantidad 1
                insert_query = "INSERT INTO Tabla4 (usuario_nombre, usuario_dni, reservacion_cantidad) VALUES (%s, %s, 1)"
                self.session.execute(insert_query, (usuario_nombre, usuario_dni))
        else:
            print(f"No se encontró el usuario con DNI {usuario_dni}.")

    # Extra (Inserción de información en tabla8)
    # Ya que tabla8 se encarga de rastrear funciones presentadas en diferentes ciudades
    # se crea mètodo para insertar nuevas funcionesy para consultar las funciones existentes por ciudad
    def insertar_funcion(
        self, ciudad_nombre, sala_nro, cine_nombre, cine_id, cantidad_funciones
    ):
        insert_query = """
        INSERT INTO Tabla8 (ciudad_nombre, sala_nro, cine_nombre, cine_id, funcion_cantidad)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.session.execute(
            insert_query,
            (ciudad_nombre, sala_nro, cine_nombre, cine_id, cantidad_funciones),
        )
