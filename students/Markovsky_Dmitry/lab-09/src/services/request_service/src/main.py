from fastapi import FastAPI
import pika
import json

app = FastAPI()

# RabbitMQ Publisher
def publish_event(event_type: str, payload: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='crm_events', exchange_type='topic', durable=True)
    channel.basic_publish(exchange='crm_events', routing_key=event_type, body=json.dumps(payload))
    connection.close()

@app.post("/api/deals")
def create_deal(client_id: str, title: str, amount: float):
    deal_id = f"D-2026-{hash(client_id+title)%10000:04d}"
    # Публикация события
    publish_event("DealInvoiced", {"deal_id": deal_id, "client_email": f"{client_id}@example.com", "amount": amount})
    return {"deal_id": deal_id}

@app.post("/api/deals/{deal_id}/mark-paid")
def mark_paid(deal_id: str):
    publish_event("DealPaid", {"deal_id": deal_id, "client_email": "client@example.com"})
    return {"message": f"Deal {deal_id} marked as paid"}

@app.get("/api/deals/{deal_id}")
def get_deal(deal_id: str):
    return {"id": deal_id, "status": "negotiation"}

@app.get("/health")
def health():
    return {"status": "ok"}
