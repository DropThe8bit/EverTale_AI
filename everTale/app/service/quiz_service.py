from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # .env에서 불러옴

def generate_quiz_from_story(story_text: str) -> dict:

    prompt = f"""
너는 어린이를 위한 동화 줄거리로부터 퀴즈를 만드는 AI야.
다음 줄거리를 읽고, 이에 맞는 퀴즈를 만들어줘.

제약 조건:
- 문제는 1개
- 선택지는 총 4개
- JSON 형식으로 반환할 것

형식 예시:
{{
  "question": "주인공이 들고 간 물건은 무엇인가요?",
  "options": ["사과", "책", "우산", "도토리"],
  "answer_index": 3
}}

동화 줄거리:
\"\"\"{story_text}\"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 어린이 동화 기반 퀴즈를 만드는 친절한 AI입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    message = response.choices[0].message.content.strip()

    try:
        quiz_data = json.loads(message)
        return quiz_data
    except json.JSONDecodeError:
        raise ValueError("GPT 응답에서 유효한 JSON을 파싱할 수 없습니다.")
