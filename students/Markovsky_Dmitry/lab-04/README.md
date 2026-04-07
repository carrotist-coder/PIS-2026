<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №4</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Проектирование интернет-систем"</p>
<p align="center"><strong>Тема:</strong> "Application Layer: Commands, Queries, Handlers"</p>
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

Реализовать **прикладной слой** (Application Layer) с разделением операций на **команды** (изменяют состояние) и **запросы** (читают данные) по паттерну CQRS.

---

## Вариант №6 - Мини-CRM «Фриланс без паники»

**Питч:** _Клиенты довольны, дедлайны живы._
**Ядро домена:** _Клиенты, Сделки, Этапы воронки, Задачи, Инвойсы_

---

## Ход выполнения работы

### 1. Команды (Commands)

**Созданные команды:**

1. **CreateDealCommand** - создание новой сделки
   - Поля: `client_id`, `title`, `amount`, `currency`, `idempotency_key`
   - Валидация: client_id не пустой, title 3-100 символов, amount > 0
   - Файл: `application/command/create_deal_command.py`

2. **MarkDealAsPaidCommand** - отметка сделки как оплаченной
   - Поля: `deal_id`
   - Валидация: deal_id не пустой
   - Файл: `application/command/mark_deal_as_paid_command.py`

3. **CancelDealCommand** - отмена сделки
   - Поля: `deal_id`, `reason`
   - Валидация: deal_id не пустой, reason не пустой
   - Файл: `application/command/cancel_deal_command.py`

**Пример кода команды:**
```python
@dataclass(frozen=True)
class CreateDealCommand:
  """
  Command for creating a new deal.

  Contains all data needed to create a deal.
  Validation is performed at the command level for primitive values.
  """

  client_id: str
  title: str
  amount: float
  currency: str = "USD"
  idempotency_key: Optional[str] = None

  def __post_init__(self):
    if not self.client_id or not self.client_id.strip():
      raise ValueError("client_id cannot be empty")

    if not self.title or not self.title.strip():
      raise ValueError("title cannot be empty")

    if len(self.title.strip()) < 3:
      raise ValueError("title must be at least 3 characters")

    if len(self.title) > 100:
      raise ValueError("title must be at most 100 characters")

    if self.amount <= 0:
      raise ValueError(f"amount must be positive, got {self.amount}")

    if self.currency not in ["USD", "BYN", "EUR"]:
      raise ValueError(f"unsupported currency: {self.currency}")

```

---

### 2. Command Handlers

**Созданные обработчики:**

1. **CreateDealHandler** - создание сделки и инвойса
   - Шаги обработки: _проверка idempotency → создание Deal → сохранение → создание инвойса → отправка уведомления_
   - Возвращает: _deal_id_
   - Файл: `application/command/handlers/create_deal_handler.py`

2. **MarkDealAsPaidHandler** - отметка сделки как оплаченной
   - Шаги: _загрузка агрегата → mark_as_paid() → сохранение_
   - Файл: `application/command/handlers/mark_deal_as_paid_handler.py`

3. **CancelDealHandler** - отмена сделки
   - Шаги: _загрузка агрегата → cancel() → сохранение_
   - Файл: `application/command/handlers/cancel_deal_handler.py`

**Пример кода handler:**
```python
"""Handler for CancelDealCommand."""

from src.application.port.outbound.deal_repository import DealRepository
from ..cancel_deal_command import CancelDealCommand


class CancelDealHandler:
  """
  Handler for CancelDealCommand.

  This handler cancels an existing deal:
  1. Load deal from repository
  2. Call domain method cancel()
  3. Save updated deal
  """

  def __init__(self, repository: DealRepository):
    self.repository = repository

  def handle(self, command: CancelDealCommand) -> None:
    """
    Execute the command.

    Args:
        command: CancelDealCommand with deal_id and reason

    Raises:
        ValueError: If deal not found or cannot be cancelled
    """
    deal = self.repository.find_by_id(command.deal_id)
    if not deal:
      raise ValueError(f"Deal {command.deal_id} not found")

    deal.cancel(command.reason)
    self.repository.save(deal)
```

**Скриншот теста:**

```
Testing started at 09:40 ...
Launching pytest with arguments students/Markovsky_Dmitry/lab-04/tests/test_cancel_deal_handler.py::TestCancelDealHandler --no-header --no-summary -q in E:\kurs3\PIS\PIS-2026

============================= test session starts =============================
collecting ... collected 2 items

students/Markovsky_Dmitry/lab-04/tests/test_cancel_deal_handler.py::TestCancelDealHandler::test_cancel_deal_success PASSED [ 50%]
students/Markovsky_Dmitry/lab-04/tests/test_cancel_deal_handler.py::TestCancelDealHandler::test_cancel_deal_not_found_raises_error PASSED [100%]

============================== 2 passed in 0.17s ==============================

Process finished with exit code 0
```

---

### 3. Queries (Запросы)

**Созданные запросы:**

1. **GetDealByIdQuery** - получить сделку по ID
   - Поля: `deal_id`
   - Файл: `application/query/get_deal_by_id_query.py`

