# PROJECT STATE — EgoBiz Wiki

## 1. Основная информация

- **Project:** EgoBiz Wiki
- **Repository:** ego-biz-wiki
- **GitHub:** https://github.com/egorover/ego-biz-wiki
- **Author:** Александр Егоров / egorover
- **Project type:** Выпускной проект курса
- **Product type:** AI Business Knowledge Assistant
- **Russian:** ИИ-ассистент по корпоративной базе знаний
- **Local path:** C:\Dev\oss\ego-biz-wiki
- **Current development stage:** Commit #09 — Post-MVP Evaluation — Completed

Демонстрационная компания: **EgoTech Solutions**

Назначение продукта: отвечать на вопросы сотрудников на основе контролируемой корпоративной базы знаний с использованием RAG.

---

## 2. Главный принцип проекта

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

Сначала создаётся простой, самодостаточный и стабильно работающий MVP.

Дополнительная функциональность, усложнение архитектуры и advanced-подходы переносятся в Roadmap и добавляются только после проверки необходимости.

---

## 3. Языковые правила

Основной язык проекта и документации — русский.

Английский используется там, где это технически необходимо или соответствует принятому техническому стандарту:

- имена файлов;
- имена директорий;
- Python identifiers;
- API endpoints;
- названия библиотек;
- названия технологий;
- технические термины;
- Git commit messages.

Пользовательская документация, пояснения, UI и ответы AI должны быть преимущественно на русском языке.

---

## 4. Методология разработки

Разработка выполняется поэтапно.

Основное правило:

> **Один чат = один завершённый Git commit.**

Каждый технический commit должен:

1. решать одну конкретную задачу;
2. быть проверен;
3. иметь обновлённую документацию, если это необходимо;
4. быть зафиксирован в Git;
5. быть отправлен в GitHub;
6. иметь проверенное состояние рабочего дерева.

После завершения технического commit дальнейшая разработка в текущем чате не продолжается.

Перед переходом к следующему техническому этапу создаётся backup и подготавливается Transfer Prompt.

---

## 5. Текущее состояние проекта

Commit #09 завершает этап первичной формальной оценки качества текущего RAG baseline.

На текущем этапе проект имеет:

- контролируемую корпоративную Knowledge Base;
- pipeline индексации документов;
- persistent ChromaDB index;
- семантический Retrieval;
- distance threshold;
- RAG pipeline c LLM;
- deterministic fallback при отсутствии достаточного контекста;
- API `/health`;
- API `/search`;
- API `/chat`;
- Streamlit UI;
- отображение источников;
- формальный evaluation dataset;
- автоматизированный evaluation runner;
- unit и integration tests;
- документацию по основным подсистемам;
- GitHub Actions CI.

Основная функциональная цепочка:

```text
Knowledge Base
      ↓
   Indexing
      ↓
   Retrieval
   /search  /chat
      ↓
   Chunks  RAG
      ↓
 Answer + Sources
```

Evaluation является отдельным слоем проверки качества и использует существующий RAG pipeline. Он не создаёт второй механизм Retrieval или отдельную реализацию RAG.

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

- **Domain** — бизнес-модели и абстракции;
- **Application** — orchestration и application services;
- **Infrastructure** — ChromaDB, embeddings, LLM и загрузка документов;
- **API** — FastAPI endpoints;
- **UI** — Streamlit presentation layer.

Application layer не должен зависеть от конкретной реализации provider.

Для внешних компонентов используются абстракции/Protocols, позволяющие изолировать application logic от конкретных SDK.

Streamlit является тонким UI-слоем и взаимодействует с backend через HTTP. RAG-логика в UI не дублируется.

Evaluation использует тот же RAG pipeline, который применяется основным `/chat` сценарием. Не создаётся отдельный retrieval-механизм только для evaluation.

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

- `chunk_size = 800`
- `chunk_overlap = 120`
- `embedding model = text-embedding-3-small`
- `RETRIEVAL_TOP_K = 5`
- `RETRIEVAL_SCORE_THRESHOLD = 1.30`

Используется Chroma distance. Меньшее значение означает более близкое векторное соответствие.

Threshold является текущим MVP baseline. Он не считается окончательно оптимальным и оценивается на формальном evaluation dataset.

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

Если после Retrieval и threshold filtering релевантных фрагментов нет, LLM не вызывается. Используется точный fallback:

