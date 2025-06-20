import openai
from app.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_story(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 상상력이 풍부한 동화 작가야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
