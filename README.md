# EverTale_AI
🏅 캡스톤 디자인 경진 대회 은상 수상 (2025.12) 🏅 <br>
🏅 졸업 프로젝트 포스터 세션 우수상 수상 (2025.12) 🏅 <br>

## 🗣️ 음성 복제 : ElevenLabs

ElevenLabs는 고품질의 감정 표현 가능한 Text-to-Speech (TTS) API를 제공하는 음성 생성 플랫폼입니다. 딥러닝 기반의 자연어 처리 기술과 음향 모델링 기술이 결합되어 사람이 말하는 것과 유사한 자연스러운 음성을 생성할 수 있습니다.

<br>

### ✅ 사용 기술 요소 및 소트프웨어 패키지

| 기술 요소 | 설명 |
| --- | --- |
| **TTS 엔진** | ElevenLabs의 자체 개발 딥러닝 기반 TTS 모델. 문장의 의미와 맥락에 따라 감정과 억양을 자연스럽게 조절 |
| **AI 음성 클로닝** | 사용자의 음성을 학습하여 개별 맞춤형 보이스 생성 가능 (VoiceLab 등 활용 시) |
| **API 기반 접근** | RESTful API 호출을 통해 음성 생성 및 결과 수신 가능 |
| **Python SDK** | `elevenlabs` 라이브러리를 통해 API 호출을 간편하게 구현 가능 |
| **음성 출력 형식** | 기본적으로 `.wav` 형식으로 제공되고 사용 목적에 따라 `.mp3`로 변환 가능 |

<br>

### ✅ 주요 API / 모델 URL

- **ElevenLabs**: https://docs.elevenlabs.io

<br>
<hr>
<br>

## 📚 스토리 생성 : ChatGPT API + Stable Diffusion + ControlNet

이 프로젝트는 어린이 참여형 동화 생성 서비스로, 사용자의 입력과 아이의 그림을 활용하여 AI가 자동으로 줄거리와 그림을 생성합니다.  
- **ChatGPT API (GPT-4o)**: 주인공 정보를 기반으로 동화 줄거리를 생성하고, 아이의 응답을 반영하여 줄거리를 확장합니다.  
- **Stable Diffusion**: 텍스트 프롬프트를 기반으로 고품질 이미지를 생성하는 **latent diffusion 모델**입니다.  
- **ControlNet**: 사용자의 scribble(낙서)나 **스케치 이미지**를 조건으로 활용하여, 그림의 형태를 보존한 채 Stable Diffusion 결과를 제어합니다.  
이 세 가지 기술을 조합하여, 사용자가 입력한 줄거리와 아이의 그림에 따라 **일관된 스타일과 내용**의 동화를 자동으로 구성할 수 있습니다.

<br>

### ✅ 사용 기술 요소 및 소프트웨어 패키지

| 기술 / 도구 | 역할 | 설명 |
| --- | --- | --- |
| **Python** | 주 개발 언어 | Google Colab 기반 스크립트 작성 |
| **OpenAI GPT API** | 텍스트 생성 | GPT-4o 사용하여 줄거리, 질문, 응답 기반 이어쓰기 처리 |
| **Hugging Face diffusers** | 이미지 생성 | Stable Diffusion + ControlNet 통합 파이프라인 |
| **ControlNet (scribble)** | 조건 이미지 반영 | 아이의 그림(선 그림, 낙서)을 기반으로 이미지 생성 가이드 |
| **Lykon/dreamshaper-8** | 모델 기반 | 감성적이고 부드러운 그림 스타일을 제공하는 SD 모델 |
| **Google Colab** | 실행 환경 | 사용자 입력, 파일 업로드, 결과 출력 등 처리 |
| **Pillow (PIL)** | 이미지 처리 | 결과 이미지 저장 및 리사이징 등 |
| **Huggingface Hub** | 모델 관리 | 모델 다운로드 및 인증 처리 |

<br>

### ✅ 주요 API / 모델 URL

- **OpenAI GPT API**: https://platform.openai.com/docs/guides/gpt  
- **Hugging Face diffusers (Stable Diffusion + ControlNet)**: https://huggingface.co/docs/diffusers/index  
- **ControlNet - scribble 모델**: https://huggingface.co/lllyasviel/sd-controlnet-scribble  
- **Dreamshaper 모델 (Stable Diffusion 기반)**: https://huggingface.co/Lykon/dreamshaper-8

