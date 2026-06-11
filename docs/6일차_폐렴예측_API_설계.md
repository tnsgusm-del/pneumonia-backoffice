# 6일차 과제: AI 폐렴 예측 및 결과 조회 API 설계 명세서

본 문서는 AI 폐렴 예측 및 결과 조회 요구사항 정의서(`REQ-PRED-001` ~ `NFR-PRED-002`)에 기반하여 설계된 최종 RESTful API 명세서입니다.
4일차/5일차의 설계 컨벤션을 엄격하게 계승하며, 가입 승인된 의료진 권한 제어 필터 및 중복 캐싱 방어 로직이 적용되어 있습니다.

---

## 🗺️ API 요약 가이드

| 요구사항 ID | 기능 요약 | Method | Endpoint | 권한 |
| :--- | :--- | :---: | :--- | :--- |
| **REQ-PRED-001** | AI 모델 활용 폐렴 예측 및 결과 기록 | `POST` | `/api/v1/ai-analysis/{record_id}` | 의료인 (`STAFF`, `ADMIN`) |
| **REQ-PRED-002** | AI 모델 활용 폐렴 예측 결과 목록 조회 | `GET` | `/api/v1/ai-analysis/records/{record_id}` | 로그인 유저 전체 |

---

## ⚡ 비기능 요구사항 (Non-Functional Requirements)

| ID | 요구사항 내용 | 적용 방식 |
| :--- | :--- | :--- |
| **NFR-PRED-001** | **AI 모델 평가 기준 충족**<br>- Recall (민감도) $\ge 0.90 \sim 0.95$ (최소 $0.90$)<br>- Accuracy $\ge 0.80 \sim 0.90$ (보조 지표) | PyTorch `SimpleCNN` 모델 평가 지표 검증 필터 수립 |
| **NFR-PRED-002** | **API 성능 보장**<br>- 모든 AI API는 최대 3초 이내에 응답해야 함 | 추론 메모리 해제(`torch.no_grad()`) 및 모델 싱글톤 인스턴스 기법 적용 |

### 🔬 [NFR-PRED-001] AI 모델 성능 평가 기준 수식 정의

AI 추론 엔진의 평가 지표는 아래의 오차 행렬(Confusion Matrix) 기준을 준수합니다.

* **TP (True Positive)**: 폐렴 환자를 폐렴으로 정확히 진단한 경우
* **FP (False Positive)**: 정상인이지만 폐렴으로 오진한 경우
* **FN (False Negative)**: **폐렴 환자인데 정상으로 오진한 경우 (⚠️ 가장 위험한 의료 오진)**
* **TN (True Negative)**: 정상인을 정상으로 정확히 진단한 경우

#### 1. Recall (민감도 / 재현율)
"실제 폐렴 환자를 얼마나 놓치지 않고 잘 잡아내는가"에 대한 임상적 핵심 기준입니다.
$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} \ge 0.90$$

#### 2. Accuracy (정확도)
전체 진단 표본 중 정상과 질환을 올바르게 예측한 비율입니다.
$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}} \ge 0.80$$

---

## 📑 상세 API 명세

### REQ-PRED-001. AI 모델 활용 폐렴 예측 수행 및 저장 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | AI 모델 활용 폐렴 예측 수행 및 결과 기록 API |
| **설명** | 지정된 진료기록 고유 ID의 X-ray 이미지를 불러와 AI 모델로 폐렴 여부를 분석하고 예측 결과를 데이터베이스에 저장함 |
| **엔드포인트** | `/api/v1/ai-analysis/{record_id}` |
| **메서드** | `POST` |
| **인증 필요** | Y (의료인 권한: `STAFF` / `ADMIN` 중 `MEDICAL` 부서 소속 유저) |

#### 2. 요청 (Request)

* **Headers**
  * `Authorization: Bearer <access_token>`

* **패스 파라미터 (Path Parameters)**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **record_id** | integer | Y | 예측 분석을 진행할 진료 기록의 고유 식별자 |

#### 3. 응답 (Response)

* **성공 (201 Created)**: 분석이 신규 완료되어 데이터베이스 적재에 성공한 상황

```json
{
  "id": 5,
  "record_id": 1,
  "is_pneumonia": true,
  "confidence": 92.45,
  "heatmap_url": "/media/xray/heatmap_c354a708-1370-40e8-9da2.jpg",
  "ai_model": "SimpleCNN_v1",
  "created_at": "2026-06-10T16:45:12"
}
```

* **성공 (200 OK)**: 중복 분석 방지 가동 시, 이미 동일 모델로 저장된 기존 판독 결과를 즉시 반환

```json
{
  "id": 5,
  "record_id": 1,
  "is_pneumonia": true,
  "confidence": 92.45,
  "heatmap_url": "/media/xray/heatmap_c354a708-1370-40e8-9da2.jpg",
  "ai_model": "SimpleCNN_v1",
  "created_at": "2026-06-10T16:45:12"
}
```

* **실패 (404 Not Found - 진료기록 없음)**

```json
{
  "detail": "지정한 진료기록(ID: 999)이 존재하지 않습니다."
}
```

* **실패 (400 Bad Request - X-ray 누락)**

```json
{
  "detail": "해당 진료기록에 첨부된 흉부 X-ray 이미지 파일이 존재하지 않아 분석을 진행할 수 없습니다."
}
```

#### 4. 비고

* 이미 해당 진료기록으로 같은 모델을 사용하여 저장된 예측 결과가 있다면 별도의 AI 추론 연산 과정을 거치지 않고 저장되어 있던 기존 데이터를 즉시 응답하는 중복 분석 방지 캐싱 로직이 적용되어 있습니다.

---

### REQ-PRED-002. AI 모델 활용 폐렴 예측 결과 목록 조회 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | AI 모델 활용 폐렴 예측 결과 목록 조회 API |
| **설명** | 지정된 환자의 진료 기록에 수반되는 흉부 X-ray 사진과 AI 예측 분석 히스토리 결과를 리스트 목록 형태로 일괄 확인하는 API |
| **엔드포인트** | `/api/v1/ai-analysis/records/{record_id}` |
| **메서드** | `GET` |
| **인증 필요** | Y (로그인 유저 전체) |

#### 2. 요청 (Request)

* **Headers**
  * `Authorization: Bearer <access_token>`

* **패스 파라미터 (Path Parameters)**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **record_id** | integer | Y | 판독 결과를 조회할 진료 기록의 고유 식별자 |

#### 3. 응답 (Response)

* **성공 (200 OK)**: 예측 기록 목록을 Array 형태로 반환

```json
[
  {
    "id": 5,
    "record_id": 1,
    "is_pneumonia": true,
    "confidence": 92.45,
    "heatmap_url": "/media/xray/heatmap_c354a708-1370-40e8-9da2.jpg",
    "ai_model": "SimpleCNN_v1",
    "created_at": "2026-06-10T16:45:12"
  }
]
```

* **실패 (404 Not Found)**

```json
{
  "detail": "해당 진료기록에 대해 가동된 AI 판독 이력이 존재하지 않습니다."
}
```
