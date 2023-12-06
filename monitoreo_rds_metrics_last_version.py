import os
import boto3
from datetime import datetime, timedelta
from jinja2 import Template
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

aws_access_key = 'ASIAYK5OT6SVR4CGSSX4'
aws_secret_key = 'D9Qwi3SRfWBOGuWyP6QmPPekYhWfc9FVx+DflUZq'
aws_session_token = "IQoJb3JpZ2luX2VjELL//////////wEaCXVzLWVhc3QtMiJHMEUCIB+1I8Fb1//1ExaVMfhp9UV3A7R9ghdlHHFSrx+lusWtAiEAoFKOejb4V+AaqQ82lk+k8CdAJXZVpckHy+hGhZLDncoqkAMIHBABGgw1NzMyMDc0NzUzNzEiDOQOXPuvYwtHF+yy3yrtAr7GL0AGK3e6RapabbzjPPieFirXrCf9RQBYba+reqT8l6d676zFM4e+nAttClPQAIPvn2dkTCTlyBvdPPWbfgFTDD8N1tnYwrXSePI5GlT5Ym0lab22FpSs3scdBp48e8f+jNyEA6cCleQ9z5vqySOSo+FaMyHDxNEvQBZdV27EEeQkqKJTVvVy5WP3h6cu/un0XAJc6Y2bZnD3fnLJBnL8RFlbaWuubhec4gQTTtxEBBymwtM3pQI4ah0a5RNTnhPgXenQXUfnEJpLUz9+4g2cwrc1qdqZb3TDp0an316VE+i4AqJL0bIReHfZXcx4XZwoxYzbP38rUxJKx6C+ynsQsMafxo249TMvQg3SJNtIgDzO8VutIdHWw4EddxSrwf2Ut85wk5dg2KJ+WKB4uv9gPVg/MFRVIeIZ6OyEsvWPPO62qmoA58id/l3NbKsbWy2RcwMu6GGC4VWoFJAA2AvxD7ecbDXiCzOXCDw8MLrJqKsGOqYBrErX5QQoWFDn3sWfp8IfXLc1OoVbaHMLuDd8zuq/51ZLzgG3pc27nl9bexYVRmmYWTOl911tKifjFVso4PGetP1IL+C0gZsXaczmmkj+VXq8w5WF1gXmsJdj8z8bjAgg+ZVTp17fbbUG2tV95pWmRcdjq66GDDgRcuOQ9PVYWRlJs1HpwGlvSGtL78RmZwh93AIEk/6KFAwtfELBwnjgzdPDaNPgKw=="

aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

output_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/'

css_path = 'C:/Users/mikeo/OneDrive/Documentos/Proyectos Mobility ADO/AWS/Script Python/metric_styles.css'

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

def get_rds_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time, period=300):
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName=metric_name,
        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_identifier}],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Average']
    )

    return response['Datapoints']

def get_db_info(rds_client, instance_identifier):
    response = rds_client.describe_db_instances(DBInstanceIdentifier=instance_identifier)
    instance = response['DBInstances'][0]
    storage_type = instance['StorageType']
    engine = instance['Engine']
    allocated_storage = instance['AllocatedStorage']

    return storage_type, engine, allocated_storage

def generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content, timestamps):
    storage_type, engine, allocated_storage = db_info

    file_path = os.path.join(output_path, f'rds_metrics_report_{region}_{instance_name}.html')

    with open(file_path, 'w') as f:
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RDS Metrics Report</title>
            <style>
                {{ css_content }}
            </style>
        </head>
        <body>
            <h1>RDS Metrics Report - {{ region }} - {{ instance_name }} ({{ instance_id }})</h1>
            <p>Instance Type: {{ instance_type }}</p>
            <p>Database Type: {{ db_info[1] }}</p>
            <p>Storage Type: {{ db_info[0] }}</p>
            <p>Allocated Storage: {{ db_info[2] }} GB</p>
            {% for metric_name, metric_data in metric_data_dict.items() %}
                <h2>Metric: {{ metric_name }}</h2>
                <img src="{{ metric_name }}.png" alt="{{ metric_name }}">
            {% endfor %}
        </body>
        </html>
        """
        template = Template(template_str)
        html_content = template.render(metric_data_dict=metric_data_dict, region=region,
                                       instance_name=instance_name, instance_id=instance_id,
                                       instance_type=instance_type, db_info=db_info, css_content=css_content)
        f.write(html_content)

def generate_plots(metric_data_dict, timestamps, region, instance_name):
    for metric_name, metric_data in metric_data_dict.items():
        plt.figure()
        plt.plot(timestamps, [data['Average'] for data in metric_data[0]], label=metric_name)
        plt.title(f'RDS Metrics - {metric_name} - {region} - {instance_name}')
        plt.xlabel('Timestamp')
        plt.ylabel('Average Value')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{metric_name}.png')

def main():
    custom_date = '01/12/2023'  
    metric_names = ['CPUUtilization', 'FreeStorageSpace', 'ReadIOPS', 'WriteIOPS',
                    'ReadLatency', 'WriteLatency', 'ReadThroughput', 'WriteThroughput', 'FreeStorageSpace']

    css_content = read_css_file(css_path)

    for region in aws_regions:
        cloudwatch_client = boto3.client('cloudwatch', region_name=region, aws_access_key_id=aws_access_key,
                                         aws_secret_access_key=aws_secret_key, aws_session_token=aws_session_token)

        rds_client = boto3.client('rds', region_name=region, aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_key, aws_session_token=aws_session_token)
        instances = rds_client.describe_db_instances()['DBInstances']

        for instance in instances:
            instance_identifier = instance['DBInstanceIdentifier']
            instance_name = instance.get('DBInstanceIdentifier')
            instance_id = instance['DBInstanceIdentifier']
            instance_type = instance['DBInstanceClass']

            db_info = get_db_info(rds_client, instance_identifier)

            end_time = datetime.strptime(custom_date, '%d/%m/%Y')
            start_time = end_time - timedelta(days=1)

            metric_data_dict = {}
            timestamps = None
            for metric_name in metric_names:
                metric_data = get_rds_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time)

                timestamps = [data['Timestamp'] for data in metric_data] if metric_data else []

                last_data = metric_data[-1] if metric_data else {}
                metric_data_dict[metric_name] = [last_data]

            generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content, timestamps)

            generate_plots(metric_data_dict, timestamps, region, instance_name)

if __name__ == "__main__":
    main()