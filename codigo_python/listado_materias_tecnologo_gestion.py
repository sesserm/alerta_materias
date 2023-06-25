from utilidad import * 

URL = 'https://fcea.udelar.edu.uy/ensenanza/las-carreras-de-fcea/243-tecnico-en-gestion-universitaria.html'
response = requests.get(URL)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'table_curricular'})

codigos = []
semestres = []

for data_materia in table.find_all('tbody'):
    rows = data_materia.find_all('tr')
    
    for row in rows:
        # Check if the row has at least two columns
        if len(row.find_all('td')) >= 2:
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

    df_filtrado.to_csv('./materias_tecnologo_gestion_univ.csv', index=False)
else:
    # MANDAR MAIL DE ERROR EN ESTA MATERIA
    destinatarios = [variables_entorno.get('MAIL')]
    asunto = 'ERROR - PROYECTO ALERTA-FCEA '
    mensaje = 'Error al hacer el scraping de las materias de: Tecnológo en Gestión Universitaria.\n\nCambió algún formato que originó un error en el scrapeo.'
    enviar_correo(destinatarios, asunto, mensaje)
