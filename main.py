import os
from fastapi import FastAPI
import requests
from funcoes import consultar_e_inserir_moedas
from models import Session, Moeda
from fastapi import HTTPException
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/listar-moedas")
def listar_moedas():
    session = Session()
    try:
        # Consulta a tabela moedas
        moedas = session.query(Moeda).all()

        # Consulta a tabela ultimaatualizacao
        ultima_atualizacao = session.execute("SELECT datahora FROM ultimaatualizacao").fetchone()

        if not ultima_atualizacao or (datetime.now() - ultima_atualizacao[0] > timedelta(days=365)):
            # Se não houver registro ou se passou mais de um ano, atualiza as moedas
            consultar_e_inserir_moedas()
            # Atualiza a data de última atualização
            session.execute("UPDATE ultimaatualizacao SET datahora = :datahora", {"datahora": datetime.now()})
            session.commit()

        if not moedas:
            # Se a tabela estiver vazia, preenche com dados da API
            consultar_e_inserir_moedas()
            moedas = session.query(Moeda).all()

        # Retorna os dados da tabela
        return {"moedas": [{"nome": moeda.nome, "cod": moeda.cod} for moeda in moedas]}
    finally:
        session.close()

@app.get("/converter")
def converter(quantia_base: float, moeda_base: str, moedas_destino: str):
    try:
        moedas_destino = [moeda.strip() for moeda in moedas_destino.split(",")]  # Converte a string em uma lista de moedas

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
            resultados.append({"moedaPara": moeda_destino, "valorConvertido": quantia_convertida, "taxaCambio": taxa_para_destino, "codigoMoeda": moeda_destino})

            #todo: adicionar a data de atualização da taxa de câmbio
            #todo: calcular a taxa de câmbio em relação a moeda base
            #todo: fazer busca do nome da moeda base na tabela de moedas
            #todo: formatar o valor convertido para duas casas decimais

        # Retorna os resultados
        return {"data": resultados}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar a API: {e}")