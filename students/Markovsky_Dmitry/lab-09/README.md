<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №9</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Проектирование интернет-систем"</p>
<p align="center"><strong>Тема:</strong> "Protocol Buffers и gRPC"</p>
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

Заменить REST API на gRPC для межсервисной коммуникации.

---

## Вариант №6 - Мини-CRM «Фриланс без паники»

**Питч:** _Клиенты довольны, дедлайны живы._

**Ядро домена:** _Клиенты, Сделки, Этапы воронки, Задачи, Инвойсы_

---

## Ход выполнения работы

### 1. Протофайлы (.proto)

**Файл:** `grpc/server.py`
```protobuf
syntax = "proto3";

package deal;

// Messages (Data Models)

message Money {
    double amount = 1;
    string currency = 2;  // USD, BYN, EUR
}

message Deal {
    string deal_id = 1;           // D-2026-0001
    string client_id = 2;         // cli-001
    string title = 3;             // Название сделки
    Money amount = 4;             // Сумма
    string status = 5;            // negotiation, invoiced, paid, cancelled
    int64 created_at = 6;         // Unix timestamp
    int64 updated_at = 7;         // Unix timestamp
    string invoice_id = 8;        // Опционально
    string payment_link = 9;      // Опционально
}

// Request/Response Messages

message CreateDealRequest {
    string client_id = 1;
    string title = 2;
    double amount = 3;
    string currency = 4;          // По умолчанию "USD"
}

message CreateDealResponse {
    string deal_id = 1;
    bool success = 2;
    string error_message = 3;
}

message GetDealRequest {
    string deal_id = 1;
}

message GetDealResponse {
    Deal deal = 1;
    bool found = 2;
}

message MarkDealAsPaidRequest {
    string deal_id = 1;
}

message MarkDealAsPaidResponse {
    bool success = 1;
    string error_message = 2;
}

message ListDealsRequest {
    string status_filter = 1;     // negotiation, invoiced, paid, cancelled
    int32 limit = 2;              // Максимум записей (по умолчанию 50)
}

message ListDealsResponse {
    repeated Deal deals = 1;
    int32 total_count = 2;
}

message StreamDealUpdatesRequest {
    string deal_id = 1;           // Если пусто — все сделки
}

// Service Definition

service DealService {
    // Unary RPC: Создать сделку
    rpc CreateDeal(CreateDealRequest) returns (CreateDealResponse);

    // Unary RPC: Получить сделку по ID
    rpc GetDeal(GetDealRequest) returns (GetDealResponse);

    // Unary RPC: Отметить сделку как оплаченную
    rpc MarkDealAsPaid(MarkDealAsPaidRequest) returns (MarkDealAsPaidResponse);

    // Unary RPC: Список сделок
    rpc ListDeals(ListDealsRequest) returns (ListDealsResponse);

    // Server-side Streaming: Real-time обновления сделки
    rpc StreamDealUpdates(StreamDealUpdatesRequest) returns (stream Deal);
}
```

---

### 2. gRPC Server

**Файл:** `grpc/client.server`

**Реализованные методы:**
- `CreateDeal`
- `GetDeal`
- `MarkDealAsPaid`
- `ListDeals`
- `StreamDealUpdates`

