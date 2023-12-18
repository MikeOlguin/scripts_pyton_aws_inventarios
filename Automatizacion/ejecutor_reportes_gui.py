import subprocess
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""
AWS_ENVIRONMENT_NUM = 5
FECHA_INICIO = "17/12/2023"
FECHA_FIN = "17/12/2023"
AWS_ENVIROMENT=''

def switch_case(case):
    cases = {
        1: "API-DEV",
        2: "API-PORD",
        3: "API-TEST",
        4: "SERV-TEST",
        5: "DATA-DEV",
        6: "DATA-PROD",
        7: "DATA-TEST",
        8: "SERV-DEV",
        9: "SERV-PROD"
    }
    return cases.get(case, "")

def run_script():
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_ENVIRONMENT_NUM, FECHA_INICIO, FECHA_FIN,AWS_ENVIROMENT
    AWS_ENVIRONMENT = switch_case(AWS_ENVIRONMENT_NUM)
    print(f"Generando reportes de {AWS_ENVIRONMENT}")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    fecha_file = (datetime.now() - timedelta(days=1)).strftime('%d%m%Y')
    dir = f'Reportes_Metricas_AWS_DB_{fecha_file}'
    output_path = os.path.join(current_directory,dir)
    print(output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Directorio '{output_path}' creado exitosamente.")
    else:
        print(f"El directorio '{output_path}' ya existe.")
        
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_SESSION_TOKEN'] = AWS_SESSION_TOKEN
    os.environ['AWS_ENVIROMENT'] = AWS_ENVIROMENT
    os.environ['FECHA_INICIO'] = FECHA_INICIO
    os.environ['FECHA_FIN'] = FECHA_FIN
    os.environ['DIR_REPORT'] = dir
    
    scripts = ["\\monitoreo_athena_metrics_auto.py","\\monitoreo_documentDB_metrics_auto.py","\\monitoreo_dynamodb_metrics_auto.py","\\monitoreo_rds_metrics_auto.py"]
    #scripts = ["\\monitoreo_dynamodb_metrics_auto.py"]
    for script in scripts:
        script = current_directory + script
        proceso_script = subprocess.Popen(["python", script])
        proceso_script.communicate()
        if proceso_script.returncode == 0:
            log_text.insert(tk.END, f"El script {script} ha terminado correctamente.\n")
        else:
            log_text.insert(tk.END, f"Error al ejecutar el script {script}.\n")

def clear_fields():
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_ENVIRONMENT_NUM, FECHA_INICIO, FECHA_FIN
    AWS_ACCESS_KEY_ID_entry.delete(0, tk.END)
    AWS_SECRET_ACCESS_KEY_entry.delete(0, tk.END)
    AWS_SESSION_TOKEN_entry.delete(0, tk.END)
    AWS_ENVIRONMENT_NUM_entry.delete(0, tk.END)
    FECHA_INICIO_entry.delete(0, tk.END)
    FECHA_FIN_entry.delete(0, tk.END)
    log_text.delete(1.0, tk.END)

# Crear la interfaz gráfica
root = tk.Tk()
root.title("AWS Script GUI")

# Crear y posicionar los elementos en la interfaz
tk.Label(root, text="AWS_ACCESS_KEY_ID:").grid(row=0, column=0, sticky="w")
AWS_ACCESS_KEY_ID_entry = tk.Entry(root)
AWS_ACCESS_KEY_ID_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="AWS_SECRET_ACCESS_KEY:").grid(row=1, column=0, sticky="w")
AWS_SECRET_ACCESS_KEY_entry = tk.Entry(root, show="*")
AWS_SECRET_ACCESS_KEY_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="AWS_SESSION_TOKEN:").grid(row=2, column=0, sticky="w")
AWS_SESSION_TOKEN_entry = tk.Entry(root)
AWS_SESSION_TOKEN_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="AWS_ENVIRONMENT_NUM:").grid(row=3, column=0, sticky="w")
AWS_ENVIRONMENT_NUM_entry = tk.Entry(root)
AWS_ENVIRONMENT_NUM_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(root, text="FECHA_INICIO:").grid(row=4, column=0, sticky="w")
FECHA_INICIO_entry = tk.Entry(root)
FECHA_INICIO_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(root, text="FECHA_FIN:").grid(row=5, column=0, sticky="w")
FECHA_FIN_entry = tk.Entry(root)
FECHA_FIN_entry.grid(row=5, column=1, padx=5, pady=5)

run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.grid(row=6, column=0, columnspan=2, pady=10)

clear_button = tk.Button(root, text="Clear Fields", command=clear_fields)
clear_button.grid(row=7, column=0, columnspan=2, pady=10)

log_text = tk.Text(root, height=10, width=50)
log_text.grid(row=8, column=0, columnspan=2, pady=10)

# Iniciar la interfaz gráfica
root.mainloop()
