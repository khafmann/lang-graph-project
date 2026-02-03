# Product Agent - AI с MCP интеграцией

## Быстрый старт

### Docker
```bash
docker-compose up --build
```

### Локально
```bash
pip install -r requirements.txt
uvicorn src.api.main:app --port 8000
```

API доступен на http://localhost:8000

## Тестирование

### Автотесты
```bash
pytest tests/ -v
```

### Ручное тестирование API

```bash
# Health check
curl http://localhost:8000/health

# Список всех продуктов
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Покажи все продукты"}'

# Продукты по категории
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Продукты в категории Электроника"}'

# Статистика
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Статистика"}'

# Товар по ID
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Покажи товар ID 1"}'

# Расчёт скидки
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Скидка 15% на товар ID 1"}'
```

### Swagger UI
http://localhost:8000/docs

## Структура

```
src/
├── mcp_server/server.py   # MCP сервер (FastMCP, 4 tools)
├── agent/
│   ├── graph.py           # LangGraph агент
│   ├── mock_llm.py        # Парсер запросов
│   └── tools.py           # Кастомные tools
└── api/main.py            # FastAPI
tests/                     # 27 тестов
```
