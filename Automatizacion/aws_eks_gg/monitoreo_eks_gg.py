import paramiko
import json
from datetime import datetime, timedelta
from jinja2 import Template, exceptions
import base64
from io import StringIO
import time
import pandas as pd
import re
'''
#########################################################
#By:           Jose Miguel Olguin Hernandez             #
#Date:         29/01/2024                               #
#Version:      1.0                                      #
#Description:  Script Oficial de monitoreo de EKS y Gol-#
#              den Gate                                 #
#Company:      CTC                                      #
#Custumer:     MADO                                     #
#########################################################
'''
PRIVATE_KEY_PATH = '/home/oracle/keys/MADOAWSPRDEC2DHEUE2PKEY02.pem'
EKS_IP = '172.26.26.23'
EKS_USER = 'dbalcazar'
COMAND_KUBECTL=''
css_path = 'metric_styles.css'
ruta_imagen = "logo_movility.txt"
#ruta_imagen = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\logo_movility.txt"
toleracia1 = '00:01:00'
toleracia2 = '00:01:00'
toleracia3 = 17  
toleracia4 = 0
toleracia5 = 'Running'
toleracia6 = 1
toleracia7 = 1
PROYECTO = 'OFERTA_BASICA_2_0'
AMBIENTE = 'PRD'
REGION =''

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"El archivo {file_path} no fue encontrado.")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def str_to_json(output):
    try:
        data = json.loads(output)
        return data
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
        
def str_to_number(valor):
    if valor is None:
        return 0.0

    if not isinstance(valor, (str, bytes)):
        return 0.0

    valor_limpio = re.sub(r'[^0-9.]', '', valor)
    try:
        return float(valor_limpio) if valor_limpio else 0.0
    except ValueError:
        return 0.0
    
