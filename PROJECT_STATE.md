# PROJECT STATE — EgoBiz Wiki

## 1. Основная информация

* **Project:** EgoBiz Wiki
* **Repository:** `ego-biz-wiki`
* **GitHub:** `https://github.com/egorover/ego-biz-wiki`
* **Author:** Александр Егоров / egorover
* **Project type:** Выпускной проект курса
* **Product type:** AI Business Knowledge Assistant
* **Russian:** ИИ-ассистент по корпоративной базе знаний
* **Local path:** `C:\Dev\oss\ego-biz-wiki`
* **Current development stage:** Commit #08 — Formal Evaluation Dataset — Completed

Демонстрационная компания: **EgoTech Solutions**

Назначение продукта: отвечать на вопросы сотрудников на основе контролируемой корпоративной базы знаний с использованием RAG.

---

## 2. Главный принцип проекта

**SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

Сначала создаётся простой, самодостаточный и стабильно работающий MVP.

Дополнительная функциональность, усложнение архитектуры и advanced-подходы переносятся в Roadmap и добавляются только после проверки необходимости.

---

## 3. Языковые правила

Основной язык проекта и документации — русский.

Английский используется там, где это технически необходимо или соответствует принятому техническому стандарту:

* имена файлов;
* имена директорий;
* Python identifiers;
* API endpoints;
* названия библиотек;
* названия технологий;
* технические термины;
* Git commit messages.

Пользовательская документация, пояснения, UI и ответы AI должны быть преимущественно на русском языке.

---

## 4. Методология разработки

Разработка выполняется поэтапно.

Основное правило:

**Один чат = один завершённый Git commit.**

Каждый commit должен:

1. решать одну конкретную задачу;
2. быть проверен;
3. иметь обновлённую документацию;
4. быть зафиксирован в Git;
5. быть отправлен в GitHub;
6. иметь проверенное состояние рабочего дерева.

После завершения commit дальнейшая разработка в текущем чате не продолжается.

Перед переходом к следующему commit создаётся backup и подготавливается Transfer Prompt.

---

## 5. Текущее состояние проекта

Commit #08 завершает этап создания формальной базы для оценки качества RAG.

На текущем этапе проект имеет:

* контролируемую корпоративную Knowledge Base;
* pipeline индексации документов;
* persistent ChromaDB index;
* семантический Retrieval;
* distance threshold;
* RAG pipeline с LLM;
* deterministic fallback при отсутствии достаточного контекста;
* API `/health`;
* API `/search`;
* API `/chat`;
* Streamlit UI;
* формальный evaluation dataset;
* документацию по основным подсистемам;
* unit и integration tests.

Основная функциональная цепочка:

```text
Knowledge Base
      ↓
   Indexing
      ↓
   Retrieval
    ↙     ↘
/search   /chat
   ↓        ↓
 Chunks    RAG
             ↓
       Answer + Sources
```

Evaluation используется как отдельный слой проверки качества и не изменяет основной RAG pipeline.

---

## 6. Архитектура и ключевые решения

Проект использует упрощённый вариант Clean Architecture с разделением ответственности:

```text
app/
├── domain/
├── application/
├── infrastructure/
└── api/

ui/
```

Основные слои:

* **Domain** — бизнес-модели и абстракции;
* **Application** — orchestration и application services;
* **Infrastructure** — ChromaDB, embeddings, LLM и загрузка документов;
* **API** — FastAPI endpoints;
* **UI** — Streamlit presentation layer.

Application layer не должен зависеть от конкретной реализации provider.

Для внешних компонентов используются абстракции/Protocols, позволяющие изолировать application logic от конкретных SDK.

Streamlit является тонким UI-слоем и взаимодействует с backend через HTTP. RAG-логика в UI не дублируется.

Не следует создавать второй механизм Retrieval для отдельных API или evaluation-задач.

---

## 7. RAG и Retrieval

### Retrieval

Retrieval выполняет:

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

Текущие параметры:

```text
chunk_size = 800
chunk_overlap = 120

embedding model = text-embedding-3-small

RETRIEVAL_TOP_K = 5
RETRIEVAL_SCORE_THRESHOLD = 1.30
```

