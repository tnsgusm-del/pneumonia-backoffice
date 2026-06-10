import os
from pathlib import Path
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

# ==========================================
# 1. 페어 과제 기반 SimpleCNN 아키텍처 클래스 정의 (가중치 레이어 매치 완료)
# ==========================================
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # model_state_dict.pth 구조 분석에 기반한 레이어 순차 구성
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, padding=1), # conv.0
            nn.ReLU(),                                                           # conv.1
            nn.MaxPool2d(kernel_size=2, stride=2),                               # conv.2
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1),# conv.3
            nn.ReLU(),                                                           # conv.4
            nn.MaxPool2d(kernel_size=2, stride=2)                                # conv.5
        )
        # 핵심 수정: 학습된 가중치 차원(32,768)과 완벽 대응하도록 입력 뉴런 크기를 32*32*32로 매핑
        self.fc = nn.Sequential(
            nn.Flatten(),                                                        # fc.0 (가중치 없음)
            nn.Linear(32 * 32 * 32, 2)                                           # fc.1 (weight, bias)
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)
        return x

# ==========================================
# 2. 글로벌 설정 및 AI 모델 메모리 상주 (Singleton)
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model_state_dict.pth"

# 연산 장치 할당 (CUDA를 사용할 수 있다면 GPU, 아니면 CPU 선택)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 모델 객체 생성 및 가중치(State Dict) 로드
model = SimpleCNN()

if MODEL_PATH.exists():
    # CPU 환경에서도 이탈 없이 모델을 불러올 수 있도록 map_location 처리 보장
    state_dict = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()  # 추론 모드 전환 (Dropout, BatchNorm 활성화 방지)
    print(f"🎉 [성공] AI 폐렴 예측 모델을 메모리에 로드했습니다. (장치: {device})")
else:
    print(f"⚠️ [경고] 모델 파일을 찾을 수 없습니다. 경로를 확인하세요: {MODEL_PATH}")

# 핵심 수정: 가중치 차원 일치를 위해 전처리 해상도를 (128, 128)로 튜닝
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])  # 흑백(1채널) 채널 스케일 정규화
])

# ==========================================
# 3. 실시간 폐렴 예측 추론 핵심 함수
# ==========================================
def predict_pneumonia(image_path: str) -> dict:
    """
    업로드된 X-ray 이미지 경로를 받아 폐렴 여부와 신뢰도를 예측합니다.
    """
    if not os.path.exists(image_path):
        return {
            "is_pneumonia": False,
            "confidence": 0.0,
            "error": "지정된 경로에 이미지 파일이 존재하지 않습니다."
        }

    try:
        # 1. 이미지 로드 및 흑백(L) 모드 변환
        image = Image.open(image_path).convert('L')
        
        # 2. 전처리 파이프라인 적용 및 배치(Batch) 차원 추가
        input_tensor = transform(image).unsqueeze(0).to(device)

        # 3. 기울기 계산을 제외한 안전한 추론 연산
        with torch.no_grad():
            outputs = model(input_tensor)
            # Softmax를 통해 각 클래스별 실시간 확률 계산
            probabilities = torch.softmax(outputs, dim=1)[0]
            
            # 예측값 최댓값의 인덱스 추출
            predicted_class = torch.argmax(probabilities).item()
            confidence = probabilities[predicted_class].item() * 100  # 백분율 변환

        # 클래스 매핑 (0: 정상, 1: 폐렴으로 분류되는 보편 사양 가정)
        is_pneumonia = True if predicted_class == 1 else False

        return {
            "is_pneumonia": is_pneumonia,
            "confidence": round(confidence, 2),  # 소수점 둘째 자리 반올림
            "ai_model": "SimpleCNN_v1"
        }

    except Exception as e:
        return {
            "is_pneumonia": False,
            "confidence": 0.0,
            "error": f"추론 도중 시스템 에러 발생: {str(e)}"
        }