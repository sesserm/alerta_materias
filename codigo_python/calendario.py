from utilidad import *
import psycopg2
from psycopg2 import sql
import datetime

URL = 'https://fcea.udelar.edu.uy/horarios-y-calendarios/examenes-y-revisiones/calendario-de-pruebas/calendarios/6756-calendario-de-pruebas-del-primer-semestre-de-2023.html'


response = requests.get(URL)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'tm-table-primary'})

for data_materia in table.find_all('tbody'):
    rows = data_materia.find_all('tr')

codigos = list()
materias = list()
enlaces_info = list()
fechas = list()
contenido_enlace = list()

# Obtengo variables de entorno a nivel global
variables_entorno = obtener_var_entorno()
contador_errores = 0

for row in rows:
    tds = row.find_all('td')
    if len(tds) >= 2:
        codigo = tds[0].text.upper().strip()
        codigo = quitar_acentos(codigo)
        codigos.append(codigo)

        fecha = tds[2].text.upper().strip()
        fecha = quitar_acentos(fecha)
        #print(fecha)
        patron_fecha = r"(\d{2}/\d{2}/\d{2}(\d{2})?|\d{2}/\d{2}/\d{4})"
        fecha_encontrada = re.search(patron_fecha, fecha)
        #print(fecha_encontrada)
        if fecha_encontrada:
            fecha = fecha_encontrada.group(1)
            print(fecha)
            fechas.append(fecha)
        else:
            contador_errores +=1
            # Se envia un mail con la cantidad de errores posteriormente
            fechas.append('01/01/9999') # Materia sin fecha en grilla
            

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
        # AQUI IDENTIFICO CUALES TIENE ENLACE DISPONIBLE, DEPUES TENGO QUE ARREGLAR CUAL MATERIA EN PATICULAR TIENE EL ENLACE ASOCIADO.
if contador_errores > 2 :
    destinatarios = [variables_entorno.get('MAIL')]
    asunto = 'ERROR - PROYECTO ALERTA-FCEA '
    mensaje = f'Existen errores en el scrapeo de la fecha del calendario.\n\nCambió algún formato que originó un error en el scrapeo. Hubo {contador_errores} errores. Probablemente fue un cambio de fecha. Revisar bien en rama Mantenimiento'
    enviar_correo(destinatarios, asunto, mensaje)
print(len(codigos), len(materias), len(fechas), len(enlaces_info))
# La longitud tiene que ser la misma para usar la funcion zip. No lo son. En donde me faltan fechas???
enlaces_analizar = list()
for i in contenido_enlace:
    if '/' in i[0]:
        enlaces_analizar.append((i[0], quitar_acentos(i[1]), i[2]))
#print(enlaces_analizar)

