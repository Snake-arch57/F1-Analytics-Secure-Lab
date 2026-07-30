FROM python:3.14-slim

# Impede escrita de arquivos .pyc e força logs diretos no stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. HARDENING: Cria grupo e usuário sem privilégios de root
#    --home explícito evita que o Debian grave "/nonexistent" como home,
#    o que quebrava a escrita do machine-id do Streamlit em ~/.streamlit
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup \
       --home /home/appuser --shell /usr/sbin/nologin appuser \
    && mkdir -p /home/appuser/.streamlit \
    && chown -R appuser:appgroup /home/appuser

# Define o HOME do processo (usado pelo Streamlit para cache e config)
ENV HOME=/home/appuser
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Instala dependências essenciais do sistema operacional
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Prepara estrutura de diretórios para caches e logs com as permissões corretas
RUN mkdir -p /app/data/cache/fastf1 /app/logs/app \
    && chown -R appuser:appgroup /app

# Instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o container
COPY . .

# HARDENING: Garante a propriedade de todos os arquivos para o appuser
RUN chown -R appuser:appgroup /app

# 2. HARDENING: Define o usuário não-root para a execução do container
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
