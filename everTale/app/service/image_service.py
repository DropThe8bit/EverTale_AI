import os
from io import BytesIO
from uuid import uuid4

from ..config import OPENAI_API_KEY
from openai import OpenAI
import requests

import boto3
import torch
from PIL import Image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

# S3 클라이언트 초기화
s3_client = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

# 모델 초기화 (단 한 번만)
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-scribble", torch_dtype=torch.float32
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "dreamlike-art/dreamlike-anime-1.0",
    controlnet=controlnet,
    torch_dtype=torch.float32,
    use_auth_token=HF_TOKEN
).to("mps")

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)

# 디바이스 상태 로그
print("MPS available:", torch.backends.mps.is_available())
print("MPS built:", torch.backends.mps.is_built())


def generate_controlnet_image(sketch_bytes: bytes, prompt: str, genre: str) -> str:
    # 1. 스케치 이미지 전처리
    sketch_image = Image.open(BytesIO(sketch_bytes)).convert("RGB").resize((512, 512))

    # TODO: 장르별 배경 및 분위기 설정할 것

    # 2. 모델 추론
    result = pipe(
        prompt="ultra detailed, dreamy cheerful atmosphere, anime style, soft light, pastel color, " + prompt,
        negative_prompt=(
            "lowres, bad anatomy, blurry, ugly, bad hands, extra fingers, cropped, poorly drawn, nsfw, "
            "bad face, bad eyes, bad mouth, deformed face, disfigured, mutated, extra eyes, extra mouth, "
            "poorly drawn face, ugly face, missing eyes, missing mouth, malformed face, asymmetrical eyes, blurry face"
        ),
        image=sketch_image,
        num_inference_steps=60,
        guidance_scale=12.5,
        controlnet_conditioning_scale=0.8
    )

    # 3. 결과 이미지 메모리 버퍼에 저장
    output_buffer = BytesIO()
    result.images[0].save(output_buffer, format="PNG")
    output_buffer.seek(0)

    filename = f"{uuid4().hex}.png"
    s3_key = f"generated_images/{filename}"

    # S3 업로드
    s3_client.upload_fileobj(
        output_buffer,
        S3_BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": "image/png"}
    )

    # URL로 완성
    image_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

    return image_url


def generate_dalle_image(prompt: str, genre: str) -> str:
    try:
        # 1. 프롬프트에 장르 정보 반영 (선택적)
        combined_prompt = f"{genre} 스타일의 장면, " + prompt

        # 2. OpenAI API로 이미지 생성 요청
        response = client.images.generate(
            model="dall-e-3",
            prompt=combined_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )

        image_url_from_openai = response.data[0].url

    except Exception as e:
        raise Exception(f"OpenAI DALL·E 3 이미지 생성 실패: {e}")

    # 3. 이미지 다운로드
    image_response = requests.get(image_url_from_openai)
    if image_response.status_code != 200:
        raise Exception("OpenAI DALL·E 3 이미지 다운로드 실패")

    image_bytes = BytesIO(image_response.content)

    # 4. S3 업로드
    filename = f"{uuid4().hex}.png"
    s3_key = f"generated_images/{filename}"

    s3_client.upload_fileobj(
        image_bytes,
        S3_BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": "image/png"}
    )

    # 5. S3 URL 반환
    s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    return s3_url
