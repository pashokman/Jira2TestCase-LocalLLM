# Jira2TestCase — Local LLM QA Assistant 🤖

Автономний ШІ-асистент для авtomатичного розуміння задач у **Jira**, уточнення вимог та генерації:

1. ✅ **Чек-листів** (QA Checklist)
2. 📝 **Тест-кейсів** (Test Cases)  
3. 🔍 **Аналізу прикріплених файлів, пов'язаних задач** (Vision support — перегляд картинок)

Працює повністю офлайн на локальних LLM через LM Studio.

---

## 🎯 Мета Проекту

ШІ-асистент, який автоматизує перші етапи QA-процесу: від **задачі в Jira** до **готових тест-кейсів**, економлячи час на більш складні та важливі речі.

### Ключові можливості

| Функціонал | Опис |
|---|---|
| 📥 **Збір даних з Jira** | Підтримка картинок/файлів через Vision API |
| 📋 **Аналіз вимог** | Генерація структурованих `requirements.md` |
| ✅ **Чек-лист** | High-level QA Checklist |
| 🧪 **Тест-кейси** | Детальні тест-кейси з кроками |
| 🔒 **Offline-first** | Працює на локальних LLM (LM Studio) |

---

## 🚀 Швидкий старт

### 1. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 2. Налаштування конфігурації

Відкрийте `config_example.py`, змініть параметри та перейменуйте його в `config.py`:

```python
LM_STUDIO_URL = "http://localhost:1234/v1"  # URL вашого LM Studio
API_KEY = "lm-studio"                        # API key LM Studio (зазвичай "lm-studio")
MODEL_NAME = "your_LLM_model"                # Ім'я вашої моделі (напр. "llama3-8b")

# Dиректорія для артефактів:
OUTPUT_DIR = "qa_artifacts"

# Jira налаштування:
JIRA_URL = "https://yourworkflow.atlassian.net/"  # Посилання на Jira
JIRA_EMAIL = "your@gmail.com"                    # Email акаунту Jira
JIRA_API_TOKEN = "your_token"                    # API Token Jira
```

### 3. Запуск

```bash
python main.py
```

**Модульний режим (4 кроки):**

1. **Збір даних** — Вхід: Опис таски з Jira, коментарі, прикріплені файли, пов'язані задачі → Вихід: `task_[ID].md`
2. **Аналіз вимог** — Вхід: `task_[ID].md` → Вихід: `requirements_[ID].md`
3. **Чек-лист** — Вхід: `requirements_[ID].md` → Вихід: `check_list_[ID].md`
4. **Тест-кейси** — Вхід: `check_list_[ID].md` → Вихід: `test_cases_[ID].md`

---

## 📁 Структура Проекту

```
jira2testcasellm/
├── main.py                      # Головний файл (меню вибору кроків)
├── config_example.py            # Налаштування LLM/Jira
├── llm_client.py                # Клієнт для запитів до LM Studio
├── jira_client.py               # Підключення до Jira API
├── utils.py                     # Утиліти
├── skills/                      # Скили для кожного кроку
│   ├── data_collecting.py      # Збір даних (Vision)
│   ├── requirements_grooming.py# Аналіз вимог
│   ├── check_list_generating.py# Генерація чек-листа
│   └── test_case_generating.py # Генерація тест-кейсів
├── qa_artifacts/               # Вихідні файли (автоматично)
├── requirements.txt            # Залежності
└── README.md                   # Цей файл
```