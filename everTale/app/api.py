from fastapi import APIRouter
from app.service import generate_story

router = APIRouter()

@router.get("/story")
def get_story(prompt: str):
    story = generate_story(prompt)
    return {"story": story}
