import pika
import json
import threading
import uvicorn
from fastapi import FastAPI

app = FastAPI()

def send_email(to: str, subject: str, body: str):
    print(f"Email sent to {to}: {subject}")

def callback(ch, method, properties, body):
    data = json.loads(body)
    event_type = method.routing_key
    if event_type == "DealInvoiced":
        send_email(data["client_email"], "Invoice Ready", f"Pay {data['amount']} USD")
    elif event_type == "DealPaid":
        send_email(data["client_email"], "Payment Confirmed", "Thank you!")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='crm_events', exchange_type='topic', durable=True)
    channel.queue_declare(queue='notification_queue', durable=True)
    channel.queue_bind(exchange='crm_events', queue='notification_queue', routing_key='DealInvoiced')
    channel.queue_bind(exchange='crm_events', queue='notification_queue', routing_key='DealPaid')
    channel.basic_consume(queue='notification_queue', on_message_callback=callback, auto_ack=False)
    print("Notification Service listening...")
    channel.start_consuming()

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    threading.Thread(target=start_rabbitmq, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8001)
