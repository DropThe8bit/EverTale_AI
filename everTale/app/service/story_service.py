from .. import dto
from ..config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

# 장르별 톤/배경/어휘
genre_guides = {
    "ADVENTURE": {
        "tone": "경이롭고 용감한 분위기, 호기심을 자극",
        "setting": "판타지 세계관(숲·성·마법)",
        "hint": "모험과 탐험을 중심으로 전개",
    },
    "FRIENDSHIP": {
        "tone": "따뜻하고 명랑한 분위기, 협동과 배려 강조",
        "setting": "유치원/학교 생활",
        "hint": "아이들 사이의 우정과 놀이",
    },
    "MORAL": {
        "tone": "잔잔하고 사려 깊은 분위기",
        "setting": "자연 속(초원·강가·동물 등장)",
        "hint": "이솝우화처럼 교훈을 주는 이야기",
    },
    "FAMILY": {
        "tone": "포근하고 다정한 분위기",
        "setting": "집·가족이 함께하는 공간",
        "hint": "사랑과 연대감을 드러내는 스토리",
    },
}

# 페이지(1~8)별 기승전결 장면 설계
beat_map = {
    1: {
        "label": "기(시작) — 세계관·주인공 소개",
        "goal": "배경과 분위기, 주인공의 기본 정보가 자연스럽게 드러난다",
        "must": ["주인공의 이름·나이·성격을 대사나 행동으로 녹이기"],
        "hint": [
            "장르 setting을 한 문장으로 열어 분위기 고정",
            "현재 상황(시간/장소/기분)을 짧게 제시"
        ],
        "style_hint": "짧은 구어체, 아이 시선에서 경쾌하게",
        "ending": "작은 호기심이 싹트는 느낌으로 가볍게 마무리(선택적)."
    },
    2: {
        "label": "기(전개) — 일상/목표 드러남",
        "goal": "주인공의 작은 목표와 일상이 보이며 동기가 형성된다",
        "must": ["주인공의 소망 또는 오늘의 작은 목표 1개"],
        "hint": [
            "친구·환경과의 상호작용으로 목표를 드러내기",
            "감정 어휘는 단순하고 따뜻하게"
        ],
        "style_hint": "대사 1~2줄로 템포를 살리기",
        "ending": "목표를 향한 소소한 결심 또는 변화의 징조(선택적)."
    },
    3: {
        "label": "승(변화) — 사건 발생",
        "goal": "분명한 변화나 사건이 등장해 긴장감이 시작된다",
        "must": ["사건/징조 1개", "주인공의 즉각 반응(감정+행동)"],
        "hint": [
            "사건은 과장하지 말고 일상에서 출발",
            "감정은 ‘놀람/궁금/걱정’ 등 간단 명료"
        ],
        "avoid": ["사건을 같은 페이지에서 바로 해결하지 않기"],
        "style_hint": "짧은 문장으로 리듬감 있게",
        "ending": "선택지가 생기는 듯한 훅(선택적)."
    },
    4: {
        "label": "승(전개) — 긴장 고조",
        "goal": "장애물이 구체화되고 시도가 부분적으로 실패한다",
        "must": ["장애물 1개 구체화", "주인공의 첫 시도와 작은 좌절"],
        "hint": [
            "우연한 해결은 금지(공통 가드레일 준수)",
            "주인공의 노력과 배움의 씨앗 암시"
        ],
        "style_hint": "행동 묘사 위주, 감정은 과잉 설명 자제",
        "ending": "더 큰 시도 또는 도움의 필요성 암시(선택적)."
    },
    5: {
        "label": "전(위기) — 갈등 본격화",
        "goal": "가장 큰 어려움 직전까지 몰리며 감정이 고조된다",
        "must": ["주인공의 망설임/두려움 한 문장", "결정을 요구하는 상황 제시"],
        "hint": [
            "환경(소리/색/움직임)으로 긴장감 보태기",
            "해결의 작은 힌트를 은근히 깔아두기"
        ],
        "style_hint": "호흡을 짧게, 문장 끝 처리를 단단하게",
        "ending": "결단 직전의 정적과 떨림(선택적)."
    },
    6: {
        "label": "전(절정) — 위기 최고조",
        "goal": "결정적 행동/도움/통찰로 위기를 정면 돌파한다",
        "must": ["핵심 행동 1개", "장르 상상력 장면 1개(마법/우정/가족애/교훈)"],
        "hint": [
            "주인공이 주도하거나 주인공의 선택이 결정적이어야 함",
            "설명보다 구체적인 장면 이미지로"
        ],
        "style_hint": "동사 중심, 리듬감 있는 전개",
        "ending": "결과 확인 직전의 숨 고르기(선택적)."
    },
    7: {
        "label": "결(전환) — 반전/실마리",
        "goal": "오해가 풀리거나 도움이 도착하고, 성장을 자각한다",
        "must": ["갈등을 풀 단서 1개", "신뢰/연대의 순간"],
        "hint": [
            "설교조 대신 짧은 대사·행동으로 메시지 전달",
            "감정의 온기를 장면 속 사물/제스처로 표현"
        ],
        "style_hint": "따뜻한 톤, 과장 없이 담백하게",
        "ending": "해결 이후의 여운을 가볍게 예고(선택적)."
    },
    8: {
        "label": "결(마무리) — 갈등 해소·따뜻한 엔딩",
        "goal": "갈등을 정리하고 장르별 메시지로 정서적 마무리를 짓는다",
        "must": [
            "갈등이 어떻게 풀렸는지 한 문장",
            "장르 메시지 반영(교훈/우정/가족사랑/모험 씨앗 중 해당)"
        ],
        "hint": [
            "마지막 문장은 짧고 선명하게",
            "설명 대신 장면·제스처·짧은 대사로 여운 남기기"
        ],
        "style_hint": "포근하고 맺음이 확실한 문장",
        "ending": "짧고 따뜻한 마무리 한 문장으로 끝맺기."
    },
}


