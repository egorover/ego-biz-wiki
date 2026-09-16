# СОСТОЯНИЕ ПРОЕКТА – EgoBiz Wiki

## 1. Основная информация

* **Проект:** EgoBiz Wiki
* **Продукт:** AI Business Knowledge Assistant
* **Репозиторий:** `ego-biz-wiki`
* **GitHub:** `https://github.com/egorover/ego-biz-wiki`
* **Локальная директория:** `C:\Dev\oss\ego-biz-wiki`

**Демо-компания:** EgoTech Solutions

**Назначение проекта:**
ИИ-ассистент по корпоративной базе знаний, который отвечает на вопросы сотрудников на основе контролируемого набора внутренних документов.

Основные области Knowledge Base:

* HR
* IT
* Security
* Operations
* Customer Operations
* FAQ
* Technical Documentation
* Business Travel

---

# 2. Главный принцип проекта

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

Главный приоритет проекта:

1. Надёжность
2. Простота
3. Полнота MVP
4. Тестируемость
5. Поддерживаемость
6. Расширяемость

Правила:

* не добавлять сложность без необходимости;
* не использовать технологии только ради демонстрации современности;
* не усложнять архитектуру ради архитектуры;
* каждая новая возможность должна быть обоснована потребностями MVP;
* всё реализованное должно быть протестировано;
* функциональность, не требуемая MVP, переносится в Roadmap.

Если простое решение надёжно закрывает задачу MVP — используется простое решение.

---

# 3. Языковые правила

Основной язык проекта и взаимодействия — **русский**.

## На русском языке

* наше общение;
* Transfer Prompt;
* README;
* PROJECT_STATE;
* документация `docs/`;
* архитектурные описания;
* технические объяснения;
* пользовательский интерфейс;
* бизнес-контент;
* ответы AI.

## На английском языке

* имена файлов;
* имена директорий;
* имена классов;
* имена функций;
* имена переменных;
* Python comments;
* Python docstrings;
* API endpoints;
* названия библиотек и технологий;
* Git commit messages;
* технические идентификаторы.

Не следует без необходимости оформлять русскоязычные инструкции, разделы или пользовательский интерфейс на английском языке.

---

# 4. Методология разработки

Главное правило:

> **ONE CHAT = ONE COMPLETED GIT COMMIT**

Один рабочий чат посвящён одной законченной Git-задаче.

После каждого Commit:

1. Реализовать задачу.
2. Запустить тесты.
3. Проверить фактическое поведение.
4. Проверить структуру проекта.
5. Проверить документацию.
6. Обновить `PROJECT_STATE.md`.
7. Проверить Git status.
8. Создать backup.
9. Зафиксировать точное состояние.
10. Подготовить Transfer Prompt для следующего этапа.
11. Остановиться.

**Не переходить автоматически к следующему Commit.**

Следующий Commit начинается только в новом чате после передачи контекста.

---

# 5. История проекта

## Commit #01 — Project Foundation

**Статус:** завершён.

Commit:

```text
ba97e70 feat: establish project foundation
```

Создан фундамент проекта:

* структура приложения;
* базовая конфигурация;
* Pydantic Settings;
* `.env` / `.env.example`;
* базовые domain/application/infrastructure слои;
* FastAPI application;
* health endpoint;
* тестовая инфраструктура;
* базовая документация;
* Git workflow.

---

## Commit #02 — Knowledge Base

**Статус:** завершён.

Commit:

```text
9bc1f68 feat: add knowledge base
```

Реализована контролируемая Knowledge Base.

Созданы:

* 23 Markdown-документа;
* `knowledge_base/manifest.yaml`;
* единая структура metadata;
* единообразный формат документов;
* документы по HR, IT, Security, Operations, Customer Operations, FAQ и другим областям.

Количество Markdown-документов:

```text
23
```

---

## Commit #03 — Indexing

**Статус:** завершён.

Основной Commit:

```text
2f6c089 feat: implement knowledge base indexing
```

Документационный Commit:

```text
b627e32 docs: update README for commit 03
```