2. **ListDealsByClientQuery** -список сделок клиента
   - Поля: `client_id, limit, offset`
   - Файл: `application/query/list_deals_by_client_query.py`

**Read DTOs:**

- **DealDto** - упрощённая модель для чтения
   - Поля: `id, client_id, title, amount, currency, status, created_at`
   - Файл: `application/query/dto/deal_dto.py`

**Пример кода:**
```python
# application/query/dto/deal_dto.py
@dataclass(frozen=True)
class DealDto:
    id: str
    client_id: str
    title: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    invoice_id: str = None
    payment_link: str = None

# application/query/get_deal_by_id_query.py
@dataclass(frozen=True)
class GetDealByIdQuery:
  """
  Query to get a deal by its ID.

  This query retrieves a single deal without modifying state.
  """

  deal_id: str

  def __post_init__(self):
    if not self.deal_id or not self.deal_id.strip():
      raise ValueError("deal_id cannot be empty")

```

---

### 4. Query Handlers

**Созданные обработчики запросов:**

1. **GetDealByIdHandler** -получение сделки по ID
   - Репозиторий: `DealRepository`
   - Возвращает: `DealDto`
   - Файл: `application/query/handlers/get_deal_by_id_handler.py`

**Пример кода:**
```python
class GetDealByIdHandler:
  """
  Handler for GetDealByIdQuery.

  This handler retrieves a deal by ID and converts it to a DTO.
  """

  def __init__(self, repository: DealRepository):
    self.repository = repository

  def handle(self, query: GetDealByIdQuery) -> Optional[DealDto]:
    """
    Execute the query.

    Args:
        query: GetDealByIdQuery with deal_id

    Returns:
        DealDto if found, None otherwise
    """
    deal = self.repository.find_by_id(query.deal_id)

    if not deal:
      return None

    return DealDto(
      id=deal.id,
      client_id=str(deal.client_id),
      title=str(deal.title),
      amount=float(deal.amount.amount),
      currency=deal.amount.currency,
      status=deal.status.value,
      created_at=deal.created_at
    )

```

**Скриншот:**

```
C:\Python311\python.exe "C:/Program Files/JetBrains/PyCharm 2025.2.5/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py" --target students/Markovsky_Dmitry/lab-04/tests/test_queries.py::TestGetDealByIdHandler 
Testing started at 09:41 ...
Launching pytest with arguments students/Markovsky_Dmitry/lab-04/tests/test_queries.py::TestGetDealByIdHandler --no-header --no-summary -q in E:\kurs3\PIS\PIS-2026

============================= test session starts =============================
collecting ... collected 2 items

students/Markovsky_Dmitry/lab-04/tests/test_queries.py::TestGetDealByIdHandler::test_get_deal_found PASSED [ 50%]
students/Markovsky_Dmitry/lab-04/tests/test_queries.py::TestGetDealByIdHandler::test_get_deal_not_found PASSED [100%]

============================== 2 passed in 0.16s ==============================

Process finished with exit code 0
```

---

### 5. Application Service (Фасад)

**Реализованный сервис:** `DealApplicationService`

**Методы:**

| Метод | Тип | Возвращает |
|-------|-----|------------|
| `create_deal(command)` | Command | deal_id (str) |
| `mark_deal_as_paid(command)` | Command | void |
| `cancel_deal(command)` | Command | void |
| `get_deal_by_id(query)` | Query | DealDto |

**Пример кода:**
```python
"""
Application service facade for Deal operations.

This service delegates to specialized Command/Query handlers
following the CQRS pattern.
"""
from src.application.command import CreateDealCommand, MarkDealAsPaidCommand, CancelDealCommand
from src.application.command.handlers import CreateDealHandler, MarkDealAsPaidHandler, CancelDealHandler
from src.application.port.outbound.deal_repository import DealRepository
from src.application.port.outbound.invoice_service import InvoiceService
from src.application.port.outbound.notification_service import NotificationService
from src.application.query.handlers import GetDealByIdHandler

from src.application.query import GetDealByIdQuery, DealDto


class DealApplicationService:
  """
  Application service facade.

  This class provides a simple interface for external clients
  and delegates all operations to specialized handlers.
  """

  def __init__(
    self,
    repository: DealRepository,
    invoice_service: InvoiceService,
    notification_service: NotificationService
  ):
    self.repository = repository
    self.invoice_service = invoice_service
    self.notification_service = notification_service

    # Initialize handlers
    self._create_deal_handler = CreateDealHandler(
      repository, invoice_service, notification_service
    )
    self._mark_paid_handler = MarkDealAsPaidHandler(repository)
    self._cancel_deal_handler = CancelDealHandler(repository)
    self._get_deal_handler = GetDealByIdHandler(repository)

  # Commands
  def create_deal(self, command: CreateDealCommand) -> str:
    """
    Create a new deal.

    Args:
        command: CreateDealCommand with deal data

    Returns:
        Created deal ID
    """
    return self._create_deal_handler.handle(command)

  def mark_deal_as_paid(self, command: MarkDealAsPaidCommand) -> None:
    """
    Mark a deal as paid.

    Args:
        command: MarkDealAsPaidCommand with deal_id
    """
    self._mark_paid_handler.handle(command)

  def cancel_deal(self, command: CancelDealCommand) -> None:
    """
    Cancel a deal.

    Args:
        command: CancelDealCommand with deal_id and reason
    """
    self._cancel_deal_handler.handle(command)

  # Queries
  def get_deal_by_id(self, query: GetDealByIdQuery) -> DealDto:
    """
    Get a deal by ID.

    Args:
        query: GetDealByIdQuery with deal_id

    Returns:
        DealDto if found, None otherwise
    """
    return self._get_deal_handler.handle(query)

```

