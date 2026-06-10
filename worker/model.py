import os
from pathlib import Path
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import io

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),  # 3 -> 1 (흑백)
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32768, 2)  # 32768, 출력 2클래스
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)
        return x

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.path.join(BASE_DIR, "worker", "models", "model_state_dict.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleCNN()
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),  # 흑백 변환
    transforms.Resize((128, 128)),                # 128x128 → 풀링 2번 → 32x32
    transforms.ToTensor(),
])

def predict_pneumonia(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)           # shape: [1, 2]
        probs = torch.softmax(output, dim=1)   # 2클래스 확률로 변환
        pneumonia_prob = probs[0][1].item()    # 클래스 1 = 폐렴 확률
    
    return pneumonia_prob