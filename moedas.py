import requests
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco de dados
DATABASE_URL = "mysql+mysqlconnector://USUARIO:SENHA@localhost/NOMEDOBANCODEDADOS" #Inserir o nome do banco de dados, usuário e senha

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Model
class Moeda(Base):
    __tablename__ = "moedas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)
    cod = Column(String(10), nullable=False)

# Cria a tabela
Base.metadata.create_all(engine)

# Cria a sessão
Session = sessionmaker(bind=engine)
session = Session()

# Insere dados na tabela
def inserir_dados(nome, cod):
    try:
        moeda = Moeda(nome=nome, cod=cod)

        session.add(moeda)
        session.commit()
        print(f"Dados inseridos com sucesso: {nome} ({cod})")
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
    finally:
        session.close()

# Função para consultar a API e inserir os dados no banco de dados
def consultar_e_inserir(api_url):
    try:
        # Consulta a API
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Extrai as moedas
        symbols = data.get("symbols", {})
        if not symbols:
            print("Moedas não encontradas na response.")
            return

        # Insere as moedas no banco de dados
        for code, name in symbols.items():
            inserir_dados(nome=name, cod=code)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar dados via API: {e}")

api_url = "https://api.exchangeratesapi.io/v1/symbols?access_key=f713e6ca651621072fb4f4b5f7f43e6a"
consultar_e_inserir(api_url)