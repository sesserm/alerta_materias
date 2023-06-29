import os
import pandas as pd
import psycopg2
import numpy as np
from dotenv import load_dotenv
from utilidad import enviar_correo, obtener_var_entorno

filename_economia = "./materias_economia.csv"
filename_contador = "./materias_contador.csv"
filename_estadistica = "./materias_estadistica.csv"
filename_admin = "./materias_administracion.csv"
filename_tecnologo_univ = "./materias_tecnologo_gestion_univ.csv"
filename_tecnologo_admin = "./materias_tecnologo_admin.csv"

csv_archivos = [filename_economia, filename_contador,
                filename_estadistica, filename_admin, filename_tecnologo_univ, filename_tecnologo_admin]

# Obtener una lista de todos los archivos en el directorio actual
archivos_cargar = os.listdir()

# Iterar sobre la lista de archivos y ejecutar cada archivo Python
for archivo in archivos_cargar:
    # Solo ejecutar archivos Python
    if archivo.endswith(".py") and archivo.startswith("listado"):
        os.system(f"python {archivo}")

for archivo in csv_archivos:
    if not os.path.isfile(archivo):
        print(f"El archivo {archivo} no existe en el directorio.")
        raise SystemExit

dfs = []

# loop para leer cada archivo y agregar su dataframe a la lista
for archivo in csv_archivos:
    df = pd.read_csv(archivo)
    dfs.append(df)

# concatenar todos los dataframes en uno único
df_total = pd.concat(dfs, ignore_index=True)

unique_df = df_total.drop_duplicates(subset='CODIGO')
unique_df = unique_df.reset_index(drop=True)

for archivo in csv_archivos:
    try:
        os.remove(archivo)
        print(f"Archivo {archivo} borrado exitosamente.")
    except OSError as e:
        print(f"Error al borrar archivo {archivo}: {e}")

print(
    f"Filas totales: {len(unique_df)}, Columnas totales: {len(unique_df.columns)}")

#Obtengo variables de entorno a nivel global
variables_entorno = obtener_var_entorno()

# Me conecto a la base
try:
    conn = open_connection()
  #  conn = psycopg2.connect(
  #      database = variables_entorno.get('PGDATABASE'),
  #      user = variables_entorno.get('PGUSER'),
  #      password = variables_entorno.get('PGPASSWORD'),
  #      host = variables_entorno.get('PGHOST'),
  #      port = variables_entorno.get('PGPORT')
  #  )
except psycopg2.DatabaseError as error:
    print(f"Ha ocurrido un error al conectar a la base de datos: {error}")
    destinatarios = [variables_entorno.get('MAIL')]
    asunto = 'ERROR - PROYECTO ALERTA-FCEA '
    mensaje = f'No se pudo conectar a la base en el script de calendario.'
    enviar_correo(destinatarios, asunto, mensaje)

cursor = conn.cursor()
QUERY = "SELECT * FROM alerta_facultad.dim_materias"
cursor.execute(QUERY)
rows = cursor.fetchall()
headers = [desc[0].upper() for desc in cursor.description]
tabla = pd.DataFrame(rows, columns=headers)
tabla = tabla.reset_index(drop=True)


if tabla.empty:
    SQL_INSERT = "INSERT INTO alerta_facultad.dim_materias (codigo, materia) VALUES (%s, %s)"
    for index, row in unique_df.iterrows():
        cursor.execute(SQL_INSERT, (row['CODIGO'], row['MATERIA']))

        # confirmar los cambios en la base de datos
    conn.commit()

    # cerrar la conexión y el cursor
    cursor.close()
    conn.close()
#Tabla es lo que esta cargado, UNIQUE_df es lo que viene del scrapeo 
else:
    if len(unique_df) != len(tabla):
        print("Los dataframes no tienen la misma cantidad de lineas.") #Puede tener de mas o de menos.
        my_set_cargado = set([frozenset(x) for x in tabla.to_numpy()])
        my_set_comparar = set([frozenset(x) for x in unique_df.to_numpy()])
        diff_set1 = my_set_cargado.difference(my_set_comparar)
        diff_tuple1 = tuple(diff_set1)
        diff_set2 = my_set_comparar.difference(my_set_cargado)
        diff_tuple2 = tuple(diff_set2)
        #Si alguna viene con algo eso implica que cambio la cantidad de filas se argegaron o sacaron materias (puede ser tambien algun cambio de nombre que lo deteca como nueva o faltante.)
        items_faltantes = list()
        #Se asume que el codigo no sera nunca igual a la materia
        if len(diff_tuple1) != 0:
            for codigo,materia in diff_tuple1:
                items_faltantes.append([codigo,materia])

        if len(diff_tuple2) != 0:
            for codigo, materia in diff_tuple2:
                items_faltantes.append([codigo, materia])    
        print(items_faltantes)
        destinatarios = [variables_entorno.get('MAIL')]
        asunto = 'ERROR - PROYECTO ALERTA-FCEA '
        mensaje = f'Error al hacer la carga del listado de materias. Dataframes no tienen el mismo len\n\nSe tienen los siguientes items faltantes (es un set por lo que puede no estar ordenado el codigo y materia):\n\n{items_faltantes}\n\nRecorda que puede ser que falten scrapear items o sean materias que las sacaron\n\nPara determinar esto: Si la materia esta en DW, entonces la sacaron y hay que quitarla. Si la materia no esta en DW falta scrapear y se debe agregar'
        enviar_correo(destinatarios, asunto, mensaje)   
        # FALTA AGREGAR FUNCION DE NOTIFICACION. SE REQUIERE MODULACION PREVIA
    else:
        print('Los dataframes tienen la misma cantidad de lineas.Son iguales?')
        my_set_cargado = set([frozenset(x) for x in tabla.to_numpy()])
        my_set_comparar = set([frozenset(x) for x in unique_df.to_numpy()])
        diff_set1 = my_set_cargado.difference(my_set_comparar)
        if len(diff_set1) == 0:
            print('Los dataframes son iguales')
            destinatarios = [variables_entorno.get('MAIL')]
            asunto = 'STATUS CORRECTO - PROYECTO ALERTA-FCEA '
            mensaje = f'Se mantienen las mismas materias de las grillas que desde la ultima vez.'
            enviar_correo(destinatarios, asunto, mensaje)
        else:
            try:
                print('Borrando registros...')
                SQL_DELETE = "DELETE FROM alerta_facultad.dim_materias"
                cursor.execute(SQL_DELETE)
                # confirmar los cambios en la base de datos
                conn.commit()
                print('Insertando registros...')
                SQL_INSERT = "INSERT INTO alerta_facultad.dim_materias (codigo, materia) VALUES (%s, %s)"
                for index, row in unique_df.iterrows():
                    cursor.execute(SQL_INSERT, (row['CODIGO'], row['MATERIA']))
                # confirmar los cambios en la base de datos
                conn.commit()
                # cerrar la conexión y el cursor
                cursor.close()
                conn.close()
            except:
                destinatarios = [variables_entorno.get('MAIL')]
                asunto = 'STATUS - PROYECTO ALERTA-FCEA'
                mensaje = f'El scrapeo vino con la misma cantidad de lineas que lo que ya estaba pero tienen alguna variacion de nombre.\n\n{diff_set1}\n\nSe sobreesribe con la nueva version.'
                enviar_correo(destinatarios, asunto, mensaje)
