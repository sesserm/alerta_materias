# Importo librerias a utilizar
from utilidad import *
import datetime
from db import open_connection, mail

# Realizo el scrapeo
URL = 'https://fcea.udelar.edu.uy/horarios-y-calendarios/examenes-y-revisiones/calendario-de-pruebas/calendarios/6756-calendario-de-pruebas-del-primer-semestre-de-2023.html'
response = requests.get(URL, timeout=120)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', {'class': 'tm-table-primary'})

# Procesamiento para incorporar la data en un DF
for data_materia in table.find_all('tbody'):
    rows = data_materia.find_all('tr')

codigos = list()
materias = list()
enlaces_info = list()
fechas = list()
contenido_enlace = list()
contador_errores = 0

for row in rows:
    tds = row.find_all('td')
    if len(tds) >= 2:
        codigo = tds[0].text.upper().strip()
        codigo = quitar_acentos(codigo)
        codigos.append(codigo)

        fecha = tds[2].text.upper().strip()
        fecha = quitar_acentos(fecha)
        patron_fecha = r"(\d{2}/\d{2}/\d{2}(\d{2})?|\d{2}/\d{2}/\d{4})"
        fecha_encontrada = re.search(patron_fecha, fecha)
        if fecha_encontrada:
            fecha = fecha_encontrada.group(1)
            fechas.append(fecha)
        else:
            contador_errores +=1
            fechas.append('01/01/9999') 

        materia = tds[1].text.upper().strip()
        materia = quitar_acentos(materia)
        materias.append(materia)
        enlace_tag = tds[1].find_all('a')
        if not enlace_tag:
            enlaces_info.append('NO')
        else:
            enlaces_info.append('SI')
            for contenido in enlace_tag:
                info = contenido.text.strip()
                contenido_enlace.append((codigo, info, fecha))

if contador_errores > 3:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = f'Existen errores en el scrapeo de la fecha del calendario.\n\nCambió algún formato que originó un error en el scrapeo. Hubo {contador_errores} errores. Probablemente fue un cambio de fecha. Revisar bien en rama Mantenimiento.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)

# Arreglo enlaces para los casos donde se tiene dos materias en una misma fila
enlaces_analizar = list()
for i in contenido_enlace:
    if '/' in i[0]:
        enlaces_analizar.append((i[0], quitar_acentos(i[1]), i[2]))

