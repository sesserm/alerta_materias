# Importo librerias a utilizar
from utilidad import *
from db import open_connection, mail

# Genero la lista de materias en base a archivos interiores
filename_economia = "./materias_economia.csv"
filename_contador = "./materias_contador.csv"
filename_estadistica = "./materias_estadistica.csv"
filename_admin = "./materias_administracion.csv"
filename_tecnologo_univ = "./materias_tecnologo_gestion_univ.csv"
filename_tecnologo_admin = "./materias_tecnologo_admin.csv"

csv_archivos = [filename_economia, filename_contador,
                filename_estadistica, filename_admin, filename_tecnologo_univ, filename_tecnologo_admin]

# Obtener una lista de todos los archivos en el directorio actual y ejecutar los listados
archivos_cargar = os.listdir()
for archivo in archivos_cargar:
    if archivo.endswith(".py") and archivo.startswith("listado"):
        os.system(f"python {archivo}")
for archivo in csv_archivos:
    if not os.path.isfile(archivo):
        raise SystemExit



# Agrego toas las materias a un DF
dfs = []
for archivo in csv_archivos:
    df = pd.read_csv(archivo)
    dfs.append(df)
df_total = pd.concat(dfs, ignore_index=True)
unique_df = df_total.drop_duplicates(subset='CODIGO')
unique_df = unique_df.reset_index(drop=True)

# Remuevo los archivos
for archivo in csv_archivos:
    try:
        os.remove(archivo)
    except OSError as e:
        raise SystemExit

# Me conecto a la base
try:
    conn = open_connection()
except psycopg2.DatabaseError as error:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = f'No se pudo conectar a la base en el script de datos_para_cargar.py.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)


# Obtengo la informacion actual (en caso de que exista)
cursor = conn.cursor()
QUERY = "SELECT * FROM alerta_facultad.dim_materias"
cursor.execute(QUERY)
rows = cursor.fetchall()
headers = [desc[0].upper() for desc in cursor.description]
tabla = pd.DataFrame(rows, columns=headers)
tabla = tabla.reset_index(drop=True)

# Procesamiento de validacion y carga de las asignaturas
if tabla.empty:
    SQL_INSERT = "INSERT INTO alerta_facultad.dim_materias (codigo, materia) VALUES (%s, %s)"
    for index, row in unique_df.iterrows():
        cursor.execute(SQL_INSERT, (row['CODIGO'], row['MATERIA']))
    conn.commit()
    cursor.close()
    conn.close()
else:
    if len(unique_df) != len(tabla):
        # Evaluo si tienen la misma cantidad de filas (puede tener mas o menos)
        my_set_cargado = set([frozenset(x) for x in tabla.to_numpy()])
        my_set_comparar = set([frozenset(x) for x in unique_df.to_numpy()])
        diff_set1 = my_set_cargado.difference(my_set_comparar)
        diff_tuple1 = tuple(diff_set1)
        diff_set2 = my_set_comparar.difference(my_set_cargado)
        diff_tuple2 = tuple(diff_set2)
        items_faltantes = list()
        #Se asume que el codigo no sera nunca igual a la materia
        if len(diff_tuple1) != 0:
            for codigo,materia in diff_tuple1:
                items_faltantes.append([codigo,materia])

        if len(diff_tuple2) != 0:
            for codigo, materia in diff_tuple2:
                items_faltantes.append([codigo, materia])    
        DESTINATARIOS = [mail()]
        ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
        MENSAJE = f'Error al hacer la carga del listado de materias. Dataframes no tienen el mismo len\n\nSe tienen los siguientes items faltantes (es un set por lo que puede no estar ordenado el codigo y materia):\n\n{items_faltantes}\n\nRecorda que puede ser que falten scrapear items o sean materias que las sacaron\n\nPara determinar esto: Si la materia esta en DW, entonces la sacaron y hay que quitarla. Si la materia no esta en DW falta scrapear y se debe agregar. Agregarlo manual en algun listado.py'
        enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
    else:
        my_set_cargado = set([frozenset(x) for x in tabla.to_numpy()])
        my_set_comparar = set([frozenset(x) for x in unique_df.to_numpy()])
        diff_set1 = my_set_cargado.difference(my_set_comparar)
        if len(diff_set1) == 0:
            DESTINATARIOS = [mail()]
            ASUNTO = 'STATUS CORRECTO - PROYECTO ALERTA-FCEA '
            MENSAJE = f'Se mantienen las mismas materias de las grillas que desde la ultima vez.'
            enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
        else:
            try:
                SQL_DELETE = "DELETE FROM alerta_facultad.dim_materias"
                cursor.execute(SQL_DELETE)
                conn.commit()
                SQL_INSERT = "INSERT INTO alerta_facultad.dim_materias (codigo, materia) VALUES (%s, %s)"
                for index, row in unique_df.iterrows():
                    cursor.execute(SQL_INSERT, (row['CODIGO'], row['MATERIA']))
                conn.commit()
                cursor.close()
                conn.close()
            except:
                DESTINATARIOS = [mail()]
                ASUNTO = 'STATUS - PROYECTO ALERTA-FCEA'
                MENSAJE = f'El scrapeo vino con la misma cantidad de lineas que lo que ya estaba pero tienen alguna variacion de nombre.\n\n{diff_set1}\n\nSe sobreesribe con la nueva version (por alguna razon fallo).'
                enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
