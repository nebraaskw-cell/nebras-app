import os
from openai import OpenAI


def generate_guidance(prompt):
    """
    Generate AI-powered guidance for Islamic educational queries.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "response": "عذراً، مفتاح API غير متوفر. يرجى التحقق من الإعدادات.",
            "provider": "error",
        }

    client = OpenAI(api_key=api_key)

    try:
        system_prompt = """
        You are an AI assistant for the Nebras platform, specializing in Islamic education.
        Provide guidance on Sunnah memorization, Prophet Mohammed's life, and Hadith.
        Always respond in Arabic, be respectful, and ensure information is authentic.
        Keep responses helpful, concise, and focused on educational aspects.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return {
            "response": response.choices[0].message.content.strip(),
            "provider": "openai",
        }
    except Exception as e:
        return {
            "response": f"عذراً، حدث خطأ في الاتصال بالمساعد الذكي: {str(e)}",
            "provider": "error",
        }

