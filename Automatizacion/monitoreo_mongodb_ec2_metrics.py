from pymongo import MongoClient, errors
from jinja2 import Template
from datetime import datetime, timedelta
import psutil
import statistics
import socket
from urllib.parse import quote_plus

def obtener_informacion_disco():
    disco = psutil.disk_usage('/')
    return {
        'total': disco.total,
        'usado': disco.used,
        'libre': disco.free,
        'porcentaje_usado': disco.percent
    }
def obtener_informacion_ram():
    ram = psutil.virtual_memory()
    return {
        'total': ram.total,
        'disponible': ram.available,
        'usado': ram.used,
        'porcentaje_usado': ram.percent
    }

def obtener_informacion_conexiones():
    conexiones = psutil.net_connections()
    estados = [conn.status for conn in conexiones]
    contador_estados = {estado: estados.count(estado) for estado in set(estados)}
    return contador_estados

def obtener_latencia(servidor, puerto, rango_fecha):
    latencias = []  
    fecha_actual = rango_fecha[0]

    while fecha_actual <= rango_fecha[1]:
        try:
            inicio_tiempo = datetime.now()
            socket.create_connection((servidor, puerto), timeout=5)
            fin_tiempo = datetime.now()
            latencia = (fin_tiempo - inicio_tiempo).total_seconds() * 1000 
            latencias.append(latencia)
        except (socket.error, socket.timeout):
            latencias.append(None)  

        fecha_actual += timedelta(seconds=60)  

    return latencias

def obtener_metricas_servidor(cliente):
    try:
        info_servidor = cliente.server_info()
        nombre_servidor = info_servidor.get('host', '')
    except errors.OperationFailure as e:
        nombre_servidor = ''  
    endpoint = cliente.address[0] if cliente.address else ''
    puerto = cliente.address[1] if cliente.address else ''
    datos_generales = {
        'version': info_servidor.get('version', ''),
        'sistema_operativo': info_servidor.get('os', {}).get('type', ''),
    }
    return nombre_servidor, endpoint, puerto, datos_generales

def obtener_info_replicas(cliente):
    try:
        info_replicas = cliente.admin.command('replSetGetStatus')
        num_replicas = len(info_replicas.get('members', []))
        estado_replicas = {str(member['_id']): member['stateStr'] for member in info_replicas.get('members', [])}
    except errors.OperationFailure as e:
        num_replicas = 0
        estado_replicas = {}
    return num_replicas, estado_replicas


ruta_pem = "MADOAWSDEKPGLB01.pem"
usuario = "admin"
contrasena = quote_plus("Mad0M0ng0DbDev@@")
ip="172.26.4.222"
port='27017'

url_conexion = f"mongodb://{usuario}:{contrasena}@{ip}:{port}/?ssl=true&ssl_ca_certs={ruta_pem}"

def obtener_metricas_mongodb(rango_fecha):
    cliente = MongoClient(url_conexion)
    bases_de_datos = cliente.list_database_names()

    num_replicas, estado_replicas = obtener_info_replicas(cliente)
    nombre_servidor, endpoint, puerto, datos_generales = obtener_metricas_servidor(cliente)
    
    metricas_totales = []

    for nombre_db in bases_de_datos:
        base_de_datos = cliente[nombre_db]

        query = {"fecha": {"$gte": rango_fecha[0], "$lte": rango_fecha[1]}}
        stats = base_de_datos.command("dbStats", query=query)

        metricas_totales.append({
            'nombre': nombre_db,
            'tamanio': stats['dataSize'],
            'documentos': stats['objects'],
            'indice_tamanio': stats['indexSize'],
            'indice_documento': stats['indexes'],
        })

    cliente.close()
    return metricas_totales, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales

def calcular_minimo(valores):
    return min(valores) if valores else None

def calcular_maximo(valores):
    return max(valores) if valores else None

def calcular_promedio(valores):
    return statistics.mean(valores) if valores else None

