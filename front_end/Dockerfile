#FROM node:19-alpine3.16

#RUN mkdir -p /usr/src/

#WORKDIR /usr/src/

#COPY . .

#RUN npm install

#RUN /bin/sh -c "apk add --no-cache bash"

#CMD ["bash"]

FROM node:19-alpine3.16

RUN mkdir -p /usr/src/

WORKDIR /usr/src/

COPY . .

COPY ../codigo_python/requirements.txt .

COPY ../codigo_python/db.py .

RUN npm install

# Instalar las dependencias de Python
RUN apk add --no-cache python3 python3-dev \
    && pip3 install --upgrade pip \
    && pip3 install -r /usr/src/requirements.txt

RUN /bin/sh -c "apk add --no-cache bash"

CMD ["bash"]