> В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.

При deterministic fallback: `sources = []`

Текущий RAG pipeline также использует fallback, если LLM возвращает пустой ответ или сам возвращает точную fallback-фразу.

Текущий prompt LLM явно требует использовать предоставленный контекст, если он содержит прямой ответ, и применять fallback только при недостатке информации.

Текущая реализация намеренно не включает:

- Agentic RAG;
- agents;
- LangGraph;
- hybrid search;
- reranking;
- external web search;
- long-term memory;
- сложную orchestration.

---

## 8. API и UI

### API

Реализованы следующие endpoints:

- `GET /health`
- `POST /search`
- `POST /chat`

Endpoint `/index` не реализован.

Индексация Knowledge Base выполняется отдельным script:

```bash
python scripts/index_knowledge_base.py
```

#### `/health`

Проверяет доступность и работоспособность backend.

Текущий ответ содержит:

- `status = ok`
- `service = EgoBiz Wiki`
- `version = 0.1.0`

#### `/search`

Выполняет Retrieval без вызова LLM.

Назначение:

- демонстрация Retrieval отдельно от RAG;
- отладка;
- проверка найденных chunks;
- подготовка данных для оценки качества.

Результат содержит информацию о найденных фрагментах, включая:

- `chunk_id`
- `document_id`
- `title`
- `source`
- `content`
- `distance`

#### `/chat`

Выполняет полный RAG pipeline и возвращает:

- `answer`
- `sources`

### Streamlit UI

UI реализован как отдельный тонкий слой.

Основные свойства:

- отправляет запросы в FastAPI;
- отображает ответ и источники;
- валидирует пустой запрос на стороне UI;
- обрабатывает недоступность backend;
- не содержит собственной RAG-логики.

Адрес backend передаётся через:

```text
STREAMLIT_API_URL
```

---

## 9. Knowledge Base

Демонстрационная база знаний принадлежит компании EgoTech Solutions.

Текущий формат — нормализованные Markdown-документы с единообразной структурой.

В Knowledge Base:

- 23 Markdown documents
- `manifest.yaml`

Основные категории:

- `customer_operations`
- `faq`
- `hr`
- `it`
- `operations`
- `security`

Документы описываются через `manifest.yaml`.

Для chunks сохраняются основные метаданные документа:

- `document_id`
- `title`
- `path`
- `source`
- `category`
- `subcategory`
- `updated_at`

Нормализованный формат документов является сознательным решением MVP и представляет собой наш идеальный документооборот.

Это не утверждение о том, что реальные корпоративные документы всегда имеют такую структуру.

Автоматическая стандартизация разнородных документов является отдельной будущей возможностью Roadmap.

---

## 10. Evaluation

Commit #09 добавляет не только формальный evaluation dataset, но и автоматизированный запуск оценки на текущем RAG pipeline.

Основные файлы:

```text
evaluation/
├── dataset.yaml
├── README.md
└── run_evaluation.py
```

Текущий dataset:

- 38 evaluation cases;
- уникальные идентификаторы `eval-001` — `eval-038`;
- контролируемое покрытие Knowledge Base;
- ожидаемые результаты;
- ожидаемые источники для source-based evaluation.

Категории:

- `relevant` — 14 cases;
- `cross_category` — 8 cases;
- `typical_user` — 4 cases;
- `source_attribution` — 4 cases;
- `out_of_kb` — 5 cases;
- `ambiguous` — 3 cases.

Используются следующие метрики:

1. Behavior Accuracy
2. Expected Source Hit Rate
3. Source Attribution Accuracy
4. Fallback Accuracy

Для метрик, связанных с expected sources, используются 30 cases, содержащих `expected_sources`.

Фактический результат текущего baseline:

- Cases: 38
- Source cases: 30
- Behavior Accuracy: 92.1%
- Expected Source Hit Rate: 100.0%
- Source Attribution Accuracy: 93.3%
- Fallback Accuracy: 100.0%

Evaluation runner использует существующий RAG pipeline, а не дублирует его логику.

`expected_topics` не оцениваются простым string containment, поскольку такой подход не позволяет надёжно определить семантическую корректность ответа.

Для fallback evaluation используется проверка наличия точной fallback-фразы в ответе. Это позволяет корректно учитывать случаи, когда модель дополнительно объясняет отсутствие информации.

