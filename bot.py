# region 🇷🇺 Русский — о файле  (нажми стрелку ▸ слева, чтобы свернуть)
"""
Эталонный бот-консультант (барбершоп «Бритва»)
==============================================
Готовый пример для задания PRACTICE.md — несколько паттернов в одном боте:
RAG (knowledge.txt) + Router (тип вопроса) + Tool Calling (record_lead) +
Structured Output (extract_booking) + Memory (история) + Judge (опц.) + Gradio.

МОДЕЛЬ — переключатель PROVIDER ниже:
  "ollama" — локально, бесплатно (для разработки на своём компьютере).
             Нужна скачанная модель:  ollama pull qwen2.5  (или llama3.2)
  "gemini" — облако Google (для ДЕПЛОЯ на сервер, где Ollama нет). Нужен GOOGLE_API_KEY.

ЗАПИСИ клиентов (см. record_lead): локально — в файл leads.json; на хостинге с
Postgres (задан DATABASE_URL) — в базу, которая переживает перезапуск. Так один и
тот же бот «помнит» записи и на компьютере, и на сервере (Render/Railway).

Запуск локально:  python bot.py
"""
# endregion

# region 🇬🇧 English — about this file  (click the ▸ arrow to collapse)
"""
A reference consultant bot (the 'Britva' barbershop)
==============================================
A ready example for the PRACTICE.md assignment — several patterns in one bot:
RAG (knowledge.txt) + Router (question type) + Tool Calling (record_lead) +
Structured Output (extract_booking) + Memory (history) + Judge (opt.) + Gradio.

MODEL — the PROVIDER switch below:
  "ollama" — local, free (for development on your own computer).
             Needs a downloaded model:  ollama pull qwen2.5  (or llama3.2)
  "gemini" — Google cloud (for DEPLOYING to a server, where there's no Ollama). Needs GOOGLE_API_KEY.

Client BOOKINGS (see record_lead): locally — to a leads.json file; on a host with
Postgres (DATABASE_URL is set) — to a database that survives restarts. So the same
bot "remembers" bookings both on your computer and on a server (Render/Railway).

Run locally:  python bot.py
"""
# endregion

import os
import sys
import json
import datetime

# RU: предохранители
# EN: guards
try:
    import gradio as gr
except ImportError:
    print("\n⚠️  Нет Gradio. Установи зависимости:  pip install -r requirements.txt\n")
    sys.exit(1)
try:
    import ollama
except ImportError:
    print("\n⚠️  Нет ollama. Установи зависимости:  pip install -r requirements.txt\n")
    sys.exit(1)
from openai import OpenAI       # RU: для облачного Gemini / EN: for the cloud Gemini
from dotenv import load_dotenv

load_dotenv()  # RU: подгружаем ключи из .env / EN: load keys from .env


# ⬇️ РУБИЛЬНИК: "ollama" (локально) | "gemini" (облако — для деплоя на сервер)
# ⬇️ SWITCH: "ollama" (local) | "gemini" (cloud — for deploying to a server)
# RU: стоит "gemini" — так бот готов к деплою (на сервере Ollama нет). Для локальной
#     бесплатной разработки переключи обратно на "ollama".
# EN: set to "gemini" so the bot is deploy-ready (no Ollama on a server). For free
#     local development switch it back to "ollama".
PROVIDER = "gemini"

OLLAMA_MODEL = "qwen2.5"          # RU: локальная модель (ollama pull qwen2.5) / EN: local model
GEMINI_MODEL = "gemini-flash-latest"  # RU: актуальная облачная модель / EN: current cloud model
USE_JUDGE = False                  # RU: включить проверку судьёй (медленнее) / EN: enable judge check (slower)

# RU: база знаний (RAG): факты из файла рядом со скриптом
# EN: knowledge base (RAG): facts from the file next to the script
KNOWLEDGE = open(os.path.join(os.path.dirname(__file__), "knowledge.txt"), encoding="utf-8").read()

# RU: файл, где «помнятся» записи клиентов ЛОКАЛЬНО
# EN: the file where client bookings are "remembered" LOCALLY
LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads.json")

# RU: адрес базы Postgres — хостинг (Render/Railway) задаёт его сам при подключении
#     базы. Есть переменная → пишем в базу (переживёт перезапуск); нет → в файл выше.
# EN: the Postgres address — the host (Render/Railway) sets it automatically when a DB
#     is attached. If present → write to the DB (survives restarts); if not → to the file above.
DATABASE_URL = os.getenv("DATABASE_URL")


