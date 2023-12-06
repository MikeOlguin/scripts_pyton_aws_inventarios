import os
import boto3
import botocore
from datetime import datetime, timedelta
from jinja2 import Template
import base64
import matplotlib.pyplot as plt
import io
import pandas as pd
'''
#########################################################
#By:           Jose Miguel Olguin Hernandez             #
#Date:         06/12/2023                               #
#Version:      1.2                                      #
#Description:  Script Oficial de monitoreo de DocumentDB#
#              AWS CloudWatch                           #
#Company:      CTC                                      #
#Custumer:     MAD                                      # 
#########################################################
'''

AWS_ACCESS_KEY_ID="ASIAYK5OT6SVZWSVA7GV"
AWS_SECRET_ACCESS_KEY="jLUddjxBRI06dcOZnEP0bv5JxXas5gKR9toZGq2k"
AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjECkaCXVzLWVhc3QtMiJIMEYCIQCXgOhX6RceHWtmMYZXsZ6TeLPqtTkyngj329QaW6dGCwIhAP1t0cgvAm+VEex8u6YQzZxsYZKMezDWjxMB5YFelyP0KpkDCJL//////////wEQARoMNTczMjA3NDc1MzcxIgwubDmb1rd5Zyv1LHAq7QL859NuF1tYliTdhA7KiQG32cV4H6KZShc0wluMXXrZrwBPZEWXHvgOfSUv9J4iNiZnRNt+X1A1GVTDjBdf+N4jsqpR4qcQXQXGCzIvhP7aWl2AFxhDVF+53SkX17CbGkPc7hEq/d7+Fndr6H7r8oPnswhVbezhMa/DErixR6hjTUUwF3VzpR2z/44vZNglkTiU+/lF/jo6GaE/nKR5Bo8y6DjQ+E2/4V6aZ84ZwBJE984lGRs3oHvJ36o7LMAFwTKrOvV02jnPat6tGfzEM425cygRmLPSuBM9OWVGlUFDoqYb5Xb1Fw9sCB2yF7Fga7F7sgIKyrWkkoW0NdOwivK2NlcTPKVcInXMKgZmEYluA4z6kr9XxTee3pg2UXwNawHHnuZCX0rajBouWwsJUzu7kWvroajVu6ZBMuDoWuTEZdjt0pWHQD8BDCqCuKlHeMhEgdFyurAw3VB9wCR/alhXDamuEYDG6GJ6qUDKSDC3xsKrBjqlAcVVn4aEk/fYvJYo2UTdMV+0Yhyut8YmoigMCaEG/1F3bpj8MqyJqhHtuDC+ckjgDW6wEqT1UNDloNpv/UYeDZ5rroyL808RD+xePtX61E8gzo1tc4QxE1Xr1qIgQgw52GAshG0LafC307P1KzO2FkFfQyaATVamf+W+/ck+fs4puz5hKGDFsq6pVVh5wvVk7X74LPmJbooeKD3lS752nMr78I4mrg=="

i_date = '06/12/2023'
f_date = '06/12/2023'

aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

output_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/'

css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/metric_styles.css'

ruta_imagen = "C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/logo_movility.png"

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

def save_metric_table_to_base64(metric_name, datapoints, cluster_identifier):
    df = pd.DataFrame(datapoints)
    df = df.sort_values(by='Timestamp')
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['Average'], marker='o', linestyle='-', color='blue')
    plt.title(f'Métrica: {metric_name} - Cluster: {cluster_identifier}')
    plt.xlabel('Timestamp')
    plt.ylabel('Valor promedio')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

    plt.close()

    return img_base64
 
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
    
def obtener_costo_diario(cliente_ce, start_time, end_time, cluster_name):
    try:
        response = cliente_ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'End': end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        results = response['ResultsByTime']
        print(response['ResultsByTime'])
        filtered_results = [result for result in results if any(tag['Key'] == 'DBClusterIdentifier' and tag['Value'] == cluster_name for tag in result.get('Tags', []))]
        costo_diario = sum(float(result['Total']['UnblendedCost']['Amount']) for result in filtered_results)
        return costo_diario
    except Exception as e:
        print(f"Error al obtener el costo diario: {e}")
        return None
    
