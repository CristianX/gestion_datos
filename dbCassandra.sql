/* Creaci�n del keyspace */
CREATE KEYSPACE danielmaldonado WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

/* Activaci�n del keyspace */
USE danielmaldonado;

/* Creaci�n de las tablas */

/* Tabla1: Informaci�n de pel�culas por categor�a */
CREATE TABLE Tabla1 (
    pelicula_nombre text,
    pelicula_categoria text,
    pelicula_actores set<text>,
    PRIMARY KEY (pelicula_nombre, pelicula_categoria)
);

/* Tabla2: Reservas de un usuario por DNI y tipo de boleto */
CREATE TABLE Tabla2 (
    tipo_boleto_nombre text,
    tipo_boleto_descuento int,
    usuario_dni text,
    reservacion_nro int,
    usuario_nombre text,
    PRIMARY KEY ((tipo_boleto_nombre, tipo_boleto_descuento), usuario_dni, reservacion_nro)
);

/* Tabla3: Salas de un cine */
CREATE TABLE Tabla3 (
    sala_nro int,
    sala_capacidad text,
    cine_nombre text,
    cine_id int,
    PRIMARY KEY ((sala_nro, sala_capacidad), cine_nombre)
);

/* Tabla4: Cantidad de reservas por usuario */
CREATE TABLE Tabla4 (
    usuario_nombre text,
    usuario_dni text,
    reservacion_cantidad int,
    PRIMARY KEY (usuario_nombre, usuario_dni)
) WITH CLUSTERING ORDER BY (usuario_dni ASC);

/* Tabla5: Reservas realizadas con una tarjeta de un banco espec�fico */
CREATE TABLE Tabla5 (
    reservacion_confirmado boolean,
    tarjeta_banco text,
    reservacion_nro int,
    PRIMARY KEY (reservacion_confirmado, tarjeta_banco, reservacion_nro)
);

/* Tabla6: Pel�culas optimizadas para todos los p�blicos */
CREATE TABLE Tabla6 (
    pelicula_nombre text,
    pelicula_categoria text,
    pelicula_actores set<text>,
    pelicula_todos_los_publicos boolean,
    PRIMARY KEY (pelicula_nombre, pelicula_categoria)
);

/* Tabla7: Usuarios con un n�mero de tel�fono espec�fico */
CREATE TABLE Tabla7 (
    usuario_nombre text,
    usuario_dni text,
    usuario_tlfs set<text>,
    PRIMARY KEY (usuario_nombre, usuario_dni)
);

/* Tabla8: Funciones presentadas en una ciudad */
CREATE TABLE Tabla8 (
    ciudad_nombre text,
    sala_nro int,
    cine_nombre text,
    cine_id int,
    funcion_cantidad int,
    ciudad_provincia text,
    ciudad_comunidad_autonoma text,
    PRIMARY KEY ((ciudad_nombre, sala_nro), cine_nombre, cine_id)
) WITH CLUSTERING ORDER BY (cine_nombre ASC, cine_id ASC);

--******Creaci�n de m�todos destinados a consultar la informaci�n de tablas soporte*********
/* Creaci�n de la tabla SoporteUsuario */
CREATE TABLE SoporteUsuario (
    dni text PRIMARY KEY,
    nombre text,
    tlfs set<text>
);

/* Creaci�n de la tabla SoportePel�cula */
CREATE TABLE SoportePelicula (
    nombre text PRIMARY KEY,
    categoria text,
    actores set<text>,
    todos_los_publicos boolean
);
