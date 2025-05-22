# EverTale_AI

## 음성 복제 : ElevenLabs
ElevenLabs는 고품질의 감정 표현 가능한 Text-to-Speech (TTS) API를 제공하는 음성 생성 플랫폼입니다. 딥러닝 기반의 자연어 처리 기술과 음향 모델링 기술이 결합되어 사람이 말하는 것과 유사한 자연스러운 음성을 생성할 수 있습니다.


### 사용 기술 요소 및 소트프웨어 패키지
| 기술 요소 | 설명 |
| --- | --- |
| **TTS 엔진** | ElevenLabs의 자체 개발 딥러닝 기반 TTS 모델. 문장의 의미와 맥락에 따라 감정과 억양을 자연스럽게 조절 |
| **AI 음성 클로닝** | 사용자의 음성을 학습하여 개별 맞춤형 보이스 생성 가능 (VoiceLab 등 활용 시) |
| **API 기반 접근** | RESTful API 호출을 통해 음성 생성 및 결과 수신 가능 |
| **Python SDK** | `elevenlabs` 라이브러리를 통해 API 호출을 간편하게 구현 가능 |
| **음성 출력 형식** | 기본적으로 `.wav` 형식으로 제공되고 사용 목적에 따라 `.mp3`로 변환 가능 |


### 주요 API / 모델 URL
- **ElevenLabs**: https://docs.elevenlabs.io

---
## 스토리 생성 : ChatGPT API + Stable Diffusion + ControlNet
이 프로젝트는 어린이 참여형 동화 생성 서비스로, 사용자의 입력과 아이의 그림을 활용하여 AI가 자동으로 줄거리와 그림을 생성합니다.
- **ChatGPT API (GPT-4o)**: 주인공 정보를 기반으로 동화 줄거리를 생성하고, 아이의 응답을 반영하여 줄거리를 확장합니다.
- **Stable Diffusion**: 텍스트 프롬프트를 기반으로 고품질 이미지를 생성하는 **latent diffusion 모델**입니다.
- **ControlNet**: 사용자의 scribble(낙서)나 **스케치 이미지**를 조건으로 활용하여, 그림의 형태를 보존한 채 Stable Diffusion 결과를 제어합니다.
이 세 가지 기술을 조합하여, 사용자가 입력한 줄거리와 아이의 그림에 따라 **일관된 스타일과 내용**의 동화를 자동으로 구성할 수 있습니다.


### 사용 기술 요소 및 소프트웨어 패키지
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


### 주요 API / 모델 URL
- **OpenAI GPT API**: https://platform.openai.com/docs/guides/gpt
- **Hugging Face diffusers (Stable Diffusion + ControlNet)**: https://huggingface.co/docs/diffusers/index
- **ControlNet - scribble 모델**: https://huggingface.co/lllyasviel/sd-controlnet-scribble
- **Dreamshaper 모델 (Stable Diffusion 기반)**: https://huggingface.co/Lykon/dreamshaper-8