Реализован indexing pipeline:

```text
Knowledge Base
      ↓
manifest.yaml
      ↓
Document loading
      ↓
Metadata
      ↓
Chunking
      ↓
Embeddings
      ↓
ChromaDB
```

Основные возможности:

* загрузка документов через `manifest.yaml`;
* сохранение document metadata;
* token-aware chunking;
* embeddings через OpenAI-compatible API;
* поддержка ProxyAPI;
* persistent ChromaDB;
* коллекция `ego_biz_wiki`;
* детерминированные `chunk_id`;
* повторный indexing через upsert;
* отсутствие логических дубликатов;
* CLI entrypoint:
  `scripts/index_knowledge_base.py`;
* документация:
  `docs/INDEXING.md`;
* unit и integration tests.

Параметры:

```text
chunk_size = 800
chunk_overlap = 120
embedding_model = text-embedding-3-small
vector_store = ChromaDB
```

Результат реального indexing:

```text
Documents loaded: 23
Chunks created: 23
Embeddings API response: HTTP 200 OK
Chroma collection: ego_biz_wiki
Chroma records: 23
```

После повторного indexing:

```text
Chroma records: 23
```

Повторный запуск не создаёт дубликаты логических chunks.

---

## Commit #04 — Retrieval

**Статус:** завершён.

Основной Commit:

```text
263c209 feat: implement retrieval
```

Документационный Commit:

```text
52e943a docs: update README for retrieval
```

Реализован `RetrievalService`.

Pipeline:

```text
User Query
    ↓
Query Embedding
    ↓
Chroma Similarity Search
    ↓
Top-K Results
    ↓
Chunks + Metadata + Source
```

Реализовано:

* query validation;
* query embedding;
* semantic similarity search;
* configurable `top_k`;
* configurable distance threshold;
* domain-level `RetrievedChunk`;
* metadata preservation;
* source attribution;
* empty-result handling;
* ordering результатов;
* Chroma adapter;
* unit tests;
* integration tests;
* real retrieval smoke tests;
* out-of-KB test.

Текущие параметры:

```text
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=1.30
```

Используется distance threshold.

Проверенные запросы:

```text
Как оформить отпуск?
Как подключиться к VPN?
Что делать при фишинговом письме?
```

Для них находятся релевантные результаты.

Out-of-KB:

```text
Как заказать домик на Марсе?
```

Релевантные результаты не возвращаются.

---

# 6. Commit #05 — RAG Pipeline

**Статус:** завершён.

Основной Commit:

```text
da7c11c feat: implement rag pipeline
```

Реализован базовый полноценный RAG pipeline:

```text
Вопрос пользователя
        ↓
RetrievalService
        ↓
Найденные фрагменты
        ↓
RAGService
        ↓
OpenAI-compatible LLM
        ↓
Ответ + источники
```

Основные компоненты:

```text
app/application/rag/service.py
app/domain/rag.py
app/infrastructure/llm/openai.py
app/infrastructure/rag.py
app/api/dependencies.py
app/api/routes/chat.py
app/api/schemas/chat.py
```

Реализовано:

* получение пользовательского запроса;
* retrieval;
* формирование context;
* LLM generation;
* ответ пользователю;
* source attribution;
* fallback при недостатке информации;
* обработка пустого ответа LLM;
* уникализация источников;
* dependency wiring через FastAPI.

---

# 7. Commit #06 — API поиска

**Статус:** завершён.

Основной Commit:

```text
7dff25b feat: implement search endpoint
```

Документационный Commit:

```text
a2b24d2 docs: update project state and readme after commit 06
```

Добавлен отдельный API endpoint:

```text
POST /search
```

Назначение:

* выполнять semantic retrieval;
* возвращать найденные chunks;
* возвращать distance;
* возвращать metadata;
* возвращать source information;
* не генерировать финальный LLM-ответ.

Текущий API:

```text
GET  /health
POST /chat
POST /search
POST /index
```

---

# 8. Текущая архитектура backend

Основная архитектура:

