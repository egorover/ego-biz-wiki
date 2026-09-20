# Architecture — EgoBiz Wiki

## 1. Назначение документа

Этот документ описывает архитектуру проекта **EgoBiz Wiki**, основные компоненты системы, их ответственность и взаимодействие.

EgoBiz Wiki разработан как компактный RAG-based AI Business Knowledge Assistant для ответов на вопросы сотрудников на основе контролируемой корпоративной Knowledge Base.

Архитектура ориентирована на рабочий MVP и намеренно избегает необоснованного усложнения.

Главный принцип:

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

---

## 2. Архитектурный принцип

Проект использует упрощённый вариант Clean Architecture с разделением ответственности между слоями.

Основные цели:

- разделение бизнес-логики и инфраструктуры;
- минимальная связанность компонентов;
- возможность замены инфраструктурных реализаций;
- тестируемость application logic;
- понятная структура проекта;
- достаточная расширяемость без преждевременного усложнения.

Application layer не должен зависеть от конкретного SDK или конкретной реализации инфраструктурного компонента.

---

## 3. Общая схема системы

```text
┌──────────────────┐
│  Streamlit UI    │
└────────┬─────────┘
         │ HTTP
         ▼
┌──────────────────┐
│     FastAPI      │
└────────┬─────────┘
         │
   ┌─────┴─────┐
   ▼           ▼
┌──────────┐ ┌──────────────┐
│Retrieval │ │ RAG Service  │
│ Service  │ └──────┬───────┘
└────┬─────┘        │
     ▼              ▼
┌──────────┐  ┌──────────────┐
│Embeddings│  │ LLM Provider │
└────┬─────┘  └──────────────┘
     ▼
┌──────────┐
│ ChromaDB │
└──────────┘
```

Отдельный indexing-контур:

```text
Knowledge Base
      ↓
  Indexing
      ↓
  ChromaDB
```

Основной пользовательский поток проходит через:

```text
Streamlit → FastAPI → Application services → Infrastructure
```

---

## 4. Слои приложения

Структура backend:

```text
app/
├── domain/
├── application/
├── infrastructure/
└── api/
```

### 4.1 Domain

`domain` содержит основные модели и абстракции системы.

Domain layer не должен зависеть от конкретных внешних сервисов.

Здесь определяются контракты, необходимые application logic для работы с инфраструктурой.

Примеры:

- query embedding provider;
- retrieval vector store;
- RAG LLM provider;
- domain models.

### 4.2 Application

`application` содержит application services и orchestration.

Основные подсистемы:

```text
app/application/
├── indexing/
├── retrieval/
└── rag/
```

Application layer отвечает за последовательность операций и бизнес-логику сценариев.

Основные сервисы:

- Indexing;
- Retrieval;
- RAG.

Application layer использует абстракции из Domain и не должен напрямую зависеть от конкретных SDK инфраструктуры.

### 4.3 Infrastructure

`infrastructure` содержит конкретные реализации внешних компонентов.

Основные направления:

```text
app/infrastructure/
├── vector_store/
├── embeddings/
└── llm/
```

Infrastructure отвечает за:

- ChromaDB;
- embedding providers;
- LLM provider;
- загрузку документов.

Таким образом, детали работы с внешними системами изолированы от application logic.

### 4.4 API

`api` предоставляет HTTP interface проекта через FastAPI.

Основные endpoints:

- `GET /health`
- `POST /search`
- `POST /chat`

Endpoint `/index` в текущем MVP отсутствует.

Индексация Knowledge Base выполняется отдельным script:

```bash
python scripts/index_knowledge_base.py
```

API layer принимает запросы, передаёт их application services и возвращает структурированные результаты.

API не должен содержать самостоятельную реализацию Retrieval или RAG.

### 4.5 UI

Пользовательский интерфейс реализован на Streamlit.

UI является тонким presentation layer.

Основные обязанности:

- ввод пользовательского вопроса;
- отправка HTTP-запросов в FastAPI;
- отображение ответа;
- отображение источников;
- обработка пользовательских ошибок;
- отображение недоступности backend.

UI не содержит собственной реализации RAG или Retrieval.

---

## 5. Основные компоненты

### 5.1 Indexing

Indexing преобразует документы Knowledge Base в данные, пригодные для semantic Retrieval.

Поток:

```text
Documents
    ↓
Document Loader
    ↓
Text Splitting
    ↓
Embeddings
    ↓
ChromaDB
```

Текущая Knowledge Base использует нормализованный Markdown-формат.

Indexing запускается отдельным script:

```bash
python scripts/index_knowledge_base.py
```

В текущем MVP отдельный API endpoint для запуска indexing не предусмотрен.

### 5.2 Embeddings

