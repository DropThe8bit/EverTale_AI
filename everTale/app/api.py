
import os, shutil, uuid
from typing import List
from fastapi import APIRouter
from fastapi import File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse

from . import dto
from .service import image_service, quiz_service, story_service, voice_cloning_service, yolo_service

router = APIRouter()

@router.post("/init", response_model=dto.InitStoryResponse)
def create_init_story(request: dto.InitStoryRequest):
    story = story_service.generate_story_from_character_info(
        genre=request.genre,
        world_view=request.worldView,
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
        page_number=request.pageNum,
        genre=request.genre,
        name=request.name,
        age=request.age,
        gender=request.gender,
        personalities=request.personalities
    )
    story = story_service.generate_story(prompt)
    return {"message": story}


@router.post("/question")
def create_question(request: dto.NextStoryRequest):
    question = story_service.generate_question_for_next_story(
        previous=request.previous,
        page_number=request.pageNum,
        genre=request.genre,
        name=request.name,
        age=request.age,
        gender=request.gender,
        personalities=request.personalities
    )
    return {"message": question}

@router.post("/next-from-answer")
def create_next_story_with_answer(request: dto.NextFromAnswerRequest):
    story = story_service.generate_story_from_question_and_answer(
        question=request.question,
        answer=request.answer,
        previous=request.previous,
        page_number=request.pageNum,
        genre=request.genre,
        name=request.name,
        age=request.age,
        gender=request.gender,
        personalities=request.personalities
    )
    return {"message": story}

@router.post("/init-character-image")
async def init_character_image(
    sketch: UploadFile = File(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    personalities: List[str] = Form(...),
    image_description: str = Form(...)
):
    sketch_bytes = await sketch.read()
    image_url = image_service.generate_init_character_image(sketch_bytes, name, age, gender, personalities,image_description)
    return JSONResponse(content={"image_url": image_url})

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
    
@router.post("/voice/register")
async def upload_voice(
    file: UploadFile = File(...),
    voice_name: str = Form(...)
):
    try:
        temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        temp_path = os.path.join("/tmp", temp_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        voice_id = voice_cloning_service.record_voice(temp_path, voice_name)

        os.remove(temp_path)

        if voice_id:
            return JSONResponse(content={"voice_id": voice_id})
        else:
            return JSONResponse(status_code=500, content={"error": "Voice cloning failed."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/voice/play", summary="음성 합성 API", description="voice_key와 텍스트를 받아 음성 스트림을 반환합니다.")
def play_voice(request: dto.TTSRequest):
    try:
        audio_stream = voice_cloning_service.synthesize_voice(
            request.voice_key,
            request.text
        )
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    
    except ValueError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/voice/delete", summary="음성 삭제 API", description="voice_key를 받아 ElevenLabs에서 해당 음성을 삭제합니다.")
def delete_voice(request: dto.DeleteVoiceRequest):
    try:
        result = voice_cloning_service.delete_voice(request.voice_key)

        if result:
            return JSONResponse(content={"message": "음성이 성공적으로 삭제되었습니다."})
        else:
            return JSONResponse(status_code=500, content={"error": "삭제 실패 또는 voice_key가 존재하지 않습니다."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@router.post("/yolo", summary="객체 탐지 API", description="이미지를 리스트로 받아 객체를 탐지하고 이미지 index와 좌표를 반환합니다.")
def detect_object(request: dto.YOLOImageUrlsRequest):
    try:
        object = yolo_service.detect_object(request.image_urls)
        return JSONResponse(content=object)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})