def str_to_time(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
        return time_obj
    except ValueError as e:
        print(f"Error al convertir la cadena a tiempo: {e}")
        return None
        
def find_alert(key, value):
    #print(f'key: {key}, value: {value}')
    css_class=''
    if value != '<none>':
        if key == 'Lag at Chkpt':
            css_class = 'class="valor_bad"' if str_to_time(value) > str_to_time(toleracia1) else 'class="valor_good"'
        elif key == 'Time Since Chkpt':    
            css_class = 'class="valor_bad"' if str_to_time(value) > str_to_time(toleracia2) else 'class="valor_good"'
        elif key == 'getportinfo':
            css_class = '<label class="valor_good lb_alert">Puertos completos</label>' if value >= toleracia3 else '<label class="valor_good lb_alert">Puertos incompletos</label>' 
        elif key == 'Error':    
            css_class = 'class="valor_bad"' if str_to_number(value) > toleracia4 else 'class="valor_good"'
        elif key == 'STATUS':    
            css_class = 'class="valor_bad"' if value != toleracia5 else 'class="valor_good"'
        elif key == 'AVAILABLE':  
            css_class = 'class="valor_good"' if str_to_number(str(value)) == toleracia6 else 'class="valor_bad"'
        elif key == 'READY':
            if '/' not in str(value):
                css_class = 'class="valor_good"' if str_to_number(str(value)) == toleracia7 else 'class="valor_bad"'
    return css_class
        
path = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\info_rs.json"
path2 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\get_nodes.json"
path3 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\describe_nodes.json"
path4 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\no_terminated_pod.json"
path5 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\resorces_pod.json"
path6 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\info_all.json"
path7 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\aws_eks_gg\\portinfo.json"
def main():
    try:
        print('Iniciando el monitoreo de EKS-GG')
        COMAND_KUBECTL ='kubectl get all -o wide'
        print(f'Ejecutando {COMAND_KUBECTL}...')
        result= run_ssh_command(COMAND_KUBECTL)
        kubectl_get_all_output = result["output"] if result["success"] else result["error"]
        kubectl_get_all_output_json = kubectl_to_json(kubectl_get_all_output)
        COMAND_KUBECTL = 'kubectl get nodes -o wide'
        print(f'Ejecutando {COMAND_KUBECTL}...')
        result2= run_ssh_command(COMAND_KUBECTL)
        kubectl_get_nodes_output = result2["output"] if result2["success"] else result2["error"]
        kubectl_get_nodes_output_json = kubectl_nodes_to_json(kubectl_get_nodes_output)
        pod = kubectl_get_all_output_json['Table_1'][0]['NODE']
        REGION =pod.split('.')[1].upper()
        COMAND_KUBECTL = f'kubectl get node {pod} -o json'
        print(f'Ejecutando {COMAND_KUBECTL} ...')
        result3= run_ssh_command(COMAND_KUBECTL)
        kubectl_describe_nodes_output = result3["output"] if result3["success"] else result3["error"]
        kubectl_describe_nodes_output_json = str_to_json(kubectl_describe_nodes_output)
        COMAND_KUBECTL = f'kubectl describe node {pod} | grep -A 7 "Non-terminated Pods"'
        print(f'Ejecutando {COMAND_KUBECTL} ...')
        result4= run_ssh_command(COMAND_KUBECTL)
        kubectl_describe_nodes_terminated_output = result4["output"] if result4["success"] else result4["error"]
        kubectl_describe_nodes_terminated_output_json = str_to_json(non_terminated_pods_to_json(kubectl_describe_nodes_terminated_output))
        COMAND_KUBECTL = f'kubectl describe node {pod} | grep -A 7 "Allocated resources"'
        print(f'Ejecutando {COMAND_KUBECTL} ...')
        result5= run_ssh_command(COMAND_KUBECTL)
        kubectl_describe_nodes_resources_output = result5["output"] if result5["success"] else result5["error"]
        kubectl_describe_nodes_resources_output_json = str_to_json(allocated_resources_to_json(kubectl_describe_nodes_resources_output))
        COMAND_KUBECTL = ['kubectl exec -it deployment/ggready -- bash','/U03/app/oracle/product/gg/deploy1/19.1_ora11g/./ggsci','info all']
        print(f'Ejecutando {COMAND_KUBECTL} ...')
        result6 = run_ssh_command_gg(COMAND_KUBECTL)
        command_gg_info_all_output = result6["output"] if result6["success"] else result6["error"]
        command_gg_info_all_output_json= gg_info_to_json(command_gg_info_all_output)
        COMAND_KUBECTL = ['kubectl exec -it deployment/ggready -- bash','/U03/app/oracle/product/gg/deploy1/19.1_ora11g/./ggsci','send mgr getportinfo']
        print(f'Ejecutando {COMAND_KUBECTL} ...')
        result7 = run_ssh_command_gg(COMAND_KUBECTL)
        command_gg_getportinfo_output = result7["output"] if result7["success"] else result7["error"]
        command_gg_getportinfo_output_json=gg_getportinfo_to_json(command_gg_getportinfo_output)
        create_report_html(kubectl_get_all_output_json,kubectl_get_nodes_output_json,kubectl_describe_nodes_output_json,kubectl_describe_nodes_terminated_output_json,kubectl_describe_nodes_resources_output_json,command_gg_info_all_output_json,command_gg_getportinfo_output_json,REGION)
        #Prueba Local
        '''
        kubectl_get_all_output_json = read_json_file(path)
        kubectl_get_nodes_output_json=read_json_file(path2)
        kubectl_describe_nodes_output_json=read_json_file(path3)
        kubectl_describe_nodes_terminated_output_json = read_json_file(path4)
        kubectl_describe_nodes_resources_output_json = read_json_file(path5)
        command_gg_info_all_output_json = read_json_file(path6)
        command_gg_getportinfo_output_json = read_json_file(path7)
        REGION = kubectl_get_all_output_json['Table_1'][0]['NODE'].split('.')[1].upper()
        create_report_html(kubectl_get_all_output_json,kubectl_get_nodes_output_json,kubectl_describe_nodes_output_json,kubectl_describe_nodes_terminated_output_json,kubectl_describe_nodes_resources_output_json,command_gg_info_all_output_json,command_gg_getportinfo_output_json,REGION)
        '''
    except Exception as e:
        print(f'ERROR AL GENERAL EL REPORTE: {e}')
    finally:
        print('Finalizando el monitoreo de EKS-GG')
    
def formatear_posible_fecha(fecha_str):
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%SZ')
        fecha_formateada = fecha_obj.strftime('%a, %d %b %Y %H:%M:%S +0000')
        return fecha_formateada
    except ValueError:
        return fecha_str
        
def create_report_html(kubectl_all_items,kubectl_get_nodes_items,kubectl_describe_nodes_items,kubectl_describe_nodes_terminated_items,kubectl_describe_nodes_resources_items,command_gg_info_all_items,command_gg_getportinfo_items,REGION):
    print(f'Iniciando creacion de docuemnto html...')
    try:
        fecha_actual = str(datetime.now().date()).replace('/', '_')
        #file_html = f'C:/Users/mikeo/OneDrive/Escritorio/REPORTE_EKS_GG_{PROYECTO}_{fecha_actual}.html'
        file_html = f'REPORTE_EKS_GG_{PROYECTO}_{fecha_actual}.html'
        codigo_base64 = read_css_file(ruta_imagen).strip()
        css_content = read_css_file(css_path)
        with open(file_html, 'w') as f:
            template_str = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Reporte de monitoreo Golden  {{PROYECTO}}</title>
                    <style>
                    {{ css_content }}
                    </style>
                </head>
                <body>
                <div class='container'>
                  <h1 class='inlineblock'>Reporte de monitoreo EKS-GoldeGate</h1>
                  <img class='inlineblock logo' src="{{codigo_base64}}" alt="Logo MADO" />
                  <h3><b class="resaltar">FECHA DE CONSULTA:</b> {{fecha_actual}}</h3>
                  <h3><b class="resaltar">PROYECTO:</b> {{PROYECTO}}</h3>
                  <h3><b class="resaltar">AMBIENTE:</b> {{AMBIENTE}}</h3>
                  <h3><b class="resaltar">REGION:</b> {{REGION}}</h3>
                  <h2>Estatus de GoldeGate</h2>
                    <div class="datagrid">
                        <table border="1">
                            <thead>
                                <tr><th class='preheader' colspan='{{len(command_gg_info_all_items[0])}}'>info all</th></tr>
                                <tr>
                            {% set first_item = command_gg_info_all_items[0] %}
                            {% for key, value in first_item.items() %}
                                <th>{{ key }}</th>
                            {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                            {% for item_table in command_gg_info_all_items %}
                                <tr>
                                {% for key, value in item_table.items() %}
                                        <td {{find_alert(key,value)}}>{{ value }}</td>
                                {% endfor %}
                                </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                    </div></br>
                    <div class="datagrid">
                        <table border="1">
                            <thead>
                                <tr><th class='preheader' colspan='{{len(command_gg_getportinfo_items[0])}}'>send mgr getportinfo {{find_alert('getportinfo',len(command_gg_getportinfo_items))}}</th></tr>
                                <tr>
                            {% set first_item = command_gg_getportinfo_items[0] %}
                            {% for key, value in first_item.items() %}
                                <th>{{ key }}</th>
                            {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                            {% for item_table in command_gg_getportinfo_items %}
                                <tr>
                                {% for key, value in item_table.items() %}
                                        <td {{find_alert(key,value)}}>{{ value }}</td>
                                {% endfor %}
                                </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                    </div></br>
                  <h3 class="terminal">Commad: kubectl get all</h3>
                      {% for table, table_data in kubectl_all_items.items() %}
                             {% for item_table in table_data %}
                             <div class="datagrid">
                                <table border="1">
                                    <thead>
                                       <tr>
                                    {% for key, value in item_table.items() %}
                                         <th>{{ key }}</th>
                                    {% endfor %}
                                       </tr>
                                    </thead>
                                    <tbody>
                                       <tr>
                                    {% for key, value in item_table.items() %}
                                         <td {{find_alert(key,value)}}>{{ value }}</td>
                                    {% endfor %}
                                       </tr>
                                    </tbody>
                                </table>
                             </div></br>
                             {% endfor %}
                      {% endfor %}
                    <h3 class="terminal">Commad: kubectl get nodes</h3>
                    {% for table, table_data in kubectl_get_nodes_items.items() %}
                    <div class="datagrid">
                        <table border="1">
                            <thead>
                               <tr>
                            {% set first_item = table_data[0] %}
                            {% for key, value in first_item.items() %}
                                <th>{{ key }}</th>
                            {% endfor %}
                               </tr>
                            </thead>
                            <tbody>
                            {% for item_table in table_data %}
                               <tr>
                               {% for key, value in item_table.items() %}
                                      <td>{{ value }}</td>
                               {% endfor %}
                               </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                    </div></br>
                    {% endfor %} 
                    <h3 class="terminal">Commad: kubectl describe node</h3>
                    <ul id="lista3">
                       <li><b>Name:</b> {{kubectl_describe_nodes_items.metadata.name}}</li>
                       <li><b>Labels:</b>
                           <ul>
                       {% for key, value in kubectl_describe_nodes_items.metadata.labels.items() %}
                              <li><b>{{ key }}:</b> {{ value }}</li>
                       {% endfor %}
                           </ul>
                       </li>
                       <li><b>Annotations:</b>
                           <ul>
                       {% for key, value in kubectl_describe_nodes_items.metadata.annotations.items() %}
                              <li><b>{{ key }}:</b> {{ value }}</li>
                       {% endfor %}
                           </ul>
                       </li>
                       <li><b>CreationTimestamp:</b> {{formatear_posible_fecha(kubectl_describe_nodes_items.metadata.creationTimestamp)}}</li>
                       <li><b>Conditions:</b>
                       {% for item_conditions in kubectl_describe_nodes_items.status.conditions %}
                           <ul>  
                       {% for key, value in item_conditions.items() %}
                              <li><b>{{ key }}:</b> {{ formatear_posible_fecha(value) }}</li>
                       {% endfor %}
                           </ul></br>
                        {% endfor %}
                       </li>
                       <li><b>Addresses:</b>
                           <ul>
                       {% for addresses_item in kubectl_describe_nodes_items.status.addresses %}
                       {% for key, value in addresses_item.items() %}
                              <li><b>{{ key }}:</b> {{ value }}</li>
                       {% endfor %}
                       {% endfor %}
                           </ul>
                       </li>
                       <li><b>Capacity:</b>
                           <ul>
                       {% for key, value in kubectl_describe_nodes_items.status.capacity.items() %}
                              <li><b>{{ key }}:</b> {{ value }}</li>
                       {% endfor %}
                           </ul>
                       </li>
                       <li><b>Allocatable:</b>
                           <ul>
                       {% for key, value in kubectl_describe_nodes_items.status.allocatable.items() %}
                              <li><b>{{ key }}:</b> {{ value }}</li>
                       {% endfor %}
                           </ul>
                       </li>
                       <li><b>System Info:</b>
                           <ul>
                       {% for key, value in kubectl_describe_nodes_items.status.nodeInfo.items() %}
                              <li><b>{{ key }}:</b> {{ value }}</li>
                       {% endfor %}
                           </ul>
                       </li>
                       <li><b>Non-terminated Pods:</b>
                           <ul>
                               <div class="datagrid">
                                   <table border="1">
                                       <thead>
                                          <tr>
                                       {% set first_item = kubectl_describe_nodes_terminated_items[0] %}
                                       {% for key, value in first_item.items() %}
                                           <th>{{ key }}</th>
                                       {% endfor %}
                                          </tr>
                                       </thead>
                                       <tbody>
                                       {% for item_table in kubectl_describe_nodes_terminated_items %}
                                          <tr>
                                          {% for key, value in item_table.items() %}
                                                 <td>{{ value }}</td>
                                          {% endfor %}
                                          </tr>
                                       {% endfor %}
                                       </tbody>
                                   </table>
                               </div></br>
                           </ul>
                       </li>
                       <li><b>Allocated resources:</b>
                           <ul>
                               <div class="datagrid">
                                   <table border="1">
                                       <thead>
                                          <tr>
                                       {% set first_item = kubectl_describe_nodes_resources_items[0] %}
                                       {% for key, value in first_item.items() %}
                                           <th>{{ key }}</th>
                                       {% endfor %}
                                          </tr>
                                       </thead>
                                       <tbody>
                                       {% for item_table in kubectl_describe_nodes_resources_items %}
                                          <tr>
                                          {% for key, value in item_table.items() %}
                                                 <td>{{ value }}</td>
                                          {% endfor %}
                                          </tr>
                                       {% endfor %}
                                       </tbody>
                                   </table>
                               </div></br>
                           </ul>
                       </li>
                    </ul>
                </div>        
                </body>
            </html>
            """
            template = Template(template_str)
            html_content = template.render(REGION=REGION,AMBIENTE=AMBIENTE,PROYECTO=PROYECTO,find_alert=find_alert,len=len,css_content=css_content,codigo_base64=codigo_base64,fecha_actual=fecha_actual,kubectl_all_items=kubectl_all_items,kubectl_get_nodes_items=kubectl_get_nodes_items,kubectl_describe_nodes_items=kubectl_describe_nodes_items,formatear_posible_fecha=formatear_posible_fecha,kubectl_describe_nodes_terminated_items=kubectl_describe_nodes_terminated_items,kubectl_describe_nodes_resources_items=kubectl_describe_nodes_resources_items,command_gg_info_all_items=command_gg_info_all_items,command_gg_getportinfo_items=command_gg_getportinfo_items)
            f.write(html_content)
            f.close()
    except exceptions.TemplateSyntaxError as syntax_error:
        print(f"Error de sintaxis en el template: {syntax_error}")
    except exceptions.TemplateError as template_error:
        print(f"Error en el template: {template_error}")
    except Exception as e:
        print(f"Error desconocido: {e}")
    print('Finalizando creacion de docuemnto html...')
    
def non_terminated_pods_to_json(non_terminated_pods_output):
    lines = non_terminated_pods_output.strip().split('\n')

    headers = [header.strip() for header in lines[1].split()]

    pods_data = []

    for line in lines[3:]:
        values = line.split()
        pod_data = {headers[i]: values[i] for i in range(len(headers))}
        pods_data.append(pod_data)

    json_data = json.dumps(pods_data)

    return json_data

def allocated_resources_to_json(allocated_resources_output):
    lines = allocated_resources_output.strip().split('\n')

    resources_data = []

    for line in lines[4:]:
        values = line.split()
        resource_data = {"Resource": values[0], "Requests": values[1], "Limits": values[2]}
        resources_data.append(resource_data)

    json_data = json.dumps(resources_data, indent=2)

    return json_data

def describe_node_to_json(describe_output):
    json_output = json.dumps(describe_output)
    return json_output

def convert_table_to_json(table_lines):
    try:
        if len(table_lines) < 2:
            return None

        df = pd.read_csv(StringIO('\n'.join(table_lines)), sep=r'\s+')

        if df.empty:
            return None

        json_output = df.to_json(orient='records')
        return json_output
    except Exception as e:
        print(f'Error al convertir la tabla a JSON: {e}')
        return None
    
def kubectl_to_json(kubectl_output):
    try:
        lines = [line.strip() for line in kubectl_output.splitlines() if line.strip()]

        table_start_indices = [i for i, line in enumerate(lines) if line.startswith("NAME")]

        tables = {}

        for i, start_index in enumerate(table_start_indices):
            table_name = f"Table_{i + 1}"

            end_index = table_start_indices[i + 1] if i + 1 < len(table_start_indices) else len(lines)

            table_lines = lines[start_index:end_index]

            json_table = convert_table_to_json(table_lines)
            if json_table is not None:
                tables[table_name] = json.loads(json_table)
            else:
                print(f'La tabla {table_name} no pudo convertirse a JSON.')

        return tables
    except Exception as e:
        print(f'Error en la función kubectl_to_json: {e}')
        return None

def convert_table_to_json_nodes(table_lines):
    try:
        headers = re.split(r'\s{2,}', table_lines[0].strip())

        rows = []

        for line in table_lines[1:]:
            values = re.split(r'\s{2,}', line.strip())

            row = {headers[i]: values[i] for i in range(min(len(headers), len(values)))}

            rows.append(row)

        return rows
    except Exception as e:
        print(f'Error al convertir la tabla a JSON: {e}')
        return None

def kubectl_nodes_to_json(kubectl_output):
    try:
        lines = [line.strip() for line in kubectl_output.splitlines() if line.strip()]

        table_start_indices = [i for i, line in enumerate(lines) if line.startswith("NAME")]

        nodes = []

        for i, start_index in enumerate(table_start_indices):
            end_index = table_start_indices[i + 1] if i + 1 < len(table_start_indices) else len(lines)

            table_lines = lines[start_index:end_index]

            json_table = convert_table_to_json_nodes(table_lines)
            if json_table is not None:
                nodes.extend(json_table)
            else:
                print(f'La tabla en el índice {i + 1} no pudo convertirse a JSON.')
        tables = {'Table_1':nodes}        
        return tables
    except Exception as e:
        print(f'Error en la función kubectl_nodes_to_json: {e}')
        return None

def read_css_file(css_path):
    with open(css_path, 'r') as css_file:
        return css_file.read()

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

def extract_get_all(output):
    if not isinstance(output, str):
        raise ValueError("El parámetro 'output' debe ser una cadena de texto.")
    lines = output.strip().split('\n')
    name_line_index = next((index for index, line in enumerate(lines) if "NAME" in line), None)

    if name_line_index is None:
        raise ValueError("No se encontró la línea que contiene 'NAME' en la salida.")
    headers_line = lines[name_line_index]
    headers = headers_line.split()
    indexes = {column: headers.index(column) for column in ['NAME', 'READY', 'STATUS', 'AGE']}
    data = []
    for line in lines[name_line_index + 1:]:
        columns = line.split()
        if all(index in range(len(columns)) for index in indexes.values()):
            entry = {column: columns[index] for column, index in indexes.items()}
            data.append(entry)
    return data

def extract_values(column, output):
    if not isinstance(output, str):
        raise ValueError("El parámetro 'output' debe ser una cadena de texto.")
    headers_line = output.strip().split('\n')[0]
    headers = headers_line.split()
    try:
        column_index = headers.index(column)
    except ValueError:
        raise ValueError(f"La columna '{column}' no se encontró en la salida.")
    lines = output.strip().split('\n')[1:]
    values = [line.split()[column_index] if len(line.split()) > column_index else '' for line in lines]
    return values

def run_ssh_command(commands):
    private_key = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = {"success": False, "output": None, "error": None}
    
    try:
        ssh.connect(EKS_IP, username=EKS_USER, pkey=private_key)
        if isinstance(commands, str):
            command = commands
        elif isinstance(commands, list):
            command = " && ".join(commands)
        else:
            raise ValueError("La entrada debe ser un comando (cadena) o una lista de comandos.")
        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        result["success"] = True
        result["output"] = output if output else None
        result["error"] = error if error else None
    except Exception as e:
        print(e)
        result["error"] = str(e)
    finally:
        ssh.close()
    
    return result

def extract_gg_info_table(info_output):
    start_line_match = re.search(r'^Program\s+Status.*$', info_output, re.MULTILINE)
    if not start_line_match:
        return None
    start_index = start_line_match.start()
    info_output = info_output[start_index:]
    end_index = info_output.find("GGSCI (")
    if end_index == -1:
        end_index = None
    info_table = info_output[:end_index].strip()
    return info_table

def gg_info_to_json(info_output):
    info_table = extract_gg_info_table(info_output)
    if info_table is None:
        return None
    lines = info_table.split('\n')
    data = []
    for line in lines[2:]: 
        columns = re.split(r'\s{2,}', line.strip())
        columns = [col if col else '<none>' for col in columns]
        program = columns[0] if len(columns) > 0 else '<none>'
        status = columns[1] if len(columns) > 1 else '<none>'
        group = columns[2] if len(columns) > 2 else '<none>'
        lag_at_chkpt = columns[3] if len(columns) > 3 else '<none>'
        time_since_chkpt = columns[4] if len(columns) > 4 else '<none>'
        data.append({
            "Program": program,
            "Status": status,
            "Group": group,
            "Lag at Chkpt": lag_at_chkpt,
            "Time Since Chkpt": time_since_chkpt
        })
    json_data = json.dumps(data, indent=2)
    return str_to_json(json_data)

def extract_gg_getportinfo_table(info_output):
    start_line_match = re.search(r'^Entry\s+Port.*$', info_output, re.MULTILINE)
    if not start_line_match:
        return None
    start_index = start_line_match.start()
    info_output = info_output[start_index:]
    end_index = info_output.find("GGSCI (")
    if end_index == -1:
        end_index = None
    info_table = info_output[:end_index].strip()
    return info_table

def gg_getportinfo_to_json(info_output):
    info_table = extract_gg_getportinfo_table(info_output)
    if info_table is None:
        return None
    lines = info_table.split('\n')
    data = []
    for line in lines[2:]: 
        columns = re.split(r'\s{2,}', line.strip())
        columns = [col if col else '<none>' for col in columns]
        entry = columns[0] if len(columns) > 0 else '<none>'
        port = columns[1] if len(columns) > 1 else '<none>'
        erro = columns[2] if len(columns) > 2 else '<none>'
        process = columns[3] if len(columns) > 3 else '<none>'
        assignated = columns[4] if len(columns) > 4 else '<none>'
        program = columns[5] if len(columns) > 4 else '<none>'
        data.append({
            "Entry": entry,
            "Port": port,
            "Error": erro,
            "Process": process,
            "Assigned": assignated,
            "Program":program
        })
    json_data = json.dumps(data, indent=2)
    return str_to_json(json_data)

def run_ssh_command_gg(commands):
    private_key = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = {"success": False, "output": None, "error": None}

    try:
        ssh.connect(EKS_IP, username=EKS_USER, pkey=private_key)
        channel = ssh.invoke_shell()

        if isinstance(commands, str):
            commands = [commands]

        for command in commands:
            channel.send(command + '\n')
            time.sleep(1)  # Asegurar tiempo suficiente para procesar la salida
            output = channel.recv(4096).decode("utf-8")
            result["success"] = True
            result["output"] = output if output else None

    except Exception as e:
        print(e)
        result["error"] = str(e)
    finally:
        channel.close()
        ssh.close()

    return result

if __name__ == "__main__":
    main()