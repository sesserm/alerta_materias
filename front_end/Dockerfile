#FROM node:19-alpine3.16

#RUN mkdir -p /usr/src/

#WORKDIR /usr/src/

#COPY . .

#RUN npm install

#RUN /bin/sh -c "apk add --no-cache bash"

#CMD ["bash"]

FROM node:19-alpine3.16

WORKDIR /usr/src/

# Copiar el código del front-end
COPY . .

# Instalar las dependencias de npm
RUN npm install

# Instalar las dependencias de Python
RUN apk add --no-cache python3 python3-dev \
    pip install --no-cache-dir -r requirements.txt

RUN /bin/sh -c "apk add --no-cache bash"

CMD ["bash"]




