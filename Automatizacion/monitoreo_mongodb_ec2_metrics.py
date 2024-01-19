from pymongo import MongoClient, errors
from jinja2 import Template
from datetime import datetime, timedelta
import statistics
import socket
import base64
import subprocess
from urllib.parse import quote_plus
import re

i_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
f_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
css_path = 'metric_styles.css'
clave_privada_path =f'/home/ec2-user/reportes/MADOAWSTSKPGLB01.pem'
ruta_imagen = 'logo_movility.png'
usuario_ssh ='ec2-user'
usuario = "admin"
contrasena = quote_plus("Mad0M0ng0DbTest@")
ip="172.26.5.22"
port='27017'
url_conexion = f"mongodb://{usuario}:{contrasena}@{ip}:{port}/"
AWS_ENVIROMENT = 'QA'

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

def obtener_base64_de_imagen(ruta_archivo):
    try:
        with open(ruta_archivo, "rb") as imagen_archivo:
            contenido = imagen_archivo.read()
            base64_data = base64.b64encode(contenido)
            base64_str = base64_data.decode("utf-8")
            return base64_str
    except FileNotFoundError:
        print(f"No se pudo encontrar el archivo: {ruta_archivo}")
        return None
    
def evaluar_valor(tipo,valor):
    #print(f'EL VALOR: {valor}')
    valor = limpiar_y_convertir(valor)
    clase = ''
    if tipo == 1:
       print('Evaluando RAM')
       clase = 'metric_good' if valor <= 70 else 'metric_warnig' if valor < 80 else 'metric_danger'
    elif tipo == 2:
       print('Evaluando Espacio en Disco')
       clase = 'metric_good' if valor <= 70 else 'metric_warnig' if valor < 80 else 'metric_danger'
    elif tipo == 3:
       print('Evaluando latencia')
       clase = 'metric_good' if valor < 10 else 'metric_warnig' if valor < 11 else 'metric_danger' 
        
    return f'class="{clase}"'
    
def limpiar_y_convertir(valor):
    if not isinstance(valor, (str, bytes)):
        # Manejar el caso en el que el valor no es una cadena o bytes
        return 0.0
    
    valor_limpio = re.sub(r'[^0-9.]', '', valor)
    
    try:
        return float(valor_limpio) if valor_limpio else 0.0
    except ValueError:
        # Manejar el caso en el que no se puede convertir a un número de punto flotante
        return 0.0
               
def ejecutar_comando_ssh(ip, puerto, clave_privada_path, usuario,comando_ssh):
    try:
        comando_ssh_completo = f'ssh -i "{clave_privada_path}" {usuario}@{ip} {comando_ssh}'
        resultado = subprocess.run(comando_ssh_completo, shell=True, check=True, capture_output=True, text=True)
        #print(resultado)
        lineas = resultado.stdout.strip().split("\n")
        return lineas
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando SSH: {e}")
        return f"Error al ejecutar el comando SSH: {e}"
           
def obtener_informacion_disco(ip, puerto, clave_privada_path, usuario):
    try:
        comando_ssh = 'df -h'
        lineas = ejecutar_comando_ssh(ip, puerto, clave_privada_path, usuario,comando_ssh)
        encabezado = lineas[0].split()
        informacion_particiones = []
        for linea in lineas[1:]:
            valores = linea.split()
            informacion_particion = {
                encabezado[0]: valores[0],
                encabezado[1]: valores[1],
                encabezado[2]: valores[2],
                encabezado[3]: valores[3],
                'porcentaje_utilizado': valores[4]
            }
            informacion_particiones.append(informacion_particion)
        #print(informacion_particiones)
        return informacion_particiones

    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando SSH: {e}"  
        
def obtener_informacion_ram(ip, puerto, clave_privada_path, usuario):
    try:
        comando_ssh = 'free -h'
        lineas = ejecutar_comando_ssh(ip, puerto, clave_privada_path, usuario, comando_ssh)
        valores = lineas[1].split()
        total = float(limpiar_y_convertir(valores[1]))
        usado = float(limpiar_y_convertir(valores[2]))
        porcentaje_usado = round((usado / total) * 100,2)
        informacion_ram = {
            'Total': valores[1],
            'Usado': valores[2],
            'Free': valores[3],
            'Avaliable': valores[6],
            'Porcentaje_utilizado': porcentaje_usado
        }

        #print(informacion_ram)
        return informacion_ram

    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando SSH: {e}"             

def obtener_informacion_conexiones(cliente):
    contador_estados = cliente.admin.command("serverStatus")["connections"]
    #print(contador_estados)
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
    #print(info_servidor)
    datos_generales = {
        'version': info_servidor.get('version', ''),
        'sistema_operativo': info_servidor.get('buildEnvironment', {}).get('target_os', ''),
    }
    #print(datos_generales)
    return nombre_servidor, endpoint, puerto, datos_generales

def obtener_info_replicas(cliente):
    try:
        info_replicas = cliente.admin.command('replSetGetStatus')
        num_replicas = len(info_replicas.get('members', []))
        estado_replicas = {str(member['_id']): {'name': member['name'], 'type_replica': member['stateStr'],'health': member['health']} for      member in info_replicas.get('members', [])}
        estado_cluster = {str(info_replicas.get('set', 'unknown')): {'ok': info_replicas.get('ok', 0)}}
    except errors.OperationFailure as e:
        num_replicas = 0
        estado_replicas = {}
        estado_cluster = {}
    return num_replicas, estado_replicas, estado_cluster

def obtener_metricas_mongodb(rango_fecha):
    cliente = MongoClient(url_conexion)
    bases_de_datos = cliente.list_database_names()

    num_replicas, estado_replicas,estado_cluster = obtener_info_replicas(cliente)
    nombre_servidor, endpoint, puerto, datos_generales = obtener_metricas_servidor(cliente)
    info_conexiones = obtener_informacion_conexiones(cliente)
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
    return metricas_totales, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales,estado_cluster,info_conexiones

def calcular_minimo(valores):
    return min(valores) if valores else None

def calcular_maximo(valores):
    return max(valores) if valores else None

def calcular_promedio(valores):
    return statistics.mean(valores) if valores else None

