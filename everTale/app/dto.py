from typing import List
from pydantic import BaseModel, Field

class InitStoryRequest(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "토토로의 모험 여행"})
    characterName: str = Field(..., json_schema_extra={"example": "토토로"})
    age: int = Field(..., json_schema_extra={"example": 8})
    gender: str = Field(..., json_schema_extra={"example": "female"})
    personalities: List[str] = Field(..., json_schema_extra={"example": ["용감함", "씩씩함"]})


class InitStoryResponse(BaseModel):
    message: str

class NextStoryRequest(BaseModel):
    previous: str = Field(..., json_schema_extra={"example": "토토로는 첫 여행지로 북부의 마탑으로 향했어요. 그녀는 마법을 배우고 싶어해요"})
    title: str = Field(..., json_schema_extra={"example": "토토로의 모험 여행"})
    characterName: str = Field(..., json_schema_extra={"example": "토토로"})
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