def call_model(messages: list[dict]) -> str:
    """
    RU: отправить список сообщений выбранной модели (ollama или gemini) и вернуть текст.
    EN: send a message list to the chosen model (ollama or gemini) and return the text.
    """
    try:
        # ── RU: локально — Ollama / EN: local — Ollama ──
        if PROVIDER == "ollama":
            return ollama.chat(model=OLLAMA_MODEL, messages=messages).message.content

        # ── RU: облако — Gemini (для деплоя) / EN: cloud — Gemini (for deploy) ──
        key = os.getenv("GOOGLE_API_KEY")
        if not key or "..." in key:
            return "⚠️ Нет GOOGLE_API_KEY в .env (нужен для PROVIDER='gemini' / деплоя)."
        client = OpenAI(
            api_key=key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return client.chat.completions.create(model=GEMINI_MODEL, messages=messages).choices[0].message.content
    except Exception as e:
        return f"⚠️ Модель не отвечает (PROVIDER={PROVIDER}): {e}"


def to_plain_text(content) -> str:
    """
    RU: Gradio 6 отдаёт content не строкой, а списком блоков вида
        [{"type": "text", "text": "..."}]. Модель ждёт обычную строку —
        эта функция достаёт текст из блоков.
    EN: Gradio 6 gives content not as a string but as a list of blocks like
        [{"type": "text", "text": "..."}]. The model expects a plain string —
        this function pulls the text out of the blocks.
    """
    if isinstance(content, list):
        return "".join(block.get("text", "") for block in content if block.get("type") == "text")
    return content


def ask(prompt: str, system: str = "Ты — помощник.") -> str:
    """
    RU: один вызов модели (вопрос → ответ).
    EN: one model call (question → answer).
    """
    return call_model([
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ])


# RU: ROUTER — определяем тип вопроса
# EN: ROUTER — figure out the question type
def classify(message: str) -> str:
    cat = ask(
        "Определи тип вопроса ОДНИМ словом из списка: цена, запись, общее. "
        f"Верни только слово.\n\nВопрос: {message}"
    ).strip().lower()
    for key in ("цена", "запись", "общее"):
        if key in cat:
            return key
    return "общее"


# RU: TOOL CALLING — реальное действие: СОХРАНЯЕМ запись клиента.
#     Две ветки: локально — в файл leads.json; на хостинге с Postgres — в базу.
# EN: TOOL CALLING — a real action: SAVE the client's booking.
#     Two branches: locally — to leads.json; on a host with Postgres — to the DB.

def _save_lead_to_file(name: str, service: str) -> int:
    """
    RU: сохранить запись в leads.json (локальная разработка). Вернуть общее число записей.
    EN: save the booking to leads.json (local dev). Return the total number of bookings.
    """
    # RU: читаем прошлые записи (нет файла — пустой список)
    # EN: read past bookings (no file — an empty list)
    leads = []
    if os.path.exists(LEADS_FILE):
        try:
            leads = json.load(open(LEADS_FILE, encoding="utf-8"))
        except Exception:
            leads = []
    leads.append({
        "name": name,
        "service": service,
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
    })
    json.dump(leads, open(LEADS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return len(leads)


def _save_lead_to_db(name: str, service: str) -> int:
    """
    RU: сохранить запись в Postgres (на хостинге — переживёт перезапуск). Вернуть число записей.
    EN: save the booking to Postgres (on a host — survives restarts). Return the count.
    """
    import psycopg2  # RU: клиент Postgres (из requirements.txt) / EN: Postgres client (from requirements.txt)
    conn = psycopg2.connect(DATABASE_URL)
    try:
        # RU: with conn — сам зафиксирует изменения (commit) при успехе
        # EN: with conn — auto-commits the changes on success
        with conn, conn.cursor() as cur:
            # RU: таблица создаётся один раз, если её ещё нет
            # EN: the table is created once, if it doesn't exist yet
            cur.execute(
                "CREATE TABLE IF NOT EXISTS leads ("
                "id SERIAL PRIMARY KEY, name TEXT, service TEXT, "
                "created_at TIMESTAMP DEFAULT NOW())"
            )
            # RU: %s — безопасная подстановка (защита от SQL-инъекций), НЕ f-строка
            # EN: %s — safe parameter substitution (SQL-injection safe), NOT an f-string
            cur.execute("INSERT INTO leads (name, service) VALUES (%s, %s)", (name, service))
            cur.execute("SELECT COUNT(*) FROM leads")
            total = cur.fetchone()[0]
        return total
    finally:
        conn.close()


def record_lead(name: str, service: str) -> str:
    # RU: есть база (на хостинге) — пишем в неё; иначе — в файл (локально)
    # EN: a DB is present (on the host) — write to it; otherwise — to a file (locally)
    if DATABASE_URL:
        total = _save_lead_to_db(name, service)
        where = "базу Postgres / Postgres DB"
    else:
        total = _save_lead_to_file(name, service)
        where = "файл leads.json / the leads.json file"
    print(f"   📒 [CRM] Записан клиент: {name} — услуга: {service}  "
          f"(хранилище: {where}; всего записей: {total})")
    return "ok"


# RU: STRUCTURED OUTPUT — достаём имя+услугу строгим JSON
# EN: STRUCTURED OUTPUT — pull name+service as strict JSON
def extract_booking(text: str) -> dict:
    raw = ask(
        'Извлеки из сообщения имя клиента и услугу. Верни СТРОГО JSON вида '
        '{"name": "...", "service": "..."}. Если чего-то нет — поставь null. '
        f"Только JSON.\n\nСообщение: {text}"
    )
    start, end = raw.find("{"), raw.rfind("}")
    try:
        return json.loads(raw[start:end + 1])
    except Exception:
        return {}


# RU: JUDGE — проверка ответа (опционально)
# EN: JUDGE — check the answer (optional)
def judge(question: str, answer: str) -> bool:
    verdict = ask(
        "Ответ вежливый и по делу? Первой строкой строго ДА или НЕТ.\n"
        f"Вопрос: {question}\nОтвет: {answer}"
    )
    first = verdict.strip().upper()
    return first.startswith("ДА") or first.startswith("YES")


# RU: главная функция чата (Gradio вызывает её на каждое сообщение)
# EN: the main chat function (Gradio calls it on every message)
def chat(message, history):
    # RU: 1) Router — тип вопроса / EN: 1) Router — the question type
    category = classify(message)

    # RU: 2) RAG + роль — системный промпт с фактами
    # EN: 2) RAG + role — system prompt with the facts
    # RU: язык ответа просим зеркалить явно и настойчиво (мягкой фразы слабой
    #     модели не хватает — она сваливается в русский на английский вопрос).
    # EN: we ask to mirror the reply language firmly (a soft line isn't enough
    #     for a weak model — it slips into Russian on an English question).
    system = (
        "Ты — вежливый администратор барбершопа «Бритва». "
        "ВАЖНОЕ ПРАВИЛО: всегда отвечай СТРОГО на языке последнего сообщения клиента. "
        "Английский вопрос — английский ответ. Русский вопрос — русский ответ. "
        "Отвечай ТОЛЬКО по фактам ниже; если факта нет — честно скажи. "
        "Будь краток и дружелюбен.\n\nФАКТЫ:\n" + KNOWLEDGE
    )
    if category == "запись":
        system += "\n\nКлиент хочет записаться. Если не хватает имени или услуги — вежливо уточни."

    # RU: 3) Memory — история разговора (нормализуем формат Gradio 6 в простые строки)
    # EN: 3) Memory — the conversation history (normalize Gradio 6 format to plain strings)
    normalized_history = [{"role": m["role"], "content": to_plain_text(m["content"])} for m in history]
    messages = [{"role": "system", "content": system}] + normalized_history + [{"role": "user", "content": message}]
    answer = call_model(messages)

    # RU: 4) Tool Calling — если запись и есть имя+услуга, СОХРАНЯЕМ клиента в файл
    # EN: 4) Tool Calling — if it's a booking with name+service, SAVE the client to the file
    if category == "запись":
        data = extract_booking(message)
        if data.get("name") and data.get("service"):
            record_lead(data["name"], data["service"])
            answer += f"\n\n✅ Готово! Записал: {data['name']} — {data['service']}."

    # RU: 5) Judge (опц.) — при провале переписываем ответ
    # EN: 5) Judge (opt.) — rewrite the answer if it fails
    if USE_JUDGE and not judge(message, answer):
        answer = ask(f"Перепиши вежливее и по делу:\n{answer}", system=system)

    return answer


if __name__ == "__main__":
    # RU: server_name/server_port — чтобы работало и локально, и на хостинге:
    #     хостинг (Render/Railway) сам передаёт порт в переменной PORT; локально её нет → 7860.
    # EN: server_name/server_port — so it works both locally and on a host:
    #     the host (Render/Railway) passes the port in the PORT env var; locally it's absent → 7860.
    gr.ChatInterface(
        chat,
        title="Барбершоп «Бритва» — AI-администратор  /  'Britva' Barbershop — AI receptionist",
        description="Спросите про услуги, цены или запишитесь.  /  Ask about services, prices, or make a booking.",
    ).launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )
