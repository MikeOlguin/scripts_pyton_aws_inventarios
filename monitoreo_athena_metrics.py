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
#Description:  Script Oficial de monitoreo de Athena    #
#              AWS CloudWatch                           #
#Company:      CTC                                      #
#Customer:     MADO                                     # 
#########################################################
'''
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_SESSION_TOKEN="//////////wEaCXVzLWVhc3QtMiJHMEUCIDuzwfuLw7EwzO2neqt36mrkN5VitjaW3x9t0zlprexcAiEAl7fWb+l0GGCauNPNsresxWUzto0W+vSbPya1MxawZFUqkAMISRABGgw1NzMyMDc0NzUzNzEiDHTmdgtIX3nowHMz3SrtAg6Q/Kk/MfkL81LL77p3n2ujx/wI642KYh2UqfZ87yKR7Lw2hC8AcHUBiscmz3YbvOt3apLtbOM9yU6hnQHwehBRii+/CNF7irycLJdYtfnRzmCmXWu0hCqyMEy8jpVedIASjb9KcqyUzsBvLtgE1k1rAD60/yXbhXmNFeBZxW5VOXTefs/pGsNfofR1Tzr65aKhNUzoWGyPp9d0dyxHqoEW/b/bf7q8L6D8/PiCDtsouD1S+9n1CvQHuAuajn0AxmdvrVq4Q8tb1bUoon6Xdivno5KzsUk01qWIgpA5yoTyOEi8LKhEVcg+LcfgQwOcyDSVQ9Wxh4sSCUJ8XxMAZiFacMUeWL4dDkydNHxb47n1Ma52mEas4wMqH44UiMxmiIrhWfF3fJdrES4RgjBaeeNyUky32ev7SWRRnmJliu3lsxH7wqRLIfddLMrLudQZXOJa6pyjb0/494qC9CsvpcGsssdKaOMp143ntxi1MPCi56sGOqYBdgbOvA/+hy2693JpFXxVrWMDguU1Nyh3lPRvl/10n4K76SotAk9F6J/WNoa2nc/nFUiEo4/e9A6HXc9HoSlSgFu24VH+yB8mJQDKjq4LXnHUUegUxjcvcmOOSs37b/cpQu7d2cneYkX1mEHnOi5OpZkb9HUBxu2FWN04zaFvjDFDaG4LQEmwRW1OVF6VJ2d/7mKzejNGGwYTIuCVicvUvFVcWjq+6w=="

AWS_ENVIROMENT='DATA_TEST'
i_date = '12/12/2023'
f_date = '12/12/2023'
NUM_QUERYS = 15
aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
#aws_regions = ['us-east-2']
output_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/'
css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/metric_styles.css'
js_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/metric.js'
ruta_imagen = "C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/logo_movility.png"
ruta_b64ND = "C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/scripts_pyton_aws_inventarios/no_disponible.txt"
def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

def save_metric_table_to_base64(metric_name, datapoints, query_execution_id):
    df = pd.DataFrame(datapoints)
    df = df.sort_values(by='Timestamp')
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['Average'], marker='o', linestyle='-', color='blue')
    plt.title(f'Métrica: {metric_name} - Query Execution: {query_execution_id}')
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

def get_databases_tables(athena_client):
    try:
        response_catalogs = athena_client.list_data_catalogs()
        data_catalogs = response_catalogs.get('DataCatalogsSummary', [])

        catalog_database_table_mapping = {}

        for data_catalog in data_catalogs:
            catalog_name = data_catalog.get('CatalogName')

            response_databases = athena_client.list_databases(CatalogName=catalog_name)
            databases = response_databases.get('DatabaseList', [])

            database_table_mapping = {}

            for database in databases:
                database_name = database.get('Name')

                response_tables = athena_client.list_table_metadata(CatalogName=catalog_name, DatabaseName=database_name)
                tables = response_tables.get('TableMetadataList', [])
                if tables:
                   table_names = [{"id": i, "table": table.get('Name')} for i, table in enumerate(tables, start=1)]
                else:
                   table_names = [{} for i, table in enumerate(tables, start=1)]    
                database_table_mapping[database_name] = table_names

            catalog_database_table_mapping[catalog_name] = database_table_mapping

        return catalog_database_table_mapping
    except Exception as e:
        print(f"Error al obtener bases de datos y tablas: {e}")
        return None

def get_athena_metrics(cloudwatch_client, metric_name, start_date, end_date):
    try:
        # Ajusta el namespace según la configuración de tu entorno
        namespace = 'AWS/Athena'

        response = cloudwatch_client.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[
                { 'Name': 'QueryState', 'Value': 'SUCCEEDED' },
                { 'Name': 'QueryType', 'Value': 'DML' }
            ],
            StartTime=start_date,
            EndTime=end_date,
            Period=300,  # Puedes ajustar esto según tus necesidades
            Statistics=['Average']
        )
        #print(response)
        # Filtra solo las entradas relevantes (puedes ajustar según sea necesario)
        metric_values = [{'Average': entry['Average'], 'Timestamp': entry['Timestamp'],'Unit': entry['Unit']} for entry in response['Datapoints']]

        return metric_values

    except Exception as e:
        print(f"Error al obtener métricas de Athena: {e}")
        return None


def get_query_execution_ids(athena_client, start_date, end_date):
    try:
        response = athena_client.list_query_executions(
            MaxResults=NUM_QUERYS,
            WorkGroup='primary'
        )
        query_execution_ids = response.get('QueryExecutionIds', [])
        return query_execution_ids

    except Exception as e:
        print(f"Error al obtener Query Execution IDs: {e}")
        return None
    
def get_query(athena_client,query_execution_id):
    try:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        query_text = response['QueryExecution']['Query']
        #print(query_text)
        return query_text
    except Exception as e:
        print(f"Error al obtener el query: {e}")
        return None
print_data_dic = {}           
def main():
    css_content = read_css_file(css_path)
    js_content = read_css_file(js_path)
    metrics_to_collect = ['EngineExecutionTime', 'ProcessedBytes', 'QueryPlanningTime','QueryQueueTime','ServiceProcessingTime','TotalExecutionTime']
    for region in aws_regions:
        metric_data_dict = {} 
        metric_data_result = {}
        athena_client = boto3.client('athena', region_name=region)
        cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        database_table_mapping = get_databases_tables(athena_client)
        #print(database_table_mapping)
        start_time = datetime.strptime(i_date+" 00:00:00", '%d/%m/%Y %H:%M:%S')
        end_time = datetime.strptime(f_date+" 23:59:59", '%d/%m/%Y %H:%M:%S')   
        query_execution_ids = get_query_execution_ids(athena_client, start_time, end_time)
        
        for query_execution_id in query_execution_ids:
            query_data_dict = {}
            query_text = get_query(athena_client,query_execution_id)
            for metric_name in metrics_to_collect:
                metric_values = get_athena_metrics(cloudwatch_client, metric_name,start_time, end_time)
                if len(metric_values) > 0:
                      graphic_metric = save_metric_table_to_base64(metric_name,metric_values,"")
                      metric_values = [{**entry, 'graphic_metric':graphic_metric} for entry in metric_values]
                else:
                    #print("Value Insert Default")
                    default_img = read_css_file(ruta_b64ND)
                    metric_values = [{**entry, 'graphic_metric':default_img} for entry in metric_values]
                    #print(metric_values)
                if len(metric_values) > 0:    
                   metric_data_dict[metric_name] = metric_values 
                #print(metric_data_dict)     
            query_data_dict["metric_data"] = metric_data_dict
            query_data_dict["Query"] = query_text
            metric_data_result[query_execution_id] = query_data_dict
        print_data_dic[region] = {'DB_MAP': database_table_mapping,"METRIC":metric_data_result}
        #print(print_data_dic)           
        '''
        for catalog, database_table_mapping in database_table_mapping.items():
            for database, tables in database_table_mapping.items():
                for table in tables:
                    start_time = datetime.strptime(i_date+" 00:00:00", '%d/%m/%Y %H:%M:%S')
                    end_time = datetime.strptime(f_date+" 23:59:59", '%d/%m/%Y %H:%M:%S')   
                    query_execution_ids = get_query_execution_ids(athena_client, start_time, end_time)
                    for query_execution_id in query_execution_ids:
                        query_text = get_query(athena_client,query_execution_id)
                        metrics_to_collect = ['EngineExecutionTime', 'ProcessedBytes', 'QueryPlanningTime','QueryQueueTime','ServiceProcessingTime','TotalExecutionTime']
                        for metric_name in metrics_to_collect:
                            metric_values = get_athena_metrics(cloudwatch_client, metric_name,start_time, end_time)
                            if metric_values is not None and len(metric_values) > 0 :
                                metric_values.append({"Query": query_text})
                                key = (catalog, database, table, metric_name)
                                metric_data_dict.setdefault(key, []).extend(metric_values)
        '''                 
    #print(print_data_dic)    
    generate_html_report(print_data_dic, css_content,js_content)

def generate_html_report(print_data_dic, css_content,js_content):
    fecha_actual = datetime.now().date()
    i_date2 = i_date.replace('/', '-')
    f_date2 = f_date.replace('/', '-')
    file_path = os.path.join(output_path, f'Athena_metrics_report_{i_date2}_al_{f_date2}_({AWS_ENVIROMENT}).html')
    codigo_base64 = obtener_base64_de_imagen(ruta_imagen)
    f = open(file_path, 'w')
    template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Athena Metrics Report</title>
            <style>
                {{ css_content }}
            </style>
            <script>
                {{js_content}}
            </script>
        </head>
        <body>
                <h1 class='inlineblock'>Reporte de métricas Athena {{fecha_actual}}</h1>
                <img class='inlineblock logo' src="data:image/png;base64, {{codigo_base64}}" alt="Logo MADO" />
                <h3><b class="resaltar">FECHA DE CONSULTA DEL:</b> {{start_time}}  AL: {{end_time}}</h3>  
                {% for region,print_data_item in print_data_dic.items() %}
                   <h2>REGIÓN: {{ region }}</h2>
                   <h3>TABLAS:</h3>
                   <div class="datagrid">
                     <table border="1">
                      <thead>
                         <tr>
                             <th>Data_Catalog</th>
                             <th>Data Base</th>
                             <th>Table</th>
                         </tr>
                       </thead>
                       <tbody>
                       {% for data_catalog,db_data_item in print_data_item.get('DB_MAP').items() %}
                          {% for db,table_data_item in db_data_item.items() %}
                             {% if table_data_item %}
                              {% for table in table_data_item %}
                                  <tr>
                                     <td>{{data_catalog}}</td>
                                     <td>{{db}}</td>
                                     <td>{{table.get('table')}}</td>
                                  </tr>
                              {% endfor %} 
                             {% else %}
                                  <tr>
                                    <td>{{data_catalog}}</td>
                                    <td>{{db}}</td>
                                    <td>No existen tablas</td>
                                  </tr>
                             {% endif %}
                          {% endfor %}
                       {% endfor %}
                       </tbody>
                       </table>
                    </div>
                    <h3>Metricas por Query</h3>
                    {% for metric_key,metric_data_item in print_data_item.get('METRIC').items() %}
                       <h4 class='title_small showMetrics' onclick='showMetrics("{{metric_key}}",event)'><label class='flecha_show'>&#11166;</label> Query: {{metric_data_item.get('Query')}}, ID: {{metric_key}}</h4>
                       <div id='{{metric_key}}' style='display:none'>
                       {% for metric_name,metric_item in metric_data_item.get('metric_data').items() %}
                          <h4 class='title_micro'>{{metric_name}}</h4>
                          <div class="datagrid">
                            <table border="1">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Average ({{ metric_item[0]['Unit'] }})</th>
                                    </tr>
                                </thead>
                                <tbody>
                                 {% for data in metric_item %}
                                 <tr>
                                    <td>{{ data['Timestamp'] }}</td>
                                    <td>{{ data['Average'] }}</td>
                                 </tr>
                                 {% endfor %}
                                </tbody>
                            </table>
                           </div>
                           <div class="graphic_metric">
                               <img src="data:image/png;base64, {{metric_item[0]['graphic_metric']}}" alt="graphic metric {{ metric_name }}" />
                           </div>
                       {% endfor %}
                       </div>   
                    {% endfor %}  
                {% endfor %}
        </body>
        </html>
        """
    template = Template(template_str)
    html_content = template.render(print_data_dic=print_data_dic, css_content=css_content, fecha_actual=fecha_actual, codigo_base64=codigo_base64, start_time=i_date, end_time=f_date,js_content=js_content)
    f.write(html_content)
    f.close()



if __name__ == "__main__":
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_ENVIROMENT'] = AWS_ENVIROMENT
    os.environ['AWS_SESSION_TOKEN'] = AWS_SESSION_TOKEN
    main()




