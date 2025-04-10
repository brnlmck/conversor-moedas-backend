import os
import requests
from models import Moeda, Session
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Cria a tabela
Base.metadata.create_all(engine)

# Cria a sessão
Session = sessionmaker(bind=engine)

# Insere dados na tabela
def inserir_dados(nome, cod):
    session = Session()
    try:
        moeda = Moeda(nome=nome, cod=cod)

        session.add(moeda)
        session.commit()
        print(f"Dados inseridos com sucesso: {nome} ({cod})")
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
        raise e
    finally:
        session.close()

# Consulta a API e insere os dados no banco de dados
def consultar_e_inserir_moedas():
    try:
        # Consulta a API
        api_url = "https://api.exchangeratesapi.io/v1/symbols?access_key=" + os.getenv("API_KEY")
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Extrai as moedas
        symbols = data.get("symbols", {})
        if not symbols:
            return {"message": "Moedas não encontradas na response."}

        # Insere as moedas no banco de dados
        for code, name in symbols.items():
            inserir_dados(nome=name, cod=code)

    except requests.exceptions.RequestException as e:
        return {"message": f"Erro ao consultar dados via API: {e}"}
    
    return {"message": "Dados inseridos com sucesso!"}
    