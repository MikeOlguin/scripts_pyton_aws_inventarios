import os
import boto3
from datetime import datetime
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
#Description:  Script Oficial de monitoreo de RDS DB    #
#              AWS CloudWatch                           #
#Company:      CTC                                      #
#Custumer:     MADO                                     # 
#########################################################
'''
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_SESSION_TOKEN=""
AWS_ENVIROMENT=''
i_date = ''
f_date = ''
aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
output_path = ''
css_path = '\\metric_styles.css'
ruta_imagen = "\\logo_movility.png"

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

def get_rds_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time, period=300):
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName=metric_name,
        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_identifier}],
        StartTime=start_time_str,
        EndTime=end_time_str,
        Period=period,
        Statistics=['Average']
    )

    return response['Datapoints']

def save_metric_table_to_base64(metric_name, datapoints, rds_identifier):
    df = pd.DataFrame(datapoints)
    df = df.sort_values(by='Timestamp')
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['Average'], marker='o', linestyle='-', color='blue')
    plt.title(f'Métrica: {metric_name} - RDS: {rds_identifier}')
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
    
def get_db_info(rds_client, instance_identifier):
    response = rds_client.describe_db_instances(DBInstanceIdentifier=instance_identifier)
    instance = response['DBInstances'][0]
    storage_type = instance['StorageType']
    engine = instance['Engine']
    allocated_storage = instance['AllocatedStorage']

    return storage_type, engine, allocated_storage

def generate_html_report(metric_data_dict, region,instance_data_dict, css_content):
    first_key = next(iter(instance_data_dict))
    fecha_actual = datetime.now().date()
    i_date2 = i_date.replace('/', '-')
    f_date2 = f_date.replace('/', '-')
    file_path = os.path.join(output_path, f'rds_metrics_report_{region}_{first_key}_{i_date2}_al_{f_date2}_({AWS_ENVIROMENT}).html')
    codigo_base64 = obtener_base64_de_imagen(ruta_imagen)
    with open(file_path, 'w') as f:
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>REPORTE DE METRICAS RDS</title>
            <style>
                {{ css_content }}
            </style>
        </head>
        <body>
            {% set key, value = instance_data_dict.items() | first %}
            <h1 class='inlineblock'>Reporte de metricas RDS {{fecha_actual}}</h1>
            <img class='inlineblock logo' src="data:image/png;base64, {{codigo_base64}}" alt="Logo MADO" />
            <h3><b class="resaltar">FECHA DE CONSULTA DEL:</b> {{start_time}}  AL: {{end_time}}</h3>
            <h3><b class="resaltar">DBInstanceIdentifier:</b> {{key}}</h3>
            <h3><b class="resaltar">REGIÓN:</b> {{region}}</h3>
            <h2>Informacion de la DB</h2>
            <div class="datagrid">
                <table class="rds-table" border="1">
                      <tbody>
                         <tr><td>DBInstanceClass</td><td>{{value['DBInstanceClass'] if 'DBInstanceClass' in value else 'N/E'}}</td></tr>
                         <tr><td>Engine</td><td>{{value['Engine'] if 'Engine' in value else 'N/E'}}</td></tr>
                         <tr><td>DBName</td><td>{{value['DBName'] if 'DBName' in value else 'N/E'}}</td></tr>
                         <tr><td>Endpoint</td><td>{{value['Endpoint']['Address'] if 'Endpoint' in value else 'N/E'}}</td></tr>
                         <tr><td>AllocatedStorage</td><td>{{value['AllocatedStorage'] if 'AllocatedStorage' in value else 'N/E'}}</td></tr>
                         <tr><td>VPC</td><td>{{value['DBSubnetGroup']['VpcId'] if 'DBSubnetGroup' in value else 'N/E'}}</td></tr>
                         <tr><td>MultiAZ</td><td>{{value['MultiAZ'] if 'MultiAZ' in value else 'N/E'}}</td></tr>
                         <tr><td>EngineVersion</td><td>{{value['EngineVersion'] if 'EngineVersion' in value else 'N/E'}}</td></tr>
                         <tr><td>LicenseModel</td><td>{{value['LicenseModel'] if 'LicenseModel' in value else 'N/E'}}</td></tr>
                         <tr><td>PubliclyAccessible</td><td>{{value['PubliclyAccessible'] if 'PubliclyAccessible' in value else 'N/E'}}</td></tr>
                         <tr><td>StorageType</td><td>{{value['StorageType'] if 'StorageType' in value else 'N/E'}}</td></tr>
                         <tr><td>MaxAllocatedStorage</td><td>{{value['MaxAllocatedStorage'] if 'MaxAllocatedStorage' in value else 'N/E'}}</td></tr>
                         <tr><td>DBInstanceStatus</td><td><div {{ 'class="available"' if value['DBInstanceStatus'] == 'available' else 'class="unavailable"' if value['DBInstanceStatus'] in ['Failed', 'Deleting'] else 'class="alert"' }}></div> {{value['DBInstanceStatus'] if 'DBInstanceStatus' in value else 'N/E'}}</td></tr>
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
        html_content = template.render(metric_data_dict=metric_data_dict, region=region,instance_data_dict=instance_data_dict, css_content=css_content,fecha_actual=fecha_actual,codigo_base64=codigo_base64,start_time=i_date,end_time=f_date)
        f.write(html_content)

def main():
    metric_names = ['CPUUtilization', 'FreeStorageSpace', 'ReadIOPS', 'WriteIOPS',
                    'ReadLatency', 'WriteLatency', 'ReadThroughput', 'WriteThroughput', 'FreeStorageSpace']

    css_content = read_css_file(css_path)

    for region in aws_regions:
        
        cloudwatch_client = boto3.client('cloudwatch', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
        rds_client = boto3.client('rds', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
        instances = rds_client.describe_db_instances()['DBInstances']
        for instance in instances:
            Engine = instance['Engine']
            if Engine != 'docdb':
               instance_data_dict = {}
               instance_identifier = instance['DBInstanceIdentifier']
               instance_data_dict[instance['DBInstanceIdentifier']] = instance
               start_time = datetime.strptime(i_date+" 00:00:00", '%d/%m/%Y %H:%M:%S')
               end_time = datetime.strptime(f_date+" 23:59:59", '%d/%m/%Y %H:%M:%S')
               metric_data_dict = {}
               for metric_name in metric_names:
                   metric_data = get_rds_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time)
                   last_data = metric_data[-1] if metric_data else {}
                   if len(metric_data) > 0:
                      graphic_metric = save_metric_table_to_base64(metric_name,metric_data,instance_identifier)
                      last_data['graphic_metric'] = graphic_metric
                   metric_data_dict[metric_name] = [last_data]
               if len(instance_data_dict) > 0:
                  generate_html_report(metric_data_dict, region,instance_data_dict, css_content)      

if __name__ == "__main__":
    print('> Iniciando ejecución de script reporte de metricas RDS...')
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ruta_imagen = current_directory+ruta_imagen
    css_path = current_directory+css_path
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_SESSION_TOKEN = os.environ['AWS_SESSION_TOKEN']
    AWS_ENVIROMENT = os.environ['AWS_ENVIROMENT']
    i_date = os.environ['FECHA_INICIO']
    f_date = os.environ['FECHA_FIN']  
    output_path = os.path.join(current_directory,os.environ['DIR_REPORT'])
    print('> Recuperacion de variables de ejecución completa...')
    print('> Iniciando generación de reportes...')
    main()
    print('> Finalizando ejecución de script reporte de metricas RDS...')