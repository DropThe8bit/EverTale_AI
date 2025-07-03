
from fastapi import APIRouter
from fastapi import File, UploadFile, Form
from fastapi.responses import JSONResponse

from . import dto
from .service import image_service, quiz_service, story_service

router = APIRouter(prefix="/ai")

@router.post("/init", response_model=dto.InitStoryResponse)
def create_init_story(request: dto.InitStoryRequest):
    story = story_service.generate_story_from_character_info(
        genre=request.genre,
        world_view=request.worldView,
        title=request.title,
        name=request.name,
        age=request.age,
        gender=request.gender,
        personalities=request.personalities
    )
    return {"message": story}

@router.post("/next-story", response_model=dto.InitStoryResponse)
def create_next_story(request: dto.NextStoryRequest):
    prompt = story_service.generate_prompt_for_next_story(
        previous=request.previous,
        scene_number=request.sceneNum,
        genre=request.genre,
        title=request.title,
        name=request.characterName,
        age=request.age,
        gender=request.gender,
        personalities=request.personalities
    )
    story = story_service.generate_story(prompt)
    return {"message": story}


@router.post("/question")
def create_question(request: dto.QuestionRequest):
    prompt = (
        f"이전 장면:\n{request.previous}\n\n"
        "아이의 참여를 유도하기 위해 질문 하나를 던져줘. 예를 들어 '주인공은 어떻게 해야 할까?'처럼 "
        "선택이나 상상을 이끌어낼 수 있도록 해줘."
    )
    question = story_service.generate_story(prompt)
    return {"message": question}

@router.post("/next-from-answer")
def create_next_story_with_answer(request: dto.NextFromAnswerRequest):
    prompt = (
        f"이전 장면:\n{request.previous}\n"
        f"아이의 대답: {request.answer}\n\n"
        "이 대답을 반영해서 다음 장면의 줄거리를 상상력 있게 이어서 써줘. 2~3문장으로 자연스럽게 전개해줘."
    )
    story = story_service.generate_story(prompt)
    return {"message": story}


@router.post("/generate-controlnet-image")
async def generate_controlnet_image(
    sketch: UploadFile = File(...),
    prompt: str = Form(...),
    genre: str = Form(...)
):
    sketch_bytes = await sketch.read()
    image_url = image_service.generate_controlnet_image(sketch_bytes, prompt, genre)
    return JSONResponse(content={"image_url": image_url})

@router.post("/generate-dalle-image")
async def generate_dalle_image(request: dto.DalleImageRequest):
    try:
        image_url = image_service.generate_dalle_image(request.prompt, request.genre)
        return JSONResponse(content={"image_url": image_url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/generate-quiz", response_model=dto.QuizResponse)
def create_quiz(request: dto.QuizRequest):
    try:
        quiz = quiz_service.generate_quiz_from_story(request.previous)
        return quiz
    except ValueError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
