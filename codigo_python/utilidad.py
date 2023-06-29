# Modulo con diversas funciones y constantes para reutilizar

from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import collections
collections.Callable = collections.abc.Callable
from db import mail, passmail

def quitar_acentos(texto):
    # Definir los caracteres acentuados y sus correspondientes caracteres sin acento
    acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
               'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    # Usar una expresión regular para reemplazar los caracteres acentuados por los sin acento
    patron_acentos = re.compile('|'.join(acentos.keys()), re.IGNORECASE)
    resultado = patron_acentos.sub(lambda x: acentos[x.group()], texto)
    return resultado

PATRON_FILTRADO = r'^(?!.*(SEMESTRE|OPCIONAL)).*$'

# Obtén la ruta absoluta del archivo actual


def obtener_var_entorno():
    current_file = os.path.abspath(__file__)
    # Obtén el directorio padre de la ruta del archivo
    parent_dir = os.path.dirname(os.path.dirname(current_file))
    # Concatena la ruta relativa al archivo .env
    env_path = os.path.join(parent_dir, '.env')
    # Carga las variables de entorno desde el archivo .env
    load_dotenv(dotenv_path=env_path)

    # Crea un diccionario para almacenar las variables de entorno
    variables = {}

    # Agrega las variables de entorno al diccionario
    for key, value in os.environ.items():
        variables[key] = value

    return variables

## CONFIGURACION DE MAIL PARA NOTIFICAR
def enviar_correo(destinatarios, asunto, mensaje):
    # Configuración del servidor SMTP de Gmail
    servidor_smtp = 'smtp.gmail.com'
    puerto_smtp = 587
    #Obtengo variables de entorno 
    #variables_entorno = obtener_var_entorno()
    remitente = mail()
    contraseña = passmail()

    # Crear el objeto de mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = ', '.join(destinatarios)
    msg['Subject'] = asunto

    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        # Iniciar la conexión SMTP
        server = smtplib.SMTP(servidor_smtp, puerto_smtp)
        server.starttls()

        # Iniciar sesión en la cuenta de correo
        server.login(remitente, contraseña)

        # Enviar el mensaje a cada destinatario
        for destinatario in destinatarios:
            server.sendmail(remitente, destinatario, msg.as_string())

        # Cerrar la conexión SMTP
        server.quit()

        print('El correo se ha enviado correctamente.')
    except Exception as e:
        print('Ha ocurrido un error al enviar el correo:', str(e))