Для документов и пользовательских запросов используются embeddings.

Текущая модель:

```text
text-embedding-3-small
```

Embedding provider изолирован через application/domain abstraction.

Это позволяет не связывать application logic с конкретным API provider.

### 5.3 Vector Store

Для хранения embeddings и выполнения semantic similarity search используется ChromaDB.

Используется persistent collection:

```text
ego_biz_wiki
```

Vector store является инфраструктурной деталью и не должен напрямую использоваться UI или domain layer.

### 5.4 Retrieval Service

Retrieval Service отвечает за поиск релевантных фрагментов Knowledge Base.

Основной поток:

```text
User Query
    ↓
Query Embedding
    ↓
ChromaDB Similarity Search
    ↓
Top-K
    ↓
Distance Threshold
    ↓
Retrieved Chunks
```

Текущие параметры MVP:

- Chunk size: 800
- Chunk overlap: 120
- Top-K: 5
- Distance threshold: 1.30

Используется Chroma distance.

Меньшее значение distance означает более близкое векторное соответствие.

Threshold является текущим MVP baseline и может быть изменён только после анализа evaluation results.

### 5.5 RAG Service

RAG Service использует Retrieval results для формирования ответа через LLM.

Поток:

```text
User Query
    ↓
Retrieval Service
    ↓
Relevant Chunks
    ↓
Context
    ↓
LLM
    ↓
Answer + Sources
```

Если Retrieval не возвращает достаточно релевантного контекста, LLM не вызывается.

В этом случае система возвращает deterministic fallback:

> В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.

Источники при fallback:

```text
sources = []
```

Production RAG также использует fallback, если LLM возвращает пустой ответ или сам возвращает точную fallback-фразу.

### 5.6 LLM Provider

Для генерации ответа используется OpenAI-compatible LLM provider.

Текущая конфигурация поддерживает:

- OpenAI API;
- OpenAI-compatible API;
- ProxyAPI через configurable base URL.

Текущая модель:

```text
gpt-4o-mini
```

Provider-specific logic не должна распространяться на application layer.

Конфигурация выполняется через environment variables и application settings.

---

## 6. Основные потоки данных

### 6.1 Indexing Flow

```text
Knowledge Base
    ↓
Document Loader
    ↓
Text Splitter
    ↓
Embedding Provider
    ↓
ChromaDB
```

Результатом является persistent vector index.

### 6.2 Search Flow

```text
User Query
    ↓
FastAPI /search
    ↓
Retrieval Service
    ↓
Embedding Provider
    ↓
ChromaDB
    ↓
Top-K + Threshold
    ↓
Search Results
```

`/search` не вызывает LLM.

Это позволяет использовать endpoint для демонстрации и диагностики Retrieval отдельно от генерации ответа.

### 6.3 Chat Flow

```text
User Query
    ↓
Streamlit UI
    ↓
FastAPI /chat
    ↓
Retrieval Service
    ↓
ChromaDB
    ↓
Relevant Context
    ↓
RAG Service
    ↓
LLM Provider
    ↓
Answer + Sources
    ↓
Streamlit UI
```

---

## 7. API Layer

FastAPI является HTTP entry point backend.

### `/health`

Используется для проверки доступности backend.

Текущий endpoint возвращает:

- `status = ok`
- `service = EgoBiz Wiki`
- `version = 0.1.0`

### `/search`

Возвращает результаты Retrieval без генерации LLM-ответа.

Основные данные результата:

- `chunk_id`
- `document_id`
- `title`
- `source`
- `content`
- `distance`

### `/chat`

Запускает полный RAG pipeline и возвращает:

- `answer`
- `sources`

### Indexing

В текущем MVP endpoint `/index` отсутствует.

Indexing запускается через:

```bash
python scripts/index_knowledge_base.py
```

API layer не реализует собственную retrieval strategy.

---

## 8. UI Layer

Streamlit UI взаимодействует с backend через HTTP.

Адрес backend задаётся через:

```text
STREAMLIT_API_URL
```

UI не знает деталей:

- ChromaDB;
- embeddings;
- chunking;
- retrieval threshold;
- LLM provider.

Эти детали остаются внутри backend.

Такое разделение позволяет изменять backend без необходимости переносить RAG logic в UI.

---

## 9. Dependency Rules

Основные правила зависимостей:

```text
Domain ↑
Application ↑
Infrastructure
API → Application
UI → API
```

Более точно:

- Domain не зависит от Infrastructure;
- Application зависит от Domain abstractions;
- Infrastructure реализует Domain abstractions;
- API использует Application services;
- UI взаимодействует с API;
- UI не использует Infrastructure напрямую.

Главное правило:

конкретная инфраструктурная реализация не должна определять архитектуру application layer.

---

