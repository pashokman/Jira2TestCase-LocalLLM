import os
import sys
import config
from llm_client import QAAssistantClient
from jira_client import get_jira_issue_data


def get_multiline_input():
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

def main():
    assistant = QAAssistantClient()
    
    print("===============================================")
    print("🤖 QA AI-Assistant — Модульний режим")
    print("===============================================")
    
    # 1. Вибір Кроку
    print("Оберіть крок, який необхідно виконати:")
    print("1️⃣  Крок 1: Збір даних (Вхід: Текст з Jira -> Вихід: task_[ID].md)")
    print("2️⃣  Крок 2: Аналіз вимог (Вхід: task_[ID].md -> Вихід: requirements_[ID].md)")
    print("3️⃣  Крок 3: Генерація чек-листа (Вхід: requirements_[ID].md -> Вихід: check_list_[ID].md)")
    print("4️⃣  Крок 4: Генерація тест-кейсів (Вхід: check_list_[ID].md -> Вихід: test_cases_[ID].md)")
    
    try:
        choice = int(input("\nВведіть номер кроку (1-4): ").strip())
        if choice not in [1, 2, 3, 4]:
            raise ValueError
    except ValueError:
        print("❌ Некоректний вибір. Будь ласка, введіть число від 1 до 4.")
        return

    # 2. Запит ID задачі
    jira_id = input("Вставте посилання на задачу в JIRA або її ID (наприклад, SCRUM-5): ").strip()
    if not jira_id:
        print("❌ ID задачі не може бути порожнім!")
        return

    # Шляхи до всіх можливих файлів
    task_file = f"task_{jira_id}.md"
    req_file = f"requirements_{jira_id}.md"
    checklist_file = f"check_list_{jira_id}.md"
    testcases_file = f"test_cases_{jira_id}.md"

    task_path = os.path.join(config.OUTPUT_DIR, task_file)
    req_path = os.path.join(config.OUTPUT_DIR, req_file)
    checklist_path = os.path.join(config.OUTPUT_DIR, checklist_file)

    # =========================================================================
    # ЛОГІКА Окремих Кроків
    # =========================================================================
    
    if choice == 1:
            print(f"\n--- [КРОК 1] Збір даних з Jira (з підтримкою Vision) ---")
                
            # Тепер отримуємо три значення: jira_id, текст і список шляхів до картинок
            jira_id, jira_raw_text, image_paths = get_jira_issue_data(jira_id)
            
            if not jira_raw_text:
                print("❌ Не вдалося отримати дані.")
                return
                
            task_file = f"task_{jira_id}.md"
            initial_content = f"ID Задачі: {jira_id}\n\n{jira_raw_text}\nУважно проаналізуй опис, коментарі та прикріплені файли (якщо вони є)."
            
            # Передаємо image_paths у клієнт
            assistant.interact_with_user(
                step_name="Збір даних (Vision)",
                system_prompt=config.PROMPT_STEP_1,
                initial_user_content=initial_content,
                output_filename=task_file,
                image_paths=image_paths # <-- Передаємо картинки моделі!
            )

    elif choice == 2:
        print(f"\n--- [КРОК 2] Аналіз вимог для {jira_id} ---")
        if not os.path.exists(task_path):
            print(f"❌ Помилка: Попередній файл '{task_file}' не знайдено в '{config.OUTPUT_DIR}'. Спочатку виконайте Крок 1.")
            return
            
        with open(task_path, "r", encoding="utf-8") as f:
            source_data = f.read()
            
        initial_content = f"Проаналізуй наступні структуровані дані задачі та сформуй вимоги:\n\n{source_data}"
        assistant.interact_with_user("Аналіз вимог", config.PROMPT_STEP_2, initial_content, req_file)

    elif choice == 3:
        print(f"\n--- [КРОК 3] Генерація чек-листа для {jira_id} ---")
        if not os.path.exists(req_path):
            print(f"❌ Помилка: Попередній файл '{req_file}' не знайдено. Спочатку виконайте Крок 2.")
            return
            
        with open(req_path, "r", encoding="utf-8") as f:
            source_data = f.read()
            
        initial_content = f"На основі цих вимог згенеруй високорівневий чек-лист перевірок:\n\n{source_data}"
        assistant.interact_with_user("Генерація чек-листа", config.PROMPT_STEP_3, initial_content, checklist_file)

    elif choice == 4:
        print(f"\n--- [КРОК 4] 🚀 Генерація тест-кейсів для {jira_id} ---")
        if not os.path.exists(checklist_path):
            print(f"❌ Помилка: Попередній файл '{checklist_file}' не знайдено. Спочатку виконайте Крок 3.")
            return
            
        with open(checklist_path, "r", encoding="utf-8") as f:
            source_data = f.read()
            
        initial_content = f"Розгорни кожен пункт цього чек-листа у детальний тест-кейс з кроками:\n\n{source_data}"
        assistant.interact_with_user("Генерація тест-кейсів", config.PROMPT_STEP_4, initial_content, testcases_file)

if __name__ == "__main__":
    main()