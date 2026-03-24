# IK Backend API

Backend на Django + Django REST Framework для разделов:

- Полномочный представитель и заместители
- Документы
- Тендеры и закупки

## Запуск

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

## API

- `GET/POST /api/representatives/`
- `GET/PUT/PATCH/DELETE /api/representatives/<id>/`
- `GET/POST /api/document-categories/`
- `GET/PUT/PATCH/DELETE /api/document-categories/<id>/`
- `GET/POST /api/documents/`
- `GET/PUT/PATCH/DELETE /api/documents/<id>/`
- `GET/POST /api/tenders/`
- `GET/PUT/PATCH/DELETE /api/tenders/<id>/`

## Swagger / OpenAPI

- `GET /api/schema/` - OpenAPI schema
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc

## Язык

Используйте query-параметр:

- `?lang=ru`
- `?lang=en`
- `?lang=ky`

Если язык не передан или передан неверно, backend вернет русский язык.

## Фильтрация документов

```http
GET /api/documents/?lang=ru&category=1
```

## Проверка

```bash
py manage.py test
```
