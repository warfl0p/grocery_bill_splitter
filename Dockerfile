FROM python:3.12.6

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

CMD ["streamlit", "run", "./app/home.py", "--server.port", "8501"]
