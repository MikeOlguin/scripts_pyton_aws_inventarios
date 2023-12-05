import os
import boto3
from datetime import datetime, timedelta
from jinja2 import Template
import botocore

AWS_ACCESS_KEY_ID="ASIA4QZYTTOM4HLGXCMH"
AWS_SECRET_ACCESS_KEY="qWOxpcmhSYUwYtHJSfEOZ1QPO7NrbMOqpY5tVlvT"
AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjENT//////////wEaCXVzLWVhc3QtMiJHMEUCIQDiRsb8MbOmhjtuS6GJb2sKVV1yr3B0a23rNJJkMY3fhgIgXxYvHlBNdQZsHNQWCPnfD6N/3YNodXA5TtJh4KfRtoQqkAMIPRABGgw4NjA3MjI3OTc0NjUiDMT+7NWhl5u2PtBieirtAppwdrHvKb5b3v9MGcpO253YFaCKWfWIZqiyEfLQtkpKzTPxrKJpc36czE/eCwXeHD1UTbFGznzAvka1GLcxxjCn/YFkIcQF06yQpsC7gjXAsTwl3lBSqn6XgJrD/KKpLxf/62gLy+0z94ZphFW/KRQFFQp5c+26UwSLyYOY5jQqCLAhl5QbcXmvf+d1w1hmelITlpaRO4eWoCZK5mvbWY1g1v81HMWPoZzlH2S00BPToBqSGqh9XpKxKnAPqIKrns4hIKQMFIORspcgE0UZ3zjCNEbTeIX5JqNlmgI3g2/gcNoBogV6LhIVWiD/vVokUqy0gYM9nzyqOQpE46NDSID9+6d4u5voFmdkRc59y996exfA4mfphSsywrSExUkIMkc3thBzLkFJe58sVupBzeEAhU2+xKzfvp4idbxRvoA+XVlm4JPqqJUi6sTJ/MZq6i1JJwJS2QAIH96VBVuZaH2p8QdlJEGqn+7zYSXHMOXzr6sGOqYBG3lwXduEQFV+i9+Nj0WsCP/hIrlEIwgHZ0CSbuxwyOe1jmDOaFI4SXLdv4v0KW4qibL9uepxdrERugLxe+I/1tHXvZrgON4obeTp4M+XWxhwAmac7GJcpICpoV2jmMkbo0rewxsHYiwTBj+y9/gd+/Vihv/2gyv0DkGuxlP9SF5xFR2CkxSA633rMRTB/4ltqLixqsw2/ntvz1GtDKKaqS5IAB3UCQ=="
aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

output_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/'

css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/metric_styles.css'

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

def get_docdb_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time, period=300):
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/DocDB',
        MetricName=metric_name,
        Dimensions=[{'Name': 'DBClusterIdentifier', 'Value': instance_identifier}],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Average']
    )

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

def generate_html_report(metric_data_dict, region, cluster_info, db_info, instances_info, css_content):
    cluster_identifier, cluster_engine, availability_zones = cluster_info
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
            <p>Cluster Engine: {{ cluster_engine }}</p>
            <p>Availability Zones: {{ availability_zones }}</p>
            <h2>Cluster Summary</h2>
            <ul>
                <li>Cluster Name: {{ cluster_identifier }}</li>
                <li>Number of Instances: {{ instances_count }}</li>
                <li>Instance Names:
                    <ul>
                        {% for instance_info in instances_info %}
                            <li>{{ instance_info[0] }}</li>
                        {% endfor %}
                    </ul>
                </li>
            </ul>
            {% for instance_info in instances_info %}
                <h2>Instance: {{ instance_info[0] }}</h2>
                <p>Engine: {{ instance_info[1] }}</p>
                <p>Instance Class: {{ instance_info[2] }}</p>
                {% for metric_name, metric_data in metric_data_dict.items() %}
                    <h3>Metric: {{ metric_name }}</h3>
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
            {% endfor %}
        </body>
        </html>
        """
        template = Template(template_str)
        html_content = template.render(
            metric_data_dict=metric_data_dict,
            region=region,
            cluster_identifier=cluster_identifier,
            cluster_engine=cluster_engine,
            availability_zones=availability_zones,
            instances_count=len(instances_info),
            instances_info=instances_info,
            css_content=css_content
        )
        f.write(html_content)

def main():
    custom_date = '02/12/2023'
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

            for instance_identifier, instance_type in cluster_instances:
                instance_name = instance_identifier
                instance_id = instance_identifier

                db_info = get_docdb_instance_info(docdb_client, instance_identifier)

                end_time = datetime.strptime(custom_date, '%d/%m/%Y')
                start_time = end_time - timedelta(days=1)

                metric_data_dict = {}
                for metric_name in metric_names:
                    metric_data = get_docdb_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time)

                    last_data = metric_data[-1] if metric_data else {}
                    metric_data_dict[metric_name] = [last_data]

                generate_html_report(metric_data_dict, region, cluster_info, db_info, cluster_instances, css_content)

if __name__ == "__main__":
    main()
