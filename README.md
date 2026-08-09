# Эталонный бот-консультант (пример для практики)

> 📖 Красиво смотреть: `Cmd+Shift+V` (Windows: `Ctrl+Shift+V`).
> 🇬🇧 English version below ⬇️

Это **готовый пример** того, что нужно собрать в задании `PRACTICE.md` — бот-
администратор барбершопа «Бритва». В нём собраны вместе сразу несколько паттернов.
Можно запустить, поговорить, посмотреть код — и сделать **своё**, по своей нише.

## Какие паттерны внутри (и где)

| Паттерн | Где в коде | Что делает |
|---|---|---|
| **RAG (база знаний)** | `knowledge.txt` + системный промпт | бот отвечает только по фактам барбершопа |
| **Router** | функция `classify()` | определяет тип вопроса: цена / запись / общее |
| **Tool Calling** | функция `record_lead()` | записывает клиента (имитация CRM) |
| **Structured Output** | функция `extract_booking()` | вытаскивает имя+услугу из сообщения в JSON |
| **Memory** | история диалога в `chat()` | бот помнит разговор |
| **Judge** | функция `judge()` (опционально) | проверяет ответ перед показом |
| **Gradio** | `.launch()` в конце | живой чат в браузере |

## Запуск

> 📁 `~/Downloads/foundations-practice` ниже — это ПРИМЕР пути. У тебя папка
> проекта может лежать в другом месте и называться иначе. Замени путь на свой:
> проще всего написать в терминале `cd ` (с пробелом) и перетащить туда папку
> проекта мышкой из Finder — путь подставится сам.

```bash
cd ~/Downloads/foundations-practice   # ← впиши СВОЙ путь к папке проекта
pip install -r requirements.txt
python bot.py
```
Откроется чат в браузере. По умолчанию — бесплатный локальный Ollama
(нужны установленное приложение Ollama и модель: `ollama pull llama3.2`,
а лучше `qwen2.5` для русского).

## Как сделать своё

1. Замени `knowledge.txt` на факты своей ниши.
2. Поправь роли/категории под себя (в `classify()` и системном промпте).
3. По желанию включи проверку ответа: в коде `USE_JUDGE = True`.

Это и есть задание `PRACTICE.md` — только нишу и детали придумываешь сам.

---
---

# 🇬🇧 English

# A reference consultant bot (example for the practice)

> 📖 View it nicely: `Cmd+Shift+V` (Windows: `Ctrl+Shift+V`).

This is a **ready-made example** of what you need to build in the `PRACTICE.md`
assignment — a receptionist bot for the 'Britva' barbershop. It brings several
patterns together at once. You can run it, chat, look at the code — and make
**your own**, for your own niche.

## Which patterns are inside (and where)

| Pattern | Where in the code | What it does |
|---|---|---|
| **RAG (knowledge base)** | `knowledge.txt` + system prompt | the bot answers only from the barbershop's facts |
| **Router** | the `classify()` function | figures out the question type: price / booking / general |
| **Tool Calling** | the `record_lead()` function | books a client (CRM simulation) |
| **Structured Output** | the `extract_booking()` function | pulls name+service from the message into JSON |
| **Memory** | the dialogue history in `chat()` | the bot remembers the conversation |
| **Judge** | the `judge()` function (optional) | checks the answer before showing it |
| **Gradio** | `.launch()` at the end | a live chat in the browser |

## Run

> 📁 `~/Downloads/foundations-practice` below is an EXAMPLE path. Your project
> folder might be somewhere else and named differently. Replace it with your
> own: easiest way — type `cd ` (with a trailing space) in the terminal, then
> drag the project folder from Finder right into the terminal window — the
> path fills in by itself.

```bash
cd ~/Downloads/foundations-practice   # ← put YOUR path to the project folder here
pip install -r requirements.txt
python bot.py
```
A chat will open in the browser. By default — the free local Ollama
(you need the Ollama app installed and a model: `ollama pull llama3.2`,
or better `qwen2.5` for some languages).

## How to make your own

1. Replace `knowledge.txt` with the facts of your niche.
2. Adjust the roles/categories for yourself (in `classify()` and the system prompt).
3. Optionally turn on answer checking: set `USE_JUDGE = True` in the code.

This is exactly the `PRACTICE.md` assignment — you just come up with the niche and details yourself.

## Deploy on Render

The repository includes `render.yaml`. Connect this repository to a Render Web Service and add the secret environment variable `GOOGLE_API_KEY`. Render will install dependencies with `pip install -r requirements.txt` and start the app with `python3 bot.py`.

Do not commit `.env` or API keys to GitHub.
