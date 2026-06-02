# 5일차 환자 관리 및 진료기록 API 설계 명세서

---

## 공통 사항

- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **응답 시간**: 모든 API 최대 3초 이내 처리
- **인증**: 로그인된 사용자만 접근 가능

### 공통 응답 형식

```json
{
  "success": true,
  "data": {},
  "message": "처리 완료"
}
```

### 에러 응답 형식

```json
{
  "success": false,
  "detail": "에러 메시지"
}
```

---

## 1. 환자 관리 API

### REQ-PTNT-001 | 환자 정보 등록

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `/patients` |
| **접근 권한** | 의료인 |

**Request Body**

```json
{
  "name": "홍길동",
  "age": 35,
  "gender": "male",
  "phone": "010-1234-5678"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| name | string | ✅ | 환자 이름 |
| age | integer | ✅ | 나이 |
| gender | string | ✅ | 성별 (male / female) |
| phone | string | ✅ | 휴대폰 번호 |

**Response (201)**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "홍길동",
    "age": 35,
    "gender": "male",
    "phone": "010-1234-5678",
    "created_at": "2026-06-02T10:00:00",
    "updated_at": "2026-06-02T10:00:00"
  },
  "message": "환자 정보가 등록되었습니다."
}
```

---

### REQ-PTNT-002 | 환자 목록 조회

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `/patients` |
| **접근 권한** | 개발진, 의료 실무진, 연구진 |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| name | string | ❌ | 이름 검색 |
| gender | string | ❌ | 성별 필터 (male / female) |
| age_min | integer | ❌ | 최소 나이 |
| age_max | integer | ❌ | 최대 나이 |

**Request 예시**

```
GET /api/v1/patients?name=홍&gender=male&age_min=20&age_max=40
```

**Response (200)**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "홍길동",
      "age": 35,
      "gender": "male",
      "phone": "010-1234-5678",
      "created_at": "2026-06-02T10:00:00",
      "updated_at": "2026-06-02T10:00:00"
    }
  ],
  "message": "환자 목록 조회 성공"
}
```

---

### REQ-PTNT-003 | 환자 정보 상세 조회

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `/patients/{patient_id}` |
| **접근 권한** | 개발진, 의료 실무진, 연구진 |

**Path Parameter**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 고유 ID |

**Response (200)**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "홍길동",
    "age": 35,
    "gender": "male",
    "phone": "010-1234-5678"
  },
  "message": "환자 상세 조회 성공"
}
```

---

### REQ-PTNT-004 | 환자 정보 수정

| 항목 | 내용 |
|------|------|
| **Method** | `PATCH` |
| **URL** | `/patients/{patient_id}` |
| **접근 권한** | 개발진, 의료 실무진, 연구진 |

**Path Parameter**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 고유 ID |

**Request Body**

```json
{
  "name": "홍길순",
  "phone": "010-9999-8888"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| name | string | ❌ | 수정할 이름 |
| phone | string | ❌ | 수정할 휴대폰 번호 |

**Response (200)**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "홍길순",
    "age": 35,
    "gender": "male",
    "phone": "010-9999-8888",
    "updated_at": "2026-06-02T11:00:00"
  },
  "message": "환자 정보가 수정되었습니다."
}
```

---

### REQ-PTNT-005 | 환자 정보 삭제

| 항목 | 내용 |
|------|------|
| **Method** | `DELETE` |
| **URL** | `/patients/{patient_id}` |
| **접근 권한** | 개발진, 의료 실무진, 연구진 |

**Path Parameter**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 고유 ID |

> ⚠️ 환자 삭제 시 관련 진료기록 및 X-Ray 이미지도 함께 영구 삭제됩니다.

**Response (200)**

```json
{
  "success": true,
  "data": null,
  "message": "환자 정보 및 관련 데이터가 삭제되었습니다."
}
```

---

## 2. 진료기록 API

### REQ-MDR-001 | 진료기록 등록

| 항목 | 내용 |
|------|------|
| **Method** | `POST` |
| **URL** | `/patients/{patient_id}/medical-records` |
| **접근 권한** | 의료인 |
| **Content-Type** | `multipart/form-data` |

**Path Parameter**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 고유 ID |

**Request Body (Form Data)**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| chart_number | string | ✅ | 진료 차트 번호 |
| symptom | string | ✅ | 진료된 증상 |
| xray_image | file | ✅ | 흉부 X-Ray 이미지 (로컬 저장) |

**Response (201)**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "patient_id": 1,
    "chart_number": "CHART-001",
    "symptom": "기침, 발열",
    "xray_image_path": "/storage/xray/patient_1_20260602.jpg",
    "created_at": "2026-06-02T10:00:00"
  },
  "message": "진료기록이 등록되었습니다."
}
```

---

### REQ-MDR-002 | 진료기록 목록 조회

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `/patients/{patient_id}/medical-records` |
| **접근 권한** | 개발진, 의료 실무진, 연구진 |

**Path Parameter**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 고유 ID |

**Response (200)**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "chart_number": "CHART-001",
      "symptom": "기침, 발열 (100자 초과 시 생략...)",
      "created_at": "2026-06-02T10:00:00"
    }
  ],
  "message": "진료기록 목록 조회 성공"
}
```

> ℹ️ 증상(symptom)은 100자 초과 시 `...` 생략 형태로 반환합니다.

---

### REQ-MDR-003 | 진료기록 상세 조회

| 항목 | 내용 |
|------|------|
| **Method** | `GET` |
| **URL** | `/patients/{patient_id}/medical-records/{record_id}` |
| **접근 권한** | 개발진, 의료 실무진, 연구진 |

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 고유 ID |
| record_id | integer | 진료기록 ID |

**Response (200)**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "chart_number": "CHART-001",
    "symptom": "기침, 발열, 호흡곤란 증상이 있으며...",
    "xray_image_url": "/storage/xray/patient_1_20260602.jpg",
    "created_at": "2026-06-02T10:00:00"
  },
  "message": "진료기록 상세 조회 성공"
}
```

---

## 3. API 목록 요약

| No | Method | URL | 기능 | 권한 |
|----|--------|-----|------|------|
| 1 | POST | `/patients` | 환자 등록 | 의료인 |
| 2 | GET | `/patients` | 환자 목록 조회 | 전체 |
| 3 | GET | `/patients/{id}` | 환자 상세 조회 | 전체 |
| 4 | PATCH | `/patients/{id}` | 환자 정보 수정 | 전체 |
| 5 | DELETE | `/patients/{id}` | 환자 삭제 | 전체 |
| 6 | POST | `/patients/{id}/medical-records` | 진료기록 등록 | 의료인 |
| 7 | GET | `/patients/{id}/medical-records` | 진료기록 목록 조회 | 전체 |
| 8 | GET | `/patients/{id}/medical-records/{rid}` | 진료기록 상세 조회 | 전체 |

---

## 4. 에러 코드

| 상태 코드 | 설명 |
|-----------|------|
| 400 | 잘못된 요청 (필수값 누락, 형식 오류) |
| 401 | 인증 실패 (미로그인) |
| 403 | 권한 없음 |
| 404 | 데이터 없음 |
| 500 | 서버 내부 오류 |
