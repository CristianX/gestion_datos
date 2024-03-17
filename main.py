from services.service_db import DBService
from models.usuario import Usuario
from models.pelicula import Pelicula
from models.reserva import Reserva


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


def actualizar_datos_pelicula():
    # Crear instancia del servicio de base de datos
    db_service = DBService()

    # Nombre de la película cuya categoría quieres actualizar
    nombre_pelicula = "Los Increibles"

    # La nueva categoría para la película
    nueva_categoria = "Accion"

    # Llamar al método para actualizar la categoría de la película
    db_service.actualizar_categoria_pelicula(nombre_pelicula, nueva_categoria)

    print(
        f"La categoría de la película '{nombre_pelicula}' ha sido actualizada a '{nueva_categoria}'."
    )


def borrar_usuario_por_nombre():
    # Crear una instancia de DBService
    db_service = DBService()

    # Nombre del usuario que deseas borrar
    nombre_usuario = "Juan Perez"

    # Llamar al método para borrar el usuario por su nombre
    db_service.borrar_usuario_por_nombre(nombre_usuario)

    print(f"Se ha intentado borrar al usuario '{nombre_usuario}'.")


def realizar_consultas_info_general():
    db_service = DBService()

    # Consulta de películas por categoría
    print("Consultando películas por categoría 'Acción':")
    db_service.consultar_peliculas_por_categoria("Accion")

    # Consulta de reservas por DNI
    print("\nConsultando reservas por DNI '123456789':")
    db_service.consultar_reservas_por_dni_tipo_boleto("123456789")

    # Consulta de salas por cine
    print("\nConsultando salas para el cine 'Cinemark Norte':")
    db_service.consultar_salas_por_cine("Cinemark Norte")

    # Consulta de reservas por usuario
    print("\nConsultando reservas para el usuario 'Juan Perez':")
    db_service.consultar_reservas_por_usuario("Juan Perez")

    # Consulta de reservas confirmadas por banco
    print("\nConsultando reservas confirmadas por el banco 'Banco X':")
    db_service.consultar_reservas_por_banco("Banco X")

    # Consulta de películas para todos los públicos
    print("\nConsultando películas para todos los públicos:")
    db_service.consultar_peliculas_todos_publicos(True)

    # Consulta de usuario por nombre
    print("\nConsultando usuario por nombre 'Juan Perez':")
    db_service.consultar_usuario_por_nombre_dni("Juan Perez", "nombre")

    # Consulta de funciones por ciudad
    print("\nConsultando funciones en la ciudad 'Quito'")
    db_service.consultar_funciones_por_ciudad("Quito")


# Interfaz de usuario
def main():
    db_service = DBService()
    while True:
        print("\n--- Sistema de Gestión de Base de Datos Cassandra ---")
        print("Seleccione una operación para continuar:")
        print("1. Consultar películas por categoría")
        print("2. Consultar reservas por DNI")
        print("3. Consultar salas por cine")
        print("4. Consultar reservas por usuario")
        print("5. Consultar reservas confirmadas por banco")
        print("6. Consultar películas para todos los públicos")
        print("7. Consultar usuario por nombre o DNI")
        print("8. Consultar funciones por ciudad")
        print("9. Insertar un nuevo usuario")
        print("10. Insertar una nueva película")
        print("11. Insertar una nueva reserva")
        print("12. Actualizar la categoría de una película")
        print("13. Borrar un usuario")
        print("0. Salir")

        opcion = input("Ingrese el número de la operación deseada: ")

        if opcion == "1":
            categoria = input("Ingrese la categoría de las películas a consultar: ")
            db_service.consultar_peliculas_por_categoria(categoria)
        elif opcion == "2":
            dni = input("Ingrese el DNI del usuario para consultar sus reservas: ")
            db_service.consultar_reservas_por_dni_tipo_boleto(dni)
        elif opcion == "3":
            cine_nombre = input("Ingrese el nombre del cine para consultar sus salas: ")
            db_service.consultar_salas_por_cine(cine_nombre)
        elif opcion == "4":
            usuario_nombre = input(
                "Ingrese el nombre del usuario para consultar sus reservas: "
            )
            db_service.consultar_reservas_por_usuario(usuario_nombre)
        elif opcion == "5":
            banco = input("Ingrese el nombre del banco para consultar las reservas: ")
            db_service.consultar_reservas_por_banco(banco)
        elif opcion == "6":
            db_service.consultar_peliculas_todos_publicos()
        elif opcion == "7":
            valor = input("Ingrese el nombre o DNI del usuario a consultar: ")
            buscar_por = (
                "nombre" if input("Buscar por nombre (n) o DNI (d)? ") == "n" else "dni"
            )
            db_service.consultar_usuario_por_nombre_dni(valor, buscar_por)
        elif opcion == "8":
            ciudad = input(
                "Ingrese el nombre de la ciudad para consultar sus funciones: "
            )
            db_service.consultar_funciones_por_ciudad(ciudad)
        elif opcion == "9":
            nombre = input("Nombre del usuario: ")
            dni = input("DNI del usuario: ")
            tlfs = set(input("Teléfonos del usuario (separados por coma): ").split(","))
            usuario = Usuario(nombre=nombre, dni=dni, tlfs=tlfs)
            db_service.insertar_usuario(usuario)
        elif opcion == "10":
            nombre = input("Nombre de la película: ")
            categoria = input("Categoría de la película: ")
            actores = set(
                input("Actores de la película (separados por coma): ").split(",")
            )
            todos_los_publicos = input("¿Es para todos los públicos? (s/n): ") == "s"
            pelicula = Pelicula(
                nombre=nombre,
                categoria=categoria,
                actores=actores,
                todos_los_publicos=todos_los_publicos,
            )
            db_service.insertar_pelicula(pelicula)
        elif opcion == "11":
            # Asegúrate de ajustar según tu modelo Reserva
            print("Función no implementada en este ejemplo.")
        elif opcion == "12":
            nombre_pelicula = input("Nombre de la película a actualizar: ")
            nueva_categoria = input("Nueva categoría de la película: ")
            db_service.actualizar_categoria_pelicula(nombre_pelicula, nueva_categoria)
        elif opcion == "13":
            nombre_usuario = input("Nombre del usuario a borrar: ")
            db_service.borrar_usuario_por_nombre(nombre_usuario)
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida, por favor intente nuevamente.")


if __name__ == "__main__":
    # test_cassandra_connection()
    # consulta_usuario_pelicula()
    # insercion_datos()
    # actualizar_datos_pelicula()
    # borrar_usuario_por_nombre()
    # realizar_consultas_info_general()
    main()
