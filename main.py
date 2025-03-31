from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()  

#Chave e configuracao ExchangeRates
API_KEY = os.getenv('f713e6ca651621072fb4f4b5f7f43e6a')
BASE_URL = os.getenv('https://v6.exchangerate-api.com/v6')

"""class CurrencyConversionRequest(BaseModel):
    from_currency: str  # Ex: "USD"
    to_currency: str    # Ex: "BRL"
    amount: float       # Ex: 100.0"""

@app.get("/")
def home():
    return {"message": "Olá, mundo!"}