```text
FastAPI
   ↓
API Routes
   ↓
Application Services
   ↓
Domain Models
   ↓
Infrastructure Adapters
   ↓
ChromaDB / OpenAI-compatible API
```

Основные слои:

```text
app/
├── api/
├── application/
├── domain/
└── infrastructure/
```

Domain-модели не должны зависеть от:

* ChromaDB;
* LangChain;
* конкретного provider SDK;
* FastAPI.

Application layer отвечает за orchestration.

Infrastructure layer отвечает за конкретные внешние технологии.

---

# 9. Текущая RAG-логика

`RAGService` получает пользовательский запрос и выполняет:

```text
query
  ↓
RetrievalService
  ↓
retrieved chunks
  ↓
если chunks отсутствуют
  ↓
fallback
```

Если релевантные chunks найдены:

```text
query
  +
retrieved context
  ↓
LLM
  ↓
answer
  +
sources
```

Источники формируются на основе metadata найденных документов.

---

# 10. Fallback

При отсутствии достаточной информации используется **точно заданный текст**:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

При fallback:

```text
sources = []
```

Fallback не должен:

* генерироваться LLM;
* изменяться UI;
* заменяться альтернативным текстом;
* смешиваться с retrieval logic.

---

# 11. Retrieval configuration

Текущие параметры:

```text
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=1.30
```

Chunking:

```text
CHUNK_SIZE=800
CHUNK_OVERLAP=120
```

Embedding model:

```text
text-embedding-3-small
```

LLM:

```text
gpt-4o-mini
```

Vector store:

```text
ChromaDB
```

Collection:

```text
ego_biz_wiki
```

Параметры являются конфигурируемыми и не должны быть без необходимости захардкожены в application code.

---

# 12. Источники и metadata

Минимальная metadata strategy:

```text
document_id
title
path
source
category
subcategory
updated_at
```

Для retrieved chunk дополнительно доступны:

```text
chunk_id
content
distance
metadata
source
```

`RetrievedChunk` является domain-level представлением результата retrieval.

Raw Chroma objects не должны передаваться в Application или API layer.

---

# 13. Commit #07 — Streamlit UI

**Текущий рабочий этап:** Commit #07 — Streamlit UI

**Статус:**

> **РЕАЛИЗОВАН — ПРОТЕСТИРОВАН — ГОТОВ К COMMIT**

Цель Commit #07:

Добавить минимальный presentation-ready пользовательский интерфейс для работы с уже существующим `/chat`.

Архитектура:

```text
Streamlit UI
     ↓ HTTP
FastAPI POST /chat
     ↓
RAGService
     ↓
RetrievalService
     ↓
ChromaDB
     ↓
LLM
     ↓
answer + sources
     ↓
Streamlit UI
```

Streamlit **не обращается напрямую** к:

* ChromaDB;
* RetrievalService;
* RAGService;
* LLM.

UI не дублирует backend business logic.

---

# 14. Реализация Streamlit UI

Добавлен файл:

```text
ui/streamlit_app.py
```

Используются:

```text
streamlit
requests
python-dotenv
```

UI содержит:

* название компании;
* название продукта;
* поле вопроса;
* кнопку отправки;
* отображение ответа;
* отображение источников;
* fallback;
* обработку пустого вопроса;
* обработку ошибки подключения к FastAPI.

Заголовок:

```text
EgoTech Solutions
```

Подзаголовок:

```text
EgoBiz Wiki — ИИ-ассистент по корпоративной базе знаний
```

Поле:

```text
Ваш вопрос
```

Кнопка:

```text
Задать вопрос
```

---

# 15. Конфигурация Streamlit

В `.env.example` добавлена:

```text
STREAMLIT_API_URL=http://127.0.0.1:8000
```

UI получает API URL через environment configuration.

Значение по умолчанию:

```text
http://127.0.0.1:8000
```

Streamlit-specific configuration не добавляется в backend `Settings`, поскольку относится непосредственно к UI.

---

# 16. Зависимости Commit #07

