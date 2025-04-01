import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# URL de conexão com o banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

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