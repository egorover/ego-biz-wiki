# RAG Pipeline

## Назначение

RAG pipeline — основной механизм EgoBiz Wiki для формирования ответов на вопросы сотрудников на основе корпоративной базы знаний.

Pipeline использует классический подход Retrieval-Augmented Generation:

```text
User Query
    ↓
Retrieval
    ↓
Retrieved Context
    ↓
LLM
    ↓
Answer + Sources
```

Основной принцип MVP:

> Ответ должен формироваться только на основе найденного контекста из корпоративной базы знаний.

Внешние знания и внешние источники не используются.

---

## Основные компоненты

RAG pipeline разделён на application, domain и infrastructure layers.

```text
app/
├── application/
│   └── rag/
│       └── service.py
├── domain/
│   └── rag.py
├── infrastructure/
│   ├── llm/
│   │   └── openai.py
│   └── rag.py
└── api/
    ├── dependencies.py
    ├── routes/
    │   └── chat.py
    └── schemas/
        └── chat.py
```

### Application layer

`RAGService` координирует основной сценарий:

1. Нормализует пользовательский запрос.
2. Выполняет retrieval.
3. Проверяет наличие релевантного контекста.
4. Формирует context для LLM.
5. Получает grounded answer.
6. Формирует список источников.

Application layer не зависит от конкретного LLM provider или vector store.

---

## Retrieval

Для поиска используется существующий `RetrievalService`.

Текущие параметры MVP:

| Parameter         |        Value |
| ----------------- | -----------: |
| `top_k`           |          `5` |
| `score_threshold` |       `1.30` |
| chunk size        | `800` tokens |
| chunk overlap     | `120` tokens |

Для ChromaDB используется distance-based retrieval.

Чем меньше distance, тем выше релевантность найденного фрагмента.

`RETRIEVAL_SCORE_THRESHOLD=1.30` используется как защитный порог:

* релевантные документы проходят retrieval;
* явно нерелевантные результаты отбрасываются;
* при отсутствии результатов LLM не вызывается.

---

## Context Construction

После retrieval найденные chunks преобразуются в единый context.

Каждый источник получает отдельный блок:

```text
[Source 1]
Title: ...
Source: ...
Content:
...

[Source 2]
Title: ...
Source: ...
Content:
...
```

В context передаются:

* название документа;
* путь к источнику;
* содержимое найденного chunk.

Это позволяет LLM использовать конкретные фрагменты корпоративной базы знаний при формировании ответа.

---

## LLM Provider

MVP использует OpenAI-compatible LLM provider.

Реализация находится в:

```text
app/infrastructure/llm/openai.py
```

Provider работает через `langchain_openai.ChatOpenAI`.

Endpoint и API key задаются конфигурацией:

```text
OPENAI_API_KEY
OPENAI_BASE_URL
CHAT_MODEL
```

Поддерживается как OpenAI API, так и совместимый API через ProxyAPI.

Application layer не содержит provider-specific логики.

---

## Grounded Answer

LLM получает два основных элемента:

```text
Question
+
Retrieved Context
```

System prompt явно задаёт ограничения:

* отвечать только на основе предоставленного context;
* не использовать внешние знания;
* не выдумывать факты;
* отвечать на русском языке.

Таким образом, LLM используется как генератор ответа поверх retrieved knowledge, а не как самостоятельный источник корпоративной информации.

---

## Fallback

Если retrieval не возвращает релевантных chunks, RAG service не вызывает LLM.

Возвращается строго определённый fallback:

```text
В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.
```

Тот же fallback применяется, если LLM возвращает пустой ответ.

При fallback список источников пуст:

```json
{
  "answer": "В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.",
  "sources": []
}
```

---

## Sources

Каждый успешный RAG response содержит список использованных документов.

Источник содержит:

```text
document_id
title
source
```

Если несколько retrieved chunks относятся к одному документу, документ отображается только один раз.

Это позволяет UI и API показывать пользователю, на каких документах основан ответ.

---

## API

Основной endpoint RAG pipeline:

```http
POST /chat
```

Request:

```json
{
  "query": "Как оформить отпуск?"
}
```

Successful response:

```json
{
  "answer": "...",
  "sources": [
    {
      "document_id": "...",
      "title": "Политика отпусков",
      "source": "..."
    }
  ]
}
```

Если релевантной информации нет:

```json
{
  "answer": "В базе знаний не найдено достаточно информации для достоверного ответа на этот вопрос.",
  "sources": []
}
```

---

## Dependency Injection

RAG service создаётся через infrastructure factory:

```text
build_rag_service()
```

Factory собирает:

```text
Embedding Provider
       ↓
Vector Store
       ↓
Retrieval Service
       ↓
LLM Provider
       ↓
RAG Service
```

FastAPI получает готовый `RAGService` через dependency:

```text
get_rag_service()
```

Application logic при этом остаётся независимой от способа создания infrastructure components.

---

## Testing

RAG pipeline покрывается unit и integration tests.

Проверяются:

* успешный ответ на основе retrieved context;
* fallback при отсутствии результатов;
* обработка пустого ответа LLM;
* построение context;
* формирование sources;
* LLM provider;
* RAG factory;
* `/chat` endpoint;
* создание FastAPI application.

Дополнительно выполнена реальная end-to-end проверка.

Положительный сценарий:

```text
Как оформить отпуск?
```

возвращает содержательный ответ и источники.

Нерелевантный запрос:

```text
Как заказать домик на Марсе?
```

возвращает fallback без источников.

---

## MVP Limitations

В текущем MVP намеренно не используются:

* Agentic RAG;
* AI agents;
* LangGraph;
* hybrid search;
* reranking;
* external web search;
* long-term conversation memory;
* сложная multi-step orchestration.

Это сознательное архитектурное решение проекта:

> SIMPLE, COMPLETE & WORKING MVP > COMPLEX, UNSTABLE PRODUCT

Дополнительные механизмы могут быть рассмотрены в Roadmap после стабилизации базового RAG pipeline.
