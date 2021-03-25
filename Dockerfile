FROM python:3.7.4-slim

WORKDIR /app

ENV PYTHONPATH /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY datasets datasets
COPY methane_helper methane_helper
COPY methane_helper/data methane_helper/data
COPY style.css .


EXPOSE 80

ENTRYPOINT ["streamlit", "run", "methane_helper/web-application.py", "--server.port", "80"]