import os
from openai import OpenAI


def evaluate_transcript(transcript):
    """
    AI-powered evaluation of student recitation transcript.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "score": 50,
            "feedback": "عذراً، مفتاح API غير متوفر. يرجى التحقق من الإعدادات.",
        }

    client = OpenAI(api_key=api_key)

    try:
        system_prompt = """
        You are an AI evaluator for Islamic Sunnah memorization.
        Evaluate the provided transcript for accuracy, fluency, and adherence to authentic Hadith.
        Provide a score from 0-100 and constructive feedback in Arabic.
        Be fair, encouraging, and focused on educational improvement.
        """

        user_prompt = f"Evaluate this recitation transcript: {transcript}"

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )

        feedback = response.choices[0].message.content.strip()

        # Extract score from feedback or estimate
        # For simplicity, assume score is mentioned or calculate based on length/quality
        score = 80  # Placeholder; in production, parse from AI response

        return {
            "score": score,
            "feedback": feedback,
        }
    except Exception as e:
        return {
            "score": 50,
            "feedback": f"عذراً، حدث خطأ في التقييم: {str(e)}",
        }