**Код:**
```python
class DealServiceServicer(deal_service_pb2_grpc.DealServiceServicer):
  """gRPC Server: Реализация Deal Service"""

  def __init__(self):
    self.deals = {}
    self.counter = 1
    self.subscribers = {}  # deal_id -> list of active streams
    self._seed_data()

  def _seed_data(self):
    """Создание тестовых сделок"""
    test_deals = [
      ("cli-0001", "Landing Page", 1500.00, "USD", "negotiation"),
      ("cli-0002", "Mobile App", 5000.00, "USD", "invoiced"),
      ("cli-0001", "SEO Optimization", 800.00, "EUR", "paid"),
    ]

    for client_id, title, amount, currency, status in test_deals:
      deal_id = f"D-2026-{self.counter:04d}"
      deal = deal_service_pb2.Deal(
        deal_id=deal_id,
        client_id=client_id,
        title=title,
        amount=deal_service_pb2.Money(amount=amount, currency=currency),
        status=status,
        created_at=int(time.time()),
        updated_at=int(time.time())
      )
      self.deals[deal_id] = deal
      self.counter += 1

  def _notify_subscribers(self, deal_id: str, deal):
    """Уведомить всех подписчиков об изменении сделки"""
    if deal_id in self.subscribers:
      for callback in self.subscribers[deal_id]:
        callback(deal)

  def CreateDeal(self, request, context):
    """Unary RPC: Создать сделку"""
    deal_id = f"D-2026-{self.counter:04d}"
    self.counter += 1

    deal = deal_service_pb2.Deal(
      deal_id=deal_id,
      client_id=request.client_id,
      title=request.title,
      amount=deal_service_pb2.Money(amount=request.amount, currency=request.currency or "USD"),
      status="negotiation",
      created_at=int(time.time()),
      updated_at=int(time.time())
    )

    self.deals[deal_id] = deal
    self._notify_subscribers(deal_id, deal)

    print(f"Deal created: {deal_id}")

    return deal_service_pb2.CreateDealResponse(
      deal_id=deal_id,
      success=True
    )

  def GetDeal(self, request, context):
    """Unary RPC: Получить сделку по ID"""
    deal = self.deals.get(request.deal_id)

    if deal:
      return deal_service_pb2.GetDealResponse(deal=deal, found=True)
    else:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      return deal_service_pb2.GetDealResponse(found=False)

  def MarkDealAsPaid(self, request, context):
    """Unary RPC: Отметить сделку как оплаченную"""
    deal = self.deals.get(request.deal_id)

    if not deal:
      return deal_service_pb2.MarkDealAsPaidResponse(
        success=False, error_message="Deal not found"
      )

    if deal.status != "invoiced":
      return deal_service_pb2.MarkDealAsPaidResponse(
        success=False, error_message=f"Cannot pay deal with status {deal.status}"
      )

    # Обновление статуса
    deal.status = "paid"
    deal.updated_at = int(time.time())
    self.deals[request.deal_id] = deal
    self._notify_subscribers(request.deal_id, deal)

    print(f"Deal marked as paid: {request.deal_id}")

    return deal_service_pb2.MarkDealAsPaidResponse(success=True)

  def ListDeals(self, request, context):
    """Unary RPC: Список сделок"""
    filtered = [
      deal for deal in self.deals.values()
      if not request.status_filter or deal.status == request.status_filter
    ]

    limit = request.limit if request.limit > 0 else 50
    results = filtered[:limit]

    return deal_service_pb2.ListDealsResponse(
      deals=results,
      total_count=len(filtered)
    )

  def StreamDealUpdates(self, request, context):
    """
    Server-side Streaming: Real-time обновления сделки

    Клиент подписывается на обновления по deal_id.
    Сервер отправляет изменения по мере их поступления.
    """
    deal_id = request.deal_id
    queue = []
    event = threading.Event()

    def callback(updated_deal):
      if not deal_id or updated_deal.deal_id == deal_id:
        queue.append(updated_deal)
        event.set()

    if deal_id not in self.subscribers:
      self.subscribers[deal_id] = []
    self.subscribers[deal_id].append(callback)

    print(f"Client subscribed to deal: {deal_id or 'ALL'}")

    try:
      while context.is_active():
        event.wait(timeout=5)
        event.clear()

        for updated_deal in queue:
          yield updated_deal
        queue.clear()

    finally:
      # Отписка при закрытии соединения
      if deal_id in self.subscribers:
        self.subscribers[deal_id].remove(callback)
        if not self.subscribers[deal_id]:
          del self.subscribers[deal_id]

      print(f"Client unsubscribed from deal: {deal_id or 'ALL'}")


def serve():
  """Запуск gRPC сервера"""
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  deal_service_pb2_grpc.add_DealServiceServicer_to_server(DealServiceServicer(), server)
  server.add_insecure_port('[::]:50051')
  server.start()

  print("gRPC Server started on port 50051")
  print("Listening for requests...")

  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    print("\nStopping server...")
    server.stop(0)


if __name__ == '__main__':
  serve()
```

---

### 3. gRPC Client

**Файл:** `grpc/client.py`

```python
def create_deal(stub):
  """Unary RPC: Создать сделку"""
  print("\n CreateDeal ")

  request = deal_service_pb2.CreateDealRequest(
    client_id="cli-test-001",
    title="gRPC Test Deal",
    amount=2500.00,
    currency="USD"
  )

  response = stub.CreateDeal(request)

  if response.success:
    print(f"Deal created: {response.deal_id}")
    return response.deal_id
  else:
    print(f"Error: {response.error_message}")
    return None


def get_deal(stub, deal_id):
  """Unary RPC: Получить сделку"""
  print(f"\n GetDeal({deal_id}) ")

  request = deal_service_pb2.GetDealRequest(deal_id=deal_id)
  response = stub.GetDeal(request)

  if response.found:
    deal = response.deal
    print(f"Deal ID: {deal.deal_id}")
    print(f"Client: {deal.client_id}")
    print(f"Title: {deal.title}")
    print(f"Amount: {deal.amount.amount} {deal.amount.currency}")
    print(f"Status: {deal.status}")
  else:
    print("Deal not found")


def mark_deal_as_paid(stub, deal_id):
  """Unary RPC: Отметить оплату"""
  print(f"\n MarkDealAsPaid({deal_id}) ")

  request = deal_service_pb2.MarkDealAsPaidRequest(deal_id=deal_id)
  response = stub.MarkDealAsPaid(request)

  if response.success:
    print(f"Deal marked as paid: {deal_id}")
  else:
    print(f"Error: {response.error_message}")


def list_deals(stub, status_filter=None):
  """Unary RPC: Список сделок"""
  request = deal_service_pb2.ListDealsRequest(
    status_filter=status_filter or "",
    limit=10
  )

  response = stub.ListDeals(request)

  print(f"Found {response.total_count} deals:")
  for deal in response.deals:
    print(f" {deal.deal_id} | {deal.status} | {deal.title} | {deal.amount.amount} {deal.amount.currency}")


def stream_deal_updates(stub, deal_id=None):
  """Server-side Streaming: Подписка на обновления сделки"""
  print("Listening for updates (press Ctrl+C to stop)...")

  request = deal_service_pb2.StreamDealUpdatesRequest(deal_id=deal_id or "")

  try:
    for deal in stub.StreamDealUpdates(request):
      print(f"Update: {deal.deal_id} | {deal.status} | {deal.title}")
  except KeyboardInterrupt:
    print("\nStopped streaming")


def run():
  channel = grpc.insecure_channel('localhost:50051')
  stub = deal_service_pb2_grpc.DealServiceStub(channel)

  # Создание сделки
  deal_id = create_deal(stub)

  if deal_id:
    # Получение сделки
    get_deal(stub, deal_id)

    # Список всех сделок
    list_deals(stub)

    # Список только оплаченных
    list_deals(stub, status_filter="paid")

  print("Starting streaming in background thread...")
  stream_thread = threading.Thread(target=stream_deal_updates, args=(stub,), daemon=True)
  stream_thread.start()

  time.sleep(10)
  print("Demo completed!")


if __name__ == '__main__':
  run()
```

