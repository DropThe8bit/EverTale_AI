# 1. 권장 베이스: CUDA 포함 PyTorch 런타임
FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

# OpenCV 헤드리스 등에 필요한 OS 패키지
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender1 && rm -rf /var/lib/apt/lists/*

# HF 캐시 + PyTorch 메모리 튜닝(선택)
ENV HF_HOME=/models/hf-cache \
    HUGGINGFACE_HUB_CACHE=/models/hf-cache \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 의존성만 먼저 복사 → 캐시 최대 활용
COPY everTale/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt \
 && pip install --no-cache-dir opencv-python-headless ultralytics

# 모델 파일을 이미지에 포함
COPY models/my_yolo_model.pt /models/my_yolo_model.pt
ENV YOLO_MODEL_PATH=/models/my_yolo_model.pt

# 4. 전체 코드 복사
COPY . /app

# 5. 컨테이너가 열 포트 설정
EXPOSE 8000

# 6. FastAPI 실행 (앱 위치가 app/main.py)
CMD ["uvicorn", "everTale.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
