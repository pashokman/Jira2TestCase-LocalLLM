from skills.data_collecting import get_data_collection_prompt
from skills.requirements_grooming import get_requirement_grooming_prompt
from skills.check_list_generating import get_check_list_generating_prompt
from skills.test_case_generating import get_test_case_generating_prompt

# Конфігурація підключення до LM Studio
LM_STUDIO_URL = "http://localhost:1234/v1"
API_KEY = "lm-studio"
MODEL_NAME = "your_LLM_model"  # Сюди можна вписати будь-яку модель, яка запущена

# Директорія для збереження артефактів тестування
OUTPUT_DIR = "qa_artifacts"

# Налаштування Jira
JIRA_URL = "https://yourworkflow.atlassian.net/"  # Ваш лінк на Jira
JIRA_EMAIL = "your@gmail.com"  # Ваш Email від Jira account
JIRA_API_TOKEN = "your_token"  # Токен


# ==========================================
# СИСТЕМНІ ПРОМПТИ ДЛЯ СКІЛІВ QA
# ==========================================

PROMPT_STEP_1 = get_data_collection_prompt()
PROMPT_STEP_2 = get_requirement_grooming_prompt()
PROMPT_STEP_3 = get_check_list_generating_prompt()
PROMPT_STEP_4 = get_test_case_generating_prompt()
