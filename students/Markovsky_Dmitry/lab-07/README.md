<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №7</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Проектирование интернет-систем"</p>
<p align="center"><strong>Тема:</strong> "CQRS и Read Models"</p>
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

Реализовать CQRS с разделением Write Model и Read Model.

---

## Вариант №6 - Мини-CRM «Фриланс без паники»

**Питч:** _Клиенты довольны, дедлайны живы._

**Ядро домена:** _Клиенты, Сделки, Этапы воронки, Задачи, Инвойсы_

---

## Ход выполнения работы

### 1. Write Model

**Агрегат:** `Deal` (из Lab #3)

**Структура:**
- Нормализованная таблица `deals`
- Инварианты: сумма > 0, нельзя оплатить без инвойса, нельзя отменить оплаченную

**Схема Write Model (нормализованная):**

```sql
CREATE TABLE deals (
    id VARCHAR(50) PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'negotiation',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    invoice_id VARCHAR(50),
    payment_link VARCHAR(500)
);
```

**Код доменной модели (из Lab #3)**
```python
# src/domain/models/deal.py
class Deal:
    def __init__(self, deal_id, client_id, title, amount, status=None):
        self._id = deal_id
        self._client_id = client_id
        self._title = title
        self._amount = amount
        self._status = status or DealStatus.NEGOTIATION
        self._events = []
    
    def mark_as_invoiced(self, invoice_id):
        if not self._status.can_transition_to(DealStatus.INVOICED):
            raise ValueError(f"Cannot invoice deal in status {self._status}")
        self._status = DealStatus.INVOICED
        self._register_event(DealInvoiced(self._id, invoice_id, self._amount))
    
    def mark_as_paid(self):
        if not self._status.can_transition_to(DealStatus.PAID):
            raise ValueError(f"Cannot mark as paid: deal in status {self._status}")
        self._status = DealStatus.PAID
        self._register_event(DealPaid(self._id))
```

---

### 2. Read Model

**Проекция:** _DealView_ - денормализованная модель для быстрого чтения.

**Схема Read Model (нормализованная):**

```sql
CREATE TABLE deal_views (
    deal_id VARCHAR(50) PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL,
    client_name VARCHAR(200),
    title VARCHAR(200) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    status_display VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    invoice_id VARCHAR(50),
    payment_link VARCHAR(500),
    is_paid BOOLEAN DEFAULT FALSE,
    days_since_created INTEGER
);
```

---

### 3. Event-Driven Sync

**События:**
- `DealCreated` → INSERT в deal_views
- `DealInvoiced` → UPDATE invoice_id, payment_link
- `DealPaid` → UPDATE status, is_paid=True
- `DealCancelled` → UPDATE status

**Код:**
```python
class DealProjection:
  """
  Projection Handler: События → DealView

  Синхронизирует Write Model и Read Model через доменные события.
  """

  STATUS_DISPLAY = {
    "negotiation": "На согласовании",
    "approval": "Требуется подтверждение",
    "invoiced": "Инвойс выставлен",
    "paid": "Оплачено",
    "cancelled": "Отменено"
  }

  def __init__(self, session: Session):
    self.session = session

  def on_deal_created(self, event: DealCreated):
    """Обработка DealCreated: INSERT в deal_views"""
    view = DealViewORM(
      deal_id=event.deal_id,
      client_id=str(event.client_id),
      client_name=None,
      title=str(event.title),
      amount=float(event.amount.amount),
      currency=event.amount.currency,
      status="negotiation",
      status_display=self.STATUS_DISPLAY["negotiation"],
      created_at=event.occurred_at,
      updated_at=event.occurred_at,
      invoice_id=None,
      payment_link=None,
      is_paid=False,
      days_since_created=0
    )
    self.session.add(view)
    self.session.commit()

  def on_deal_invoiced(self, event: DealInvoiced):
    """Обработка DealInvoiced: UPDATE invoice_id, payment_link"""
    view = self.session.query(DealViewORM).filter_by(
      deal_id=event.deal_id
    ).first()

    if view:
      view.invoice_id = event.invoice_id
      # В реальности payment_link приходит из InvoiceService
      view.payment_link = f"https://pay.example.com/{event.invoice_id}"
      view.status = "invoiced"
      view.status_display = self.STATUS_DISPLAY["invoiced"]
      view.updated_at = datetime.now()
      self.session.commit()

  def on_deal_paid(self, event: DealPaid):
    """Обработка DealPaid: UPDATE status, is_paid"""
    view = self.session.query(DealViewORM).filter_by(
      deal_id=event.deal_id
    ).first()

    if view:
      view.status = "paid"
      view.status_display = self.STATUS_DISPLAY["paid"]
      view.is_paid = True
      view.updated_at = datetime.now()
      self.session.commit()

  def on_deal_cancelled(self, event: DealCancelled):
    """Обработка DealCancelled: UPDATE status"""
    view = self.session.query(DealViewORM).filter_by(
      deal_id=event.deal_id
    ).first()

    if view:
      view.status = "cancelled"
      view.status_display = self.STATUS_DISPLAY["cancelled"]
      view.updated_at = datetime.now()
      self.session.commit()


# Event Bus Integration
class EventBus:
  def __init__(self, projection: DealProjection):
    self.projection = projection
    self.handlers = {
      "DealCreated": self.projection.on_deal_created,
      "DealInvoiced": self.projection.on_deal_invoiced,
      "DealPaid": self.projection.on_deal_paid,
      "DealCancelled": self.projection.on_deal_cancelled
    }

  def publish(self, event):
    event_type = event.__class__.__name__
    handler = self.handlers.get(event_type)
    if handler:
      handler(event)
```

---

## Таблица критериев оценки

| Критерий | Баллы | Выполнено |
|----------|-------|-----------|
| Write Model | 20 | ✅ |
| Read Model | 25 | ✅ |
| Event-Driven Sync | 25 | ✅ |
| Оптимизация запросов | 15 | ✅ |
| Тесты проекций | 10 | ✅ |
| Качество документации | 5 | ✅ |
| **ИТОГО** | **100** | |

---

## Контрольные вопросы

1. **В чём разница между CQRS и CQS?**
   - CQS (Command Query Separation) - принцип на уровне методов: команды изменяют состояние и ничего не возвращают, запросы возвращают данные и ничего не изменяют. CQRS (Command Query Responsibility Segregation) - расширение на уровень архитектуры: разные модели данных для чтения и записи, которые могут храниться в разных БД и масштабироваться независимо.

2. **Почему Read Model денормализованная?**
   - Чтобы ускорить запросы и избежать JOIN-ов. Денормализация позволяет выполнить один SELECT без объединения таблиц, что критично для высоконагруженных read-сценариев. Данные дублируются, но это допустимая плата за производительность.

3. **Как синхронизировать модели при сбое?**
   - Используется механизм retry с экспоненциальной задержкой. События сохраняются в outbox table, и фоновый worker повторяет обработку. При повторяющихся сбоях событие помечается как failed и отправляется алерт администратору. Также можно использовать Kafka с guaranteed delivery.

4. **Что такое Eventual Consistency?**
   - Это модель согласованности, при которой Read Model может быть неактуальной некоторое время после изменения Write Model (обычно миллисекунды-секунды). В отличие от строгой согласованности, eventual consistency даёт более высокую производительность и доступность. В контексте CQRS это приемлемо, так как пользователь может не сразу увидеть свои изменения.

---

## Ссылка на репозиторий

👉 **GitHub:** _[[URL репозитория](https://github.com/carrotist-coder/PIS-2026)]_

---

## Вывод

В ходе работы реализовано CQRS-разделение для Deal Service:
- Write Model (нормализованная таблица deals) сохраняет доменную логику и инварианты. Агрегат Deal из Lab #3 обеспечивает целостность данных.
- Read Model (денормализованная таблица deal_views) оптимизирована для быстрых запросов. Добавлены индексы и предвычисленные поля (days_since_created, status_display).
- Event-Driven Synchronization через Projection Handler синхронизирует модели при каждом доменном событии (DealCreated, DealInvoiced, DealPaid, DealCancelled).

---

**Дата выполнения:** _07.04.2026_  
**Оценка:** _____________  
**Подпись преподавателя:** _____________
