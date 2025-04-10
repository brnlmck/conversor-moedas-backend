import os
from fastapi import FastAPI
import requests
from funcoes import consultar_e_inserir_moedas
from models import Session, Moeda
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/listar-moedas")
def listar_moedas():
    session = Session()
    try:
        # Consulta a tabela moedas
        moedas = session.query(Moeda).all()
        if not moedas:
            # Se a tabela estiver vazia, preenche com dados da API
            consultar_e_inserir_moedas()
            moedas = session.query(Moeda).all()

        # Retorna os dados da tabela
        return {"moedas": [{"nome": moeda.nome, "cod": moeda.cod} for moeda in moedas]}
    finally:
        session.close()

def filtrar_moedas_por_codigo(codigo_moedas):
    session = Session()
    try:
        moedas = session.query(Moeda).filter(Moeda.cod.in_(codigo_moedas)).all()
        return {moeda.cod: moeda.nome for moeda in moedas}
    finally:
        session.close()

@app.get("/converter")
def converter(quantia_base: float, moeda_base: str, moedas_destino: str):
    try:
        moedas_destino = [moeda.strip() for moeda in moedas_destino.split(",")]  # Converte a string em uma lista de moedas

        # Valida os dados de entrada
        if not quantia_base or not moeda_base or not moedas_destino:
            raise HTTPException(status_code=400, detail="Entrada inválida.")

        moedas = filtrar_moedas_por_codigo(moedas_destino)
        # Consulta a API
        api_url = ("https://api.exchangeratesapi.io/v1/latest?access_key=" + os.getenv("API_KEY"))
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Taxas de conversão
        rates = data.get("rates", {})
        if not rates:
            return {"message": "Moedas não encontradas na response."}

        # Data e hora
        datahora = data.get("timestamp")
        if not datahora:
            raise HTTPException(status_code=500, detail="Data e hora não encontradas na response.")

        # Checa se a moeda base está na resposta
        taxa_base_para_euro = rates.get(moeda_base)
        if taxa_base_para_euro is None:
            raise HTTPException(
                status_code=400,
                detail=f"Taxa de conversão não encontrada para a moeda base {moeda_base}"
            )

        # Faz a conversão para as moedas de destino
        resultados = []
        for moeda_destino in moedas_destino:
            taxa_para_destino = rates.get(moeda_destino)
            if taxa_para_destino is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Taxa de conversão não encontrada para {moeda_destino}"
                )
            taxa_relativa = taxa_para_destino / taxa_base_para_euro
            # Converte de euro para a moeda de destino
            quantia_convertida = quantia_base * taxa_relativa
            resultados.append({
                "moedaPara": moedas.get(moeda_destino, ""),
                "valorConvertido": round(quantia_convertida, 2),
                "taxaCambio": taxa_relativa,
                "codigoMoeda": moeda_destino
            })

            #todo: fazer busca do nome da moeda base na tabela de moedas

        # Retorna os resultados
        return {"timestamp": datetime.fromtimestamp(datahora).strftime('%d-%m-%Y %H:%M:%S'), "data": resultados, "moedas": moedas}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar a API: {e}")