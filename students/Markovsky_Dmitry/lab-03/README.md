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

1. **_[Название Entity 1]_** - _[описание]_
   - ID поле: `_[имя поля]_`
   - Бизнес-правила: _[какие инварианты]_
   - Файл: `domain/entities/_[имя файла]_.py`

2. **_[Название Entity 2]_** - _[описание]_
   - ID поле: `_[имя поля]_`
   - Бизнес-правила: _[инварианты]_
   - Файл: `domain/entities/_[имя файла]_.py`

**Пример кода** (одна Entity):
```python
_[Вставьте код вашей Entity с invariants]_
```

**Скриншот тестов:**

_[Скриншот pytest для проверки инвариантов Entity]_

---

### 3. Aggregate Root (Корневой агрегат)

**Aggregate Root:** _[Название агрегата]_

**Границы агрегата:**
- Корень: `_[корневая сущность]_`
- Внутренние сущности: `_[список сущностей]_`
- Value Objects: `_[список VO]_`

**Инварианты агрегата:**

| № | Инвариант | Как проверяется |
|---|----------|----------------|
| 1 | _[Пример: Нельзя активировать заявку без группы]_ | _[В методе activate()]_ |
| 2 | _[Инвариант 2]_ | _[Метод]_ |
| 3 | _[Инвариант 3]_ | _[Метод]_ |

**Пример кода Aggregate Root:**
```python
_[Вставьте код вашего Aggregate Root с методами]_
```

**Скриншот тестов инвариантов:**

_[Скриншот pytest для проверки инвариантов агрегата]_

---

### 4. Domain Events (Доменные события)

**Созданные события:**

1. **_[Событие 1]_** - _[когда генерируется]_
   - Данные: `_[какие поля]_`
   - Файл: `domain/events/_[имя файла]_.py`

2. **_[Событие 2]_** - _[когда генерируется]_
   - Данные: `_[поля]_`
   - Файл: `domain/events/_[имя файла]_.py`

**Пример кода события:**
```python
_[Вставьте код одного Domain Event]_
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
