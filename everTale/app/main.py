from fastapi import FastAPI
from .api import router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(root_path="/ai")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost:8080"] 등으로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "EverTale AI 서버가 정상 실행 중입니다."}

@app.get("/debug/cuda")
def cuda_health():
    import torch, os
    return {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count(),
        "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None,
        "visible_devices": os.getenv("NVIDIA_VISIBLE_DEVICES", "")
    }
