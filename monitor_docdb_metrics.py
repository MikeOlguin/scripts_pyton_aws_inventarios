import boto3
from datetime import datetime, timedelta
from jinja2 import Template
import os
# Variables de entorno
AWS_ACCESS_KEY_ID="ASIAYK5OT6SVYZLF35OE"
AWS_SECRET_ACCESS_KEY="A98GalX4TJzKh61Rbx5DtMMI3IQuRMI/pnRq/1E1"
AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjENP//////////wEaCXVzLWVhc3QtMiJHMEUCIAPQA7NzsXxrk2vy97YivFe73ShlodCTeJLbyIcCYWw3AiEAxeLvLyKpn7QsvKCegR9SvxwHY8oxIQSghSYPOvTaOB0qkAMIPBABGgw1NzMyMDc0NzUzNzEiDO0j3AotcNzxRd9zgCrtAkAZbbz6sWASYfN1hzQ12/WY6mNKuNS1otAbiCKArO8aGIdiN+VjcD8n6VY/eeEe91YGsd9uVBfKmcTBwMWmy4ljaTFsKXgwTUpR/UaXA4lRCEbsUVT660mMKh+ocfQhgCw+5gMce8sUYl0r1u7J4DcWQMTIcgCJ91hmbSZT2OtTEQmWR2ZqMQsHyfSC8NEt0d42ZEbamqh+z9XwO9KRebZXQUdxzpg17F5iq7DN4ml9/zmaK37fNsYBnibCKVbgpyyhGCiZ59XZaB5+gajUyY2rOTtDoqGwDof8BkxDVVRWFLzfC3zu1wzqIp/1ILDfLczzUwbddFfvmkxzKePJrEXpgMXxsRmebp6K5CmZw51KnnB/3fbt5+OUDOf0dp/MjrkP8USkY4z0spsh2a0QxM6xJ0YIch2eMFXkTd6nw2Vz9Q7smRqnKO5FeihsdWDvS1V7cYJqlTQkgwssRm5jSDER4hqtBC8P/ivl111VMKnVr6sGOqYBkoVGacJe1HD07Q3xSwfq0aBnZdkkWizmNPWsaBgTkDfmSUCppTdA0nLIxUN1h0Fyfpec5bfv8JlUq4Wzvqjr71DmBeQpWaFhZ25iqGqNMLNCfdBcABvfx+K+uy/WQZNxTK3I1JjrzqT+hPUgfvn0/pmDELMndZbHxj4FTJ53XRDKOSHyZDozaFJ/G8lXzh3NVRtXX+FC1Vr1ZAqAmAgPBmYIwtQvhg=="
# Arreglo de regiones de AWS en EUA
regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
# Configurar la fecha para la que se desean las métricas (formato: DD/MM/YYYY)
fecha_deseada = "02/12/2023"
fecha_objetivo = datetime.strptime(fecha_deseada, "%d/%m/%Y")
# Lista para almacenar la información del clúster
cluster_info = []

# Lista para almacenar la información del clúster
cluster_info = []

# Lista para almacenar la información de las métricas por clúster
metric_info = []

