#FROM node:19-alpine3.16

#RUN mkdir -p /usr/src/

#WORKDIR /usr/src/

#COPY . .

#RUN npm install

#RUN /bin/sh -c "apk add --no-cache bash"

#CMD ["bash"]

# Etapa 1: Construir la parte de Node.js
FROM node:19-alpine3.16 AS node_stage

RUN mkdir -p /usr/src/

WORKDIR /usr/src/

# Copiar los archivos relacionados con Node.js
COPY . .
RUN npm install

# Construir la aplicación de Node.js
RUN npm run build

# Etapa 2: Construir la parte de Python
FROM python:3.8.7-slim-buster AS python_stage

RUN apt-get update && apt install -y iputils-ping

RUN mkdir -p /usr/src/

WORKDIR /usr/src/

# Copiar los archivos relacionados con Python
COPY ../codigo_python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de Python
COPY ../codigo_python/db.py .

# Etapa final: Combinar las dos etapas anteriores
FROM node:19-alpine3.16

WORKDIR /usr/src/

# Copiar los archivos de la etapa de Node.js
COPY --from=node_stage /usr/src/dist/ ./dist/

# Copiar los archivos de la etapa de Python
COPY --from=python_stage /usr/src/ .

# Instalar bash
RUN apk add --no-cache bash

CMD ["bash"]