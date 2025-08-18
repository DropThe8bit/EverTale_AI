from ultralytics import YOLO
from typing import List, Dict, Any

import os
import cv2
import random
import requests
import numpy as np

YOLO_MODEL_PATH = os.environ["YOLO_MODEL_PATH"]

def load_model() -> YOLO:
    try:
        model = YOLO(YOLO_MODEL_PATH)
        print("모델이 성공적으로 로드되었습니다.")
        return model
    except Exception as e:
        print(f"모델 로드 중 오류가 발생했습니다: {e}")
        return None

def _url_to_bgr(url: str) -> np.ndarray:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    arr = np.frombuffer(resp.content, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"이미지 디코딩 실패: {url}")
    return img

def detect_object(image_paths: List[str]) -> Dict[str, Any]:
    """
    입력: 이미지 URL 리스트(최대 8장)
    처리: 모든 이미지를 탐지 → (이미지idx, 객체좌표) 후보들을 모은 뒤 → 랜덤으로 1개 선택
    출력: {"index": int, "url":..., "detection": {"center_x":..., "center_y":..., "half_width":..., "half_height":...}}
          탐지 후보가 전혀 없으면 {"index": None, "url": None, "detection": None}
    """
    model = load_model()
    urls = image_paths[:8]
    candidates: List[Dict[str, Any]] = []

    for idx, url in enumerate(urls):
        try:
            img = _url_to_bgr(url)
            results = model.predict(source=img, verbose=False)
            if not results or results[0].boxes is None or results[0].boxes.shape[0] == 0:
                continue

            for box in results[0].boxes.xyxy:
                xmin, ymin, xmax, ymax = box
                center_x = float((xmin + xmax) / 2.0)
                center_y = float((ymin + ymax) / 2.0)
                half_width = float((xmax - xmin) / 2.0)
                half_height = float((ymax - ymin) / 2.0)

                candidates.append({
                    "index": idx+1,
                    "url": url,
                    "detection": {
                        "xCoordinate": center_x,
                        "yCoordinate": center_y,
                        "width": half_width,
                        "height": half_height,
                    }
                })
        except Exception:
            continue

    if not candidates:
        return {"index": None, "url": None, "detection": None}

    chosen = random.choice(candidates)
    return chosen