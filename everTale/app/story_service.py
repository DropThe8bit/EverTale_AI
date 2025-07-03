from .config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_story(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 상상력이 풍부한 동화 작가야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def make_prompt(title, name, age, gender, personalities):
    personality_str = ", ".join(personalities)
    return (
        f"동화 제목: {title}\n"
        f"주인공 이름은 {name}이고, 나이는 {age}살이며 성별은 {gender}야.\n"
        f"{personality_str} 성격을 가진 주인공의 흥미롭고 감동적인 동화의 시작 부분을 2~3줄 써줘.\n"
        f"아이들이 흥미롭게 읽을 수 있도록 상상력을 풍부하게 써줘."
    )

def generate_story_from_character_info(title, name, age, gender, personalities):
    prompt = make_prompt(title, name, age, gender, personalities)
    return generate_story(prompt)

def generate_prompt_for_next_story(previous, title, name, age, gender, personalities):
    personality_str = ", ".join(personalities)
    return (
        f"동화 제목: {title}\n"
        f"이전 줄거리: {previous}\n"
        f"주인공 이름은 {name}, 나이는 {age}살, 성별은 {gender}야.\n"
        f"이 주인공은 {personality_str} 성격을 가지고 있어.\n"
        f"이어서 다음 장면을 상상력 있게 이어서 써줘.\n"
        f"아이들이 흥미롭게 읽을 수 있게, 자연스럽게 다음 이야기를 2~3줄 만들어줘."
    )

