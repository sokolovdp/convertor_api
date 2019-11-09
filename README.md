# API конвертации валют
Простой демо веб-сервис на asyncio, который предоставляет API для конвертации валют. Данные можно хранить в Redis или Postgres (для этого требуется перекомпиляция кода, и предварительный запуск программы init_postgres для инициализации базы). 
Код разработан для демо целей и предполагает локальный запуск. 

## To start server
```text
python3 -m converter_server.py
```
host=0.0.0.0 port=8888

## Должны работать следующие локейшены:

- GET localhost:8888/convert?from=RUR&to=USD&amount=42: перевести amount из валюты from в валюту to. Ответ в JSON.

- POST localhost:8888/database?merge=1: залить данные по валютам в хранилище. Если merge == 0, то старые данные инвалидируются. Если merge == 1, то новые данные перетирают старые, но старые все еще акутальны, если не перетерты.

## Json запроса POST:
```json
{ "rates":
	[
	    {
	        "from_curr": "USD",
	        "to_curr": "RUB",
	        "rate": 100.50
	    },
	    {
	        "from_curr": "RUB",
	        "to_curr": "USD",
	        "rate": 0.005
	    },
	     {
	        "from_curr": "YYY",
	        "to_curr": "RUB",
	        "rate": 100.50
	    },
	    {
	        "from_curr": "RUB",
	        "to_curr": "YYY",
	        "rate": 0.005
	    }
	]
}
```



## Json ответа на GET, если нет ошибки (статус=200):
```json
{
    "to_amount": "100500.00"
}
```

## Json ответа на POST, если нет ошибки (статус=200):
```json
{
     "result": "rates updated"
}
```

## Json ответа на GET|POST, если есть ошибка (статус >= 400):
```json
{
    "error": "описание ошибки"
}
```

## Postman тесты

https://www.getpostman.com/collections/9db81bc74495bffb357e
