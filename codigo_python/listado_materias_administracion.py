# Importo librerias a utilizar
from utilidad import *
from db import mail

# Realizo el scrapeo
URL = 'https://fcea.udelar.edu.uy/depto-adm-ensenanza/lic-adm-ciencias-adm.html'
response = requests.get(URL, timeout=120)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', {'class': 'table_curricular'})
tbodies = table.find_all('tbody')

# Obtengo la primera tabla
tabla_1 = tbodies[0]

# Obtén la segunda tabla
tabla_2 = tbodies[1]

# Procesamiento para incorporar la data en un DF
codigos = list()
semestres = list()

for tr in tabla_1.find_all('tr'):
    codigo = tr.find_all('td')[0].text.upper().strip()
    codigo = quitar_acentos(codigo)
    codigos.append(codigo)

    semestre = tr.find_all('td')[1].text.upper().strip()
    semestre = quitar_acentos(semestre)
    semestres.append(semestre)

for tr in tabla_2.find_all('tr'):
    codigo = tr.find_all('td')[0].text.upper().strip()
    codigo = quitar_acentos(codigo)
    codigos.append(codigo)

    semestre = tr.find_all('td')[1].text.upper().strip()
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
    df_filtrado.to_csv('./materias_administracion.csv', index=False)

# Alerta en caso de error de scrapeo    
else:
    DESTINATARIOS = [mail()]
    ASUNTO = 'ERROR - PROYECTO ALERTA-FCEA '
    MENSAJE = 'Error al hacer el scraping de las materias de: Licenciatura en Administración.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(DESTINATARIOS, ASUNTO, MENSAJE)
