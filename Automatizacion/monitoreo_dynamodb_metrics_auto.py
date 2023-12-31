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
#Description:  Script Oficial de monitoreo de DynamoDB  #
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

regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"] 

output_path = 'C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\'

css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/metric_styles.css'

ruta_imagen = "C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/logo_movility.png"

metric_data_dict={} 

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()
    
def save_metric_table_to_base64(metric_name, datapoints, rds_identifier):
    df = pd.DataFrame(datapoints)
    df = df.sort_values(by='Timestamp')
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['Average'], marker='o', linestyle='-', color='blue')
    plt.title(f'Métrica: {metric_name} - Table: {rds_identifier}')
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
       
def main():    
    for region in regions:
        print(f"region = {region}")
        dynamodb = boto3.resource('dynamodb', region_name = region)
        for table in dynamodb.tables.all():
            print(f"tablas = "+table.table_name) 
            css_content = read_css_file(css_path)
            cw = boto3.resource('cloudwatch',region) 
            namespace = "AWS/DynamoDB"
            metric_namelist= ["ProvisionedReadCapacityUnits","ConsumedWriteCapacityUnits","ProvisionedReadCapacityUnits","ProvisionedWriteCapacityUnits"]
            for metric_name in metric_namelist:
                metric = cw.Metric(namespace, metric_name) 
                start_time = datetime.strptime(i_date+" 00:00:00", '%d/%m/%Y %H:%M:%S')
                end_time = datetime.strptime(f_date+" 23:59:59", '%d/%m/%Y %H:%M:%S')                                                                                             
                stat_types = ['Average']
                period = 60
                stats = metric.get_statistics(StartTime=start_time, EndTime=end_time, Period=period, Statistics=stat_types, Dimensions=[{'Name': 'TableName','Value':table.table_name},])
                stats = stats['Datapoints']##diccionario 
                last_data= stats[-1] if stats else {}
                if len(stats) > 0:
                      graphic_metric = save_metric_table_to_base64(metric_name,stats,table.table_name)
                      last_data['graphic_metric'] = graphic_metric
                metric_data_dict[metric_name] = [last_data]        
                generate_html_report(metric_data_dict,region, table.table_name, css_content)

def generate_html_report(metric_data_dict, region, table, css_content):  
    fecha_actual = datetime.now().date()
    i_date2 = i_date.replace('/', '-')
    f_date2 = f_date.replace('/', '-')
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, f'Dynamo_metrics_report_{region}_{table}_{i_date2}_al_{f_date2}_({AWS_ENVIROMENT}).html')
    codigo_base64 = obtener_base64_de_imagen(ruta_imagen)
    f = open (file_path, 'w')
    template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte de metricas Dynamo DB</title>
            <style>
                {{ css_content }}
            </style>
        </head>
        <body>
                <h1 class='inlineblock'>Reporte de metricas Dynamo DB {{fecha_actual}}</h1> 
                <img class='inlineblock logo' src="data:image/png;base64, {{codigo_base64}}" alt="Logo MADO" />
                <h3><b class="resaltar">FECHA DE CONSULTA DEL:</b> {{start_time}}  AL: {{end_time}}</h3>
                <h3><b class="resaltar">TABLA:</b> {{table}}</h3>
                <h3><b class="resaltar">REGIÓN:</b> {{region}}</h3>
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
    html_content = template.render(metric_data_dict=metric_data_dict, region=region,table=table, css_content=css_content,fecha_actual=fecha_actual,codigo_base64=codigo_base64,start_time=i_date,end_time=f_date)
    f.write(html_content)
    f.close()  

if __name__ == "__main__":
    print('> Iniciando ejecución de script reporte de metricas DynamoDB...')
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_SESSION_TOKEN = os.environ['AWS_SESSION_TOKEN']
    AWS_ENVIROMENT = os.environ['AWS_ENVIROMENT']
    i_date = os.environ['FECHA_INICIO']
    f_date = os.environ['FECHA_FIN']
    output_path = output_path+os.environ['DIR_REPORT']
    if 'DEV' in AWS_ENVIROMENT:
        output_path  = output_path+'\\DynamoDB\\DEV\\'
        print('Ambiente de producción (DEV)')
    elif 'PROD' in AWS_ENVIROMENT:
        output_path  = output_path+'\\DynamoDB\\PROD\\'
        print('Ambiente de producción (PROD)')
    elif 'TEST' in AWS_ENVIROMENT:
        output_path  = output_path+'\\DynamoDB\\QA\\'
        print('Ambiente de prueba (TEST)')
    else:
        print('Ambiente no reconocido')
    print('> Recuperacion de variables de ejecución completa...')
    print('> Iniciando generación de reportes...')
    main()
    print('> Finalizando ejecución de script reporte de metricas DynamoDB...')                  