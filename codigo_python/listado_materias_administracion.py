from utilidad import *

URL = 'https://fcea.udelar.edu.uy/depto-adm-ensenanza/lic-adm-ciencias-adm.html'
response = requests.get(URL)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'table_curricular'})

tbodies = table.find_all('tbody')

# Obtén la primera tabla
tabla_1 = tbodies[0]

# Obtén la segunda tabla
tabla_2 = tbodies[1]

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

print(len(codigos), len(semestres))
# PARA USAR LA FUNCION ZIP, TIENEN QUE EXISTIR LA MISMA CANTIDAD DE CODIGOS Y SEMESTRES

# Obtengo variables de entorno a nivel global
variables_entorno = obtener_var_entorno()

if len(codigos) == len(semestres):
    datos = zip(codigos, semestres)
    df = pd.DataFrame(datos, columns=["CODIGO", "MATERIA"])
    mask = df['MATERIA'].str.contains(PATRON_FILTRADO)
    df_filtrado = df[mask]
    df_filtrado.drop(df_filtrado[df_filtrado['CODIGO'] == ''].index, inplace=True)
    df_filtrado.drop(df_filtrado[df_filtrado['MATERIA'] == ''].index, inplace=True)

    df_filtrado.to_csv('./materias_administracion.csv', index=False)

else:
    destinatarios = [variables_entorno.get('MAIL')]
    asunto = 'ERROR - PROYECTO ALERTA-FCEA '
    mensaje = 'Error al hacer el scraping de las materias de: Licenciatura en Administración.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(destinatarios, asunto, mensaje)