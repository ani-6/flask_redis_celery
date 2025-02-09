FROM python:3.12.9-alpine3.21

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

WORKDIR /app/app

CMD ["python", "app.py"]
