import os
from io import BytesIO
from uuid import uuid4
from typing import List
import contextlib
from openai import OpenAI
import requests
from typing import Tuple, Optional
import re

import boto3
import torch
from PIL import Image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from diffusers.models.attention_processor import AttnProcessor
from dotenv import load_dotenv


# 환경 변수 로드
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)



# S3 유틸
s3_client = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

def make_s3_key(prefix: str = "generated_images", ext: str = "png") -> str:
    filename = f"{uuid4().hex}.{ext.lstrip('.')}"
    return f"{prefix.rstrip('/')}/{filename}"

def s3_public_url(key: str) -> str:
    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key.lstrip('/')}"

def upload_png_bytes_to_s3(buf: BytesIO, key_prefix: str = "generated_images") -> str:
    key = make_s3_key(prefix=key_prefix, ext="png")
    buf.seek(0)
    s3_client.upload_fileobj(
        buf,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "image/png"},
    )
    return s3_public_url(key)


# 디바이스 정책 (CUDA/MPS만 허용, CPU 금지)
def ensure_device(stage: str):
    if torch.cuda.is_available():
        dev = "cuda"
        dt = torch.float16
        print(f"[INFO] CUDA detected during {stage}: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        dev = "mps"
        dt = torch.float16
        print(f"[INFO] Apple Silicon MPS detected during {stage}")
    else:
        msg = f"[ERROR] No GPU backend (CUDA/MPS) during {stage}. CPU is not allowed."
        print(msg)
        raise RuntimeError(msg)
    return dev, dt

device, dtype = ensure_device("startup")

# CUDA 최적화 옵션
if device == "cuda":
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.benchmark = True


# 보조 유틸(오토캐스트, 검증)
def amp_autocast():
    if device == "cuda":
        return torch.autocast(device_type="cuda", dtype=torch.float16)
    return contextlib.nullcontext()

def require_gpu(stage: str):
    ok = torch.cuda.is_available() or (
        torch.backends.mps.is_available() and torch.backends.mps.is_built()
    )
    if not ok:
        msg = f"[ERROR] GPU backend lost during {stage}. CPU is not allowed."
        print(msg)
        raise RuntimeError(msg)

def param_on_device(module, dev_type: str) -> bool:
    try:
        first = next(module.parameters())
        return getattr(first, "device", None) and first.device.type == dev_type
    except StopIteration:
        return True
    except Exception:
        return all(
            getattr(p, "device", None) and p.device.type == dev_type
            for p in module.parameters()
        )

def assert_pipeline_on_device(pipe_):
    if not param_on_device(pipe_.unet, device):
        raise RuntimeError(f"[ERROR] UNet not on {device}.")
    cn = getattr(pipe_, "controlnet", None)
    if cn is not None:
        if isinstance(cn, list):
            for i, c in enumerate(cn):
                if not param_on_device(c, device):
                    raise RuntimeError(f"[ERROR] ControlNet[{i}] not on {device}.")
        else:
            if not param_on_device(cn, device):
                raise RuntimeError(f"[ERROR] ControlNet not on {device}.")
    if getattr(pipe_, "vae", None) is not None and not param_on_device(pipe_.vae, device):
        raise RuntimeError(f"[ERROR] VAE not on {device}.")


# 모델 경로 해상(캐시 우선)
def resolve_path(repo_id: str, default_id: Optional[str] = None) -> str:
    base = os.environ.get("HF_HOME", "/models/hf-cache")
    local = os.path.join(base, repo_id)
    return local if os.path.exists(local) else (default_id or repo_id)


# 파이프라인 로드
def load_pipeline():
    # ControlNet: Scribble
    ensure_device("loading pipeline")
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-scribble",
        torch_dtype=dtype,
        token=HF_TOKEN
    )

    # Base model: dreamshaper-8 (SD1.5)
    pipe_ = StableDiffusionControlNetPipeline.from_pretrained(
        "Lykon/dreamshaper-8",
        controlnet=controlnet,
        torch_dtype=dtype,
        token=HF_TOKEN,
    ).to(device)

    # 스케줄러: UniPC (코랩과 동일화)
    pipe_.scheduler = UniPCMultistepScheduler.from_config(pipe_.scheduler.config)
    pipe_.to(device)
    assert_pipeline_on_device(pipe_)
    return pipe_

