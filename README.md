## Регистрация пользователей
``` json
curl -X POST -d "username=user1&password=12345&email=user@yandex.ru" http://127.0.0.1:8000/api/users/
```

## Получение токена
``` json
curl -X POST -d "username=user1&password=12345" http://127.0.0.1:8000/api/get_token/
```
<br>
# API методы для пользователей
Каждый метод применяется для текущего пользователя

## Получить список тестов
``` json
curl -H "Authorization:Token 015ef053ff60f8acbaaec3d47967f690e99e99ee" http://127.0.0.1:8000/api/tests/
```

``` json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Elementary Math Test",
      "subject": {
        "id": 1,
        "title": "Math"
      }
    },
    {
      "id": 2,
      "title": "The Second World War",
      "subject": {
        "id": 2,
        "title": "History"
      }
    }
  ]
}
```

#### *Далее, для краткости, будут указаны только http запросы.

## Получить тест по id
``` json
curl -H ... http://127.0.0.1:8000/api/tests/1/
```
``` json
{
  "id": 1,
  "title": "Elementary Math Test",
  "subject": {
    "id": 1,
    "title": "Math"
  }
}
```

## Начать тест
``` json
curl -X POST -d ... http://127.0.0.1:8000/api/tests/1/start_test/
```
### Ошибки
Код ошибки      | detail
----------------|----------------------
400             | Test session is already started


## Получить список вопросов
``` json
curl -H ... http://127.0.0.1:8000/api/tests/1/tasks/
```
``` json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "number": 1,
      "question": "What is result of 2 + 2?",
      "question_type": "txt",
      "possible_answers": [
        {
          "id": 6,
          "text": "2"
        },
        {
          "id": 7,
          "text": "3"
        },
        {
          "id": 8,
          "text": "0"
        },
        {
          "id": 9,
          "text": "4"
        }
      ]
    },
    {
      "id": 2,
      "number": 2,
      "question": "What is result of 5!?",
      "question_type": "txt",
      "possible_answers": [
        {
          "id": 10,
          "text": "120"
        },
        {
          "id": 11,
          "text": "13"
        },
        {
          "id": 12,
          "text": "5"
        },
        {
          "id": 13,
          "text": "720"
        }
      ]
    }
  ]
}
```

### Ошибки
Код ошибки      | detail
----------------|----------------------
400             | Permission denied. There are not started sessions.

## Получить вопрос по id
``` json
curl -H ... http://127.0.0.1:8000/api/tests/1/tasks/1/
```
``` json
{
  "id": 1,
  "number": 1,
  "question": "What is result of 2 + 2?",
  "question_type": "txt",
  "possible_answers": [
    {
      "id": 6,
      "text": "2"
    },
    {
      "id": 7,
      "text": "3"
    },
    {
      "id": 8,
      "text": "0"
    },
    {
      "id": 9,
      "text": "4"
    }
  ]
}
```

Где ***question_type*** это тип вопроса. Тип может принимать 3 значения:
* ***txt*** - Текстовый вопрос
* ***aud*** - Ссылка на аудиовопрос
* ***vid*** - Ссылка на видеовопрос

### Ошибки
Код ошибки      | detail
----------------|----------------------
400             | Permission denied. There are not started sessions.


## Ответить на вопрос
``` json
curl -X POST -d ... http://127.0.0.1:8000/api/tests/1/tasks/2/answer/?var1=10&var2=11
```
Где var1 ...varN - id ответов на вопрос

``` json
{
  "id": 44,
  "user": 3,
  "test_session": 22,
  "task": "2",
  "answers": [
    {
      "id": 10,
      "text": "120"
    },
    {
      "id": 11,
      "text": "13"
    }
  ],
  "answered_datetime": "2016-09-22T20:42:36.567852"
}
```
При этом сессия автоматический закрывается при ответе на последний возможный ответ теста.

### Ошибки
Код ошибки      | detail
----------------|----------------------
400             | There are not started sessions
400             | Invalid answer index
400             | Too many answers
400             | This task is already answered
400             | Not int parameter


## Получить статистику по тесту (время начала и окончания тестовой сессии, количество верных ответов)
``` json
curl -H ... http://127.0.0.1:8000/api/tests/1/stats/
```
``` json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 22,
      "test": 1,
      "user": 3,
      "start_datetime": "2016-09-22T19:45:53.764254",
      "finish_datetime": "2016-09-22T20:47:42.293814",
      "test_stats": {
        "correct_answers": 1,
        "tasks_count": 3
      }
    },
    {
      "id": 23,
      "test": 1,
      "user": 3,
      "start_datetime": "2016-09-22T20:48:09.525663",
      "finish_datetime": null,
      "test_stats": {
        "correct_answers": 1,
        "tasks_count": 3
      }
    }
  ]
}
```
При этом сессия автоматический закрывается при ответе на последний возможный ответ теста.

### Ошибки
Код ошибки      | detail
----------------|----------------------
400             | Not found stats for user #1 and test #2

## Получить статистику для конкретной тестовой сессии
``` json
curl -H ... http://127.0.0.1:8000/api/tests/1/stats/1/
```

## Получить информацию о текущем пользователе
``` json
curl -H ... http://127.0.0.1:8000/api/about_me/
```

<br>
# API методы для администратора
Каждый метод позволяет осуществить как GET, так и POST запрос.
Для каждого метода можно сделать детализированный запрос по индексу элемента, например: 
``` json
curl ... http://127.0.0.1:8000/api/users/1/
```

## Получить список пользователей
``` json
curl ... http://127.0.0.1:8000/api/users/
```
## Получить спсиок вопросов
``` json
curl ... http://127.0.0.1:8000/api/tasks/
```
## Получить спсиок тестов
``` json
curl ... http://127.0.0.1:8000/api/tests/
```
## Получить спсиок тем
``` json
curl ... http://127.0.0.1:8000/api/subjects/
```
## Получить спсиок ответов
``` json
curl ... http://127.0.0.1:8000/api/answers/
```
## Получить спсиок со статистикой для тестовых сессий
``` json
curl ... http://127.0.0.1:8000/api/stats/
```
