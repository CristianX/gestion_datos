from cassandra.cluster import Cluster

# from cassandra.auth import PlainTextAuthProvider


def get_session(keyspace_name="danielmaldonado"):
    # Configurando la conexión a la bdd con ip y tipo de autentificación
    cluster_address = ["127.0.0.1"]
    auth_provider = None

    # Creación de clustery sesion
    cluster = Cluster(cluster_address, auth_provider=auth_provider)
    session = cluster.connect(keyspace_name)

    return session
