import subprocess
import os
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""
AWS_ENVIRONMENT = "API-DEV"
FECHA_INICIO = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
FECHA_FIN = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')

def run_script():
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_ENVIRONMENT, FECHA_INICIO, FECHA_FIN
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID_entry.get()
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_entry.get()
    AWS_SESSION_TOKEN = AWS_SESSION_TOKEN_entry.get()
    AWS_ENVIRONMENT = environment_combobox.get()
    FECHA_INICIO = FECHA_INICIO_entry.get()
    FECHA_FIN = FECHA_FIN_entry.get()
    log_text.insert(tk.END, f"##################INICIANDO METRICAS DE AMBIENTE {AWS_ENVIRONMENT}##################\n", "progress")
    print(f"Generando reportes de {AWS_ENVIRONMENT}")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    fecha_file = (datetime.now() - timedelta(days=1)).strftime('%d%m%Y')
    dir = f'Reportes_Metricas_AWS_DB_{fecha_file}'
    output_path = os.path.join(current_directory,dir)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Directorio '{output_path}' creado exitosamente.")
    else:
        print(f"El directorio '{output_path}' ya existe.")
        
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_SESSION_TOKEN'] = AWS_SESSION_TOKEN
    os.environ['AWS_ENVIROMENT'] = AWS_ENVIRONMENT
    os.environ['FECHA_INICIO'] = FECHA_INICIO
    os.environ['FECHA_FIN'] = FECHA_FIN
    os.environ['DIR_REPORT'] = dir
    scripts = ["\\monitoreo_athena_metrics_auto.py", "\\monitoreo_documentDB_metrics_auto.py",
           "\\monitoreo_dynamodb_metrics_auto.py", "\\monitoreo_rds_metrics_auto.py"]
    for script in scripts:
        name_script = script
        script = current_directory + script
        log_text.insert(tk.END, f"Ejecutando script {name_script} ...\n", "progress")
        proceso_script = subprocess.Popen(["python", script])
        proceso_script.communicate()
        if proceso_script.returncode == 0:
            log_text.insert(tk.END, f"El script {name_script} ha terminado correctamente.\n", "success")
        else:
            log_text.insert(tk.END, f"Error al ejecutar el script {name_script}.\n", "error")
    log_text.insert(tk.END, f"##################FINALIZANDO METRICAS DE AMBIENTE {AWS_ENVIRONMENT}##################\n", "progress")
'''   
def run_script():
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_ENVIRONMENT, FECHA_INICIO, FECHA_FIN
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID_entry.get()
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_entry.get()
    AWS_SESSION_TOKEN = AWS_SESSION_TOKEN_entry.get()
    AWS_ENVIRONMENT = environment_combobox.get()
    FECHA_INICIO = FECHA_INICIO_entry.get()
    FECHA_FIN = FECHA_FIN_entry.get()
    log_text.insert(tk.END, f"##################INICIANDO METRICAS DE AMBIENTE {AWS_ENVIRONMENT}##################\n", "progress")
    print(f"Generando reportes de {AWS_ENVIRONMENT}")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    fecha_file = (datetime.now() - timedelta(days=1)).strftime('%d%m%Y')
    dir = f'Reportes_Metricas_AWS_DB_{fecha_file}'
    output_path = os.path.join(current_directory,dir)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Directorio '{output_path}' creado exitosamente.")
    else:
        print(f"El directorio '{output_path}' ya existe.")
        
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_SESSION_TOKEN'] = AWS_SESSION_TOKEN
    os.environ['AWS_ENVIROMENT'] = AWS_ENVIRONMENT
    os.environ['FECHA_INICIO'] = FECHA_INICIO
    os.environ['FECHA_FIN'] = FECHA_FIN
    os.environ['DIR_REPORT'] = dir
    scripts = ["\\monitoreo_athena_metrics_auto.py", "\\monitoreo_documentDB_metrics_auto.py",
           "\\monitoreo_dynamodb_metrics_auto.py", "\\monitoreo_rds_metrics_auto.py"]
    def execute_script(script_name, script_path):
        log_text.insert(tk.END, f"Ejecutando script {script_name} ...\n", "progress")
        proceso_script = subprocess.Popen(["python", script_path])
        proceso_script.communicate()
        if proceso_script.returncode == 0:
            log_text.insert(tk.END, f"El script {script_name} ha terminado correctamente.\n", "success")
        else:
            log_text.insert(tk.END, f"Error al ejecutar el script {script_name}.\n", "error")

    threads = []
    for script in scripts:
        name_script = script
        script_path = current_directory + script
        thread = threading.Thread(target=execute_script, args=(name_script, script_path))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    log_text.insert(tk.END, f"##################FINALIZANDO METRICAS DE AMBIENTE {AWS_ENVIRONMENT}##################\n", "progress")
'''