def generar_html(info_disco, info_ram, info_conexiones, latencias, metricas_mongodb, es_cluster, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales,estado_cluster,rango_fecha): 
    css_content = read_css_file(css_path)
    codigo_base64 = obtener_base64_de_imagen(ruta_imagen)
    fecha_actual = (datetime.now().date()) - timedelta(days=1)
    region = 'us-east-2'
    template_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>REPORTE DE METRICAS MONGODB</title>
        <style>
                {{ css_content }}
        </style>
    </head>
    <body>
        <h1 class='inlineblock'>Reporte de metricas MongoDB {{fecha_actual}}</h1>
        <img class='inlineblock logo' src="data:image/png;base64, {{codigo_base64}}" alt="Logo MADO" />
        <h3><b class="resaltar">FECHA DE CONSULTA DEL:</b> {{rango_fecha[0]}}  AL: {{rango_fecha[1]}}</h3>
        <h3><b class="resaltar">REGIÓN:</b> {{region}}</h3>
        {% if es_cluster %}
            <h2>Información del Cluster</h2>
            <div class="datagrid">
                <table class="rds-table" border="1">
                    <tbody>
                    {% for rs, clt in estado_cluster.items() %}
                         <tr><td>Versión MongoDB: </td><td>{{datos_generales.version}}</td></tr>
                         <tr><td>Sistema Operativo: </td><td>{{datos_generales.sistema_operativo}}</td></tr>
                         <tr><td>ID Replica: </td><td>{{rs}}</td></tr>
                         <tr><td>Estado del Cluster: </td><td><div {{'class="available"' if clt.ok|trim == '1.0' else 'class="unavailable"' }}></div> {{'available' if clt.ok|trim == '1.0' else 'unavailable' }}</td></tr>
                         <tr><td>Endpoint: </td><td>{{endpoint}}</td></tr>
                         <tr><td>Puerto: </td><td>{{puerto}}</td></tr>
                         <tr><td>Número de réplicas: </td><td>{{num_replicas}}</td></tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
            <h3>Estado de las Réplicas</h3>
            <div class="datagrid">
                <table class="rds-table" border="1">
                    <tbody>
                    {% for id_replica, replica in estado_replicas.items() %}
                         <tr><td colspan='2' class='colspan_mark'>Replica {{ id_replica }}</td></tr>
                         <tr><td>Endpoint: </td><td>{{replica.name}}</td></tr>
                         <tr><td>Tipo: </td><td>{{replica.type_replica}}</td></tr>
                         <tr><td>Estado Replica: </td><td><div {{'class="available"' if replica.health|trim == '1.0' else 'class="unavailable"' }}></div> {{'available' if replica.health|trim == '1.0' else 'unavailable' }}</td></tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <h2>Información del Servidor</h2>
            <p>Nombre del servidor: {{ nombre_servidor }}</p>
            <p>Endpoint: {{ endpoint }}</p>
            <p>Puerto: {{ puerto }}</p>
            <h3>Datos Generales</h3>
            <p>Versión de MongoDB: {{ datos_generales.version }}</p>
            <p>Sistema Operativo: {{ datos_generales.sistema_operativo }}</p>
        {% endif %}
        <h2>Conexiones</h2>
        <div class="datagrid">
            <table class="rds-table" border="1">
                <tbody>
                {% for estado, cantidad in info_conexiones.items() %}
                     <tr><td>{{estado}}</td><td>{{cantidad}}</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        <h1>Métricas de MongoDB</h1>
        <div class="datagrid">
            <table class="rds-table" border="1">
                <tbody>
                {% for metrica in metricas_mongodb %}
                     <tr><td colspan='2' class='colspan_mark'>DB_NAME: {{metrica.nombre}}</td></tr>
                     <tr><td>Tamaño de la base de datos: </td><td>{{metrica.tamanio}} bytes</td></tr>
                     <tr><td>Número total de documentos: </td><td>{{metrica.documentos}}</td></tr>
                     <tr><td>Tamaño del índice: </td><td>{{metrica.indice_tamanio}} bytes</td></tr>
                     <tr><td>Número total de índices: </td><td>{{metrica.indice_documento}}</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        <h2>Uso de Disco</h2>
        <div class="datagrid">
            <table class="rds-table" border="1">
                <tbody>
                {% for disco in info_disco %}
                     <tr><td colspan='2' class='colspan_mark'>Filesystem: {{disco.Filesystem}}</td></tr>
                     <tr><td>Tamaño: </td><td>{{disco.Size}}</td></tr>
                     <tr><td>Utilizado: </td><td>{{disco.Used}}</td></tr>
                     <tr><td>Disponible: </td><td>{{disco.Avail}}</td></tr>
                     <tr><td>Porcentaje de uso: </td><td {{evaluar_valor(2,disco.porcentaje_utilizado)}}>{{disco.porcentaje_utilizado}}</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        <h2>Uso de RAM</h2>
        <div class="datagrid">
            <table class="rds-table" border="1">
                <tbody>
                     <tr><td>Total de RAM:</td><td>{{ info_ram.Total }}</td></tr>
                     <tr><td>RAM Utilizada:</td><td>{{ info_ram.Usado }}</td></tr>
                     <tr><td>RAM Free:</td><td>{{ info_ram.Free }}</td></tr>
                     <tr><td>RAM Avaliable:</td><td>{{ info_ram.Avaliable }}</td></tr>
                     <tr><td>Porcentaje de uso de RAM:</td><td {{evaluar_valor(1,info_ram.Porcentaje_utilizado)}}>{{ info_ram.Porcentaje_utilizado }}%</td></tr>
                </tbody>
            </table>
        </div>
        <h2>Estadísticas de Latencia</h2>
        {% if latencias %}
            <div class="datagrid">
                <table class="rds-table" border="1">
                    <tbody>
                         <tr><td>Latencia Mínima:</td><td {{evaluar_valor(3,min(latencias))}}>{{ min(latencias) }} ms</td></tr>
                         <tr><td>Latencia Máxima:</td><td {{evaluar_valor(3,max(latencias))}}>{{ max(latencias) }} ms</td></tr>
                         <tr><td>Latencia Promedio:</td><td {{evaluar_valor(3,mean(latencias))}}>{{ mean(latencias) }} ms</td></tr>
                    </tbody>
                </table>
            </div>
        {% else %}
            <p>No se pudieron recopilar estadísticas de latencia.</p>
        {% endif %}
    </body>
    </html>
    """
    i_date2 = rango_fecha[0].strftime("%d-%m-%Y")
    f_date2 = rango_fecha[1].strftime("%d-%m-%Y")
    file_html = f'mongodb_metrics_report_{region}_{i_date2}_al_{f_date2}_({AWS_ENVIROMENT}).html'
    with open(file_html, "w") as html_file:
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
            datos_generales=datos_generales,
            estado_cluster=estado_cluster,
            css_content = css_content,
            codigo_base64 = codigo_base64,
            fecha_actual = fecha_actual,
            rango_fecha = rango_fecha,
            region = region,
            evaluar_valor = evaluar_valor
        ))
    print("Archivo HTML generado exitosamente.")

def main():
    print(i_date)
    print(f_date)
    start_time = datetime.strptime(i_date+" 00:00:00", '%d/%m/%Y %H:%M:%S')
    end_time = datetime.strptime(f_date+" 23:59:59", '%d/%m/%Y %H:%M:%S')
    rango_fecha_mongodb = (start_time, end_time)
    #print(rango_fecha_mongodb)
    info_disco = obtener_informacion_disco(ip,22,clave_privada_path,usuario_ssh)
    info_ram = obtener_informacion_ram(ip,22,clave_privada_path,usuario_ssh)
    latencias = obtener_latencia(ip, port, rango_fecha_mongodb)

    metricas_mongodb, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales,estado_cluster,info_conexiones = obtener_metricas_mongodb(rango_fecha_mongodb)

    es_cluster = num_replicas > 1  

    generar_html(info_disco, info_ram, info_conexiones, latencias, metricas_mongodb, es_cluster, num_replicas, estado_replicas, nombre_servidor, endpoint, puerto, datos_generales,estado_cluster,rango_fecha_mongodb)

if __name__ == "__main__":
    main()