Evaluation не использует LLM-as-a-Judge или специализированные evaluation frameworks.

---

## 11. Результаты и выявленные ограничения Evaluation

Текущая оценка показывает, что базовый RAG pipeline корректно проходит основную часть контролируемых сценариев, но выявляет отдельные ограничения.

### Retrieval limitations

**eval-017:**

Один из ожидаемых документов не попадает в текущий Top-K при заданных параметрах Retrieval.

**eval-023:**

Один из ожидаемых документов также не попадает в текущий Top-K.

Эти случаи относятся к ограничениям текущего vector retrieval baseline.

### Ambiguous queries

**eval-036, eval-037, eval-038:**

Для этих кейсов ожидалось explicit clarification, однако текущий MVP возвращает answer.

Это отражает отсутствие отдельного механизма управления неоднозначными запросами.

### Fallback evaluation

**eval-035** первоначально показал необходимость уточнения логики evaluation classifier.

Ответ содержал fallback-фразу вместе с пояснением и нерелевантными источниками. Evaluation classifier был скорректирован так, чтобы наличие точной fallback-фразы классифицировалось как fallback.

Это изменение относится к evaluation logic и не изменяет production RAG contract.

### Принцип интерпретации результатов

Цель Evaluation не заключается в искусственном достижении 100% любой ценой.

Выявленные ограничения фиксируются как baseline limitations.

Усложнение Retrieval или добавление новых механизмов должно рассматриваться только при наличии подтверждённой необходимости.

В частности, текущие результаты сами по себе не являются основанием для автоматического добавления:

- hybrid search;
- reranking;
- query expansion;
- Agentic RAG;
- отдельного clarification engine.

Главный критерий:

> **Сначала измерить проблему — затем усложнять систему.**

---

## 12. Тестирование и верификация

Текущее состояние автоматических тестов:

- 55 passed
- 1 warning

Команда:

```bash
pytest -q
```

Результат:

```text
55 passed, 1 warning
```

Evaluation-specific tests:

- 8 passed

Warning относится к внешней зависимости Starlette/AnyIO:

```text
DeprecationWarning
```

и не связан с проектной логикой.

Кроме автоматических тестов, для основных пользовательских сценариев используются ручные smoke-проверки.

### Релевантный запрос

Пример:

> Как оформить отпуск?

Ожидается:

- релевантный контекст;
- grounded answer;
- корректные источники.

### Нерелевантный запрос

Пример:

> Как заказать домик на Марсе?

При текущем threshold ожидается отсутствие достаточного Retrieval context и срабатывание deterministic fallback без вызова LLM.

### UI

Проверены:

- пустой запрос;
- успешный запрос;
- отображение результата;
- обработка недоступного backend.

---

## 13. Ключевая структура

```text
ego-biz-wiki/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
│
├── evaluation/
│   ├── dataset.yaml
│   ├── README.md
│   └── run_evaluation.py
│
├── knowledge_base/
│   ├── customer_operations/
│   ├── faq/
│   ├── hr/
│   ├── it/
│   ├── operations/
│   ├── security/
│   └── manifest.yaml
│
├── scripts/
│   └── index_knowledge_base.py
│
├── tests/
│   ├── integration/
│   └── unit/
│
├── ui/
│   └── streamlit_app.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── EgoBiz_Wiki.bat
├── PROJECT_STATE.md
└── pyproject.toml
```

Ключевые подсистемы:

- `app/application/indexing/`
- `app/application/retrieval/`
- `app/application/rag/`
- `app/infrastructure/vector_store/`
- `app/infrastructure/embeddings/`
- `app/infrastructure/llm/`
- `app/api/`
- `ui/`
- `evaluation/`

Dockerfile в текущей версии проекта отсутствует.

---

## 14. История commits

| Commit | Назначение | Статус |
|--------|------------|--------|
| #01 | Project Foundation | Complete |
| #02 | Knowledge Base | Complete |
| #03 | Indexing | Complete |
| #04 | Retrieval | Complete |
| #05 | RAG Pipeline | Complete |
| #06 | API Search | Complete |
| #07 | Streamlit UI | Complete |
| #08 | Formal Evaluation Dataset | Complete |
| #09 | Post-MVP Evaluation | Complete |

Основная история разработки соответствует последовательному расширению одного MVP без создания параллельных архитектурных решений.

После Commit #09 был выполнен отдельный технический CI commit:

