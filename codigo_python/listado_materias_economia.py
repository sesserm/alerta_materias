# Importo librerias a utilizar
from utilidad import *
from db import mail

# Realizo el scrapeo
URL = 'https://fcea.udelar.edu.uy/ensenanza-dpto-economia/licenciatura-en-economia.html'
response = requests.get(URL, timeout=120)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', {'class': 'table_curricular'})

# Procesamiento para incorporar la data en un DF
for data_materia in table.find_all('tbody'):
    rows = data_materia.find_all('tr')

codigos = list()
semestres = list()

for row in rows:
    codigo = row.find_all('td')[0].text.upper().strip()
    codigo = quitar_acentos(codigo)
    codigos.append(codigo)

    semestre = row.find_all('td')[1].text.upper().strip()
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
    df_filtrado = df_filtrado.append(
        {'CODIGO': 'I51', 'MATERIA': 'INTRODUCCION A LA METODOLOGIA'}, ignore_index=True)
    df_filtrado = df_filtrado.append(
        {'CODIGO': 'MC128', 'MATERIA': 'COMPL.METODOS CUANTITATIVOS. II'}, ignore_index=True)
    df_filtrado = df_filtrado.append(
        {'CODIGO': 'S48 (15082 EDUPER)', 'MATERIA': 'PLANEAMIENTO ESTRATEGICO UNIVERSITARIO'}, ignore_index=True)
    df_filtrado.to_csv('./materias_economia.csv', index=False)

# Alerta en caso de error de scrapeo 
else:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = 'Error al hacer el scraping de las materias de: Licenciatura en Economía.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)