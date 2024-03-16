from services.service_db import DBService
from models.usuario import Usuario
from models.pelicula import Pelicula
from models.reserva import Reserva


# def test_cassandra_connection():
#     session = get_session()
#     # Consulta de prueba: obtener todos los keyspaces
#     rows = session.execute("SELECT keyspace_name FROM system_schema.keyspaces;")
#     for row in rows:
#         print(row.keyspace_name)

#     # Asegúrate de cerrar la sesión
#     session.shutdown()


def consulta_usuario_pelicula():
    db_service = DBService()
    usuario = db_service.consultar_usuario_por_dni("123456789")
    if usuario:
        print(f"Usuario encontrado: {usuario.nombre}")
    else:
        print("Usuario no encontrado")

    pelicula = db_service.consultar_pelicula_por_nombre("Los Increibles")
    if pelicula:
        print(f"Película encontrada: {pelicula.nombre}")
    else:
        print("Película no encontrada")


def insercion_datos():
    # Crear una instancia de DBService
    db_service = DBService()

    # Ejemplo de inserción de un Usuario
    usuario = Usuario(
        nombre="Juan Perez", dni="123456789", tlfs={"555-1234", "555-5678"}
    )
    db_service.insertar_usuario(usuario)

    # Ejemplo de inserción de una Película
    pelicula = Pelicula(
        nombre="Los Increibles",
        categoria="Familia",
        actores={"Brad Bird"},
        todos_los_publicos=True,
    )
    db_service.insertar_pelicula(pelicula)

    # Ejemplo de inserción de una Reserva-Compra
    # Asume que tienes un modelo o estructura para ReservaCompra
    reserva = Reserva(
        usuario_dni="123456789",
        tipo_boleto_nombre="General",
        tipo_boleto_descuento=10,
        reservacion_nro=1,
        usuario_nombre="Juan Pérez",  # Asegúrate de incluir este argumento
        confirmado=True,  # Este es un argumento opcional
        tarjeta_banco="Banco X",  # Este es un argumento opcional
    )

    db_service.insertar_reserva_compra(reserva)

    # Ejemplo de inserción de una sala en un cine
    cine_nombre = "Cinemark Norte"
    cine_id = 1
    sala_nro = 5
    sala_capacidad = "120"
    db_service.insertar_sala_en_cine(cine_nombre, cine_id, sala_nro, sala_capacidad)


if __name__ == "__main__":
    # test_cassandra_connection()
    consulta_usuario_pelicula()
    insercion_datos()
