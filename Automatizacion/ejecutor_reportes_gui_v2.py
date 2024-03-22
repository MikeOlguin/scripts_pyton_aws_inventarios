import subprocess
import os
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from recuperador_credenciales import getCredencialesAWS
URL_DEFAULT = 'https://mobilityado.awsapps.com/start/#/?tab=accounts'
scripts = ["\\monitoreo_athena_metrics_auto.py", "\\monitoreo_documentDB_metrics_auto.py",
          "\\monitoreo_dynamodb_metrics_auto.py", "\\monitoreo_rds_metrics_auto.py"]

def crea_dir(output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Directorio '{output_path}' creado exitosamente.")
        dir_serv = ["\\Athena", "\\DynamoDB","\\DocumentDB", "\\RDS","\\MongoDB","\\GoldenGate"]
        dir_amb = ["\\DEV", "\\QA","\\PROD"]
        for dir_s in dir_serv: 
            serv_path  = output_path+dir_s
            print(f"Directorio '{serv_path}'.")
            if not os.path.exists(serv_path):
                os.makedirs(serv_path)
                print(f"Directorio '{serv_path}' creado exitosamente.")
                for dir_a in dir_amb: 
                    amb_path  = serv_path+dir_a
                    if not os.path.exists(amb_path):
                        os.makedirs(amb_path)
                        print(f"Directorio '{amb_path}' creado exitosamente.")
                    else:
                        print(f"El directorio '{amb_path}' ya existe.")
            else:
                print(f"El directorio '{serv_path}' ya existe.")
    else:
        print(f"El directorio '{output_path}' ya existe.")

def run_program():
    usuario = usuario_entry.get().strip()
    contrasena = contraseña_entry.get().strip()
    url = url_entry.get().strip()
    fecha_inicio = FECHA_INICIO_entry.get()
    fecha_fin = FECHA_FIN_entry.get()
    if not usuario or not contrasena or not url:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return
    else:
        try:
            log_text.insert(tk.END, f"########INICIANDO PROGRAMA########\n", "progress")
            log_text.insert(tk.END, f"########INICIA PROCESO DE OBTENCIÓN DE CREDENCIALES########\n", "progress")
            credenciales = getCredencialesAWS(usuario,contrasena,url)
            log_text.insert(tk.END, f"########TERMINA PROCESO DE OBTENCIÓN DE CREDENCIALES########\n", "success")
            log_text.insert(tk.END, f"########INICIA PROCESO DE GENERACIÓN DE DIRECTORIOS########\n", "progress")
            current_directory = os.path.dirname(os.path.abspath(__file__))
            fecha_file = (datetime.now() - timedelta(days=1)).strftime('%d%m%Y')
            dir = f'Reportes_Metricas_AWS_DB_{fecha_file}'
            output_path = os.path.join(current_directory,dir)
            crea_dir(output_path)
            log_text.insert(tk.END, f"########FINALIZANDO PROCESO DE GENERACIÓN DE DIRECTORIOS########\n", "success")
            log_text.insert(tk.END, f"########INICIA PROCESO DE GENERACIÓN DE REPORTES AWS########\n", "progress")
            for account in credenciales:
                if account['GET']:
                   log_text.insert(tk.END, f"########INICA CUENTA: {account['ACCOUNT']}########\n", "progress")
                   os.environ['AWS_ACCESS_KEY_ID'] = account['ACCESS_KEY_ID']
                   os.environ['AWS_SECRET_ACCESS_KEY'] = account['SECRET_ACCESS_KEY']
                   os.environ['AWS_SESSION_TOKEN'] = account['SESSION_TOCKEN']
                   os.environ['AWS_ENVIROMENT'] = account['ACCOUNT'].upper()
                   os.environ['FECHA_INICIO'] = fecha_inicio
                   os.environ['FECHA_FIN'] = fecha_fin
                   os.environ['DIR_REPORT'] = dir
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
                   log_text.insert(tk.END, f"########FINALIZA CUENTA: {account['ACCOUNT']}########\n", "success")
                else:
                    log_text.insert(tk.END, f"########LAS CREDENCIALES DE LA CUENTA {account['ACCOUNT']} NO SE RECUPERARON########\n", "error")
        except Exception as e:
             log_text.insert(tk.END, f"########ERROR EN EL PROCESO {e}########\n", "error")
        finally:
             log_text.insert(tk.END, f"########FINALIZANDO PROGRAMA########\n", "success")

root = tk.Tk()
root.title("AWS Script GUI")
root.geometry("600x400+50+50")
margin_frame = tk.Frame(root, padx=20, pady=20)
margin_frame.pack(expand=True, fill="both")
tk.Label(margin_frame, text="Usuario:").grid(row=0, column=0, sticky="w")
usuario_entry = tk.Entry(margin_frame, width=40)  # Más largo
usuario_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Label(margin_frame, text="Contraseña:").grid(row=1, column=0, sticky="w")
contraseña_entry = tk.Entry(margin_frame, show="*", width=40)  # Más largo
contraseña_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Label(margin_frame, text="URL:").grid(row=2, column=0, sticky="w")
url_entry = tk.Entry(margin_frame, width=40)
url_entry.insert(0, URL_DEFAULT)
url_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Label(margin_frame, text="FECHA_INICIO:").grid(row=4, column=0, sticky="w")
FECHA_INICIO_entry = DateEntry(margin_frame, date_pattern='dd/MM/yyyy')
FECHA_INICIO_entry.set_date(datetime.now() - timedelta(days=1))
FECHA_INICIO_entry.grid(row=4, column=1, padx=5, pady=5)
tk.Label(margin_frame, text="FECHA_FIN:").grid(row=5, column=0, sticky="w")
FECHA_FIN_entry = DateEntry(margin_frame, date_pattern='dd/MM/yyyy')
FECHA_FIN_entry.set_date(datetime.now() - timedelta(days=1))
FECHA_FIN_entry.grid(row=5, column=1, padx=5, pady=5)
run_button = tk.Button(margin_frame, text="Run Script", command=run_program)
run_button.grid(row=6, column=0, columnspan=2, pady=10)
log_text = tk.Text(margin_frame, height=10, width=70)
log_text.grid(row=8, column=0, columnspan=2, pady=10)
log_text.tag_configure("success", foreground="green")
log_text.tag_configure("error", foreground="red")
log_text.tag_configure("progress", foreground="blue")
root.mainloop()