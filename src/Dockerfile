FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
CMD python3 app.py