import os
from io import BytesIO
from uuid import uuid4
from typing import List

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

device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "dreamlike-art/dreamlike-anime-1.0",
    controlnet=controlnet,
    torch_dtype=torch.float32,
    use_auth_token=HF_TOKEN
).to(device)

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)

# 디바이스 상태 로그
print("MPS available:", torch.backends.mps.is_available())
print("MPS built:", torch.backends.mps.is_built())


# 공통: S3 업로드 유틸
def make_s3_key(prefix: str = "generated_images", ext: str = "png") -> str:
    filename = f"{uuid4().hex}.{ext.lstrip('.')}"
    return f"{prefix.rstrip('/')}/{filename}"

def s3_public_url(key: str) -> str:
    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key.lstrip('/')}"

def upload_png_bytes_to_s3(
    file_like: BytesIO,
    key_prefix: str = "generated_images",
    content_type: str = "image/png"
) -> str:
    if hasattr(file_like, "seek"):
        try:
            file_like.seek(0)
        except Exception:
            pass

    key = make_s3_key(prefix=key_prefix, ext="png")

    s3_client.upload_fileobj(
        file_like,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type}
    )
    return s3_public_url(key)

# 이미지 생성 함수들
NEGATIVE_PROMPT = (
    "lowres, bad anatomy, blurry, ugly, bad hands, extra fingers, cropped, poorly drawn, nsfw, "
    "bad face, bad eyes, bad mouth, deformed face, disfigured, mutated, extra eyes, extra mouth, "
    "poorly drawn face, ugly face, missing eyes, missing mouth, malformed face, asymmetrical eyes, blurry face"
)

def generate_init_character_image(
    sketch_bytes: bytes,
    name: str,
    age: int,
    gender: str,
    personalities: List[str],
    image_description: str
) -> str:
    sketch_image = Image.open(BytesIO(sketch_bytes)).convert("RGB").resize((512, 512))

    result = pipe(
        prompt=(
            f"A character named {name}, "
            f"{age} years old, "
            f"{'a boy' if gender.lower() == 'male' else 'a girl'}, "
            f"who is {', '.join(personalities)}. "
            f"{image_description.strip().capitalize()}"
        ),
        negative_prompt=NEGATIVE_PROMPT,
        image=sketch_image,
        num_inference_steps=60,
        guidance_scale=12.5,
        controlnet_conditioning_scale=0.8
    )

    output_buffer = BytesIO()
    result.images[0].save(output_buffer, format="PNG")

    return upload_png_bytes_to_s3(output_buffer, key_prefix="generated_images")

def generate_controlnet_image(sketch_bytes: bytes, prompt: str, genre: str) -> str:
    sketch_image = Image.open(BytesIO(sketch_bytes)).convert("RGB").resize((512, 512))

    result = pipe(
        prompt="ultra detailed, dreamy cheerful atmosphere, anime style, soft light, pastel color, " + prompt,
        negative_prompt=NEGATIVE_PROMPT,
        image=sketch_image,
        num_inference_steps=60,
        guidance_scale=12.5,
        controlnet_conditioning_scale=0.8
    )

    output_buffer = BytesIO()
    result.images[0].save(output_buffer, format="PNG")

    return upload_png_bytes_to_s3(output_buffer, key_prefix="generated_images")

def generate_dalle_image(prompt: str, genre: str) -> str:
    try:
        combined_prompt = f"{genre} 스타일의 장면, " + prompt

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

    image_response = requests.get(image_url_from_openai)
    if image_response.status_code != 200:
        raise Exception("OpenAI DALL·E 3 이미지 다운로드 실패")

    image_bytes = BytesIO(image_response.content)
    return upload_png_bytes_to_s3(image_bytes, key_prefix="generated_images")

