import os 
import random 
import requests

from io import BytesIO
from typing import Optional

ELEVEN_API_KEY = os.environ["ELEVEN_API_KEY"]

def record_voice(audio_file_path: str, voice_name: str) -> Optional[str]:
    """
    프론트에서 업로드된 녹음 파일과 사용자 지정 음성 이름을 받아 ElevenLabs로 전송하고 voice_id를 반환합니다.
    :param audio_file_path: 로컬에 저장된 녹음 파일 경로
    :return: 생성된 voice_id 또는 None
    """
    try:
        voice_id = clone_voice(audio_file_path, voice_name)
        if voice_id:
            return voice_id
        else:
            print("voice_id 생성 실패")
            return None
    except Exception as e:
        print("오류 발생:", str(e))
        return None


def clone_voice(audio_path: str, voice_name: str) -> Optional[str]:
    """
    ElevenLabs의 voice cloning API에 요청을 보내 사용자 음성을 등록합니다.
    :param audio_path: 로컬에 저장된 음성 파일 경로
    :voice_name: 음성 파일 이름
    :return: 생성된 voice_id 또는 None
    """
    url = "https://api.elevenlabs.io/v1/voices/add"

    headers = {
        "xi-api-key": ELEVEN_API_KEY
    }

    files = {
        "files": open(audio_path, "rb")
    }

    data = {
        "name": voice_name,
        "description": "사용자가 정의한 커스텀 음성입니다.",
        "labels": "{}"
    }

    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        return response.json().get("voice_id")
    else:
        print(response.text)
        return None

def synthesize_voice(voice_id: str, text: str) -> BytesIO:
    """
    주어진 voice_id와 텍스트를 기반으로 ElevenLabs API에 요청하여 음성 데이터를 반환합니다.
    :param voice_id: 등록된 voice_id
    :param text: 음성으로 변환할 텍스트
    :return: 음성 데이터를 담은 BytesIO 스트림
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"음성 합성 실패: {response.status_code} {response.text}")

    return BytesIO(response.content)

def delete_voice(voice_id: str) -> bool:
    """
    ElevenLabs API를 통해 지정된 voice_id를 삭제합니다.
    :param voice_id: 삭제할 voice_id
    :return: 성공 시 True, 실패 시 False
    """
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False
