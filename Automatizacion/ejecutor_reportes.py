import subprocess
import os
from datetime import datetime,timedelta

AWS_ACCESS_KEY_ID="ASIA2UWAKU7WS3YJI36G"
AWS_SECRET_ACCESS_KEY="WDECEfqSLTKTgH2Eo44KqRTa4EBBA44+862n84Bp"
AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEEsaCXVzLWVhc3QtMiJIMEYCIQC4ODlHuLpGMjrPrKpr7PmW9x/bO9dL7LBPPL0lKQaw5QIhALRzE8NqFSk+quTjJ7yH/34WYbX/JljzY6BSbs9zNYfYKpkDCMT//////////wEQARoMNzMxNjIxNTMzNjc3IgzeM2buZxEXLM9/e1Eq7QLpR7R3YWgT0WB/YGDDFkTzEZEAaxZxmTQuyQj5qfR3kU2SHyvf4m87mp9D2dFnrlejAdVmoG6Uhgbi42Q0QlER1wls3wQhJcTS+hR35Zy5B23iNHQW1WVXFpxq17CBDb9mCNuzhLz4iJMpYwOKvKw4F6Oc7Ng0trdqUmabchF9ZVy3EZNEkj3c5uWwJMYPzo8yjyVq+oQMcaN5rVoqEj9oL8wXMI4waCNwqIIlxN2bA9W1HYCiGtmn5jgKOQtjIeVgPO1fnkQyPJ6AF2IDq60MPk7BjQSy3wTjPxd/qhvav75gu3krD0Qs4tmBY1h/a9eykBmVwgNCCEoj243A8bj9qFyp3pRegFO/52nEtVsQPjJPQyC+WmGnpaqWUszzKWRnhruq/X8KJDfcQ3EORoaYVbIKB5+DBd0+pY7w7cp85MuLa/p6W6ftS6A2AeYKZyg1kQVktB75iYh6qhLO6p5x02gFDuCpyRDOA36UvDCHqIKsBjqlAR9F241QkPNSdAZyLT5VM4hnvEA2uZcTd8XD8w+8G2h7UJwg2Vsob8SfytboyCSGzdTl2ml9TQIGs9sIPJ8+B3+fz63c0sKBXnztDIpd6/hRWUpnXhvPhd8x8r+whNs2rc4R/Imq/Op4qQkX591fLvS/4Rhb3DnX380iRCTCd88h9o5FwgFFduFaCsykIPd6ZQ2VVibO59P3m7jmr6U/tlirUTf1sQ=="

AWS_ENVIROMENT_NUM=9
AWS_ENVIROMENT=''

FECHA_INICIO = '17/12/2023'
FECHA_FIN = '17/12/2023'
rojo = "\033[91m"
verde = "\033[92m"
negrita = "\033[1m"
subrayado = "\033[4m"
inverso = "\033[7m"
fin_color = "\033[0m"

def switch_case(case):
    cases = {
        1: 'API-DEV',
        2: 'API-PORD',
        3: 'API-TEST',
        4: 'SERV-TEST',
        5: 'DATA-DEV',
        6: 'DATA-PROD',
        7: 'DATA-TEST',
        8: 'SERV-DEV',
        9: 'SERV-PROD'
    }
    return cases.get(case, '')

def main():
    AWS_ENVIROMENT = switch_case(AWS_ENVIROMENT_NUM)
    print(f'Generando reportes de {AWS_ENVIROMENT}')
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
        script = current_directory+script
        proceso_script = subprocess.Popen(["python",script])
        proceso_script.communicate()  
        if proceso_script.returncode == 0:
            print(verde+negrita + subrayado + f"El script {script} ha terminado correctamente."+fin_color)
        else:
            print(rojo+negrita + subrayado + f"Error al ejecutar el script {script}."+fin_color)

if __name__ == "__main__":
    main()
    