# Iterar sobre las regiones
for region in regions:
    # Crear un cliente de DocumentDB en la región actual
    client_docdb = boto3.client('docdb', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)

    # Crear un cliente de CloudWatch en la región actual
    client_cloudwatch = boto3.client('cloudwatch', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)

    # Obtener información del clúster
    clusters = client_docdb.describe_db_clusters()
    
    for cluster in clusters["DBClusters"]:
        # Obtener información adicional del clúster usando describe_db_cluster_snapshots
        snapshots = client_docdb.describe_db_cluster_snapshots(DBClusterIdentifier=cluster["DBClusterIdentifier"])

        # Intentar obtener el tamaño asignado desde la información de la última instantánea
        allocated_storage = next((snap["AllocatedStorage"] for snap in snapshots.get("DBClusterSnapshots", []) if "AllocatedStorage" in snap), "N/A")

        # Obtener el ID de la VPC, manejar el caso en el que la clave podría no estar presente
        vpc_id = cluster.get("VpcId", "N/A")

        # Agregar información del clúster
        cluster_info.append({
            "region": region,
            "cluster_identifier": cluster["DBClusterIdentifier"],
            "instance_count": len(cluster.get("DBClusterMembers", [])),  # Número de instancias en el clúster
            "cluster_status": cluster["Status"],
            "allocated_storage": allocated_storage,
            "availability_zones": ', '.join(cluster["AvailabilityZones"]),
            "backup_retention_period": cluster["BackupRetentionPeriod"],
            "db_subnet_group": cluster["DBSubnetGroup"],
            "endpoint": cluster["Endpoint"],
            "engine": cluster["Engine"],
            "engine_version": cluster["EngineVersion"],
            "vpc_security_groups": ', '.join([group["VpcSecurityGroupId"] for group in cluster["VpcSecurityGroups"]]),
            "vpc": vpc_id,
            "instances": [],  # Inicializar la lista de instancias
        })

        # Agregar un renglón vacío como separador entre clústeres
        cluster_info.append({})

        # Obtener información de las instancias directamente usando el identificador del clúster
        instances = client_docdb.describe_db_instances(Filters=[{"Name": "db-cluster-id", "Values": [cluster["DBClusterIdentifier"]]}])
        
        for idx, instance in enumerate(instances["DBInstances"], start=1):
            # Agregar información de las instancias a la lista del clúster correspondiente
            cluster_info[-2]["instances"].append({
                "instance_number": idx,  # Número consecutivo de la instancia en el clúster
                "instance_identifier": instance["DBInstanceIdentifier"],
                "instance_status": instance["DBInstanceStatus"],
            })

        # Obtener las métricas para el día deseado
        end_time = fecha_objetivo + timedelta(days=1)
        metrics = client_cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "m1",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/DocDB",
                            "MetricName": "CPUUtilization",
                            "Dimensions": [
                                {
                                    "Name": "DBClusterIdentifier",
                                    "Value": cluster["DBClusterIdentifier"]
                                },
                            ]
                        },
                        "Period": 60,
                        "Stat": "Average",
                    },
                    "ReturnData": True,
                },
            ],
            StartTime=fecha_objetivo,
            EndTime=end_time,
        )

        # Obtener el valor promedio de la métrica
        average_value = metrics["MetricDataResults"][0]["Values"][0] if metrics["MetricDataResults"][0]["Values"] else "N/A"

        # Agregar información de la métrica por clúster
        metric_info.append({
            "region": region,
            "cluster_identifier": cluster["DBClusterIdentifier"],
            "metric_name": "CPUUtilization",
            "average_value": average_value,
        })

# Crear un archivo HTML con la información recopilada
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Información del Cluster DocumentDB y Métricas de CloudWatch</title>
    <style>
        .cluster-separator {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Información del Cluster DocumentDB y Métricas de CloudWatch</h1>
    <p>Fecha de las métricas: {{ fecha_deseada }}</p>
    <table border="1">
        <tr>
            <th>Región</th>
            <th>Identificador del Clúster</th>
            <th>Número de Instancias en el Clúster</th>
            <th>Estado del Clúster</th>
            <th>Allocated Storage</th>
            <th>Availability Zones</th>
            <th>Backup Retention Period</th>
            <th>DB Subnet Group</th>
            <th>Endpoint</th>
            <th>Engine</th>
            <th>Engine Version</th>
            <th>VPC Security Groups</th>
            <th>VPC</th>
            <th>Métrica</th>
            <th>Valor Promedio</th>
        </tr>
        {% for cluster in cluster_info %}
        {% if cluster.region %}
        <tr>
            <td>{{ cluster.region }}</td>
            <td>{{ cluster.cluster_identifier }}</td>
            <td>{{ cluster.instance_count }}</td>
            <td>{{ cluster.cluster_status }}</td>
            <td>{{ cluster.allocated_storage }}</td>
            <td>{{ cluster.availability_zones }}</td>
            <td>{{ cluster.backup_retention_period }}</td>
            <td>{{ cluster.db_subnet_group }}</td>
            <td>{{ cluster.endpoint }}</td>
            <td>{{ cluster.engine }}</td>
            <td>{{ cluster.engine_version }}</td>
            <td>{{ cluster.vpc_security_groups }}</td>
            <td>{{ cluster.vpc }}</td>
            <td>{{ metric_info[loop.index0].metric_name }}</td>
            <td>{{ metric_info[loop.index0].average_value }}</td>
        </tr>
        {% else %}
        <tr class="cluster-separator"><td colspan="15">&nbsp;</td></tr>
        {% endif %}
        {% for instance in cluster.instances %}
        <tr>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
            <td>{{ instance.instance_number }}</td>
            <td>{{ instance.instance_identifier }}</td>
            <td>{{ instance.instance_status }}</td>
            <td colspan="10"></td>
        </tr>
        {% endfor %}
        {% endfor %}
    </table>
</body>
</html>
"""

# Estructura de datos para almacenar información detallada de las instancias en cada clúster
detailed_cluster_info = []

# Procesar información del clúster y las instancias
for cluster in cluster_info:
    if cluster.get("region"):
        detailed_info = cluster.copy()
        detailed_info["instances"] = [instance for instance in cluster.get("instances", [])]
        detailed_cluster_info.append(detailed_info)

template = Template(html_template)
rendered_html = template.render(fecha_deseada=fecha_deseada, cluster_info=detailed_cluster_info, metric_info=metric_info)

# Guardar el archivo HTML
with open("cluster_and_metrics_info.html", "w") as html_file:
    html_file.write(rendered_html)

print("Información exportada a cluster_and_metrics_info.html")