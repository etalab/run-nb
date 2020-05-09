FROM surnet/alpine-python-wkhtmltopdf:3.7.3-0.12.5-small
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
# TODO: volume for output?
