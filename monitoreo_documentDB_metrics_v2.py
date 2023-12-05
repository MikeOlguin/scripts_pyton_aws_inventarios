import os
import boto3
import botocore
from datetime import datetime, timedelta
from jinja2 import Template

AWS_ACCESS_KEY_ID = "ASIAYK5OT6SVSXNVTQVF"
AWS_SECRET_ACCESS_KEY = "1+D6q9qkBf2NNVLwDn+6WcYbrvlT4fbZnlKkhMvl"
AWS_SESSION_TOKEN = "IQoJb3JpZ2luX2VjEPz//////////wEaCXVzLWVhc3QtMiJIMEYCIQCiQy1OjqJDBvwaeMCLWdUU8OdRZ4oN50aU5Vs4ZGRRjwIhAMvwdz3ARLxfdJHo81XMJQZ8b1hjO2Z8rggnbIPea2OaKpADCGUQARoMNTczMjA3NDc1MzcxIgxToBuknvj5bNvOWqEq7QKOwgOnaqC28pOrJWlJCH86qac3hzdJsfe2wvwIvPKitaJmYjrGyObXj+ZjGQIg4fUvTW88Y1h25Q5UaDXiPT9Jnd9lzyYF37TgZZyR7K0gVZUFadUR4k6pbuIU3MQfVPsDISA/9OTPhxSmYet39PDAprrqFNhq8596N7yAeGDW55vdmOXa0h/OuCBroQCyv/ILYiUjlAgVicHrd2ooLqmsY4NyriAYKGsBeTAZP88FH9hIhc/MfRV1yP7Lu5r87Uf4y36W9PYcgXF15t2HhzxG8LCxLl+6asCkaA4RGB4FZOn9BIhB1MjsKz9sHyZByoTClqW1dApXbsQ3hKVjM+6kI5hB5KkF2XhsoM4BuiJTZyyqtllk5T8BcL9qYVhC0TsuDK8NiADhGHgL0ozPCMDdPa/uWqEjLL5hG96Yh5/2f/UL9ASQ8z5iQIjgTnpzqgWbRAhlj5uYc47/OONKVLTPS0m+T0bIkA0VMZreVzC+3rirBjqlAfv2G7pYmfBWitu99EB+obY+GTA2750B0vQVtyqic0rHWHtz3x/LTLbvoc3UKVNlY4KVDR/aJlKvLpFXJo4DudGt5SjoquWO0mGwPFi3VfhqVIu6INszYgAEEAzBdo+dg64D7PIx0qe59Vk/sxPQp+heM08JpqUiJrRH4lTQJKb5HimevWrI924puJIoKTt9clGEQ6Om0uu06SCQgEXpJz9ifd2hkA=="
aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

output_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/'

css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/metric_styles.css'

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()


def get_docdb_metric(cloudwatch_client, cluster_identifier, metric_name, start_time, end_time, period=300):
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/DocDB",
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": "DBClusterIdentifier", "Value": cluster_identifier}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )
    return response["MetricDataResults"][0]["Values"]


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


def generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content):
    storage_type, engine, allocated_storage = db_info

    file_path = os.path.join(output_path, f'docdb_metrics_report_{region}_{instance_name}.html')

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
            <h1>DocDB Metrics Report - {{ region }} - {{ instance_name }} ({{ instance_id }})</h1>
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
    custom_date = '30/11/2023'
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
            for instance_identifier, instance_type in cluster_instances:
                instance_name = instance_identifier
                instance_id = instance_identifier

                db_info = get_db_info(docdb_client, instance_identifier)

                end_time = datetime.strptime(custom_date, '%d/%m/%Y')
                start_time = end_time - timedelta(days=1)

                metric_data_dict = {}
                for metric_name in metric_names:
                    metric_data = get_docdb_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time)

                    last_data = metric_data[-1] if metric_data else "N/A"
                    metric_data_dict[metric_name] = [{"Timestamp": end_time, "Average": last_data}]

                generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content)


if __name__ == "__main__":
    main()