---

### 6. Тестирование

**Юнит-тесты:**

| Тест | Что проверяет | Статус |
|------|---------------|--------|
| `test_create_handler` | Создание агрегата, вызов save() | ✅ |
| `test_handler_publishes_events` | Публикация доменных событий | ✅ |
| `test_query_handler_not_found` | Обработка ошибки "не найдено" | ✅ |

**Скриншот pytest:**

_[Вывод pytest с 100% покрытием handlers]_

---

## Таблица критериев оценки

| Критерий | Баллы | Выполнено |
|----------|-------|-----------|
| Команды (DTOs): иммутабельность, валидация примитивов | 15 | ✅ |
| Command Handlers: транзакции, события, сохранение | 25 | ✅ |
| Запросы (DTOs): read-модели без побочных эффектов | 10 | ✅ |
| Query Handlers: преобразование домена в DTO | 15 | ✅ |
| Application Service (фасад): делегирование | 20 | ✅ |
| Юнит-тесты handlers: mocker, события | 10 | ✅ |
| Качество документации | 5 | ✅ |
| **ИТОГО** | **100** | |

---

## Контрольные вопросы

1. **В чём разница между Command и Query?**
   - Command изменяет состояние системы (create, update, delete) и возвращает void или ID. Query только читает данные и возвращает DTO, не изменяя состояние.

2. **Почему Command Handler возвращает только ID, а не весь объект?**
   - Чтобы избежать утечки доменной модели наружу. Клиент после создания должен сделать отдельный GET-запрос, что соответствует принципу CQRS.

3. **Где должна выполняться валидация: в команде, обработчике или доменной модели?**
   - Примитивы (not empty, positive) - в команде/обработчике. Бизнес-инварианты (нельзя отменить оплаченную сделку) - в доменной модели.

4. **Можно ли вызывать Query из Command Handler?**
   - Технически можно, но не рекомендуется (нарушает CQRS). Лучше загружать данные через Repository.

5. **Зачем разделять Request DTO (от клиента) и Command (внутренний)?**
   - Request DTO зависит от формата API (HTTP/JSON). Command - внутренняя структура приложения. Разделение позволяет независимо менять API и бизнес-логику.

---

## Ссылка на репозиторий

👉 **GitHub:** _[[URL репозитория](https://github.com/carrotist-coder/PIS-2026)]_

**Структура папки:**
```
src/application/
├── __init__.py                         
├── command/
│   ├── __init__.py                     
│   ├── create_deal_command.py
│   ├── mark_deal_as_paid_command.py
│   ├── cancel_deal_command.py
│   └── handlers/
│       ├── __init__.py                 
│       ├── create_deal_handler.py
│       ├── mark_deal_as_paid_handler.py
│       └── cancel_deal_handler.py
├── query/
│   ├── __init__.py                     
│   ├── get_deal_by_id_query.py
│   ├── list_deals_by_client_query.py
│   ├── dto/
│   │   ├── __init__.py                 
│   │   └── deal_dto.py
│   └── handlers/
│       ├── __init__.py                 
│       └── get_deal_by_id_handler.py
├── service/
│   ├── __init__.py                     
│   └── deal_application_service.py
└── port/
    ├── __init__.py                     
    ├── inbound/
    │   └── __init__.py                 
    └── outbound/
        ├── __init__.py                 
        ├── deal_repository.py
        ├── invoice_service.py
        └── notification_service.py
```

---

## Вывод

В ходе выполнения работы реализован прикладной слой для Deal Service с разделением на команды и запросы по паттерну CQRS. Созданы 3 команды (CreateDeal, MarkDealAsPaid, CancelDeal) с иммутабельными DTO и валидацией примитивов. Реализованы соответствующие Command Handlers, которые загружают агрегат, вызывают доменные методы и сохраняют изменения. Добавлены 2 запроса (GetDealById, ListDealsByClient) с read-моделью DealDto. Query Handler преобразует доменные сущности в DTO без изменения состояния. Application Service выступает фасадом, делегируя вызовы специализированным хендлерам. Написаны юнит-тесты с моками, покрывающие все сценарии.

Что получилось: Чёткое разделение команд и запросов, изоляция доменной логики от прикладного слоя, хорошая тестируемость.

Проблемы: Пришлось добавить idempotency_key в репозиторий, так как изначально его не было.

---

**Дата выполнения:** _06.04.2026_  
**Оценка:** _____________  
**Подпись преподавателя:** _____________
