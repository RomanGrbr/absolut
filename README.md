## Запуск проекта

```docker compose up --build```


## Документация

После запуска сервера интерактивная документация доступна по адресу:

```
http://localhost:8000/api/docs/
```

---

## Роли пользователей

`admin` - Создавать и редактировать опросы, просматривать статистику.

`respondent` - Проходить опросы.


## Создание опроса

### 1. Создать опрос

```bash
curl -X POST http://localhost:8000/api/surveys/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Овощи"
  }'
```

```json
{
  "id": 1,
  "title": "Овощи"
}
```

### 2. Добавить вопрос с вариантами ответов

```bash
curl -X POST http://localhost:8000/api/surveys/1/questions/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ты любишь буратту с помидорами?",
    "order": 1,
    "choices": [
      {"text": "Да", "order": 1},
      {"text": "Нет", "order": 2},
      {"text": "У меня непереносимость лактозы", "order": 3}
    ]
  }'
```

```json
{
  "id": 1,
  "text": "Ты любишь буратту с помидорами?",
  "order": 1,
  "choices": [
    {"id": 1, "text": "Да", "order": 1},
    {"id": 2, "text": "Нет", "order": 2},
    {"id": 3, "text": "У меня непереносимость лактозы", "order": 3}
  ]
}
```

### 3. Добавить ещё один вопрос

```bash
curl -X POST http://localhost:8000/api/surveys/1/questions/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ты любишь огурцы?",
    "order": 2,
    "choices": [
      {"text": "Да", "order": 1},
      {"text": "Нет", "order": 2},
      {"text": "Только в коктейлях", "order": 3}
    ]
  }'
```

### 4. Просмотреть опрос целиком

```bash
curl http://localhost:8000/api/surveys/1/ \
  -u admin:password
```

```json
{
  "id": 1,
  "title": "Овощи",
  "author_username": "admin",
  "created_at": "2026-03-10T10:00:00Z",
  "questions": [
    {
      "id": 1,
      "text": "Ты любишь буратту с помидорами?",
      "order": 1,
      "choices": [
        {"id": 1, "text": "Да", "order": 1},
        {"id": 2, "text": "Нет", "order": 2},
        {"id": 3, "text": "У меня непереносимость лактозы", "order": 3}
      ]
    },
    {
      "id": 2,
      "text": "Ты любишь огурцы?",
      "order": 2,
      "choices": [
        {"id": 4, "text": "Да", "order": 1},
        {"id": 5, "text": "Нет", "order": 2},
        {"id": 6, "text": "Только в коктейлях", "order": 3}
      ]
    }
  ]
}
```

---

## Прохождение опроса

### 1. Посмотреть список доступных опросов

```bash
curl http://localhost:8000/api/surveys/ \
  -u user:password
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "title": "Овощи",
      "author_username": "admin",
      "created_at": "2026-03-10T10:00:00Z",
      "questions_count": 2
    }
  ]
}
```

### 2. Начать опрос — создать сессию

```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -u user:password \
  -H "Content-Type: application/json" \
  -d '{"survey": 1}'
```

```json
{
  "id": 1,
  "survey": 1,
  "started_at": "2026-03-110T11:00:00Z",
  "completed_at": null,
  "is_completed": false,
  "duration_seconds": null
}
```

### 3. Получить следующий вопрос

```bash
curl http://localhost:8000/api/surveys/1/next-question/ \
  -u user:password
```

```json
{
  "id": 1,
  "text": "Ты любишь буратту с помидорами?",
  "order": 1,
  "choices": [
    {"id": 1, "text": "Да", "order": 1},
    {"id": 2, "text": "Нет", "order": 2},
    {"id": 3, "text": "У меня непереносимость лактозы", "order": 3}
  ]
}
```

### 4. Ответить на вопрос

```bash
curl -X POST http://localhost:8000/api/answers/ \
  -u user:password \
  -H "Content-Type: application/json" \
  -d '{
    "session": 1,
    "question": 1,
    "choice": 1
  }'
```

```json
{
  "id": 1,
  "session": 1,
  "question": 1,
  "choice": 1,
  "answered_at": "2024-01-15T11:00:30Z"
}
```

### 5. Повторять шаги 3–4 до завершения

Запросы `GET /api/surveys/1/next-question/` и `POST /api/answers/` повторяются для каждого вопроса.

Когда все вопросы отвечены, `GET /api/surveys/1/next-question/` вернёт `204 No Content` — опрос завершён автоматически.

---

## Статистика по опросу

Доступна только администраторам.

```bash
curl http://localhost:8000/api/surveys/1/stats/ \
  -u admin:password
```

```json
{
  "survey_id": 1,
  "total_sessions": 10,
  "completed_sessions": 8,
  "avg_duration_seconds": 124.5,
  "questions": [
    {
      "question_id": 1,
      "question_text": "Ты любишь буратту с помидорами?",
      "answers": [
        {"username": "user1", "choice_id": 1, "choice_text": "Да"},
        {"username": "user2", "choice_id": 3, "choice_text": "У меня непереносимость лактозы"}
      ]
    }
  ]
}
```
