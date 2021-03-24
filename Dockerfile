FROM python:3.7.4-slim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY datasets datasets
COPY utils utils

COPY style.css .
COPY web-application.py .

EXPOSE 80

ENTRYPOINT ["streamlit", "run", "web-application.py", "--server.port", "80"]