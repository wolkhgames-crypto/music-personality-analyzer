# 🚀 Инструкция по запуску

## Вариант 1: Локальный запуск (для тестирования)

### Шаг 1: Установите Python
Скачайте Python 3.8+ с https://www.python.org/downloads/
При установке поставьте галочку "Add Python to PATH"

### Шаг 2: Установите зависимости
Откройте командную строку в папке проекта и выполните:
```bash
pip install -r requirements.txt
```

### Шаг 3: Запустите приложение
```bash
python app.py
```

### Шаг 4: Откройте браузер
Перейдите на http://localhost:5000

---

## Вариант 2: Деплой на Railway (рекомендуется)

### Шаг 1: Создайте GitHub репозиторий
1. Зайдите на https://github.com
2. Создайте новый репозиторий (например "music-personality")
3. Загрузите все файлы проекта

### Шаг 2: Подключите к Railway
1. Зайдите на https://railway.app
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш репозиторий
5. Railway автоматически:
   - Определит Python
   - Установит зависимости из requirements.txt
   - Запустит приложение через Procfile

### Шаг 3: Получите URL
После деплоя Railway выдаст публичный URL типа:
`https://music-personality-production.up.railway.app`

---

## Вариант 3: Деплой без GitHub

### Через Railway CLI:
1. Установите Railway CLI: https://docs.railway.app/develop/cli
2. В папке проекта выполните:
```bash
railway login
railway init
railway up
```

---

## Проверка работы

После запуска откройте сайт и:
1. Введите имя, возраст, пол
2. Введите 20 треков (название + исполнитель)
3. Нажмите "Анализировать"
4. Подождите 10-20 секунд
5. Получите результат с типом личности

---

## Что делать если не работает

### Ошибка подключения к БД
Проверьте данные в app.py (строки 9-15):
- host
- port
- database
- user
- password

### Ошибка OpenRouter API
Проверьте API ключ в app.py (строка 18)

### Ошибка "Module not found"
Установите зависимости: `pip install -r requirements.txt`

---

## Файлы проекта

- `app.py` — Backend (Flask + PostgreSQL + OpenRouter)
- `templates/index.html` — Frontend (HTML + CSS + JavaScript)
- `requirements.txt` — Зависимости Python
- `Procfile` — Команда запуска для Railway
- `README.md` — Документация

---

## Контакты

Для конференции: 20 апреля 2026, 8:00 МСК
