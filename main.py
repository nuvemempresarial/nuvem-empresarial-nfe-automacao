from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

IUGU_API_KEY = os.getenv("IUGU_API_KEY")
NF_API_URL = os.getenv("NF_API_URL")  # Endpoint da API de emissão de NF-e

class IuguWebhook(BaseModel):
    event: str
    data: dict

@app.post("/webhook/iugu")
async def iugu_webhook(payload: IuguWebhook):
    if payload.event == "invoice.status_changed":
        invoice = payload.data
        status = invoice.get("status")
        if status == "paid":
            customer_email = invoice.get("customer_email")
            amount = invoice.get("total_cents", 0) / 100.0
            external_id = invoice.get("id")

            response = requests.post(NF_API_URL, json={
                "cliente_email": customer_email,
                "valor": amount,
                "referencia_pagamento": external_id
            }, headers={
                "Authorization": f"Bearer {IUGU_API_KEY}"
            })

            return {"nf_status": response.status_code, "message": "NF-e enviada"}

    return {"message": "Evento ignorado"}