```text
dc6d7a6 ci: add GitHub Actions test workflow
```

Этот commit не является новым numbered functional commit.

Документальная синхронизация после Commit #09 не является новым техническим этапом и не получает номер #10.

---

## 15. CI / CD

GitHub Actions CI реализован в:

```text
.github/workflows/ci.yml
```

CI запускается:

- при push в `main`;
- при pull_request в `main`.

Используется matrix для:

- Python 3.12
- Python 3.13

Основные шаги CI:

1. checkout repository;
2. setup Python;
3. установка test dependencies;
4. запуск `pytest -q`.

Текущий CI workflow успешно проходит.

**CI реализован.**

**CD не реализован.**

Автоматический deployment в текущий MVP не входит.

---

## 16. Известные ограничения

Текущий проект является демонстрационным MVP и не позиционируется как полноценная production enterprise-платформа.

Текущие ограничения:

- контролируемая локальная Knowledge Base;
- основной документный формат MVP — Markdown;
- Retrieval основан на vector similarity search;
- используется фиксированный MVP top-k;
- threshold является baseline;
- два evaluation cases показывают ограничения текущего Top-K retrieval;
- ambiguous cases не имеют отдельного clarification behavior;
- нет hybrid search;
- нет reranking;
- нет Agentic RAG;
- нет external web search;
- нет long-term conversation memory;
- нет автоматической стандартизации произвольных форматов документов;
- evaluation dataset предназначен для MVP-оценки и может расширяться;
- Docker/containerized deployment не реализован;
- CD/deployment automation не реализован.

Любое изменение Retrieval должно быть обосновано результатами evaluation, а не только предположением о возможном улучшении.

---

## 17. Roadmap

### Ближайшее направление

Анализ результатов формальной оценки и определение того, требуют ли выявленные ограничения изменения текущего MVP baseline.

### Возможные дальнейшие направления

- анализ отдельных Retrieval failures;
- проверка необходимости изменения top-k и `RETRIEVAL_SCORE_THRESHOLD`;
- повторное измерение после обоснованных изменений;
- улучшение обработки ambiguous queries, если это потребуется для MVP;
- Document Standardization для разнородных форматов:
  - PDF;
  - DOCX;
  - XLSX;
  - HTML;
  - TXT;
  - другие форматы;
- containerized deployment, если он будет обоснован требованиями курса или дальнейшего использования;
- deployment automation / CD как отдельный будущий этап.

Advanced-подходы не добавляются без подтверждённой необходимости.

---

## 18. Следующий технический этап

Следующий технический этап ещё не выбран автоматически.

После завершения документальной синхронизации необходимо отдельно проанализировать результаты Evaluation и принять решение:

- оставить текущий Retrieval baseline без изменений;
- либо выполнить ограниченное, обоснованное улучшение.

При принятии решения необходимо руководствоваться главным принципом проекта:

> **SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT**

Исторический отчётный этап является отдельной задачей документации и не изменяет техническую нумерацию commits.

---

## 19. Git state

Последний нумерованный функциональный commit:

```text
ba6d3ce feat: add post-mvp evaluation
```

Это **Commit #09 — Post-MVP Evaluation**.

Последний Git commit:

```text
dc6d7a6 ci: add GitHub Actions test workflow
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

После последнего CI commit:

```text
HEAD -> main
origin/main -> main
working tree clean
```

Commit #09 содержит:

- `app/infrastructure/llm/openai.py`
- `evaluation/run_evaluation.py`
- `tests/test_evaluation.py`

CI commit содержит:

- `.github/workflows/ci.yml`

Временные `.bak` файлы, использовавшиеся во время разработки evaluation, были удалены до Commit #09.

Текущая документальная синхронизация должна изменить только документацию:

- `README.md`
- `PROJECT_STATE.md`
- `evaluation/README.md`

Эти изменения могут быть зафиксированы отдельным Git commit без порядкового номера.

После документальной синхронизации необходимо проверить:

```bash
git diff --check
pytest -q
git status
git diff
```

После успешной проверки документация фиксируется отдельным Git commit и отправляется в `origin/main`.

После push необходимо убедиться, что:

- `HEAD == origin/main`
- working tree clean

После этого техническая история проекта остаётся завершённой на Commit #09, а `dc6d7a6` рассматривается как отдельный CI commit без изменения numbered history.
