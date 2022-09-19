# AsteriskNG Server

Пример серверной части для виджета [AsteriskNG](https://github.com/iqtek/asterisk_ng).

## Установка

```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn asterisk_ng_server:app --host 0.0.0.0 --port 8080
```