if len(codigos) == len(materias) == len(fechas) == len(enlaces_info):
    datos = zip(codigos, materias, fechas, enlaces_info)
    df = pd.DataFrame(
        datos, columns=["CODIGO", "MATERIA", "FECHA", "NOTA_DISPONIBLE"])
    # SEPARO LAS MATERIAS QUE ESTEN JUNTAS
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
        # print(juntos[index][0])
        # print(juntos[index][2])
        if item[1].count('/') == 1:
            codigo_split = item[0].split('/')
            trimmed_codigo = list(map(str.strip, codigo_split))
            materia_split = item[1].split('/')
            trimmed_materia = list(map(str.strip, materia_split))
            fecha_agregar = []
            # Agrego la fecha 2 veces dado que siempre viene una sola vez en el calendario.
            fecha_agregar.append((juntos[index][2]))
            fecha_agregar.append((juntos[index][2]))

            # Tengo que agregar el enlace a la materia que corresponda. Por lo menos una va a ser SI.

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
    # LE ADJUDICO A TODO QUE NO POR DEFAULT Y LUEGO ACTUALIZO A SI LAS QUE CORRESPONDAN
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
        conn = psycopg2.connect(
            database=variables_entorno.get('PGDATABASE'),
            user=variables_entorno.get('PGUSER'),
            password=variables_entorno.get('PGPASSWORD'),
            host=variables_entorno.get('PGHOST'),
            port=variables_entorno.get('PGPORT')
        )
    except psycopg2.DatabaseError as error:
        print(f"Ha ocurrido un error al conectar a la base de datos: {error}")
        destinatarios = [variables_entorno.get('MAIL')]
        asunto = 'ERROR - PROYECTO ALERTA-FCEA '
        mensaje = f'No se pudo conectar a la base en el script de calendario.'
        enviar_correo(destinatarios, asunto, mensaje)

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
                print(row)
                cursor.execute(
                    SQL_INSERT, (row['CODIGO'], row['MATERIA'], row['FECHA'], row["NOTA_DISPONIBLE"]))

                # confirmar los cambios en la base de datos
            conn.commit()

            # cerrar la conexión y el cursor
            cursor.close()
            conn.close()
        except:
            destinatarios = [variables_entorno.get('MAIL')]
            asunto = 'ERROR - PROYECTO ALERTA-FCEA '
            mensaje = f'Error al hacer la carga de calendario. Error en el insert.\n\n{row}'
            enviar_correo(destinatarios, asunto, mensaje)

    # Tabla es lo que esta cargado, final_df es lo que viene del scrapeo
    else:
        try:
            print('Borrando registros...')
            SQL_DELETE = "DELETE FROM alerta_facultad.calendario"
            cursor.execute(SQL_DELETE)
            # confirmar los cambios en la base de datos
            conn.commit()
            print('Insertando registros...')
            SQL_INSERT = "INSERT INTO alerta_facultad.calendario (codigo, materia, fecha, nota_disponible) VALUES (%s, %s, %s, %s)"
            for index, row in final_df.iterrows():
                cursor.execute(
                    SQL_INSERT, (row['CODIGO'], row['MATERIA'], row['FECHA'], row["NOTA_DISPONIBLE"]))
            conn.commit()

            ## Hago los joins y todo el procesamiento
            join_query = sql.SQL("SELECT c.codigo, c.materia, c.fecha, c.nota_disponible, u.usuario, u.nota_disponible, u.medio, u.fecha_solicitud FROM alerta_facultad.calendario AS c INNER JOIN alerta_facultad.usuarios AS u ON c.codigo = u.codigo AND c.fecha = u.fecha_evaluacion")
              # Ejecuta la consulta SQL
            cursor.execute(join_query)

            # Recupera todos los resultados del cursor
            join_results = cursor.fetchall()
            notificaciones_enviadas = set()
            for row in join_results:
                print(row)
                if row[3] == 'SI' and row[5] == 'NO' and (row[0], row[1], row[2]) not in notificaciones_enviadas:
                    print('Nota disponible!')
                    codigo = row[0]
                    materia = row[1]
                    fecha_postgres = row[2].strftime("%Y-%m-%d")
                    fecha_mails = row[2].strftime("%d-%m-%Y")
                    usuario = row[4]
                    medio = row[6]
                    fecha_solicitud = row[7]
                    destinatarios = [usuario]
                    asunto = 'NOTA DISPONIBLE ALERTA-FCEA '
                    mensaje = f"""
¡Hola!
                    
Te informamos que ya se encuentra disponible la nota correspondiente a {row[1]} del {fecha_mails}.

Recuerda estar al pendiente de la grilla oficial en caso de que se realicen modificaciones posteriores a esta notificación.

¡Saludos!"""
                    enviar_correo(destinatarios, asunto, mensaje)
                    notificaciones_enviadas.add((row[0], row[1], row[2]))
                    #Insertar registro en tabla historica y borrar de usuarios
                    try:
                        insert_query = sql.SQL(
                            "INSERT INTO alerta_facultad.usuarios_historicos (medio, usuario, codigo, materia, nota_disponible, fecha_evaluacion, fecha_solicitud) values({},{},{},{},{},{},{})").format(
                            sql.Literal(medio), sql.Literal(usuario), sql.Literal(codigo), sql.Literal(materia), sql.Literal('SI'), sql.Literal(fecha_postgres), sql.Literal(fecha_solicitud))
                        # Confirmar los cambios en la base de datos
                        cursor.execute(insert_query)
                        conn.commit()
                        delete_query = sql.SQL("DELETE FROM alerta_facultad.usuarios WHERE usuario = {} AND codigo = {} and fecha_evaluacion = {}").format(
                            sql.Literal(usuario), sql.Literal(codigo), sql.Literal(fecha_postgres))
                        cursor.execute(delete_query)
                        conn.commit()
                    except:
                        destinatarios = [variables_entorno.get('MAIL')]
                        asunto = 'ERROR - PROYECTO ALERTA-FCEA '
                        mensaje = f'Error al mover los datos a la tabla historica.'
                        enviar_correo(destinatarios, asunto, mensaje)
                else:
                    pass
            # cerrar la conexión y el cursor
            cursor.close()
            conn.close()

        except:
            destinatarios = [variables_entorno.get('MAIL')]
            asunto = 'ERROR - PROYECTO ALERTA-FCEA '
            mensaje = f'Error al borrar y volver a cargar los datos del calendario.'
            enviar_correo(destinatarios, asunto, mensaje)