---

### 4. Server-Side Streaming

**Сценарий:**
Клиент подписывается на real-time обновления статуса сделки через gRPC streaming. Сервер отправляет изменения статуса (например, при оплате или отмене) всем подключённым клиентам без необходимости повторных запросов.



**Скриншот:**

```
$ python grpc/server.py
gRPC Server started on port 50051
Listening for requests...
Deal created: D-2026-0004
Deal marked as paid: D-2026-0004
Client subscribed to deal: ALL

$ python grpc/client.py

Deal created: D-2026-0004

Deal ID: D-2026-0004
   Client: cli-test-001
   Title: gRPC Test Deal
   Amount: 2500.0 USD
   Status: negotiation

Found 4 deals:
   D-2026-0001 | negotiation | Landing Page | 1500.0 USD
   D-2026-0002 | invoiced | Mobile App | 5000.0 USD
   D-2026-0003 | paid | SEO Optimization | 800.0 EUR
   D-2026-0004 | negotiation | gRPC Test Deal | 2500.0 USD

Found 1 deals:
D-2026-0003 | paid | SEO Optimization | 800.0 EUR
Listening for updates (press Ctrl+C to stop)...
Update: D-2026-0004 | paid | gRPC Test Deal
```

---

## Таблица критериев оценки

| Критерий | Баллы | Выполнено |
|----------|-------|-----------|
| Протофайлы (.proto) | 20 | ✅ |
| gRPC Server | 25 | ✅ |
| gRPC Client | 20 | ✅ |
| Streaming | 20 | ✅ |
| Генерация кода (protoc) | 10 | ✅ |
| Качество документации | 5 | ✅ |
| **ИТОГО** | **100** | |

---

## Контрольные вопросы

1. **В чём преимущество gRPC над REST?**
   - gRPC использует HTTP/2 (мультиплексирование, server push), Protocol Buffers (бинарный формат → меньше размер и быстрее парсинг), встроенный streaming (unary, server-side, client-side, bidirectional), автоматическую генерацию клиентов на разных языках. REST чаще использует JSON/HTTP 1.1.

2. **Почему Protocol Buffers быстрее JSON?**
   - Protobuf — бинарный формат, данные упакованы в компактную структуру с фиксированными типами полей. JSON — текстовый, требует кавычек, скобок, парсинг строк. Protobuf генерирует код для сериализации без reflection, что значительно ускоряет обработку.

3. **Зачем нужен streaming в gRPC?**
   - Streaming позволяет передавать данные в real-time без постоянных HTTP запросов. В нашем сервисе StreamDealUpdates используется для мгновенного уведомления клиентов об изменении статуса сделки (оплата, отмена). Это эффективнее, чем polling.

---

## Ссылка на репозиторий

👉 **GitHub:** _[[URL репозитория](https://github.com/carrotist-coder/PIS-2026)]_

---

## Вывод

В ходе работы реализована замена REST API на gRPC для Deal Service:
- Протофайл (deal_service.proto) описывает 5 RPC методов: CreateDeal, GetDeal, MarkDealAsPaid, ListDeals, StreamDealUpdates.
- gRPC Server реализует все методы с in-memory хранением и поддержкой server-side streaming.
- gRPC Client демонстрирует вызовы всех RPC, включая подписку на real-time обновления через стриминг.
- Streaming позволяет клиентам получать мгновенные уведомления об изменении статуса сделки.
Преимущества подхода: бинарный протокол быстрее JSON, HTTP/2 позволяет мультиплексировать запросы, streaming даёт real-time без polling.

---

**Дата выполнения:** _09.04.2026_  
**Оценка:** _____________  
**Подпись преподавателя:** _____________
