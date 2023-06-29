from utilidad import *

URL = 'https://fcea.udelar.edu.uy/ensenanza/las-carreras-de-fcea/154-contador-publico.html'
response = requests.get(URL)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'table_curricular'})

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

print(len(codigos), len(semestres))

# Obtengo variables de entorno a nivel global
variables_entorno = obtener_var_entorno()

# PARA USAR LA FUNCION ZIP, TIENEN QUE EXISTIR LA MISMA CANTIDAD DE CODIGOS Y SEMESTRES
if len(codigos) == len(semestres):
    datos = zip(codigos, semestres)
    df = pd.DataFrame(datos, columns=["CODIGO", "MATERIA"])
    mask = df['MATERIA'].str.contains(PATRON_FILTRADO)
    df_filtrado = df[mask]
    df_filtrado.drop(df_filtrado[df_filtrado['CODIGO'] == ''].index, inplace=True)
    df_filtrado.drop(df_filtrado[df_filtrado['MATERIA'] == ''].index, inplace=True)

    df_filtrado.to_csv('./materias_contador.csv', index=False)
else:
    destinatarios = [variables_entorno.get('MAIL')]
    asunto = 'ERROR - PROYECTO ALERTA-FCEA '
    mensaje = 'Error al hacer el scraping de las materias de: Contador Público.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(destinatarios, asunto, mensaje)