В `pyproject.toml` добавлены:

```text
streamlit>=1.48,<2.0
requests>=2.32,<3.0
```

После изменения зависимостей выполнено:

```text
python -m pip install -e .
```

Streamlit установлен и импортируется успешно.

Проверенная версия:

```text
Streamlit 1.64.0
```

---

# 17. Проверки Commit #07

## Проверка синтаксиса

Выполнено:

```text
python -m compileall .\ui\streamlit_app.py
```

Результат:

```text
успешно
```

---

## Запуск FastAPI

FastAPI запущен на:

```text
http://127.0.0.1:8000
```

API отвечает корректно.

---

## Запуск Streamlit

Streamlit запущен на:

```text
http://localhost:8501
```

UI открывается корректно.

---

# 18. UI-тест — релевантный вопрос

Проверен вопрос:

```text
Как подключиться к корпоративному VPN?
```

Получен содержательный ответ из Knowledge Base.

UI корректно отображает:

```text
Ответ
```

и список:

```text
Источники
```

---

# 19. UI-тест — пустой вопрос

Проверено нажатие кнопки без пользовательского запроса.

Получено:

```text
Введите вопрос.
```

Backend при этом не вызывается.

---

# 20. UI-тест — вопрос вне Knowledge Base

Проверен запрос:

```text
Какой сегодня курс биткоина?
```

Получен точный fallback:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

Источники не отображаются:

```text
sources = []
```

Это соответствует логике MVP.

---

# 21. UI-тест — ошибка backend

Проверена ситуация недоступного FastAPI.

UI корректно отображает:

```text
Не удалось получить ответ от API. Убедитесь, что FastAPI запущен.
```

Дополнительно отображается техническая информация об ошибке подключения.

После теста configuration была восстановлена.

Обычный режим:

```text
STREAMLIT_API_URL=http://127.0.0.1:8000
```

повторно проверен.

---

# 22. Полный test suite

После реализации Commit #07 выполнено:

```text
pytest
```

Результат:

```text
45 passed, 1 warning
```

Предупреждение относится к внешней зависимости:

```text
Starlette / AnyIO
```

и не связано с логикой проекта.

---

# 23. Проверка линтера

Попытка выполнить:

```text
ruff check .\ui\streamlit_app.py
```

показала, что `ruff` не установлен в текущем `.venv`.

Также:

```text
python -m ruff check .\ui\streamlit_app.py
```

не выполнена, поскольку пакет `ruff` отсутствует.

Принято решение:

**не добавлять Ruff в runtime dependencies проекта только ради локальной проверки Commit #07.**

Это не является функциональной ошибкой проекта.

---

# 24. Текущая структура проекта

Основная структура:

```text
ego-biz-wiki/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── health.py
│   │   │   └── search.py
│   │   │
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── chat.py
│   │       ├── health.py
│   │       └── search.py
│   │
│   ├── application/
│   │   ├── indexing/
│   │   │   └── service.py
│   │   ├── rag/
│   │   │   └── service.py
│   │   └── retrieval/
│   │       └── service.py
│   │
│   ├── domain/
│   │   ├── chunk.py
│   │   ├── document.py
│   │   ├── rag.py
│   │   └── retrieval.py
│   │
│   └── infrastructure/
│       ├── rag.py
│       ├── config/
│       │   └── settings.py
│       ├── embeddings/
│       │   └── openai.py
│       ├── indexing/
│       │   ├── chunker.py
│       │   └── manifest.py
│       ├── llm/
│       │   └── openai.py
│       ├── loaders/
│       │   └── markdown.py
│       └── vector_store/
│           └── chroma.py
│
├── knowledge_base/
│   ├── *.md
│   └── manifest.yaml
│
├── scripts/
│   └── index_knowledge_base.py
│
├── tests/
│
├── docs/
│
├── ui/
│   └── streamlit_app.py
│
├── .chroma/
├── backup/
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── PROJECT_STATE.md
```

---

# 25. Knowledge Base — архитектурное решение

Для MVP сознательно используется стандартизированный внутренний формат:

* Markdown;
* English `snake_case` для технических имён;
* русский бизнес-контент;
* единый `manifest.yaml`;
* единая metadata strategy;
* единообразная структура документов.

Это является:

> **нашим идеальным документооборотом**

То есть нормализованным внутренним форматом демонстрационного MVP.

Это **не утверждение**, что реальные корпоративные документы всегда организованы таким образом.

---

# 26. Document Standardization

Автоматическая стандартизация разнородных корпоративных документов **не входит в текущий MVP**.

В будущем Roadmap предусмотрена feature:

```text
Document Standardization
```

Она должна рассматривать обработку различных форматов, например:

```text
PDF
DOCX
XLSX
HTML
TXT
```

и других источников с последующим приведением их к единому внутреннему представлению Knowledge Base.

---

# 27. Безопасность

API key хранится только во внешнем:

```text
.env
```

`.env` не отслеживается Git.

Проверка:

```text
git check-ignore .env
```

ожидаемый результат:

```text
.env
```

Секреты:

* не должны попадать в Git;
* не должны попадать в README;
* не должны попадать в PROJECT_STATE;
* не должны логироваться;
* не должны попадать в тестовые fixtures.

`.env.example` содержит только безопасные шаблонные значения.

---

# 28. Что сознательно НЕ реализуется в текущем MVP

Не добавлять без отдельного обоснования:

* Agentic RAG;
* agents;
* LangGraph;
* hybrid search;
* reranking;
* web search;
* long-term memory;
* сложное conversation state;
* WebSocket;
* streaming;
* React;
* отдельный frontend server;
* authentication;
* chat-history database;
* сложную orchestration layer;
* дополнительные vector databases;
* ненужные abstraction layers.

Принцип:

> Если возможность не требуется для демонстрации надёжного MVP — она остаётся в Roadmap.

---

# 29. Ограничения текущего MVP

Текущий проект рассчитан на:

* контролируемую Knowledge Base;
* небольшой объём документов;
* классический RAG;
* один пользовательский запрос за раз;
* текущий chat context без долгосрочной памяти;
* локальный ChromaDB;
* OpenAI-compatible LLM/Embedding API;
* минимальный Streamlit интерфейс.

Параметры retrieval и chunking пока являются рабочими настройками MVP и должны быть дополнительно подтверждены evaluation.

---

# 30. Evaluation

Следующим значимым этапом после завершения Commit #07 является:

## Commit #08 — Formal Evaluation Dataset

Цель:

Создать формальный evaluation dataset для объективной проверки качества:

* retrieval;
* RAG;
* fallback;
* source attribution;
* типовых пользовательских вопросов.

Целевой размер:

```text
30–40 evaluation cases
```

Dataset должен включать:

* релевантные вопросы;
* вопросы с однозначным ответом;
* вопросы по разным категориям Knowledge Base;
* out-of-KB вопросы;
* потенциально неоднозначные вопросы;
* ожидаемые источники/темы;
* ожидаемое поведение системы.

После формирования dataset необходимо оценить качество существующего простого RAG **до добавления дополнительной сложности**.

---

# 31. Roadmap после MVP

Возможные будущие направления:

### Document Standardization

Автоматическая обработка:

```text
PDF
DOCX
XLSX
HTML
TXT
```

и других форматов.

### Улучшение Retrieval

Только после подтверждения необходимости evaluation:

* hybrid search;
* reranking;
* дополнительные retrieval strategies.

### Расширение памяти

* conversation history;
* long-term memory.

### Расширение интерфейса

* более полноценный chat UI;
* streaming;
* дополнительные пользовательские возможности.

### Production capabilities

* authentication;
* access control;
* monitoring;
* audit;
* deployment infrastructure.

Все перечисленное является Roadmap, а не обязательной частью текущего MVP.

---

# 32. Git State

Последний завершённый Commit:

```text
a2b24d2 docs: update project state and readme after commit 06
```

На момент подготовки Commit #07:

```text
HEAD = a2b24d2
origin/main = a2b24d2
```

