import paramiko
import json
from datetime import datetime
from jinja2 import Template
import base64
from io import StringIO
import os
import pandas as pd
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
path = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\info_rs.json"
path2 = "C:\\Users\\mikeo\\OneDrive\\Documentos\\Proyectos Mobility ADO\\AWS\\scripts_pyton_aws_inventarios\\Automatizacion\\get_nodes.json"

def main():
    print('Iniciando el monitoreo de EKS')
    '''
    COMAND_KUBECTL ='kubectl get all -o wide'
    print(f'Ejecutando {COMAND_KUBECTL}...')
    result= run_ssh_command(COMAND_KUBECTL)
    kubectl_get_all_output = result["output"] if result["success"] else result["error"]
    kubectl_get_all_output_json = kubectl_to_json(kubectl_get_all_output)
    COMAND_KUBECTL = 'kubectl get nodes -o wide'
    print(f'Ejecutando {COMAND_KUBECTL}...')
    result2= run_ssh_command(COMAND_KUBECTL)
    kubectl_get_nodes_output = result2["output"] if result2["success"] else result2["error"]
    kubectl_get_nodes_output_json = kubectl_to_json(kubectl_get_nodes_output)
    print(kubectl_get_nodes_output_json)
    create_report_html(kubectl_get_all_output_json,kubectl_get_nodes_output_json)
    #Prueba Local
    '''
    kubectl_output_json = read_json_file(path)
    kubectl_get_nodes_output_json=read_json_file(path2)
    create_report_html(kubectl_output_json,kubectl_get_nodes_output_json)
    
def create_report_html(kubectl_all_items,kubectl_get_nodes_items):
    print(f'Iniciando creacion de docuemnto html...')
    try:
        fecha_actual = datetime.now().date()
        file_html = f'reporte_eks_gg.html'
        codigo_base64 = read_css_file(ruta_imagen).strip()
        css_content = read_css_file(css_path)
        with open(file_html, 'w') as f:
            template_str = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Reporte de metricas DocumentDB</title>
                    <style>
                    {{ css_content }}
                    </style>
                </head>
                <body>
                  <h1 class='inlineblock'>Reporte de monitoreo EKS-GoldeGate</h1>
                  <img class='inlineblock logo' src="{{codigo_base64}}" alt="Logo MADO" />
                  <h3><b class="resaltar">FECHA DE CONSULTA:</b> {{fecha_actual}}</h3>
                  <h3 class="terminal">Commad: kubectl get all</h3>
                      {% for table, table_data in kubectl_all_items.items() %}
                             {% for item_table in table_data %}
                             <div class="datagrid">
                                <table border="1">
                                    <thead>
                                    {% for key, value in item_table.items() %}
                                       <th>{{ key }}</th>
                                    {% endfor %}
                                    </thead>
                                    <tbody>
                                    {% for key, value in item_table.items() %}
                                       <td>{{ value }}</td>
                                    {% endfor %}
                                    </tbody>
                                </table>
                             </div></br>
                             {% endfor %}
                      {% endfor %}
                </body>
            </html>
            """
            template = Template(template_str)
            html_content = template.render(css_content=css_content,codigo_base64=codigo_base64,fecha_actual=fecha_actual,kubectl_all_items=kubectl_all_items,kubectl_get_nodes_items=kubectl_get_nodes_items)
            f.write(html_content)
            f.close()
    except Exception as e:
        print(f"Error al obtener información de la instancia: {e}")
    print('Finalizando creacion de docuemnto html...')

def convert_table_to_json(table_lines):
    try:
        # Verificar si hay suficientes líneas para construir el DataFrame
        if len(table_lines) < 2:
            return None

        # Crear un DataFrame desde las líneas de la tabla
        df = pd.read_csv(StringIO('\n'.join(table_lines)), sep=r'\s+')

        # Verificar si el DataFrame tiene datos
        if df.empty:
            return None

        # Convertir el DataFrame a formato JSON
        json_output = df.to_json(orient='records')
        return json_output
    except Exception as e:
        print(f'Error al convertir la tabla a JSON: {e}')
        return None

def kubectl_to_json(kubectl_output):
    try:
        # Dividir la cadena en líneas y eliminar líneas en blanco
        lines = [line.strip() for line in kubectl_output.splitlines() if line.strip()]

        # Encontrar los índices donde comienza cada tabla
        table_start_indices = [i for i, line in enumerate(lines) if line.startswith("NAME")]

        # Crear un diccionario para almacenar DataFrames de cada tabla
        tables = {}

        # Iterar sobre los índices de inicio de tabla
        for i, start_index in enumerate(table_start_indices):
            # Obtener el nombre de la tabla (usar el índice de inicio como clave)
            table_name = f"Table_{i + 1}"

            # Encontrar el índice donde termina la tabla actual (usar el próximo índice de inicio o el final de las líneas)
            end_index = table_start_indices[i + 1] if i + 1 < len(table_start_indices) else len(lines)

            # Obtener las líneas de la tabla actual
            table_lines = lines[start_index:end_index]

            # Convertir la tabla a JSON y agregar al diccionario
            json_table = convert_table_to_json(table_lines)
            if json_table is not None:
                tables[table_name] = json.loads(json_table)
            else:
                print(f'La tabla {table_name} no pudo convertirse a JSON.')

        return tables
    except Exception as e:
        print(f'Error en la función kubectl_to_json: {e}')
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

def run_ssh_command(command):
    private_key = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = {"success": False, "output": None, "error": None}
    try:
        ssh.connect(EKS_IP, username=EKS_USER, pkey=private_key)
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

if __name__ == "__main__":
    main()