import os
import base64
from openai import OpenAI
import config

class QAAssistantClient:
    def __init__(self):
        self.client = OpenAI(base_url=config.LM_STUDIO_URL, api_key=config.API_KEY)
        self.model = config.MODEL_NAME
        if not os.path.exists(config.OUTPUT_DIR):
            os.makedirs(config.OUTPUT_DIR)

    def _encode_image_to_base64(self, image_path):
        """Конвертує локальну картинку в base64 рядок"""
        ext = os.path.splitext(image_path)[1].lower().replace('.', '')
        if ext == 'jpg': ext = 'jpeg'
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/{ext};base64,{encoded_string}"

    def interact_with_user(self, step_name, system_prompt, initial_user_content, output_filename, image_paths=None):
        """
        Мультимодальна взаємодія. Підтримує передачу списку картинок image_paths.
        """
        output_path = os.path.join(config.OUTPUT_DIR, output_filename)
        
        # Формуємо контент користувача (текст + картинки, якщо є)
        user_content = [{"type": "text", "text": initial_user_content}]
        
        if image_paths:
            print(f"🖼️ Додавання {len(image_paths)} зображень до контексту моделі...")
            for img_path in image_paths:
                try:
                    b64_image = self._encode_image_to_base64(img_path)
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": b64_image}
                    })
                except Exception as e:
                    print(f"⚠️ Не вдалося обробити картинку {img_path}: {e}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        print(f"\n🚀 Запуск скіла: {step_name}")

        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2
                )
                
                ai_output = response.choices[0].message.content
                print("\n" + "="*40 + "\n🤖 РЕЗУЛЬТАТ ВІД ШІ:\n" + "="*40)
                print(ai_output)
                print("="*40)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(ai_output)
                print(f"💾 Результат збережено у: {output_path}")

                print("\n📋 Ваші дії (Правки / або 'ОК' для затвердження):")
                user_feedback = input("Введіть вашу відповідь: ").strip()

                if user_feedback.lower() in ["ok", "ок", "так", "затверджую"]:
                    break
                print("Вношу зміни.")
                
                # При повторних ітераціях (правках) передаємо вже тільки текст фідбеку
                messages.append({"role": "assistant", "content": ai_output})
                messages.append({"role": "user", "content": [{"type": "text", "text": f"Внеси правки: {user_feedback}"}]})

            except Exception as e:
                print(f"❌ Помилка LM Studio API: {e}")
                break