import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
import os
from io import BytesIO
from PIL import Image
from pathlib import Path
from uuid import uuid4

# MPS 사용 가능 여부 확인
print("MPS available:", torch.backends.mps.is_available())
print("MPS built:", torch.backends.mps.is_built())

# 모델 초기화는 모듈 단에서 1회만
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-scribble", torch_dtype=torch.float32
)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "Lykon/dreamshaper-8",
    controlnet=controlnet,
    torch_dtype=torch.float32,
    use_auth_token=os.getenv("HF_TOKEN")
).to("mps")

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)

# 이미지 저장 경로
BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_SAVE_DIR = Path("static/images")
IMAGE_SAVE_DIR.mkdir(parents=True, exist_ok=True)


def generate_image_from_sketch(sketch_bytes: bytes, prompt: str) -> str:
    # 스케치 이미지 전처리
    sketch_image = Image.open(BytesIO(sketch_bytes)).convert("RGB").resize((512, 512))

    # 모델 추론
    result = pipe(
        prompt=prompt,
        negative_prompt="lowres, bad anatomy, blurry, ugly, bad hands, extra fingers, poorly drawn, nsfw",
        image=sketch_image,
        num_inference_steps=60,
        guidance_scale=12.5,
        controlnet_conditioning_scale=0.8
    )

    # 파일 이름 및 경로 지정
    filename = f"{uuid4().hex}.png"
    file_path = IMAGE_SAVE_DIR / filename

    # 이미지 저장
    result.images[0].save(file_path, format="PNG")

    # 접근 가능한 이미지 URL 반환
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    return f"{BASE_URL}/static/images/{filename}"
