import os
import re
import config
from jira import JIRA

def get_jira_issue_data(jira_url_or_id):
    """
    Підключається до Jira API, витягує опис, коментарі, підзадачі (subtasks).
    Завантажує ВСІ вкладення з батьківської таски та її підзадач у локальну теку.
    """
    jira_options = {'server': config.JIRA_URL}
    try:
        jira = JIRA(options=jira_options, basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN))
    except Exception as e:
        print(f"❌ Помилка авторизації в Jira: {e}")
        return None, None, []

    match = re.search(r'([A-Z]+-\d+)', jira_url_or_id.upper())
    if not match:
        print("❌ Не вдалося знайти ID задачі.")
        return None, None, []
    
    parent_id = match.group(1)
    print(f"🔍 Знайдено ID батьківської задачі: {parent_id}.")

    # Створюємо базову теку для артефактів цієї таски
    task_attachments_dir = os.path.join(config.OUTPUT_DIR, "attachments", parent_id)
    if not os.path.exists(task_attachments_dir):
        os.makedirs(task_attachments_dir)

    # Список для накопичення всіх шляхів до картинок (для Vision)
    all_downloaded_images = []

    def process_single_issue(issue_id, is_subtask=False):
        """Внутрішня функція для обробки однієї таски (батьківської або підзадачі)"""
        try:
            print(f"📥 Завантаження даних для {'підзадачі' if is_subtask else 'головної задачі'} {issue_id}...")
            issue = jira.issue(issue_id)
            
            summary = issue.fields.summary
            description = issue.fields.description if issue.fields.description else "Опис відсутній"
            status = issue.fields.status.name
            
            # Збір коментарів
            comments = issue.fields.comment.comments
            comments_text = "\n".join([f"  - [{c.author.displayName}]: {c.body}" for c in comments]) if comments else "  Коментарі відсутні."

            # Збір та завантаження вкладень
            attachments = issue.fields.attachment
            attachments_text_list = []
            
            if attachments:
                for a in attachments:
                    filename_lower = a.filename.lower()
                    # Зберігаємо все в одну теку, але додаємо префікс ID таски, щоб уникнути збігу імен
                    unique_filename = f"{issue_id}_{a.filename}"
                    local_path = os.path.join(task_attachments_dir, unique_filename)
                    
                    try:
                        with open(local_path, "wb") as f:
                            f.write(a.get())
                        file_info = f"  - Файл збережено: `attachments/{parent_id}/{unique_filename}` ({round(a.size/1024, 2)} KB)"
                        
                        # Перевірка на текст
                        if any(filename_lower.endswith(ext) for ext in ['.txt', '.md', '.json', '.csv', '.xml']):
                            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                                file_content = f.read()
                            file_info += f"\n      📄 ВМІСТ ФАЙЛУ:\n      \"\"\"\n      {file_content}\n      \"\"\""
                        
                        # Перевірка на картинку
                        elif any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                            all_downloaded_images.append(local_path)
                            file_info += f" 🖼️ [Додано до Vision]"
                        else:
                            file_info += " 📦 [Бінарний файл]"
                            
                    except Exception as e:
                        file_info = f"  - Файл: `{a.filename}` ⚠️ [Помилка завантаження: {e}]"
                    
                    attachments_text_list.append(file_info)
                attachments_text = "\n".join(attachments_text_list)
            else:
                attachments_text = "  Прикріплені файли відсутні."

            # Формуємо блок тексту для цієї конкретної таски
            prefix = "===> СУБТАСКА" if is_subtask else "ГОЛОВНА ЗАДАЧА"
            issue_block = f"""
=================================================================
{prefix}: {issue_id} | Статус: {status}
Назва: {summary}
=================================================================
📝 ОПИС:
{description}

💬 КОМЕНТАРІ:
{comments_text}

📎 ВКЛАДЕННЯ ТА ЇХНІЙ ВМІСТ:
{attachments_text}
"""
            return issue_block
        except Exception as e:
            print(f"❌ Помилка обробки задачі {issue_id}: {e}")
            return f"\n❌ Не вдалося завантажити дані для {issue_id}\n"

    try:
        # 1. Спочатку обробляємо головну таску
        main_issue = jira.issue(parent_id)
        final_structured_text = process_single_issue(parent_id, is_subtask=False)
        
        # 2. Перевіряємо наявність підзадач
        subtasks = main_issue.fields.subtasks
        if subtasks:
            print(f"🔗 Знайдено підзадачі ({len(subtasks)} шт.). Починаємо збір даних...")
            final_structured_text += "\n\n" + "="*65 + "\n🔗 ПОВ'ЯЗАНІ ПІДЗАДАЧІ (SUB-TASKS)\n" + "="*65 + "\n"
            
            for subtask in subtasks:
                subtask_block = process_single_issue(subtask.key, is_subtask=True)
                final_structured_text += subtask_block + "\n"
        else:
            final_structured_text += "\n\n🔗 Пов'язані підзадачі відсутні.\n"

        return parent_id, final_structured_text, all_downloaded_images

    except Exception as e:
        print(f"❌ Помилка при отриманні даних з Jira: {e}")
        return None, None, []