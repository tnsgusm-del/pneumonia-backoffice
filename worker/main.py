import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from worker.redis_client import redis_client
from worker.model import predict_pneumonia

TASK_QUEUE = "ai_task_queue"

print("🚀 AI Worker 시작 - 작업 대기 중...")

while True:
    try:
        # 블로킹 방식으로 큐에서 작업 꺼내기 (타임아웃 0 = 무한 대기)
        result = redis_client.blpop(TASK_QUEUE, timeout=0)
        if result is None:
            continue

        _, raw = result
        task = json.loads(raw)
        task_id = task["task_id"]
        image_path = task["image_path"]
        channel = task["channel"]

        print(f"📋 작업 수신: task_id={task_id}, image={image_path}")

        # AI 추론 실행
        prediction = predict_pneumonia(image_path)
        prediction["task_id"] = task_id

        # 결과를 Redis Pub/Sub으로 발행
        redis_client.publish(channel, json.dumps(prediction))
        print(f"✅ 결과 발행 완료: task_id={task_id}, result={prediction}")

    except Exception as e:
        print(f"❌ 워커 에러: {e}")
        continue
