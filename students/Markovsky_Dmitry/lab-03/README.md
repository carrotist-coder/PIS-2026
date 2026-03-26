<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №3</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Проектирование интернет-систем"</p>
<p align="center"><strong>Тема:</strong> "Реализация Domain Layer с DDD-паттернами"</p>
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

Научиться применять тактические паттерны DDD (Entities, Value Objects, Aggregates, Domain Events) для реализации **доменного слоя** с инвариантами и доменной логикой.

---

## Вариант №6 - Мини-CRM «Фриланс без паники»

**Питч:** _Клиенты довольны, дедлайны живы._
**Ядро домена:** _Клиенты, Сделки, Этапы воронки, Задачи, Инвойсы_

---

## Ход выполнения работы

### 1. Value Objects (Ценностные Объекты)

**Созданные Value Objects:**

1. **Money** - денежная сумма с валютой
   - Валидация: сумма >= 0, валюта из списка (USD, BYN, EUR)
   - Иммутабельность: ✅
   - Файл: `domain/value_objects/money.py`

2. **DealStatus** - статус сделки (enum)
   - Валидация: только допустимые значения
   - Иммутабельность: ✅
   - Файл: `domain/value_objects/deal_status.py`

3. **ClientId** - идентификатор клиента
   - Валидация: не пустой, формат cli-XXXX
   - Иммутабельность: ✅
   - Файл: `domain/value_objects/client_id.py`

4. **DealTitle** - название сделки
   - Валидация: не пустое, длина 3-100 символов
   - Иммутабельность: ✅
   - Файл: `domain/value_objects/deal_title.py`

**Пример кода (Money):**

```python
class Money:
    """
    Value Object representing money amount with currency.
    
    Immutable value object that encapsulates amount validation and
    currency formatting logic.
    """
    
    SUPPORTED_CURRENCIES = {"USD", "BYN", "EUR"}
    
    def __init__(self, amount: Union[int, float, Decimal, str], currency: str = "USD"):
        """
        Initialize Money object.
        
        Args:
            amount: Monetary value (must be >= 0)
            currency: Currency code (USD, BYN, EUR)
            
        Raises:
            ValueError: If amount is negative or currency is not supported
        """
        if isinstance(amount, str):
            self.amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            self.amount = Decimal(str(amount))
        else:
            self.amount = amount
        
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency: {currency}. "
                f"Supported: {self.SUPPORTED_CURRENCIES}"
            )
        
        self.currency = currency
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"
    
    def add(self, other: "Money") -> "Money":
        """
        Add two Money objects (same currency).
        
        Args:
            other: Money object to add
            
        Returns:
            New Money object with sum
            
        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} != {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)
```

**Скриншот:**

_[Вставьте скриншот pytest-тестов для VO]_

---

### 2. Entities (Сущности)

**Созданные Entity:**

1. **_Deal_** - _основная сущность сделки_
   - ID поле: `deal_id`
   - Бизнес-правила: нельзя выставить инвойс на оплаченную сделку, нельзя отменить оплаченную
   - Файл: `domain/entities/deal.py`

2. **_Invoice_** - _инвойс (счёт)_
   - ID поле: `invoice_id`
   - Бизнес-правила: инвойс нельзя изменить после оплаты
   - Файл: `domain/entities/invoice.py`

**Пример кода** (одна Entity):
```python
class Deal:
    """Entity: business deal with a client."""
    
    def __init__(
        self,
        deal_id: str,
        client_id: ClientId,
        title: DealTitle,
        amount: Money,
        status: DealStatus = None
    ):
        """
        Initialize Deal entity.
        
        Args:
            deal_id: Unique identifier
            client_id: Client reference
            title: Deal title
            amount: Deal value
            status: Initial status (default: NEGOTIATION)
        """
        self._id = deal_id
        self._client_id = client_id
        self._title = title
        self._amount = amount
        self._status = status or DealStatus.NEGOTIATION
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._events: List[DomainEvent] = []
        
        self._validate()
        self._register_event(DealCreated(deal_id, client_id, title, amount))
    
    def _validate(self) -> None:
        """Validate business invariants."""
        if self._amount.amount <= 0:
            raise ValueError(f"Deal amount must be positive, got: {self._amount.amount}")
    
    def _register_event(self, event: DomainEvent) -> None:
        """Register a domain event."""
        self._events.append(event)
    
    def mark_as_invoiced(self, invoice_id: str) -> None:
        """Mark deal as invoiced."""
        if not self._status.can_transition_to(DealStatus.INVOICED):
            raise ValueError(
                f"Cannot invoice deal: current status is {self._status}, "
                f"expected NEGOTIATION or APPROVAL"
            )
        
        self._status = DealStatus.INVOICED
        self._updated_at = datetime.now()
        self._register_event(DealInvoiced(self._id, invoice_id, self._amount))
    
    def mark_as_paid(self) -> None:
        """Mark deal as paid."""
        if not self._status.can_transition_to(DealStatus.PAID):
            raise ValueError(
                f"Cannot mark as paid: deal is in status {self._status}, "
                f"expected INVOICED"
            )
        
        self._status = DealStatus.PAID
        self._updated_at = datetime.now()
        self._register_event(DealPaid(self._id))
    
    def cancel(self, reason: str) -> None:
        """Cancel the deal."""
        if not self._status.can_transition_to(DealStatus.CANCELLED):
            raise ValueError(
                f"Cannot cancel deal: deal is in status {self._status}"
            )
        
        self._status = DealStatus.CANCELLED
        self._updated_at = datetime.now()
        self._register_event(DealCancelled(self._id, reason))
    
    def get_events(self) -> List[DomainEvent]:
        """Get all registered events."""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear all registered events."""
        self._events.clear()
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def client_id(self) -> ClientId:
        return self._client_id
    
    @property
    def title(self) -> DealTitle:
        return self._title
    
    @property
    def amount(self) -> Money:
        return self._amount
    
    @property
    def status(self) -> DealStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Equality based on ID
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Deal):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"Deal(id='{self._id}', client='{self._client_id}', amount={self._amount}, status={self._status})"
```

