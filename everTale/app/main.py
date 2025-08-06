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
