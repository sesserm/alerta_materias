from utilidad import *

URL = 'https://fcea.udelar.edu.uy/depto-adm-ensenanza/tecnicatura-admin-ciencias-adm.html'
response = requests.get(URL)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'table_curricular'})

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

print(len(codigos), len(semestres))
# PARA USAR LA FUNCION ZIP, TIENEN QUE EXISTIR LA MISMA CANTIDAD DE CODIGOS Y SEMESTRES

#Obtengo variable de entorno
variables_entorno = obtener_var_entorno()

if len(codigos) == len(semestres):
    datos = zip(codigos, semestres)
    df = pd.DataFrame(datos, columns=["CODIGO", "MATERIA"])
    mask = df['MATERIA'].str.contains(PATRON_FILTRADO)
    df_filtrado = df[mask]
    df_filtrado.drop(df_filtrado[df_filtrado['CODIGO'] == ''].index, inplace=True)
    df_filtrado.drop(df_filtrado[df_filtrado['MATERIA'] == ''].index, inplace=True)

    df_filtrado.to_csv('./materias_tecnologo_admin.csv', index=False)
else:
    # MANDAR MAIL DE ERROR EN ESTA MATERIA
    destinatarios = [variables_entorno.get('MAIL')]
    asunto = 'ERROR - PROYECTO ALERTA-FCEA '
    mensaje = 'Error al hacer el scraping de las materias de: Tecnicatura en Administración.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(destinatarios, asunto, mensaje)