pipe = load_pipeline()

def _tune_attention_for_device(pipe_):
    if device == "mps":
        try:
            pipe_.unet.set_attn_processor(AttnProcessor())
            if hasattr(pipe_, "controlnet") and pipe_.controlnet is not None:
                if isinstance(pipe_.controlnet, list):
                    for c in pipe_.controlnet:
                        c.set_attn_processor(AttnProcessor())
                else:
                    pipe_.controlnet.set_attn_processor(AttnProcessor())
            print("[INFO] MPS: AttnProcessor applied")
        except Exception as e:
            print("[WARN] MPS attention tuning failed:", e)
    elif device == "cuda":
        try:
            pipe_.enable_xformers_memory_efficient_attention()
            print("[INFO] xFormers attention enabled")
        except Exception:
            try:
                from torch.backends.cuda import sdp_kernel
                sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=True)
                print("[INFO] SDPA: flash disabled, math/mem_efficient enabled")
            except Exception as e:
                print("[WARN] Could not adjust SDPA kernels:", e)


# LoRA 적용
def load_lora(pipe_):
    adapter_name = "screencap"
    pipe_.load_lora_weights(
        "LarryAIDraw/animeScreencapStyle_v230epochs",
        weight="animeScreencapStyle_v230epochs.safetensors",
        adapter_name=adapter_name
    )
    pipe_.set_adapters("screencap", adapter_weights=0.4)
    return pipe_

pipe = load_lora(pipe)


# 프롬프트/파라미터
STYLE_SUFFIX_ANIMAL = (
    "child friendly, storybook, ultra detailed, dreamy cheerful atmosphere, "
    "cute animal illustration, storybook animal art, cartoon animal style, "
    "soft light, pastel color, soft shading, masterpiece, best quality"
)
STYLE_SUFFIX_HUMAN = "child friendly, storybook, ultra detailed, dreamy cheerful atmosphere, anime style, anime face, soft light, pastel color, soft shading, masterpiece, best quality"
STYLE_SUFFIX_SCN  = "child friendly, storybook, ultra detailed, dreamy cheerful atmosphere, anime style, anime face, soft light, pastel color, soft shading, masterpiece, best quality"

NEGATIVE_PROMPT = (
    "nsfw, nudity, naked, explicit, erotic, sensual, suggestive, sexual, cleavage, lingerie, underwear, "
    "swimsuit, bikini, see-through, revealing outfit, exposed skin, body focus, fetish, lewd, "
    "kissing, intimate pose, provocative pose, bed scene, bedroom suggestive, "
    "adult content, 18+, hentai, porn, obscene, "
    "bad anatomy, bad hands, extra fingers, lowres, blurry, deformed, mutated, cropped, poorly drawn, asymmetrical eyes"
)

GENRE_PROMPTS = {
    "adventure":  "((adventurous whimsical tone)), magical atmosphere, soft pastel palette, sense of discovery, wonder",
    "friendship": "((warm cheerful tone)), playful cooperative mood, bright friendly colors, laughter and smiles",
    "moral":      "((calm thoughtful tone)), gentle harmonious mood, soft natural palette, reflective and kind",
    "family":     "((cozy affectionate tone)), warm golden light, homely comfort, caring and supportive mood",
}

GENRE_NEGATIVES = {
    "adventure":  "overly dark gritty mood, heavy dystopian vibes",
    "friendship": "gloomy or hostile tone, aggressive conflict",
    "moral":      "noisy chaotic mood, harsh rushed pacing",
    "family":     "cold distant mood, harsh neon glare",
}