**Скриншот тестов:**

_[Скриншот pytest для проверки инвариантов Entity]_

---

### 3. Aggregate Root (Корневой агрегат)

**Aggregate Root:** _Deal_

**Границы агрегата:**
- Корень: `Deal` (сделка)
- Внутренние сущности: `Invoice` (инвойс)
- Value Objects: `Money, DealStatus, ClientId, DealTitle`

**Инварианты агрегата:**

| № | Инвариант | Как проверяется |
|---|----------|----------------|
| 1 | Сумма сделки должна быть положительной | В _validate() при создании |
| 2 | Нельзя выставить инвойс на уже оплаченную сделку | В mark_as_invoiced() проверка статуса |
| 3 | Нельзя оплатить сделку без инвойса | В mark_as_paid() проверка статуса INVOICED |
| 4 | Нельзя отменить оплаченную сделку | В cancel() проверка статуса PAID |

**Пример кода Aggregate Root:**
```python
class DealAggregate:
    """
    Aggregate Root: Deal with its invoice.
    
    This aggregate encapsulates the deal and its associated invoice,
    ensuring consistency between them.
    """
    
    def __init__(self, deal: Deal):
        """
        Initialize deal aggregate.
        
        Args:
            deal: Deal entity (root)
        """
        self._deal = deal
        self._invoice: Optional[Invoice] = None
    
    def create_invoice(self, invoice_id: str) -> None:
        """
        Create an invoice for the deal.
        
        Args:
            invoice_id: Unique invoice identifier
            
        Raises:
            ValueError: If invoice already exists
        """
        if self._invoice is not None:
            raise ValueError(f"Invoice already exists for deal {self._deal.id}")
        
        self._invoice = Invoice(invoice_id, self._deal.id, self._deal.amount)
        self._deal.mark_as_invoiced(invoice_id)
    
    def mark_as_paid(self) -> None:
        """
        Mark the deal as paid.
        
        Raises:
            ValueError: If no invoice exists
        """
        if self._invoice is None:
            raise ValueError(f"Cannot pay deal {self._deal.id} without invoice")
        
        self._invoice.mark_as_paid()
        self._deal.mark_as_paid()
    
    def cancel(self, reason: str) -> None:
        """
        Cancel the deal.
        
        Args:
            reason: Cancellation reason
        """
        self._deal.cancel(reason)
    
    def set_payment_link(self, payment_link: str) -> None:
        """
        Set payment link for the invoice.
        
        Args:
            payment_link: URL for payment
            
        Raises:
            ValueError: If no invoice exists
        """
        if self._invoice is None:
            raise ValueError(f"Cannot set payment link: no invoice for deal {self._deal.id}")
        
        self._invoice.set_payment_link(payment_link)
    
    def get_events(self) -> List[DomainEvent]:
        """Get all events from the aggregate."""
        events = self._deal.get_events()
        return events
    
    def clear_events(self) -> None:
        """Clear all events from the aggregate."""
        self._deal.clear_events()
    
    # Properties
    @property
    def deal(self) -> Deal:
        return self._deal
    
    @property
    def invoice(self) -> Optional[Invoice]:
        return self._invoice
    
    def __repr__(self) -> str:
        return f"DealAggregate(deal={self._deal.id}, invoice={self._invoice.id if self._invoice else 'None'})"
```

**Скриншот тестов инвариантов:**

_[Скриншот pytest для проверки инвариантов агрегата]_

---

### 4. Domain Events (Доменные события)

**Созданные события:**

