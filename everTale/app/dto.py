from typing import List
from pydantic import BaseModel, Field

class InitStoryRequest(BaseModel):
    genre: str = Field(..., json_schema_extra={"example": "ADVENTURE"})
    worldView: str = Field(..., json_schema_extra={"example": "토로로는 모험을 좋아해요. 오늘은 또 어디로 모험을 떠날지 설레요."})
    title: str = Field(..., json_schema_extra={"example": "토토로의 모험 여행"})
    name: str = Field(..., json_schema_extra={"example": "토토로"})
    age: int = Field(..., json_schema_extra={"example": 8})
    gender: str = Field(..., json_schema_extra={"example": "female"})
    personalities: List[str] = Field(..., json_schema_extra={"example": ["용감함", "씩씩함"]})


class InitStoryResponse(BaseModel):
    message: str

class NextStoryRequest(BaseModel):
    previous: str = Field(..., json_schema_extra={"example": "토토로는 첫 여행지로 북부의 마탑으로 향했어요. 그녀는 마법을 배우고 싶어해요"})
    sceneNum: int = Field(..., json_schema_extra={"example": "2"})
    genre: str = Field(..., json_schema_extra={"example": "ADVENTURE"})
    title: str = Field(..., json_schema_extra={"example": "토토로의 모험 여행"})
    name: str = Field(..., json_schema_extra={"example": "토토로"})
    age: int = Field(..., json_schema_extra={"example": 8})
    gender: str = Field(..., json_schema_extra={"example": "female"})
    personalities: List[str] = Field(..., json_schema_extra={"example": ["용감함", "씩씩함"]})


class QuestionRequest(BaseModel):
    previous: str = Field(..., description="이전 줄거리")

    class Config:
        json_schema_extra = {
            "example": {
                "previous": "주인공은 친구와 함께 숲을 탐험하고 있었습니다."
            }
        }

class NextFromAnswerRequest(BaseModel):
    previous: str = Field(..., description="이전 줄거리")
    answer: str = Field(..., description="아이의 대답")

    class Config:
        json_schema_extra = {
            "example": {
                "previous": "주인공은 친구와 함께 숲을 탐험하고 있었습니다.",
                "answer": "주인공은 용감하게 동굴 안으로 들어가야 해요."
            }
        }

class QuizRequest(BaseModel):
    previous: str = Field(...,json_schema_extra={"example":"숲 초입 나무 밑에서 부스럭 부스럭 소리가 들렸어요. 토로로는 나무로 가까이 다가갔어요. 찍찍찍..찍찍 소리는 점점 커지는데... 맙소사 아기 다람쥐가 나무에서 떨어서 풀 사이에 힘겹게 숨을 쉬고 있었어요."})

class QuizResponse(BaseModel):
    question: str
    option1: str
    option2: str
    option3: str
    option4: str
    answer: str

class DalleImageRequest(BaseModel):
    prompt: str = Field(...,json_schema_extra={"example":"A cute rabbit flying with balloons across the sky"})
    genre: str = Field(...,json_schema_extra={"example":"모험"})


class ControlNetImageRequest(BaseModel):
    prompt: str = Field(..., description="줄거리")
    genre: str = Field(..., description="장르")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A cute rabbit flying with balloons across the sky",
                "genre": "모험"
            }
        }

class TTSRequest(BaseModel):
    voice_key: str = Field(
        ...,
        description="ElevenLabs에서 발급받은 voice_key (예: '9c74576ba45e6852f1c7d03')",
        json_schema_extra={"example": "9c74576ba45e6852f1c7d03"}
    )
    text: str = Field(
        ...,
        description="복제된 음성으로 재생할 텍스트",
        json_schema_extra={"example": "안녕, 오늘은 어떤 이야기를 들려줄까?"}
    )

class DeleteVoiceRequest(BaseModel):
    voice_key: str = Field(
        ...,
        description="삭제할 voice_key",
        json_schema_extra={"example": "9c74576ba45e6852f1c7d03"}
    )