def get_docdb_metric(cloudwatch_client, cluster_identifier, metric_name, start_time, end_time, period=300):
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/DocDB',
        MetricName=metric_name,
         Dimensions=[{'Name': 'DBClusterIdentifier', 'Value': cluster_identifier}],
        StartTime=start_time_str,
        EndTime=end_time_str,
        Period=period,
        Statistics=['Average']
    )
    #print(response)
    #print(response['Datapoints'])
    return response['Datapoints']


def get_db_info(docdb_client, instance_identifier):
    try:
        response = docdb_client.describe_db_instances(DBInstanceIdentifier=instance_identifier)
        instance = response['DBInstances'][0]
        storage_type = instance.get('StorageType')
        engine = instance.get('Engine')
        allocated_storage = instance.get('AllocatedStorage')
        return storage_type, engine, allocated_storage
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'DBInstanceNotFoundFault':
            print(f"La instancia con el identificador '{instance_identifier}' no fue encontrada.")
        else:
            print(f"Error desconocido al obtener información de la instancia: {e}")
        return None, None, None


def get_docdb_cluster_instances(docdb_client, cluster_identifier):
    try:
        response = docdb_client.describe_db_clusters(DBClusterIdentifier=cluster_identifier)
        #print("Response from describe_db_clusters:")
        #print(response)
        cluster_members = response['DBClusters'][0].get('DBClusterMembers', [])
        return [(member['DBInstanceIdentifier'], member.get('DBInstanceClass', 'N/A')) for member in cluster_members]
    except botocore.exceptions.ClientError as e:
        print(f"Error al obtener información de instancias en el clúster: {e}")
        return []


def get_docdb_cluster_info(docdb_client, cluster_identifier):
    try:
        response = docdb_client.describe_db_clusters(DBClusterIdentifier=cluster_identifier)
        cluster = response['DBClusters'][0]
        return cluster['DBClusterIdentifier'], cluster['Engine'], cluster['AvailabilityZones']
    except botocore.exceptions.ClientError as e:
        print(f"Error al obtener información del clúster: {e}")
        return None, None, None

def get_docdb_instance_info(docdb_client, instance_identifier):
    try:
        response = docdb_client.describe_db_instances(DBInstanceIdentifier=instance_identifier)
        if response['DBInstances']:
            instance = response['DBInstances'][0]
            instance_info = {
                "instance_id": instance.get('DBInstanceIdentifier', 'N/A'),
                "instance_class": instance.get('DBInstanceClass', 'N/A'),
                "Engine": instance.get('Engine', 'N/A'),
                "EngineVersion": instance.get('EngineVersion', 'N/A'),
                "DBInstanceStatus": instance.get('DBInstanceStatus', 'N/A'),
                "Endpoint": instance.get('Endpoint', 'N/A').get('Address'),
                "VPC": instance.get('DBSubnetGroup', 'N/A').get('VpcId')
            }
            return instance_info
        else:
            print(f"No se encontraron instancias con el identificador '{instance_identifier}'.")
            return None
    except botocore.exceptions.ClientError as e:
        print(f"Error al obtener información de la instancia: {e}")
        return None


def generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, css_content,cluster_identifier,instances_data_dict,start_time,end_time):
    fecha_actual = datetime.now().date()
    i_date2 = i_date.replace('/', '-')
    f_date2 = f_date.replace('/', '-')
    file_path = os.path.join(output_path, f'docdb_metrics_report_{region}_{cluster_identifier}_{i_date2}_al_{f_date2}.html')
    codigo_base64 = obtener_base64_de_imagen(ruta_imagen)
    with open(file_path, 'w') as f:
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte de metricas DocumentDB</title>
            <style>
                {{ css_content }}
            </style>
        </head>
        <body>
            <h1 class='inlineblock'>Reporte de metricas DocumentDB {{fecha_actual}}</h1>
            <img class='inlineblock logo' src="data:image/png;base64, {{codigo_base64}}" alt="Logo MADO" />
            <h3><b class="resaltar">FECHA DE CONSULTA DEL:</b> {{start_time}}  AL: {{end_time}}</h3>
            <h3><b class="resaltar">CLUSTER:</b> {{cluster_identifier}}</h3>
            <h3><b class="resaltar">REGIÓN:</b> {{region}}</h3>
            <h2>Instancias del Cluster</h2>
                <div class="datagrid">
                      <table border="1">
                          <thead>
                             <tr>
                                 <th>instance_id</th>
                                 <th>instance_class</th>
                                 <th>Engine</th>
                                 <th>EngineVersion</th>
                                 <th>DBInstanceStatus</th>
                                 <th>Endpoint</th>
                                 <th>VPC</th>
                             </tr>
                           </thead>
                           <tbody>
                        {% for instance_id, instance_data in instances_data_dict.items() %}
                             <tr>
                                 <td>{{ instance_data[0]['instance_id'] }}</td>
                                 <td>{{ instance_data[0]['instance_class'] }}</td>
                                 <td>{{ instance_data[0]['Engine'] }}</td>
                                 <td>{{ instance_data[0]['EngineVersion'] }}</td>
                                 <td><div {{ 'class="available"' if instance_data[0]['DBInstanceStatus'] == 'available' else 'class="unavailable"' }}></div> {{ instance_data[0]['DBInstanceStatus'] }}</td>
                                 <td>{{ instance_data[0]['Endpoint'] }}</td>
                                 <td>{{ instance_data[0]['VPC'] }}</td>
                             </tr>
                        {% endfor %}
                           </tbody>
                      </table>
                </div>
            {% for metric_name, metric_data in metric_data_dict.items() %}
                <h2>Metric: {{ metric_name }}</h2>
                <div class="datagrid">
                     <table border="1">
                      <thead>
                         <tr>
                             <th>Timestamp</th>
                             <th>Average ({{ metric_data[0]['Unit'] }})</th>
                         </tr>
                       </thead>
                       <tbody>  
                         {% for data in metric_data %}
                             <tr>
                                 <td>{{ data['Timestamp'] }}</td>
                                 <td>{{ data['Average'] }}</td>
                             </tr>
                         {% endfor %}
                        </tbody>
                     </table>
                </div>
                <div class="graphic_metric">
                     <img src="data:image/png;base64, {{metric_data[0]['graphic_metric']}}" alt="graphic metric {{ metric_name }}" />
                <div>
            {% endfor %}
        </body>
        </html>
        """
        template = Template(template_str)
        html_content = template.render(metric_data_dict=metric_data_dict, region=region,
                                       instance_name=instance_name, instance_id=instance_id,
                                       instance_type=instance_type, css_content=css_content,cluster_identifier=cluster_identifier,instances_data_dict=instances_data_dict,fecha_actual=fecha_actual,codigo_base64=codigo_base64,start_time=start_time,end_time=end_time)
        f.write(html_content)


def main():
    metric_names = ['CPUUtilization','FreeableMemory','FreeLocalStorage','VolumeBytesUsed',"DatabaseConnections", 'ReadIOPS', 'WriteIOPS',
                    'ReadLatency', 'WriteLatency', 'ReadThroughput', 'WriteThroughput']

    css_content = read_css_file(css_path)

    for region in aws_regions:
        cloudwatch_client = boto3.client('cloudwatch', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)

        docdb_client = boto3.client('docdb', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
        '''
        ce_client = boto3.client('ce', region_name=region,
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                         aws_session_token=AWS_SESSION_TOKEN)
        '''
        clusters = docdb_client.describe_db_clusters()['DBClusters']
        
        for cluster in clusters:
            cluster_identifier = cluster['DBClusterIdentifier']
            cluster_instances = get_docdb_cluster_instances(docdb_client, cluster_identifier)
            start_time = datetime.strptime(i_date+" 00:00:00", '%d/%m/%Y %H:%M:%S')
            end_time = datetime.strptime(f_date+" 23:59:59", '%d/%m/%Y %H:%M:%S')
            metric_data_dict = {}
            instances_data_dict = {}
            #daily_cost = obtener_costo_diario(ce_client,start_time,end_time,cluster_identifier)
            #print("COSTO DIARIO-------")
            #print(daily_cost)
            for metric_name in metric_names:
                metric_data = get_docdb_metric(cloudwatch_client, cluster_identifier, metric_name, start_time, end_time)
                last_data = metric_data[-1] if metric_data else {}
                graphic_metric = save_metric_table_to_base64(metric_name,metric_data,cluster_identifier)
                last_data['graphic_metric'] = graphic_metric
                metric_data_dict[metric_name] = [last_data]
            for instance_identifier, instance_type in cluster_instances:
                instance_name = instance_identifier
                instance_id = instance_identifier
                db_info2 = get_docdb_instance_info(docdb_client, instance_identifier)
                instances_data_dict[instance_identifier] = [db_info2]
            generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, css_content,cluster_identifier,instances_data_dict,start_time,end_time)


if __name__ == "__main__":
    main()