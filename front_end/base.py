import io
import psycopg2
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv
#from ..codigo_python.db import open_connection, mail

# Obtén la ruta absoluta del archivo actual
current_file = os.path.abspath(__file__)

# Obtén el directorio padre de la ruta del archivo
parent_dir = os.path.dirname(os.path.dirname(current_file))

# Concatena la ruta relativa al archivo .env
env_path = os.path.join(parent_dir, '.env')

# Carga las variables de entorno desde el archivo .env
load_dotenv(dotenv_path=env_path)

# Conectarse a la base de datos
# Luego utilizar la version produccion (v.ent en el servidor)
conn = psycopg2.connect(
    host= os.environ.get('PGHOST'),
    database= os.environ.get('PGDATABASE'),
    user= os.environ.get('PGUSER'),
    password= os.environ.get('PGPASSWORD'),
    port= os.environ.get('PGPORT')
)

#try:
#    conn = open_connection()
#except psycopg2.DatabaseError as error:
#        destinatarios = [mail()]
#        asunto = 'ERROR - PROYECTO ALERTA-FCEA '
#        mensaje = f'No se pudo conectar a la base en el script que genera el index.html.'
#        enviar_correo(destinatarios, asunto, mensaje)

# Crear un cursor
cur = conn.cursor()
cur2 = conn.cursor()

# Ejecutar una consulta
cur.execute(
    "SELECT codigo, materia FROM alerta_facultad.dim_materias order by materia")
cur2.execute("SELECT codigo, fecha FROM alerta_facultad.calendario")

# Obtener los resultados
rows = cur.fetchall()
rows2 = cur2.fetchall()
dates_dict = {}
for item in rows2:
    codigo = item[0]
    fecha_str = item[1].strftime("%Y-%m-%d")  # Convertir datetime.date a cadena
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    if codigo in dates_dict:
        dates_dict[codigo].append(fecha)
    else:
        dates_dict[codigo] = [fecha]
#print(dates_dict)

# Crear una cadena de texto en formato HTML
output = io.StringIO()
output.write("<!DOCTYPE html>\n")
output.write("<html>\n")
output.write("<head>\n")
output.write("<meta charset=\"UTF-8\">\n")
output.write("<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\n")
output.write(
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
output.write("<title>Genera tu alerta</title>\n")
output.write("<link rel=\"stylesheet\" href=\"front_end/styles.css\">\n")
output.write("</head>\n")
output.write("<body>\n")
output.write("<div class=\"container\">\n")
output.write("<div class=\"filtros-container\">\n")
output.write("<div class=\"filtro\">\n")
output.write("<label for=\"input1\">Codigo:</label>\n")
output.write(
    "<input type=\"text\" id=\"input1\" placeholder=\"Ingresa un código...\">\n")
output.write("</div>\n")
output.write("<div class=\"filtro\">\n")
output.write("<label for=\"input2\">Materia:</label>\n")
output.write(
    "<input type=\"text\" id=\"input2\" placeholder=\"Ingresa una materia...\">\n")
output.write(
    "<button class=\"continuar\" id=\"continuar-btn\">Continuar</button>\n")
output.write(
    "<button class=\"limpiar\"  id=\"limpiar-btn\">Limpiar Seleccion <span id = \"seleccionados\" > 0 seleccionados </span></button>\n")
output.write("</div>\n")
output.write("</div>\n")
output.write("<table>\n")
output.write("<thead>\n")
output.write("<tr>\n")
output.write("<th>Codigo</th>\n")
output.write("<th>Materia</th>\n")
output.write("<th>Alerta</th>\n")
output.write("<th>Fecha</th>\n")  # add a new column
output.write("</tr>\n")
output.write("</thead>\n")
output.write("<tbody>\n")
id_counter = 1  # start with id 1
for row in rows:
    codigo = row[0]
    fecha_list = dates_dict.get(codigo, "SIN DATO")
    if fecha_list != "SIN DATO":  # Verificar si hay fechas disponibles 
        fecha_list.sort(key=lambda fecha: datetime.strptime(
            fecha, "%d-%m-%Y"))  # Ordenar las fechas
        output.write(f"<tr data-id='{id_counter}'>\n")
        output.write(f"<td>{row[0]}</td>\n")
        output.write(f"<td>{row[1]}</td>\n")
        output.write("<td><input type='checkbox'></td>\n")
        output.write("<td>\n")
        output.write("<select>\n")
        for fecha in fecha_list:
            output.write(f"<option value='{fecha}'>{fecha}</option>\n")
        output.write("</select>\n")
        output.write("</td>\n")
        output.write("</tr>\n")
        id_counter += 1  # increment the id counter
output.write("</tbody>\n")
output.write("</table>\n")
output.write("</div>\n")
output.write("<script src=\"front_end/app.js\"></script>\n")
output.write("<script src=\"front_end/estructura_fecha.js\"></script>\n")
output.write("</body>\n")
output.write("</html>\n")

# Escribir la cadena de texto en un archivo HTML
with open("../index.html", "w", encoding="utf-8") as f:
    f.write(output.getvalue())

# Cerrar el cursor y la conexión a la base de datos
cur.close()
cur2.close()
conn.close()
