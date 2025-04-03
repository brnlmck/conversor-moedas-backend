import os
from fastapi import FastAPI
import requests
from funcoes import consultar_e_inserir_moedas
from models import Session, Moeda
from fastapi import HTTPException

app = FastAPI()

@app.get("/listar-moedas")
def listar_moedas():
    session = Session()
    try:
        # Consulta a tabela moedas
        moedas = session.query(Moeda).all()
        if not moedas:
            # Se a tabela estiver vazia, preenche com dados da API
            result = consultar_e_inserir_moedas()
            #return result
            moedas = session.query(Moeda).all()

        # Retorna os dados da tabela
        return {"moedas": [{"nome": moeda.nome, "cod": moeda.cod} for moeda in moedas]}
    finally:
        session.close()

@app.get("/converter")
def converter(base: dict):
    try:
        quantia_base = base.get("quantia_base")
        moeda_base = base.get("moeda_base")
        moedas_destino = base.get("moedas_destino")

        # Valida os dados de entrada
        if not quantia_base or not moeda_base or not moedas_destino:
            raise HTTPException(status_code=400, detail="Entrada inválida.")

        # Consulta a API
        api_url = ("https://api.exchangeratesapi.io/v1/latest?access_key=" + os.getenv("API_KEY"))
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Taxas de conversão
        rates = data.get("rates", {})
        if not rates:
            return {"message": "Moedas não encontradas na response."}

        # Checa se a moeda base está na resposta
        taxa_base_para_euro = rates.get(moeda_base)
        if taxa_base_para_euro is None:
            raise HTTPException(
                status_code=404,
                detail=f"Taxa de conversão não encontrada para a moeda base {moeda_base}"
            )

        # Converte de moeda base para euro
        quantia_em_euros = quantia_base / taxa_base_para_euro

        # Faz a conversão para as moedas de destino
        resultados = []
        for moeda_destino in moedas_destino:
            taxa_para_destino = rates.get(moeda_destino)
            if taxa_para_destino is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Taxa de conversão não encontrada para {moeda_destino}"
                )
            # Converte de euro para a moeda de destino
            quantia_convertida = quantia_em_euros * taxa_para_destino
            resultados.append({"moeda": moeda_destino, "quantia_convertida": quantia_convertida})

        # Retorna os resultados
        return {"moeda_base": moeda_base, "quantia_base": quantia_base, "resultados": resultados}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar a API: {e}")