Используется Chroma `distance`. Меньшее значение означает более близкое векторное соответствие.

Threshold является текущим MVP baseline. Он не считается окончательно оптимальным и должен оцениваться на формальном evaluation dataset.

### RAG

Основная цепочка `/chat`:

```text
User Query
    ↓
RetrievalService
    ↓
Relevant Chunks
    ↓
RAGService
    ↓
OpenAI-compatible LLM
    ↓
Answer + Sources
```

Если после Retrieval и threshold filtering релевантных фрагментов нет, LLM не вызывается.

Используется точный fallback:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

При fallback:

```text
sources = []
```

Текущая реализация намеренно не включает:

* Agentic RAG;
* agents;
* LangGraph;
* hybrid search;
* reranking;
* external web search;
* long-term memory;
* сложную orchestration.

---

## 8. API и UI

### API

Реализованы следующие endpoints:

```text
GET  /health
POST /index
POST /search
POST /chat
```

### `/health`

Проверяет доступность и работоспособность backend.

### `/index`

Запускает indexing pipeline для Knowledge Base и обновления persistent ChromaDB index.

### `/search`

Выполняет Retrieval без вызова LLM.

Назначение:

* демонстрация Retrieval отдельно от RAG;
* отладка;
* проверка найденных chunks;
* подготовка данных для оценки качества.

Результат содержит информацию о найденных фрагментах, включая:

```text
chunk_id
document_id
title
source
content
distance
```

### `/chat`

Выполняет полный RAG pipeline и возвращает:

```text
answer
sources
```

### Streamlit UI

UI реализован как отдельный тонкий слой.

Основные свойства:

* отправляет запросы в FastAPI;
* отображает ответ и источники;
* валидирует пустой запрос на стороне UI;
* обрабатывает недоступность backend;
* не содержит собственной RAG-логики.

Адрес backend передаётся через:

```text
STREAMLIT_API_URL
```

---

## 9. Knowledge Base

Демонстрационная база знаний принадлежит компании **EgoTech Solutions**.

Текущий формат — нормализованные Markdown-документы с единообразной структурой.

В Knowledge Base:

```text
23 Markdown documents
manifest.yaml
```

Основные категории:

* `customer_operations`
* `faq`
* `hr`
* `it`
* `operations`
* `security`

Документы описываются через `manifest.yaml`.

Для chunks сохраняются основные метаданные документа:

```text
document_id
title
path
source
category
subcategory
updated_at
```

Нормализованный формат документов является сознательным решением MVP и представляет собой **наш идеальный документооборот**.

Это не утверждение о том, что реальные корпоративные документы всегда имеют такую структуру.

Автоматическая стандартизация разнородных документов является отдельной будущей возможностью Roadmap.

---

## 10. Evaluation

Commit #08 добавляет формальный evaluation dataset для систематической оценки качества RAG.

Основные файлы:

```text
evaluation/
├── dataset.yaml
└── README.md
```

Текущий dataset:

* **38 evaluation cases**;
* уникальные идентификаторы кейсов;
* покрытие существующей Knowledge Base;
* ожидаемые результаты и ссылки на соответствующие документы используются как основа для последующей оценки Retrieval/RAG.

`evaluation/dataset.yaml` является машинно-читаемым источником evaluation cases.

`evaluation/README.md` описывает назначение, структуру и правила работы с dataset.

Важно:

**Evaluation dataset не является второй Knowledge Base.**

Он используется исключительно для контролируемой проверки поведения существующего RAG pipeline.

Commit #08 создаёт формальную основу для измерения качества. Оптимизация Retrieval не выполняется автоматически только из-за появления dataset.

---

## 11. Тестирование и верификация

На текущем состоянии проекта:

```text
45 passed
1 warning
```

Команда:

```powershell
pytest -q
```

Результат:

```text
45 passed, 1 warning
```

Warning относится к внешней зависимости Starlette/AnyIO и имеет характер `DeprecationWarning`.

Это не является ошибкой проектной логики.

Кроме автоматических тестов, для основных пользовательских сценариев используются ручные smoke-проверки.

### Релевантный запрос

Пример:

```text
Как оформить отпуск?
```

Ожидается:

* релевантный контекст;
* grounded answer;
* корректные источники.