if len(codigos) == len(materias) == len(fechas) == len(enlaces_info):
    datos = zip(codigos, materias, fechas, enlaces_info)
    df = pd.DataFrame(
        datos, columns=["CODIGO", "MATERIA", "FECHA", "NOTA_DISPONIBLE"])
    # Asumo que hay como maximo 2 codigos cuando hay barra
    para_arreglar = df[df['CODIGO'].str.contains('/')]
    nuevo_df = df.loc[~df['CODIGO'].str.contains('/')]
    codigo_lista = para_arreglar['CODIGO'].tolist()
    materia_lista = para_arreglar['MATERIA'].tolist()
    fecha_lista = para_arreglar['FECHA'].tolist()
    nota_lista = para_arreglar['NOTA_DISPONIBLE'].tolist()
    juntos = list(zip(codigo_lista, materia_lista, fecha_lista, nota_lista))
    final = []
    lista_interes = list()
    for index, item in enumerate(juntos):
        if item[1].count('/') == 1:
            codigo_split = item[0].split('/')
            trimmed_codigo = list(map(str.strip, codigo_split))
            materia_split = item[1].split('/')
            trimmed_materia = list(map(str.strip, materia_split))
            fecha_agregar = []
            # Agrego la fecha 2 veces dado que siempre viene una sola vez en el calendario.
            fecha_agregar.append((juntos[index][2]))
            fecha_agregar.append((juntos[index][2]))
            final.append(
                list(zip(trimmed_codigo, trimmed_materia, fecha_agregar)))
        else:
            codigo_split = item[0].split('/')
            trimmed_codigo = list(map(str.strip, codigo_split))
            materia_split = item[1].split('\xa0')
            trimmed_materia = list(map(str.strip, materia_split))
            fecha_agregar = []
            fecha_agregar.append((juntos[index][2]))
            fecha_agregar.append((juntos[index][2]))
            final.append(
                list(zip(trimmed_codigo, trimmed_materia, fecha_agregar)))
    flat_list = [item for sublist in final for item in sublist]
    flat_list_df = pd.DataFrame(
        flat_list, columns=["CODIGO", "MATERIA", "FECHA"])
    flat_list_df['NOTA_DISPONIBLE'] = 'NO'
    # Adjudico que "no" a todo por default y luego actualizo a "si" a las que correspondan.
    for i in enlaces_analizar:
        condition = (flat_list_df['FECHA'] == i[2]) & (
            flat_list_df['MATERIA'].str.contains(i[1]))
        flat_list_df.loc[condition, 'NOTA_DISPONIBLE'] = 'SI'
    final_df = nuevo_df.append(flat_list_df, ignore_index=True)
    final_df = final_df[~final_df['MATERIA'].str.contains(
        'DIAGNOSTICA', case=False)]

    def convertir_fecha(fecha):
        fecha_objeto = datetime.datetime.strptime(
            fecha, "%d/%m/%y" if len(fecha) == 8 else "%d/%m/%Y"
        )
        fecha_formateada = fecha_objeto.strftime("%Y-%m-%d")
        return fecha_formateada

    final_df['FECHA'] = final_df['FECHA'].apply(convertir_fecha)

    # Me conecto a la base
    try:
        conn = open_connection()
    except psycopg2.DatabaseError as error:
        DESTINATARIOS = [mail()]
        ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
        MENSAJE = f'No se pudo conectar a la base en el script de calendario.'
        enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)

    # Comienza el procesamiento central de calendario
    cursor = conn.cursor()
    QUERY = "SELECT * FROM alerta_facultad.calendario"
    cursor.execute(QUERY)
    rows = cursor.fetchall()
    headers = [desc[0].upper() for desc in cursor.description]
    tabla = pd.DataFrame(rows, columns=headers)
    tabla = tabla.reset_index(drop=True)

    if tabla.empty:
        try:
            SQL_INSERT = "INSERT INTO alerta_facultad.calendario (codigo, materia, fecha, nota_disponible) VALUES (%s, %s, %s, %s)"
            for index, row in final_df.iterrows():
                cursor.execute(
                    SQL_INSERT, (row['CODIGO'], row['MATERIA'], row['FECHA'], row["NOTA_DISPONIBLE"]))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            DESTINATARIOS = [mail()]
            ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
            MENSAJE = f'Error al hacer la carga de calendario. Error en el insert.\n\n{row}'
            enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)

    # Ejecuto la comparacion con la informacion hasta el momento.
    else:
        try:
            SQL_DELETE = "DELETE FROM alerta_facultad.calendario"
            cursor.execute(SQL_DELETE)
            conn.commit()
            SQL_INSERT = "INSERT INTO alerta_facultad.calendario (codigo, materia, fecha, nota_disponible) VALUES (%s, %s, %s, %s)"
            for index, row in final_df.iterrows():
                cursor.execute(
                    SQL_INSERT, (row['CODIGO'], row['MATERIA'], row['FECHA'], row["NOTA_DISPONIBLE"]))
            conn.commit()

            # Hago los joins y todo el procesamiento
            join_query = sql.SQL("SELECT c.codigo, c.materia, c.fecha, c.nota_disponible, u.usuario, u.nota_disponible, u.medio, u.fecha_solicitud FROM alerta_facultad.calendario AS c INNER JOIN alerta_facultad.usuarios AS u ON c.codigo = u.codigo AND c.fecha = u.fecha_evaluacion")
            cursor.execute(join_query)
            join_results = cursor.fetchall()
            for row in join_results:
                if row[3] == 'SI' and row[5] == 'NO':
                    codigo = row[0]
                    materia = row[1]
                    fecha_postgres = row[2].strftime("%Y-%m-%d")
                    fecha_mails = row[2].strftime("%d-%m-%Y")
                    usuario = row[4]
                    medio = row[6]
                    fecha_solicitud = row[7]
                    DESTINATARIOS = [usuario]
                    ASUNTO = 'NOTA DISPONIBLE ALERTA-FCEA '
                    MENSAJE = f"""
¡Hola!
                    
Te informamos que ya se encuentra disponible la nota correspondiente a {row[1]} del {fecha_mails}.

Recuerda estar al pendiente de la grilla oficial en caso de que se realicen modificaciones posteriores a esta notificación.

¡Saludos!"""
                    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
                    # Insertar registro en tabla historica y borrar de usuarios
                    try:
                        insert_query = sql.SQL(
                            "INSERT INTO alerta_facultad.usuarios_historicos (medio, usuario, codigo, materia, nota_disponible, fecha_evaluacion, fecha_solicitud) values({},{},{},{},{},{},{})").format(
                            sql.Literal(medio), sql.Literal(usuario), sql.Literal(codigo), sql.Literal(materia), sql.Literal('SI'), sql.Literal(fecha_postgres), sql.Literal(fecha_solicitud))
                        cursor.execute(insert_query)
                        conn.commit()
                        delete_query = sql.SQL("DELETE FROM alerta_facultad.usuarios WHERE usuario = {} AND codigo = {} and fecha_evaluacion = {}").format(
                            sql.Literal(usuario), sql.Literal(codigo), sql.Literal(fecha_postgres))
                        cursor.execute(delete_query)
                        conn.commit()
                    except:
                        DESTINATARIOS = [mail()]
                        ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
                        MENSAJE = f'Error al mover los datos a la tabla historica.'
                        enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
                else:
                    pass
            cursor.close()
            conn.close()

        except:
            DESTINATARIOS = [mail()]
            ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
            MENSAJE = f'Error al borrar y volver a cargar los datos del calendario o al notificar al usuario.'
            enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
