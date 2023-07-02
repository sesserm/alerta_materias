# Importo librerias a utilizar
from utilidad import *
from db import mail

# Realizo el scrapeo
URL = 'https://fcea.udelar.edu.uy/depto-met-cuant-ensenanza/licenciatura-en-estadistica.html'
response = requests.get(URL, timeout=120)
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all('table', {'class': 'table_curricular'})

# Procesamiento para incorporar la data en un DF
codigos = list()
semestres = list()

for tabla in tables:
    filas = tabla.find_all('tr')
    for fila in filas:
        celdas = fila.find_all('td')
        if len(celdas) >= 2:
            codigo = celdas[0].text.strip().upper()
            codigo = quitar_acentos(codigo)
            codigos.append(codigo)
            semestre = celdas[1].text.strip().upper()
            semestre = quitar_acentos(semestre)
            semestres.append(semestre)

# Genero archivo para cargar
if len(codigos) == len(semestres):
    datos = zip(codigos, semestres)
    df = pd.DataFrame(datos, columns=["CODIGO", "MATERIA"])
    mask = df['MATERIA'].str.contains(PATRON_FILTRADO)
    df_filtrado = df[mask]
    df_filtrado.drop(df_filtrado[df_filtrado['CODIGO'] == ''].index, inplace=True)
    df_filtrado.drop(df_filtrado[df_filtrado['MATERIA'] == ''].index, inplace=True)

# Alerta en caso de error de scrapeo 
else:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = 'Error al hacer el scraping de las materias de: Licenciatura en Estadística.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)

# Genero el arreglo para aquellos casos donde se tienen dos asignaturas en un mismo codigo
columna_1 = list()
columna_2 = list()

for tabla in tables:
    filas = tabla.find_all('tr')
    for fila in filas:
        celdas = fila.find_all('td')
        if len(celdas) >= 2:
            parrafos_col1 = celdas[0].find_all('p')
            for parrafo in parrafos_col1:
                parrafo = parrafo.text.strip().upper()
                parrafo = quitar_acentos(parrafo)
                columna_1.append(parrafo)

            parrafos_col2 = celdas[1].find_all('p')
            for parrafo in parrafos_col2:
                parrafo = parrafo.text.strip().upper()
                parrafo = quitar_acentos(parrafo)
                columna_2.append(parrafo)

columna1_filtrada = [
    elem for elem in columna_1 if "SEMESTRE" not in elem and "CODIGO" not in elem]
columna2_filtrada = [
    elem for elem in columna_2 if "SEMESTRE" not in elem and "CODIGO" not in elem]

# Me quedo con los elementos faltantes:
elementos_no_encontrados = [
    e for e in columna2_filtrada if e not in df_filtrado['MATERIA'].values]
elementos_no_encontrados = [elem.replace(
    " ", "") for elem in elementos_no_encontrados]

elementos_no_encontrados = list(set(elementos_no_encontrados))

# Agrego los elementos no encontrados de forma manual
if len(codigos) == len(semestres):
    df_filtrado = df_filtrado.append(
        {'CODIGO': '1411', 'MATERIA': 'COMPUTACION  I (FING)'}, ignore_index=True)
    df_filtrado = df_filtrado.append(
        {'CODIGO': '1322', 'MATERIA': 'PROGRAMACION I (FING)'}, ignore_index=True)
    df_filtrado = df_filtrado.append(
        {'CODIGO': 'MA069', 'MATERIA': 'COMPUTACION (FCIEN-SE DICTA CA DOS AÑOS)'}, ignore_index=True)
    df_filtrado = df_filtrado.append(
        {'CODIGO': '1062', 'MATERIA': 'CALCULO DIFERENCIAL E INTEGRAL EN VARIAS VARIABLES (FING) (SUSTITUYE EL CURSO DE CALCULO II COD. 1022 - FING)'}, ignore_index=True)
    df_filtrado = df_filtrado.append(
        {'CODIGO': '1061', 'MATERIA': 'CALCULO DIF. E INT.EN UNA VARIABLE(SUSTITUYE EL CURSO DE CALC. I COD1020 FING)'}, ignore_index=True)
    df_filtrado.to_csv('./materias_estadistica.csv', index=False)

# Alerta en caso de error de scrapeo
else:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = 'Error al hacer el scraping de las materias de: Licenciatura en Estadística.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)