# Dockerfile

# 1. Usar uma imagem base oficial do Python
FROM python:3.9-slim

# 2. Definir o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copiar o arquivo de dependências
COPY requirements.txt .

# 4. Instalar as dependências
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copiar os arquivos do projeto para o diretório de trabalho no container
COPY . .

# 6. Expor a porta que o Uvicorn usará
EXPOSE 8000

# 7. Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]