## 10. Configuration and Providers

Конфигурация проекта централизована через application settings.

Основные параметры включают:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `CHAT_MODEL`
- `EMBEDDING_MODEL`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `RETRIEVAL_TOP_K`
- `RETRIEVAL_SCORE_THRESHOLD`
- `STREAMLIT_API_URL`

Provider abstraction позволяет использовать OpenAI-compatible API без изменения application logic.

Замена provider должна выполняться на уровне configuration/infrastructure.

---

## 11. Persistence

ChromaDB используется как persistent vector store.

Индекс строится из документов Knowledge Base и сохраняется между запусками приложения.

Knowledge Base и vector index являются разными сущностями:

```text
Knowledge Base
      ↓
   Indexing
      ↓
  Vector Store
```

Evaluation dataset также является отдельным компонентом и не является частью Knowledge Base.

---

## 12. Testing

Проект использует unit и integration tests.

Тестирование покрывает основные компоненты и пользовательские сценарии:

- indexing;
- Retrieval;
- RAG;
- API;
- UI;
- fallback behavior;
- evaluation logic.

Текущий результат тестов:

- 55 passed
- 1 warning

Команда:

```bash
pytest -q
```

Предупреждение связано с deprecated API в зависимости Starlette/AnyIO и не является ошибкой проектной логики.

---

## 13. Evaluation

Evaluation является отдельным слоем проверки качества.

Структура:

```text
evaluation/
├── dataset.yaml
├── README.md
└── run_evaluation.py
```

Текущий dataset содержит:

```text
38 evaluation cases
```

Evaluation runner использует существующий production RAG pipeline.

Evaluation используется для контролируемого анализа:

- Retrieval quality;
- соответствия ответа ожидаемому поведению;
- source attribution;
- поведения fallback;
- покрытия основных сценариев Knowledge Base.

Текущие baseline metrics:

- Behavior Accuracy: 92.1%
- Expected Source Hit Rate: 100.0%
- Source Attribution Accuracy: 93.3%
- Fallback Accuracy: 100.0%

Evaluation не содержит собственной Retrieval implementation.

Основной принцип:

> Evaluation измеряет существующую систему, а не создаёт альтернативный RAG pipeline.

---

## 14. CI

Для автоматической проверки проекта используется GitHub Actions.

Workflow:

```text
.github/workflows/ci.yml
```

CI запускается:

- при push в `main`;
- при pull_request в `main`.

Используется matrix:

- Python 3.12
- Python 3.13

Основные шаги:

```text
Checkout
    ↓
Setup Python
    ↓
Install test dependencies
    ↓
pytest -q
```

Текущий CI workflow успешно проходит.

CI является частью текущего проекта.

CD и автоматический deployment в текущем MVP не реализованы.

---

## 15. Architectural Constraints

Для MVP сознательно не используются:

- Agentic RAG;
- agents;
- LangGraph;
- hybrid search;
- reranking;
- external web search;
- long-term memory;
- сложная orchestration.

Это не технические запреты на будущее, а текущие архитектурные ограничения MVP.

Любое усложнение должно быть обосновано реальной проблемой и подтверждено результатами Evaluation.

Docker/containerized deployment также не является частью текущей реализации MVP.

---

## 16. Project Structure

Ключевая структура проекта:

```text
ego-biz-wiki/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── evaluation/
│   ├── dataset.yaml
│   ├── README.md
│   └── run_evaluation.py
├── knowledge_base/
├── scripts/
├── tests/
├── ui/
├── docs/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── README.md
├── PROJECT_STATE.md
└── pyproject.toml
```

Dockerfile в текущей версии проекта отсутствует.

---

## 17. Roadmap

Архитектура допускает дальнейшее расширение без изменения базовой структуры.

Возможные направления:

1. Retrieval optimization;
2. дополнительные evaluation scenarios;
3. Document Standardization;
4. поддержка PDF/DOCX/XLSX/HTML/TXT;
5. дополнительные infrastructure providers;
6. containerized deployment при наличии обоснованной необходимости;
7. advanced Retrieval approaches при подтверждённой необходимости;
8. deployment automation / CD.

Потенциальное расширение должно проходить через измерение результата.

Основной принцип:

```text
Measure
   ↓
Identify Problem
   ↓
Change
   ↓
Evaluate
```

---

## 18. Итоговая архитектурная модель

EgoBiz Wiki построен вокруг простой последовательности:

```text
Knowledge Base
      ↓
   Indexing
      ↓
   ChromaDB
      ↓
   Retrieval
      ↓
   Context
      ↓
     RAG
      ↓
     LLM
      ↓
 Answer + Sources
```

Пользовательский доступ:

```text
Streamlit UI → FastAPI → Application services → Infrastructure
```