1. **DealCreated** - _при создании сделки_
   - Данные: `deal_id, client_id, title, amount`
   - Файл: `domain/events/deal_events.py`

2. **DealInvoiced** - _при выставлении инвойса_
   - Данные: `deal_id, invoice_id, amount`
   - Файл: `domain/events/deal_events.py`

3. **DealPaid** - _при оплате сделки_
   - Данные: `deal_id`
   - Файл: `domain/events/deal_events.py`

4. **DealCancelled** - _при отмене сделки_
   - Данные: `deal_id, reason`
   - Файл: `domain/events/deal_events.py`

**Пример кода события:**
```python
@dataclass
class DomainEvent:
    """Base class for all domain events."""
    
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()


@dataclass
class DealCreated(DomainEvent):
    """Event raised when a deal is created."""
    
    deal_id: str
    client_id: ClientId
    title: DealTitle
    amount: Money


@dataclass
class DealInvoiced(DomainEvent):
    """Event raised when an invoice is created for a deal."""
    
    deal_id: str
    invoice_id: str
    amount: Money


@dataclass
class DealPaid(DomainEvent):
    """Event raised when a deal is paid."""
    
    deal_id: str


@dataclass
class DealCancelled(DomainEvent):
    """Event raised when a deal is cancelled."""
    
    deal_id: str
    reason: str
```

**Скриншот:**

_[Скриншот теста регистрации события]_

---

### 5. Юнит-тесты

**Покрытие тестами:**

| Компонент | Количество тестов | Покрытие | Статус |
|-----------|-------------------|----------|--------|
| Value Objects | _[число]_ | _[%]_ | ✅ |
| Entities | _[число]_ | _[%]_ | ✅ |
| Aggregate Root | _[число]_ | _[%]_ | ✅ |
| Domain Events | _[число]_ | _[%]_ | ✅ |

**Скриншот pytest:**

_[Вставьте pytest --cov или pytest -v вывод]_

---

## Таблица критериев оценки

| Критерий | Баллы | Выполнено |
|----------|-------|-----------|
| Value Objects: корректная валидация, иммутабельность | 20 | ❌ / ✅ |
| Entities: identity-based equality, инварианты | 20 | ❌ / ✅ |
| Aggregate Root: границы, инварианты, публичные методы | 25 | ❌ / ✅ |
| Domain Events: регистрация событий при изменении состояния | 15 | ❌ / ✅ |
| Юнит-тесты: покрытие инвариантов, edge-cases | 15 | ❌ / ✅ |
| Качество документации | 5 | ❌ / ✅ |
| **ИТОГО** | **100** | |

---

## Бонусы

| Бонус | Баллы | Выполнено |
|-------|-------|-----------|
| Repository интерфейс (только интерфейс без реализации) | +5 | ❌ / ✅ |
| Specification Pattern для запросов | +4 | ❌ / ✅ |
| Domain Services для сложной логики | +3 | ❌ / ✅ |
| Event Bus (in-memory) для публикации событий | +3 | ❌ / ✅ |

**ИТОГО бонусов:** _[число]_ / 15

---

## Контрольные вопросы

1. **В чём отличие Value Object от Entity?**
   - _[Ваш ответ]_

2. **Почему Aggregate Root должен инкапсулировать доступ к внутренним сущностям?**
   - _[Ваш ответ]_

3. **Какая роль Domain Events? Приведите пример из вашей системы.**
   - _[Ваш ответ]_

4. **Как вы проверяете инварианты в вашем агрегате? Приведите пример.**
   - _[Ваш ответ]_

5. **Почему Value Objects делаются иммутабельными?**
   - _[Ваш ответ]_

---

## Ссылка на репозиторий

👉 **GitHub:** _[URL вашего репозитория]_

**Структура папки:**
```
lab-03/
├── Отчет.md
├── domain/
│   ├── value_objects/
│   │   ├── _[файлы VO]_.py
│   ├── entities/
│   │   ├── _[файлы Entity]_.py
│   ├── aggregates/
│   │   ├── _[файлы Aggregate]_.py
│   └── events/
│       ├── _[файлы Events]_.py
└── tests/
    ├── test_value_objects.py
    ├── test_entities.py
    ├── test_aggregates.py
    └── test_events.py
```

---

## Вывод

✍️ _[Напишите краткий вывод: что получилось, какие проблемы возникли, насколько доменный слой изолирован от технических деталей]_

**Примеры выводов:**
- "Реализован доменный слой с 3 агрегатами и 5 Value Objects. Инварианты проверяются в конструкторах и методах агрегатов. Все тесты проходят."
- "Aggregate Root корректно инкапсулирует доступ к Group через метод assign_group(). Domain Events регистрируются при изменении состояния."

---

**Дата выполнения:** _[Дата]_  
**Оценка:** _____________  
**Подпись преподавателя:** _____________