<br>
<hr>
<br>

## 🖼️ 이스터에그 : 객체탐지 Yolov8 모델

일러스트 속 객체 탐지에 최적화된 YOLOv8 모델을 파인튜닝하여, 일러스트 내 특정 객체 좌표에 부모의 사랑이 담긴 음성 메시지를 숨겨둡니다. 아이가 동화를 읽으며 그림을 클릭할 때, 해당 좌표가 감지되면 숨겨진 이스터에그(음성 메시지)가 재생되어 놀이 요소처럼 즐길 수 있습니다.

<br>

### ✅ 사용 기술 요소 및 소트프웨어 패키지

| 기술 요소 / 도구 | 역할 | 설명 |
| --- | --- | --- |
| **Python** | 주 개발 언어 | Google Colab 기반 스크립트 작성 |
| **Google Colab** | 실행 환경 | 모델 파인튜닝, 사용자 입력, 파일 업로드, 결과 출력 등 처리 |
| **Yolov8 Model** | AI모델 | 실시간 객체 탐지 분야에서 매우 높은 정확도와 속도를 동시에 목표로 하는 모델 |

<br>

### ✅  모델 URL

- **Yolov8**: https://docs.ultralytics.com/ko/models/yolov8

---
## 디렉토리 구조
```
evertale_ai/
├─ .github/ # Github Actions
│
├─ everTale/
│  ├─ app/
│  │  ├─ service # 기능별 비즈니스 로직 모음
│  │  ├─ api.py # 엔드포인트 정의 및 서비스 호출 연결
│  │  ├─ config.py # 환경변수 로딩 및 설정값 관리
│  │  ├─ dto.py # 요청/응답 DTO 정의
│  │  ├─ main.py # 서버 엔트리포인트
│  │  └─ __init__.py
│  ├─ static # 정적 리소스 저장
│  ├─ .env # 로컬 실행용 환경변수
|  └─ requirements.txt # Python 의존성 목록
│
├─ models # YOLO 모델 가중치/실험 파일 
├─ Dockerfile
├─ .gitignore
└─ README.md
```
- `.github/`: CI/CD(예: GitHub Actions 배포), 이슈/PR 템플릿 등 협업 자동화 설정
- `everTale/`: FastAPI 기반 AI 서버 코드가 들어있는 메인 패키지
- `everTale/app/`: API 엔드포인트(`api.py`)와 설정(`config.py`), 요청/응답 스키마(`dto.py`), 서버 시작점(`main.py`), 그리고 기능 로직(`service/`)
- `everTale/static/`: 실행 중 필요한 정적 파일(샘플/임시 결과물 등)을 저장하는 용도
- `everTale/.env`: OpenAI 키, HuggingFace 토큰, 모델 경로 등 실행 환경변수를 담는 파일
- `requirements.txt`: 로컬 실행을 위한 파이썬 라이브러리 의존성 목록
- `models/`: YOLO 등 모델 가중치 파일(.pt)과 실험/검증 노트북(.ipynb)을 보관
- `Dockerfile`: 동일한 환경에서 실행/배포가 가능하도록 도커 이미지를 빌드하는 설정

---
## 로컬 실행 방법
### 1. 레포 내려받기(git clone)
```
git clone https://github.com/DropThe8bit/EverTale_AI.git evertale_ai
cd evertale_ai
```
### 2. 가상환경 설치
```
conda create -n evertale-ai python=3.10 -y
conda activate evertale-ai
```
### 3. requirements.txt 설치
```
pip install --upgrade pip
pip install -r everTale/requirements.txt
```
### 4. .env 파일 생성
- 실행 환경변수를 채워넣습니다.
```
OPENAI_API_KEY=
HF_TOKEN=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
S3_BUCKET_NAME=
S3_BASE_URL=
ELEVEN_API_KEY=
YOLO_MODEL_PATH=
```
### 5. 로컬 서버 실행
- 터미널에 아래 코드를 작성해 직접 실행합니다.
```
cd everTale
uvicorn app.main:app --reload
```

