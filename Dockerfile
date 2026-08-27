FROM python:3.12-slim

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia só requirements primeiro (cache)
COPY requirements.txt .

# Instala Python deps - sem cache para ficar leve
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código (sem .venv, output, etc - usa .dockerignore)
COPY . .

# Garante pastas
RUN mkdir -p output temp_audio assets

# Variáveis (Railway vai injetar)
ENV PYTHONUNBUFFERED=1
ENV TELEGRAM_TOKEN=""
ENV CANAL_ID=""

# Roda o bot
CMD ["python", "telegram_bot.py"]