### Нерелевантный запрос

Пример:

```text
Как заказать домик на Марсе?
```

При текущем threshold ожидается отсутствие достаточного Retrieval context и срабатывание deterministic fallback без вызова LLM.

### UI

Проверены:

* пустой запрос;
* успешный запрос;
* отображение результата;
* обработка недоступного backend.

---

## 12. Структура проекта

Ключевая структура:

```text
ego-biz-wiki/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── evaluation/
│   ├── dataset.yaml
│   └── README.md
├── knowledge_base/
├── scripts/
├── tests/
├── ui/
├── docs/
├── .env.example
├── Dockerfile
├── README.md
├── PROJECT_STATE.md
└── pyproject.toml
```

Ключевые подсистемы:

```text
app/application/indexing/
app/application/retrieval/
app/application/rag/
app/infrastructure/vector_store/
app/infrastructure/embeddings/
app/infrastructure/llm/
app/api/
ui/
evaluation/
```

---

## 13. История commits

| Commit | Назначение                | Статус    |
| ------ | ------------------------- | --------- |
| #01    | Project Foundation        | Completed |
| #02    | Knowledge Base            | Completed |
| #03    | Indexing                  | Completed |
| #04    | Retrieval                 | Completed |
| #05    | RAG Pipeline              | Completed |
| #06    | API Search                | Completed |
| #07    | Streamlit UI              | Completed |
| #08    | Formal Evaluation Dataset | Completed |

Основная история разработки соответствует последовательному расширению одного MVP без создания параллельных архитектурных решений.

---

## 14. Известные ограничения

Текущий проект является демонстрационным MVP и не позиционируется как полноценная production enterprise-платформа.

Текущие ограничения:

* контролируемая локальная Knowledge Base;
* основной документный формат MVP — Markdown;
* Retrieval основан на vector similarity search;
* используется фиксированный MVP `top-k`;
* threshold пока является baseline;
* нет hybrid search;
* нет reranking;
* нет Agentic RAG;
* нет external web search;
* нет long-term conversation memory;
* нет автоматической стандартизации произвольных форматов документов;
* evaluation dataset предназначен для MVP-оценки и может расширяться.

Любое изменение Retrieval должно быть обосновано результатами evaluation, а не только предположением о возможном улучшении.

---

## 15. Roadmap

### Ближайшее направление

Анализ результатов формальной оценки и проверка качества текущего Retrieval baseline.

### Следующие возможные направления

1. Анализ evaluation results.
2. Проверка необходимости изменения `top-k` и `RETRIEVAL_SCORE_THRESHOLD`.
3. Итеративное улучшение Retrieval только при наличии подтверждённой проблемы.
4. Document Standardization для разнородных форматов:

   * PDF;
   * DOCX;
   * XLSX;
   * HTML;
   * TXT;
   * другие форматы.

Advanced-подходы не добавляются без подтверждённой необходимости.

---

## 16. Следующий шаг

**Следующий этап: анализ результатов Evaluation.**

Перед изменением Retrieval необходимо:

1. запустить формальную оценку на текущем baseline;
2. зафиксировать результаты;
3. определить обнаруженные ошибки;
4. классифицировать причины ошибок;
5. только после этого принять решение о необходимости изменений.

Если текущие метрики показывают достаточное качество для MVP, Retrieval не усложняется.

---

## 17. Git state

Последний опубликованный commit перед фиксацией Commit #08:

```text
db49c25 feat: add Streamlit UI
```

Текущая ветка:

```text
main
```

Remote:

```text
origin
https://github.com/egorover/ego-biz-wiki.git
```

На момент подготовки Commit #08:

```text
HEAD -> main
origin/main -> main
```

Изменения Commit #08:

```text
evaluation/README.md
evaluation/dataset.yaml
PROJECT_STATE.md
```

Состояние после подготовки документа должно быть проверено командами:

```powershell
git diff --check
pytest -q
git status
```

После успешной проверки изменения Commit #08 фиксируются одним Git commit и отправляются в `origin/main`.

После push необходимо убедиться, что:

```text
HEAD == origin/main
working tree clean
```

После завершения Commit #08 создаётся backup и подготавливается Transfer Prompt для следующего этапа.
