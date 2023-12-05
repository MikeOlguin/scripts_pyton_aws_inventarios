import os
import boto3
import botocore
from datetime import datetime, timedelta
from jinja2 import Template

AWS_ACCESS_KEY_ID="ASIAYK5OT6SVR7CXF3V6"
AWS_SECRET_ACCESS_KEY="Yiww4ZS+TRtGfYqW/L6FuNF8GDPF/npWonxhTpCN"
AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEAAaCXVzLWVhc3QtMiJHMEUCIQCiBTR7ndZJ24SOrOZ3yXhf7JNtrKM7aKJ/PuPyFSFHtwIgQ7nfdvglPq4AKBHimY7vd+Jg4AJRjdRq/3xR4N4NiLwqkAMIaRABGgw1NzMyMDc0NzUzNzEiDJqQIl2L35josqs63SrtAh82LykGX+AxjGfVrhULAU+xXp1CRDrvGG1RcFXan6WZJzXOCjqSE4Cb3Tu1h+XNhdMh/hv9r87zh1F4mUN2XiAZR2dL6HbSp0S4fyYHI9MaJ1CqISz9BNz5b6uoLZfDbbxV+oyNzaG8eI7FcAj+StZLkU7KCB3XFmEezDo22PDCiagri3feHeA6Qg0H+PPKqQ8xzGT8ZHfoASdlLKyjDMtvZ5ACFg/5/A28XDr9VT8tkj9WBq1EukEcz7kbwjMuWcax/TtKt0aFcA+FHsqyQV8u1bNlFJOGxc5EL4mX07NHQU7i2ZoYFjS0Ov2GSiFiSATk+jiV63NbRvYqIy3B0FBNwW75uaO9wPeS9KNbFyZlLgDYGHKK8fFHqCcrhzgyRgRZPLtnKrJiE76DQbxJ6iBfjqzqxZ//+LYc0J+AUIC2e0N9zeVdl8Rq1y72j3jrOHIbhh925FmHwiQu516VuoVCq0eTqjMEkziSur2FMKHFuasGOqYB0NdB3maoW7NR78GIc0XJYVwMYOAvU1l4YUGzdz47nRp2k9sTPVdBT2JnFxjSQvDr6mVVopkTPlJCHJkVnQGPHEmwHH00fCRyQIKwyiNoPOiNoP7VNxxFcjWFvPpdgsT/J2k/3ib9j949wowEGS3kC+VOPnoZwOkaT6EqWPmA5MNTmHDRxIxFoElF9lzMy7dEvWpIJtsh45cz2L2RuomGssqCE/pBkg=="

custom_date = '02/12/2023'

aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

output_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/'

css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/metric_styles.css'

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()


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
        print("Response from describe_db_clusters:")
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
        print(response)
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


def generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content,cluster_identifier):
    storage_type, engine, allocated_storage = db_info

    file_path = os.path.join(output_path, f'docdb_metrics_report_{region}_{cluster_identifier}.html')

    with open(file_path, 'w') as f:
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DocDB Metrics Report</title>
            <style>
                {{ css_content }}
            </style>
        </head>
        <body>
            <h1>DocDB Metrics Report - {{ region }} - {{ cluster_identifier }}</h1>
            <p>Instance Type: {{ instance_type }}</p>
            <p>Database Type: {{ db_info[1] }}</p>
            <p>Storage Type: {{ db_info[0] }}</p>
            <p>Allocated Storage: {{ db_info[2] }} GB</p>
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
            {% endfor %}
        </body>
        </html>
        """
        template = Template(template_str)
        html_content = template.render(metric_data_dict=metric_data_dict, region=region,
                                       instance_name=instance_name, instance_id=instance_id,
                                       instance_type=instance_type, db_info=db_info, css_content=css_content)
        f.write(html_content)


def main():
    metric_names = ['CPUUtilization', 'FreeStorageSpace', 'ReadIOPS', 'WriteIOPS',
                    'ReadLatency', 'WriteLatency', 'ReadThroughput', 'WriteThroughput', 'FreeStorageSpace']

    css_content = read_css_file(css_path)

    for region in aws_regions:
        cloudwatch_client = boto3.client('cloudwatch', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)

        docdb_client = boto3.client('docdb', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
        clusters = docdb_client.describe_db_clusters()['DBClusters']

        for cluster in clusters:
            cluster_identifier = cluster['DBClusterIdentifier']
            cluster_info = get_docdb_cluster_info(docdb_client, cluster_identifier)
            cluster_instances = get_docdb_cluster_instances(docdb_client, cluster_identifier)
            print(cluster_info)
            end_time = datetime.strptime(custom_date, '%d/%m/%Y')
            start_time = end_time - timedelta(days=1)
            metric_data_dict = {}
            for metric_name in metric_names:
                metric_data = get_docdb_metric(cloudwatch_client, cluster_identifier, metric_name, start_time, end_time)
                last_data = metric_data[-1] if metric_data else {}
                metric_data_dict[metric_name] = [last_data]
            for instance_identifier, instance_type in cluster_instances:
                instance_name = instance_identifier
                instance_id = instance_identifier
                db_info = get_docdb_instance_info(docdb_client, instance_identifier)
                
                print(cluster_identifier)
            generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content,cluster_identifier)


if __name__ == "__main__":
    main()