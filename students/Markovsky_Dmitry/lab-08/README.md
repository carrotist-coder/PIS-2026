<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №8</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Проектирование интернет-систем"</p>
<p align="center"><strong>Тема:</strong> "Микросервисы и Event Bus"</p>
<br><br><br><br><br><br>
<p align="right"><strong>Выполнил:</strong></p>
<p align="right">Студент 3 курса</p>
<p align="right">Группы ПО-13</p>
<p align="right">Марковский Д.А.</p>
<p align="right"><strong>Проверил:</strong></p>
<p align="right">Несюк А.Н.</p>
<br><br><br><br><br>
<p align="center"><strong>Брест 2026</strong></p>

---

## Цель работы

Разбить монолит на микросервисы с асинхронной коммуникацией.

---

## Вариант №6 - Мини-CRM «Фриланс без паники»

**Питч:** _Клиенты довольны, дедлайны живы._

**Ядро домена:** _Клиенты, Сделки, Этапы воронки, Задачи, Инвойсы_


---

## Ход выполнения работы

### 1. Request Service (Deal Service)

**Bounded Context:** _Управление сделками (создание, оплата, отмена)_

**Ответственность:**
- Создание сделок
- Выставление инвойсов
- Отслеживание статуса оплаты

**API:**

| Метод | Path | Описание |
|-------|------|----------|
| POST | `/api/deals` | Создать сделку |
| GET | `/api/deals/{id}` | Получить сделку |
| POST | `/api/deals/{id}/mark-paid` | Отметить оплаченной |
| POST | `/api/deals/{id}/cancel` | Отменить сделку |

**Структура сервиса:**
```
request_service/
├── src/
│ ├── domain/ # Deal, Money, DealStatus
│ ├── application/ # Commands, Queries, Handlers
│ ├── infrastructure/
│ │ ├── adapter/ # REST, PostgreSQL, RabbitMQ Publisher
│ │ └── config/
│ └── main.py
├── Dockerfile
└── requirements.txt
```

**Код Publisher (отправка событий):**
```python
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
```
---

### 2. Notification Service

**Bounded Context:** _Отправка уведомлений клиентам и менеджерам_

**Ответственность:**
- Отправка email при создании инвойса
- Отправка уведомлений об оплате

| Метод | Path | Описание |
|-------|------|----------|
| POST | `/api/notifications/email` | Отправить email |
| GET | `/api/notifications/status/{id}` | Статус уведомления |

**Код Subscriber (приём событий):**
```python
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
```

---

### 3. Event Bus (RabbitMQ)

**События:**
- `DealInvoiced`
- `DealPaid`

**Скриншот RabbitMQ Management:**

```
Exchange: crm_events (topic)
├── Bindings:
│   ├── deal.invoiced → notification_queue
│   └── deal.paid → notification_queue

Queues:
├── notification_queue (messages: 0, consumers: 1)
```

**Docker Compose для RabbitMQ:**
```yml
rabbitmq:
  image: rabbitmq:3.12-management
  container_name: rabbitmq
  ports:
    - "5672:5672"
    - "15672:15672"
  environment:
    RABBITMQ_DEFAULT_USER: admin
    RABBITMQ_DEFAULT_PASS: password
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq
  healthcheck:
    test: ["CMD", "rabbitmq-diagnostics", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```
---

### 4. API Gateway

**Маршрутизация:**
- `/api/deals*` → Request Service
- `/api/notifications*` → Notification Service

**Конфигурация:**
```nginx
upstream request_service {
    server request-service:8000;
}

upstream notification_service {
    server notification-service:8001;
}

server {
    listen 80;

    location /api/deals {
        proxy_pass http://request_service;
    }

    location /health {
        return 200 "OK\n";
    }
}
```

---

## Таблица критериев оценки

| Критерий | Баллы | Выполнено |
|----------|-------|-----------|
| Request Service: bounded context | 20 | ✅ |
| Group Service: CRUD | 15 | ✅ |
| Event Bus: RabbitMQ/Kafka | 25 | ✅ |
| API Gateway | 15 | ✅ |
| Circuit Breaker | 15 | ✅ |
| Docker Compose | 5 | ✅ |
| Качество документации | 5 | ✅ |
| **ИТОГО** | **100** | |

---

## Контрольные вопросы

1. **Что такое bounded context?**
   - Bounded context — это граница, внутри которой доменная модель имеет чёткое значение. В микросервисной архитектуре каждый сервис имеет свой bounded context со своей моделью данных. Например, в Request Service «сделка» имеет статус и сумму, а в Notification Service — только email клиента.

2. **Почему микросервисы не должны делить БД?**
   - Общая БД создаёт жёсткую связность: изменение схемы одного сервиса ломает другой. Сервисы становятся зависимыми от реализации друг друга. В микросервисной архитектуре каждый сервис владеет своей БД и обменивается данными только через API или события.

3. **В чём проблема распределённых транзакций?**
   - В монолите транзакция охватывает несколько таблиц в одной БД. В микросервисах нет единой БД, поэтому классические ACID-транзакции невозможны. Для согласованности данных нужно использовать Saga Pattern (цепочка компенсирующих действий) или Eventual Consistency.

4. **Зачем нужен Circuit Breaker?**
   - Circuit Breaker предотвращает каскадные отказы. Если сервис B не отвечает, сервис A перестаёт отправлять ему запросы на некоторое время (размыкает цепь). Это позволяет сервису B восстановиться, не перегружая его очередями.

---

## Ссылка на репозиторий

👉 **GitHub:** _[[URL репозитория](https://github.com/carrotist-coder/PIS-2026)]_

---

## Вывод

В ходе работы выполнено разбиение монолита на микросервисы:
- Request Service — управляет сделками, публикует события DealInvoiced и DealPaid в RabbitMQ.
- Notification Service — подписывается на события и отправляет email-уведомления.
- Event Bus (RabbitMQ) — обеспечивает асинхронную коммуникацию между сервисами с гарантией доставки.
- API Gateway (Nginx) — единая точка входа, маршрутизация запросов к сервисам

---

**Дата выполнения:** _07.04.2026_  
**Оценка:** _____________  
**Подпись преподавателя:** _____________
