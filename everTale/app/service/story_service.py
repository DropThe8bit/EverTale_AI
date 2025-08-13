from ..config import OPENAI_API_KEY
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


def make_prompt(genre, world_view, name, age, gender, personalities):
    personality_str = ", ".join(personalities)
    return (
        f"장르: {genre}\n"
        f"주인공 이름은 {name}이고, 나이는 {age}살이며 성별은 {gender}야.\n"
        f"{world_view}를 참고해서 {personality_str} 성격을 가진 주인공의 흥미롭고 감동적인 동화의 시작 부분을 2~3줄 써줘.\n"
        f"아이들이 흥미롭게 읽을 수 있도록 상상력을 풍부하게 써줘."
    )

def generate_story_from_character_info(genre, world_view, name, age, gender, personalities):
    prompt = make_prompt(genre, world_view, name, age, gender, personalities)
    return generate_story(prompt)

def generate_prompt_for_next_story(scene_number, genre, previous, name, age, gender, personalities):
    personality_str = ", ".join(personalities)

    stage_map = {
        1: "기(시작): 세계관과 주인공을 소개하는 장면이야.",
        2: "기(전개): 주인공의 평범한 일상이나 목표가 드러나는 장면이야.",
        3: "승(변화): 이야기에 변화를 주는 사건이 발생하는 장면이야.",
        4: "승(전개): 사건이 커지고 긴장감이 높아지는 장면이야.",
        5: "전(위기): 갈등이 본격적으로 시작되고 주인공이 어려움을 겪는 장면이야.",
        6: "전(절정): 갈등이 최고조에 달하고 주인공이 위기에 처한 장면이야.",
        7: "결(전환): 위기를 극복할 실마리가 보이고 상황이 반전되는 장면이야.",
        8: "결(마무리): 모든 갈등이 해소되고 이야기가 따뜻하게 마무리되는 장면이야."
    }

    stage = stage_map.get(scene_number, "알 수 없는 장면 번호입니다. scene_number는 1부터 8 사이여야 합니다.")

    return (
        f"[장르] {genre}\n"
        f"[현재 장면: {scene_number}페이지 / {stage}]\n\n"
        f"[이전 줄거리 요약]\n{previous}\n\n"
        f"[주인공 정보]\n"
        f"- 이름: {name}\n"
        f"- 나이: {age}살\n"
        f"- 성별: {gender}\n"
        f"- 성격: {personality_str}\n\n"
        f"위 정보를 바탕으로 {scene_number}번째 장면을 2~3문장으로 이어서 써줘.\n"
        f"아이들이 흥미롭게 읽을 수 있도록, 따뜻하고 창의적인 문장으로 자연스럽게 이야기를 이어줘."
    )



