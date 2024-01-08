import os
import shutil

def analizar_archivos_html(rutas_principales):
    for ruta in rutas_principales:
        if not os.path.exists(ruta):
            print(f"La ruta {ruta} no existe.")
            return
        archivos = os.listdir(ruta)
        for archivo in archivos:
            archivo_completo = os.path.join(ruta, archivo)
            if os.path.isfile(archivo_completo) and archivo.endswith('.html'):
                if 'DEV' in archivo:
                    carpeta_destino = 'DEV'
                elif 'TEST' in archivo:
                    carpeta_destino = 'QA'
                elif 'SPKOFEQA' in archivo:
                    carpeta_destino = 'QA'
                elif 'PROD' in archivo:
                    carpeta_destino = 'PROD'
                elif 'PORD' in archivo:
                    carpeta_destino = 'PROD'
                else:
                    print(f"El archivo {archivo} no contiene DEV, TEST o PROD en su nombre.")
                    continue

                shutil.move(archivo_completo, os.path.join(ruta, carpeta_destino, archivo))
                print(f"Se movió el archivo {archivo} a la carpeta {carpeta_destino}.")

            

fecha = '06012024'

rutas_a_analizar = [
    rf'C:\Users\mikeo\OneDrive\Documentos\Proyectos Mobility ADO\AWS\scripts_pyton_aws_inventarios\Automatizacion\Reportes_Metricas_AWS_DB_{fecha}\Athena',
    rf'C:\Users\mikeo\OneDrive\Documentos\Proyectos Mobility ADO\AWS\scripts_pyton_aws_inventarios\Automatizacion\Reportes_Metricas_AWS_DB_{fecha}\DocumentDB',
    rf'C:\Users\mikeo\OneDrive\Documentos\Proyectos Mobility ADO\AWS\scripts_pyton_aws_inventarios\Automatizacion\Reportes_Metricas_AWS_DB_{fecha}\DynamoDB',
    rf'C:\Users\mikeo\OneDrive\Documentos\Proyectos Mobility ADO\AWS\scripts_pyton_aws_inventarios\Automatizacion\Reportes_Metricas_AWS_DB_{fecha}\RDS'
]
analizar_archivos_html(rutas_a_analizar)