GENRE_PARAMS = {
    "adventure": {"controlnet_conditioning_scale": 0.8, "guidance_scale": 12},
    "friendship": {"controlnet_conditioning_scale": 0.8, "guidance_scale": 12},
    "moral": {"controlnet_conditioning_scale": 0.8, "guidance_scale": 12},
    "family": {"controlnet_conditioning_scale": 0.8, "guidance_scale": 12},
}

_SCN_SYSTEM = (
    "You are a prompt engineer for Stable Diffusion with ControlNet (scribble/line-art). "
    "Rewrite the user's Korean scene description into a compact, high-quality ENGLISH prompt. "
    "Constraints:\n"
    "- Keep it short and vivid (max ~30 tokens), comma-separated fragments.\n"
    "- Prefer nouns/adjectives; minimize verbs/sentences.\n"
    "- Child-friendly, warm, imaginative tone; avoid adult/violent content.\n"
    "- Emphasize line-art, clean outlines, obeying sketch contours (ControlNet scribble).\n"
    "- Mention main subject, setting, mood, and key props if critical.\n"
    "- Do NOT include negative prompts, aspect ratio, steps, seeds, or quotes.\n"
    "- Output ONLY the prompt line, no extra text."
)

def _shorten_words(text: str, max_words: int) -> str:
    w = text.split()
    return " ".join(w[:max_words])

def _select_top_traits(traits, k=3):
    return ", ".join([t.strip() for t in traits if t.strip()][:k])

def build_character_prompt(name: str, age: int, gender: str, personalities: list, image_description: str) -> str:
    gender_lower = gender.lower()

    if gender_lower.startswith("m"):
        gender_short = "male"
    elif gender_lower.startswith("f"):
        gender_short = "female"
    elif gender_lower.startswith("a"):
        gender_short = "animal"
    else:
        gender_short = "female"

    image_desc_short = build_scene_prompt(image_description.strip())
    core = f"one character only, {gender_short}, {image_desc_short}"

    style_suffix = STYLE_SUFFIX_ANIMAL if gender_short == "animal" else STYLE_SUFFIX_HUMAN

    prompt = f"{core}, {style_suffix}"
    return (prompt[:320]).rstrip(", ")

def _cleanup_prompt(s: str, max_len: int = 320) -> str:
    if not s:
        return s
    # 줄바꿈 → 콤마/공백
    s = s.replace("\r", "\n")
    s = ", ".join(line.strip() for line in s.splitlines() if line.strip())

    # 따옴표/백틱/양끝 공백 제거
    s = s.strip().strip('"').strip("'").strip("`").strip()

    # 문장형 마침표가 끝에 붙으면 제거(조각 나열을 선호)
    s = re.sub(r"[\.!?]\s*$", "", s)

    # 중복 콤마/공백 정리
    s = re.sub(r"\s*,\s*,+", ", ", s)     # ,, → ,
    s = re.sub(r"\s{2,}", " ", s)         # 다중 공백 → 1칸
    s = re.sub(r"\s*,\s*", ", ", s)       # 콤마 양옆 공백 표준화
    s = re.sub(r"(^,\s*|\s*,\s*$)", "", s)  # 앞/뒤 콤마 제거

    # 길이 제한
    s = s[:max_len].rstrip(", ").rstrip()
    return s

def build_scene_prompt(prompt_main: str) -> str:
    try:
        print("[build_scene_prompt] prompt_main:", repr(prompt_main))  # 입력 확인

        resp = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            messages=[
                {"role": "system", "content": _SCN_SYSTEM},
                {"role": "user", "content": prompt_main.strip()},
            ],
            timeout=20,  # seconds
        )

        print("[build_scene_prompt] raw resp:", resp)  # 전체 응답 확인

        text = resp.choices[0].message.content or ""
        print("[build_scene_prompt] extracted text:", repr(text))  # 모델이 뱉은 원문

        text = _cleanup_prompt(text, max_len=320)
        print("[build_scene_prompt] cleaned text:", repr(text))  # 정제된 프롬프트

        if not text:
            print("[build_scene_prompt] cleaned text empty, returning original.")
            return prompt_main

        print("[build_scene_prompt] returning final:", repr(text))
        return text

    except Exception as e:
        print("[build_scene_prompt] Exception:", e)
        return _cleanup_prompt(prompt_main, max_len=320)


