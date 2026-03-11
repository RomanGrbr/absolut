## Запуск проекта

```docker compose up --build```


## Документация доступна по адресу:

```
http://localhost:8000/api/docs/
```


## Роли пользователей

`admin` - Создавать и редактировать опросы, просматривать статистику.

`respondent` - Проходить опросы.


## Создание опроса

### 1. Создать опрос

```
POST http://localhost:8000/api/surveys/
```

### 2. Добавить вопрос с вариантами ответов

```
POST http://localhost:8000/api/surveys/1/questions/
```

### 3. Просмотреть опрос целиком

```
GET http://localhost:8000/api/surveys/1/
```

Ответ

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


## Прохождение опроса

### 1. Посмотреть список доступных опросов

```
GET http://localhost:8000/api/surveys/
```

### 2. Начать опрос — создать сессию

```
POST http://localhost:8000/api/sessions/
```

### 3. Получить следующий вопрос

```
GET http://localhost:8000/api/surveys/1/next-question/
```

### 4. Ответить на вопрос

```
POST http://localhost:8000/api/answers/
```

### 5. Повторять шаги 3–4 до завершения

Запросы `GET /api/surveys/1/next-question/` и `POST /api/answers/` повторяются для каждого вопроса.

Когда все вопросы отвечены, `GET /api/surveys/1/next-question/` вернёт `204 No Content` — опрос завершён автоматически.

---

## Статистика по опросу

Доступна только администраторам.

```
http://localhost:8000/api/surveys/1/stats/
```