# 출력 형식/금지어
guardrails = {
    "style_rules": [
        "총 3~5문장.",
        "아이들이 이해하기 쉬운 어휘.",
        "현재 시점처럼 생동감 있게.",
        "대사는 0~1문장(필요할 때만).",
        "문장 길이는 8~18자로 짧고 리듬감 있게.",
        "종결 어미를 다양화(했어요/하고/한다/하자 섞기).",
    ],
    "forbidden": [
        "과도한 공포/폭력/비하",
        "연애·신체 노출·성인 맥락",
        "장황한 설정 나열",
        "영어 번역투(과잉 수식, 수동 표현, '과연~?' 수사 의문)",
        "‘것/상황/문제’ ‘있었다/했다’ 반복",
    ]
}


def generate_story(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 상상력이 풍부한 동화 작가야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_story_from_character_info(genre, world_view, name, age, gender, personalities):
    prompt = make_initial_prompt(genre, world_view, name, age, gender, personalities)
    return generate_story(prompt)

def make_initial_prompt(genre, world_view, name, age, gender, personalities) -> str:
    g = genre_guides.get(genre, genre_guides["ADVENTURE"])
    beat = beat_map.get(1, beat_map[1])
    personality_str = ", ".join(personalities)

    return (
        f"[역할]\n"
        f"너는 유아·아동 대상 동화 작가야. 아이가 읽기 쉬운 말로, 따뜻하고 창의적으로 1페이지(시작 장면)를 써줘.\n\n"
        f"[장르]\n"
        f"{genre} — 톤: {g['tone']} | 배경: {g['setting']} | 힌트: {g['hint']} \n\n"
        f"[세계관 힌트]\n{world_view}\n\n"
        f"[현재 장면] 1페이지 / {beat['label']}\n"
        f"- 장면 목적: {beat['goal']}\n"
        f"- 반드시 포함: {', '.join(beat['must']) if beat['must'] else '자연스러운 전개'}\n"
        f"- 힌트: {', '.join(beat.get('hint', [])) if beat.get('hint') else '없음'}\n"
        f"- 장면 마무리: {beat['ending']} (선택적)\n\n"
        f"[주인공 정보]\n"
        f"- 이름: {name}\n"
        f"- 나이: {age}살\n"
        f"- 성별: {gender}\n"
        f"- 성격: {personality_str}\n\n"
        f"[스타일 규칙]\n"
        f"- " + "\n- ".join(guardrails["style_rules"]) + "\n"
        f"- {beat.get('style_hint', '')}\n\n"
        f"[금지]\n"
        f"- " + "\n- ".join(guardrails["forbidden"]) + "\n\n"                                                                                     
        f"[출력 형식]\n"
        f"- 한국어로 3~5문장.\n"
        f"- 문단 머리표, 번호, 메타설명 없이 순수 서사만 출력.\n"
        f"- 마지막 문장은 다음 장면이 기대되게 가볍게 여운을 남김.\n\n"
        f"[이어서 작성]\n"
        f"위 정보를 바탕으로 1페이지 시작 장면을 써줘."
    )

def generate_prompt_for_next_story(
    page_number: int,
    genre: str,
    previous: str,
    name: str,
    age: int,
    gender: str,
    personalities: list[str],
) -> str:

    personality_str = ", ".join(personalities)
    g = genre_guides.get(genre, genre_guides["ADVENTURE"])
    beat = beat_map.get(page_number, beat_map[1])

    return (
        f"[역할]\n"
        f"너는 유아·아동 대상 동화 작가야. 번역투를 피하고 자연스러운 한국어 구어체로, 이전 줄거리에 자연스럽게 이어지게 작성해줘.\n\n"
        f"[장르]\n"
        f"{genre} — 톤: {g['tone']} | 배경: {g['setting']} | 힌트: {g.get('hint', '')}\n\n"
        f"[현재 장면] {page_number}페이지 / {beat['label']}\n"
        f"- 장면 목적: {beat['goal']}\n"
        f"- 반드시 포함: {', '.join(beat['must']) if beat['must'] else '자연스러운 전개'}\n"
        f"- 힌트: {', '.join(beat.get('hint', [])) if beat.get('hint') else '없음'}\n"
        f"- 장면 마무리: {beat['ending']} (선택적)\n\n"
        f"[이전 줄거리 요약]\n{previous}\n\n"
        f"[주인공 정보]\n"
        f"- 이름: {name}\n"
        f"- 나이: {age}살\n"
        f"- 성별: {gender}\n"
        f"- 성격: {personality_str}\n\n"
        f"[스타일 규칙]\n"
        f"- " + "\n- ".join(guardrails["style_rules"]) + "\n"
        f"- {beat.get('style_hint', '')}\n\n"
        f"[금지]\n"
        f"- " + "\n- ".join(guardrails["forbidden"]) + "\n\n"
        f"[출력 형식]\n"
        f"- 한국어로 3~5문장.\n"
        f"- 문단 머리표, 번호, 메타설명 없이 순수 서사만 출력.\n"
        f"- 8페이지가 아니면 마지막 문장은 다음 장면이 기대되게 가볍게 여운을 남김.\n"
        f"- 8페이지면 따뜻하게 마무리.\n\n"
        f"[이어서 작성]\n"
        f"위의 정보를 바탕으로 {page_number}번째 장면을 이어서 써줘."
    )


