from fastapi import FastAPI
from funcoes import consultar_e_inserir_moedas
from models import Session, Moeda

app = FastAPI()

@app.get("/listar-moedas/")
def listar_moedas():
    session = Session()
    try:
        # Consulta a tabela moedas
        moedas = session.query(Moeda).all()
        if not moedas:
            # Se a tabela estiver vazia, preenche com dados da API
            result = consultar_e_inserir_moedas()
            return result

        # Retorna os dados da tabela
        return {"moedas": [{"nome": moeda.nome, "cod": moeda.cod} for moeda in moedas]}
    finally:
        session.close()