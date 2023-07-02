# Importo librerias a utilizar
from utilidad import *
from db import mail

# Realizo el scrapeo
URL = 'https://fcea.udelar.edu.uy/depto-adm-ensenanza/tecnicatura-admin-ciencias-adm.html'
response = requests.get(URL, timeout=120)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', {'class': 'table_curricular'})

# Procesamiento para incorporar la data en un DF
for data_materia in table.find_all('tbody'):
    rows = data_materia.find_all('tr')

codigos = []
semestres = []
for row in rows:
    # Verifica si la fila tiene al menos 3 columnas
    if len(row.find_all('td')) >= 3:
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
    df_filtrado.to_csv('./materias_tecnologo_admin.csv', index=False)

# Alerta en caso de error de scrapeo
else:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = 'Error al hacer el scraping de las materias de: Tecnicatura en Administración.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)