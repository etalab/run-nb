FROM python:3.7-buster

# install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb
RUN apt update && \
    apt install -y -q ./wkhtmltox_0.12.5-1.stretch_amd64.deb && \
    apt clean && \
    rm -rf /var/lib/apt/lists

WORKDIR /app
COPY requirements/install.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
# TODO: volume for output?
