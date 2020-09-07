FROM python:3.7-buster

# install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb
RUN apt update && \
    apt install -y -q ./wkhtmltox_0.12.5-1.stretch_amd64.deb && \
    apt install -y -q locales && \
    apt clean && \
    rm -rf /var/lib/apt/lists

RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

ENV TZ="Europe/Paris"

VOLUME /app/output