def width_height():
    if device == "cuda":
        return 768, 768
    elif device == "mps":
        return 768, 768
    raise RuntimeError("[ERROR] width_height(): CPU path reached")


# 이미지 생성 API 로직
def generate_init_character_image(
    sketch_bytes: bytes,
    name: str,
    age: int,
    gender: str,
    personalities: List[str],
    image_description: str,
) -> str:
    require_gpu("init character image generation")

    sketch_image = Image.open(BytesIO(sketch_bytes)).convert("RGB").resize((512, 512))
    prompt = build_character_prompt(name, age, gender, personalities, image_description)

    print("[prompt]: {prompt}".format(prompt=prompt))
    width, height = width_height()

    with torch.inference_mode(), amp_autocast():
        result = pipe(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            image=sketch_image,
            num_inference_steps=50,
            guidance_scale=12.5,
            controlnet_conditioning_scale=0.8,
            width=width,
            height=height,
        )

    buf = BytesIO()
    result.images[0].save(buf, format="PNG")
    return upload_png_bytes_to_s3(buf, key_prefix="generated_images")

def generate_controlnet_image(sketch_bytes: bytes, prompt: str, genre: str) -> str:
    require_gpu("controlnet image generation")

    sketch_image = Image.open(BytesIO(sketch_bytes)).convert("RGB").resize((512, 512))
    width, height = width_height()

    base_prompt = build_scene_prompt(prompt)

    full_prompt, genre_negative, genre_params = compose_prompts(base_prompt, genre)
    prompt = f"{full_prompt}, {STYLE_SUFFIX_HUMAN}"
    print("[prompt]: {prompt}".format(prompt=prompt))

    negative_prompt = merge_negative_prompt(NEGATIVE_PROMPT, genre_negative)
    guidance_scale = genre_params.get("guidance_scale")
    control_scale = genre_params.get("controlnet_conditioning_scale")
    print("[genre]",genre)
    print("[genre_param]",genre_params)


    with torch.inference_mode(), amp_autocast():
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=sketch_image,
            num_inference_steps=50,
            guidance_scale=guidance_scale,
            controlnet_conditioning_scale=control_scale,
            width=width,
            height=height,
        )

    buf = BytesIO()
    result.images[0].save(buf, format="PNG")
    return upload_png_bytes_to_s3(buf, key_prefix="generated_images")

def normalize_genre(genre: str) -> str:
    g = genre.strip().lower()
    return g

def compose_prompts(base_prompt: str, genre: str) -> Tuple[str, Optional[str], dict]:
    key = normalize_genre(genre)
    genre_add = GENRE_PROMPTS.get(key)
    genre_neg = GENRE_NEGATIVES.get(key)
    params = GENRE_PARAMS.get(key, {})

    if genre_add:
        full = f"{base_prompt}, {genre_add}"
    else:
        full = base_prompt

    return full, genre_neg, params

def merge_negative_prompt(base_negative: Optional[str], genre_negative: Optional[str]) -> Optional[str]:
    if base_negative and genre_negative:
        return f"{base_negative}, {genre_negative}"
    return base_negative or genre_negative

def generate_dalle_image(prompt: str) -> str:
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format="url",
        )
        image_url_from_openai = response.data[0].url
    except Exception as e:
        raise Exception(f"OpenAI DALL·E 3 이미지 생성 실패: {e}")

    image_response = requests.get(image_url_from_openai)
    if image_response.status_code != 200:
        raise Exception("OpenAI DALL·E 3 이미지 다운로드 실패")

    image_bytes = BytesIO(image_response.content)
    return upload_png_bytes_to_s3(image_bytes, key_prefix="generated_images")
