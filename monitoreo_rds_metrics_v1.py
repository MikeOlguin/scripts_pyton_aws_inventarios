import os
import boto3
from datetime import datetime, timedelta
from jinja2 import Template

AWS_ACCESS_KEY_ID="ASIAYK5OT6SVZTUG6WGO"
AWS_SECRET_ACCESS_KEY="ffsQBiKgBFYDfdkr8bpwydu3JQk7FCuYjaefbKAC"
AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEP7//////////wEaCXVzLWVhc3QtMiJIMEYCIQDZZerQyqLDyi/zaVVwtHqODnwXzXbOz43/6tFv2YF9ewIhAJWgcMfGkhUSerey3CQ5/HBb1HUjqOdi7rjeROctwJkNKpADCGgQARoMNTczMjA3NDc1MzcxIgw8MNLb4RsIve11KV8q7QJnFQKjmZdzGm8RVy+hWG//HZxsBBx6E+1hQICmMMUxvTn+M4RxoUamRdJw+/yV7ZqaAqUkeMW8UIzG1E+xiSBUjz+7WHAknjMcNqqhwDJFxCcGD4JsDjEPNMZmZqkElqP5f4j8ofxD6E0GXIFzgbCzo6MC+NrapFvseZ9+56M1Wcz20+1H0BMHoCleiIYCvqRAQDGTTdQZwMEZdQxDj+nNOj8VYjWdHnnnK8cqn2Gk7wpFSvtqICA1KI2S3i45w4QEIgrDdExksv5D4FOAAmepUM1InFwl5mveFc7/AJywofZZIX0dLPkkd3/kjK6iEOGNvufcNdrE6mRJXpU0sehQkfshsf3GMoXp2Bacy83jUUl9CokTPf1Fa900jEgPRmraftJWdk29KbebcoouMexPZMClElz88eKqYM3wvrZlm3YzJBDAhDUsIeKaLSMJ/dPwcIBcOWxO8sg8fQdM7mzKm3MqKJaQc9Z0aw9CcTDypbmrBjqlARAAr6QVeQEyut96tKRrUvHYvwI3AV2Z5ouRfYbdLiJPpNZmteMnFBx4kZljDF5FLHWTK/35r2hWvSkdegFMVl1svwFs6RsuF9tXICfmxhibYu9CmWYD0YcrWZCRFAxM/zaQz26wGt5wvQKztJvVOmDT7ikm5ZFFkLvKJSp69vAFsMMQQXbv7P2ByDszGSU8/WJxrQ7vTm9dDVJtnPDfF/IJkCQiDA=="

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

def generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content):
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
    custom_date = '02/12/2023'  
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
            instance_identifier = instance['DBInstanceIdentifier']
            instance_name = instance.get('DBInstanceIdentifier')
            instance_id = instance['DBInstanceIdentifier']
            instance_type = instance['DBInstanceClass']

            db_info = get_db_info(rds_client, instance_identifier)

            end_time = datetime.strptime(custom_date, '%d/%m/%Y')
            start_time = end_time - timedelta(days=1)

            metric_data_dict = {}
            for metric_name in metric_names:
                metric_data = get_rds_metric(cloudwatch_client, instance_identifier, metric_name, start_time, end_time)

                last_data = metric_data[-1] if metric_data else {}
                metric_data_dict[metric_name] = [last_data]

            generate_html_report(metric_data_dict, region, instance_name, instance_id, instance_type, db_info, css_content)

if __name__ == "__main__":
    main()