Текущие изменения:

```text
M  .env.example
M  pyproject.toml
?? ui/
?? PROJECT_STATE.md.backup
```

`PROJECT_STATE.md.backup` является локальным backup и **не должен включаться в Commit #07**.

Commit #07 ещё не создан.

Планируемый Git commit message:

```text
feat: implement streamlit ui
```

---

# 33. Backup policy

Backup создаётся перед переходом к следующему этапу.

Текущий локальный backup:

```text
PROJECT_STATE.md.backup
```

Backup-файлы не должны случайно попадать в Git commit.

После завершения Commit #07 необходимо создать финальный backup текущего состояния перед переходом в новый чат.

---

# 34. Финальный workflow Commit #07

Перед завершением текущего этапа:

```text
VERIFY
   ↓
UPDATE PROJECT_STATE
   ↓
VERIFY PROJECT_STATE
   ↓
UPDATE README
   ↓
VERIFY README
   ↓
git diff --check
   ↓
git status
   ↓
git add только файлов Commit #07
   ↓
git commit
   ↓
git push
   ↓
VERIFY GitHub / origin
   ↓
VERIFY clean working tree
   ↓
CREATE BACKUP
   ↓
UPDATE PROJECT_STATE с фактическим commit hash
   ↓
VERIFY PROJECT_STATE
   ↓
PREPARE TRANSFER PROMPT
   ↓
STOP
```

---

# 35. Completion checklist — Commit #07

## Реализация

* [x] Streamlit dependency added
* [x] Requests dependency added
* [x] `ui/` created
* [x] `ui/streamlit_app.py` created
* [x] API URL configuration added
* [x] UI title configured
* [x] User question input implemented
* [x] `/chat` integration implemented
* [x] Answer display implemented
* [x] Sources display implemented
* [x] Empty input handling implemented
* [x] Fallback behavior verified
* [x] Backend error handling verified

## Проверка

* [x] Streamlit starts
* [x] FastAPI starts
* [x] UI opens
* [x] Normal question tested
* [x] Empty question tested
* [x] Out-of-KB question tested
* [x] Backend error tested
* [x] Normal configuration restored
* [x] Full pytest suite passed

## Tests

```text
45 passed, 1 warning
```

## Документация

* [ ] `PROJECT_STATE.md` updated
* [ ] `README.md` updated
* [ ] documentation verified

## Git

* [ ] `git diff --check`
* [ ] `git status` verified
* [ ] Commit #07 created
* [ ] Commit #07 pushed
* [ ] GitHub state verified
* [ ] working tree clean
* [ ] backup created
* [ ] final PROJECT_STATE updated
* [ ] Transfer Prompt prepared

---

# 36. Текущая точка проекта

На данный момент:

**Commit #01 — Project Foundation** ✅

**Commit #02 — Knowledge Base** ✅

**Commit #03 — Indexing** ✅

**Commit #04 — Retrieval** ✅

**Commit #05 — RAG Pipeline** ✅

**Commit #06 — API Search** ✅

**Commit #07 — Streamlit UI**
**РЕАЛИЗОВАН — ПРОТЕСТИРОВАН — ОЖИДАЕТ COMMIT** ⏳

Следующий этап:

**Commit #08 — Formal Evaluation Dataset**

Но переход к Commit #08 выполняется **только в новом чате после полного завершения и фиксации Commit #07**.

---

# 37. Правило сохранения состояния

`PROJECT_STATE.md` является главным техническим документом передачи контекста проекта.

При его последующих обновлениях:

* не удалять завершённые этапы;
* не сокращать историю;
* не заменять технические детали кратким summary;
* не переписывать фактические результаты предположениями;
* сохранять commit hashes;
* сохранять реальные результаты тестов;
* сохранять архитектурные решения;
* сохранять ограничения MVP;
* сохранять причины важных решений;
* актуализировать только изменившееся состояние.

> **PROJECT_STATE должен позволять продолжить разработку проекта в новом чате без необходимости восстанавливать историю по памяти.**