root = tk.Tk()
root.title("AWS Script GUI")
root.geometry("650x400+50+50")

margin_frame = tk.Frame(root, padx=20, pady=20)
margin_frame.pack(expand=True, fill="both")

tk.Label(margin_frame, text="AWS_ACCESS_KEY_ID:").grid(row=0, column=0, sticky="w")
AWS_ACCESS_KEY_ID_entry = tk.Entry(margin_frame)
AWS_ACCESS_KEY_ID_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(margin_frame, text="Limpiar", command=lambda: AWS_ACCESS_KEY_ID_entry.delete(0, tk.END)).grid(row=0, column=2)

tk.Label(margin_frame, text="AWS_SECRET_ACCESS_KEY:").grid(row=1, column=0, sticky="w")
AWS_SECRET_ACCESS_KEY_entry = tk.Entry(margin_frame, show="*")
AWS_SECRET_ACCESS_KEY_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(margin_frame, text="Limpiar", command=lambda: AWS_SECRET_ACCESS_KEY_entry.delete(0, tk.END)).grid(row=1, column=2)

tk.Label(margin_frame, text="AWS_SESSION_TOKEN:").grid(row=2, column=0, sticky="w")
AWS_SESSION_TOKEN_entry = tk.Entry(margin_frame)
AWS_SESSION_TOKEN_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(margin_frame, text="Limpiar", command=lambda: AWS_SESSION_TOKEN_entry.delete(0, tk.END)).grid(row=2, column=2)

tk.Label(margin_frame, text="AWS_ENVIRONMENT:").grid(row=3, column=0, sticky="w")
environments = ["API-DEV", "API-PROD", "API-TEST", "SERV-TEST", "DATA-DEV", "DATA-PROD", "DATA-TEST", "SERV-DEV", "SERV-PROD"]
environment_combobox = ttk.Combobox(margin_frame, values=environments, state="readonly")
environment_combobox.set(AWS_ENVIRONMENT)
environment_combobox.grid(row=3, column=1, padx=5, pady=5)

tk.Label(margin_frame, text="FECHA_INICIO:").grid(row=4, column=0, sticky="w")
FECHA_INICIO_entry = DateEntry(margin_frame, date_pattern='dd/MM/yyyy')
FECHA_INICIO_entry.set_date(datetime.now() - timedelta(days=1))
FECHA_INICIO_entry.grid(row=4, column=1, padx=5, pady=5)
tk.Button(margin_frame, text="Limpiar", command=lambda: FECHA_INICIO_entry.delete(0, tk.END)).grid(row=4, column=2)

tk.Label(margin_frame, text="FECHA_FIN:").grid(row=5, column=0, sticky="w")
FECHA_FIN_entry = DateEntry(margin_frame, date_pattern='dd/MM/yyyy')
FECHA_FIN_entry.set_date(datetime.now() - timedelta(days=1))
FECHA_FIN_entry.grid(row=5, column=1, padx=5, pady=5)
tk.Button(margin_frame, text="Limpiar", command=lambda: FECHA_FIN_entry.delete(0, tk.END)).grid(row=5, column=2)

run_button = tk.Button(margin_frame, text="Run Script", command=run_script)
run_button.grid(row=6, column=0, columnspan=2, pady=10)

log_text = tk.Text(margin_frame, height=10, width=70)
log_text.grid(row=8, column=0, columnspan=2, pady=10)
log_text.tag_configure("success", foreground="green")
log_text.tag_configure("error", foreground="red")
log_text.tag_configure("progress", foreground="blue")

root.mainloop()