def generar_html(info_disco, info_ram, info_conexiones, latencias, metricas_mongodb, es_cluster, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales): 
    template_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Información del Sistema y MongoDB</title>
    </head>
    <body>
        <h1>Información del Sistema</h1>
        
        <h2>Uso de Disco</h2>
        <p>Total de espacio en disco: {{ info_disco.total }} bytes</p>
        <p>Espacio usado: {{ info_disco.usado }} bytes</p>
        <p>Espacio libre: {{ info_disco.libre }} bytes</p>
        <p>Porcentaje de uso: {{ info_disco.porcentaje_usado }}%</p>

        <h2>Uso de RAM</h2>
        <p>Total de RAM: {{ info_ram.total }} bytes</p>
        <p>RAM disponible: {{ info_ram.disponible }} bytes</p>
        <p>RAM usada: {{ info_ram.usado }} bytes</p>
        <p>Porcentaje de uso de RAM: {{ info_ram.porcentaje_usado }}%</p>

        <h2>Conexiones</h2>
        {% for estado, cantidad in info_conexiones.items() %}
            <p>{{ estado }}: {{ cantidad }}</p>
        {% endfor %}

        <h1>Métricas de MongoDB</h1>
        {% for metrica in metricas_mongodb %}
            <h2>{{ metrica.nombre }}</h2>
            <p>Tamaño de la base de datos: {{ metrica.tamanio }} bytes</p>
            <p>Número total de documentos: {{ metrica.documentos }}</p>
            <p>Tamaño del índice: {{ metrica.indice_tamanio }} bytes</p>
            <p>Número total de índices: {{ metrica.indice_documento }}</p>
            <!-- Agrega más métricas específicas de MongoDB según sea necesario -->
        {% endfor %}

        {% if es_cluster %}
            <h2>Información del Cluster</h2>
            <p>Nombre del servidor: {{ nombre_servidor }}</p>
            <p>Endpoint: {{ endpoint }}</p>
            <p>Puerto: {{ puerto }}</p>
            <p>Número de réplicas: {{ num_replicas }}</p>
            <h3>Estado de las Réplicas</h3>
            {% for id_replica, estado_replica in estado_replicas.items() %}
                <p>Replica {{ id_replica }}: {{ estado_replica }}</p>
            {% endfor %}
        {% else %}
            <h2>Información del Servidor</h2>
            <p>Nombre del servidor: {{ nombre_servidor }}</p>
            <p>Endpoint: {{ endpoint }}</p>
            <p>Puerto: {{ puerto }}</p>
            <h3>Datos Generales</h3>
            <p>Versión de MongoDB: {{ datos_generales.version }}</p>
            <p>Sistema Operativo: {{ datos_generales.sistema_operativo }}</p>
            <!-- Agrega más datos generales según sea necesario -->
        {% endif %}

        <h2>Estadísticas de Latencia</h2>
        {% if latencias %}
            <p>Latencia Mínima: {{ min(latencias) }} ms</p>
            <p>Latencia Máxima: {{ max(latencias) }} ms</p>
            <p>Latencia Promedio: {{ mean(latencias) }} ms</p>
        {% else %}
            <p>No se pudieron recopilar estadísticas de latencia.</p>
        {% endif %}
    </body>
    </html>
    """

    with open("informacion_sistema_mongodb.html", "w") as html_file:
        html_file.write(Template(template_html).render(
            info_disco=info_disco,
            info_ram=info_ram,
            info_conexiones=info_conexiones,
            metricas_mongodb=metricas_mongodb,
            latencias=latencias,
            min=calcular_minimo,
            max=calcular_maximo,
            mean=calcular_promedio,
            es_cluster=es_cluster,
            num_replicas=num_replicas,
            estado_replicas=estado_replicas,
            nombre_servidor=nombre_servidor,
            endpoint=endpoint,
            puerto=puerto,
            datos_generales=datos_generales
        ))

    print("Archivo HTML generado exitosamente.")

def main():
    rango_fecha_mongodb = (datetime(2023, 10, 1), datetime(2023, 10, 1))

    info_disco = obtener_informacion_disco()
    info_ram = obtener_informacion_ram()
    info_conexiones = obtener_informacion_conexiones()
    latencias = obtener_latencia(ip, port, rango_fecha_mongodb)

    metricas_mongodb, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales = obtener_metricas_mongodb(rango_fecha_mongodb)

    es_cluster = num_replicas > 1  # Determina si es un clúster con réplica

    generar_html(info_disco, info_ram, info_conexiones, latencias, metricas_mongodb, es_cluster, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales)

if __name__ == "__main__":
    main()
