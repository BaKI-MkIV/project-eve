FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=eve_backend.settings

EXPOSE 4000

CMD ["gunicorn", "eve_backend.wsgi:application", "--bind", "0.0.0.0:4000"]