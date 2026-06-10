# 5일차 과제: 환자 관리 및 진료기록 API 설계 명세서

본 문서는 5일차 환자 관리 및 진료기록 요구사항 정의서(REQ-PTNT-001 ~ NFR-MDR-001)에 기반하여 설계된 RESTful API 명세서입니다. 4일차 피드백에서 다듬어진 글로벌 API 컨벤션 정책(영문 대문자 Enum 적용, PATCH 메서드 부분 수정 활용, DELETE 시 204 No Content 규격 준수, 중복 필드 제거 등)을 엄격하게 계승하여 작성되었습니다.

---

## 🗺️ API 요약 가이드

| 요구사항 ID | 기능 요약 | Method | Endpoint | 권한 |
| :--- | :--- | :---: | :--- | :--- |
| **REQ-PTNT-001** | 환자 정보 등록 | `POST` | `/api/v1/patients` | 의료인 (`STAFF`, `ADMIN`) |
| **REQ-PTNT-002** | 환자 목록 조회 (검색/필터) | `GET` | `/api/v1/patients` | 로그인 유저 전체 |
| **REQ-PTNT-003** | 환자 정보 상세 조회 | `GET` | `/api/v1/patients/{patient_id}` | 로그인 유저 전체 |
| **REQ-PTNT-004** | 환자 정보 수정 (Partial) | `PATCH` | `/api/v1/patients/{patient_id}` | 로그인 유저 전체 |
| **REQ-PTNT-005** | 환자 정보 삭제 (즉시 삭제) | `DELETE` | `/api/v1/patients/{patient_id}` | 로그인 유저 전체 |
| **REQ-MDR-001** | 진료기록 등록 (이미지 포함) | `POST` | `/api/v1/medical-records` | 의료인 (`STAFF`, `ADMIN`) |
| **REQ-MDR-002** | 진료기록 목록 조회 | `GET` | `/api/v1/patients/{patient_id}/medical-records` | 로그인 유저 전체 |
| **REQ-MDR-003** | 진료기록 상세 조회 | `GET` | `/api/v1/medical-records/{record_id}` | 로그인 유저 전체 |

---

## ⚡ 비기능 요구사항 (Non-Functional Requirements)

| ID | 요구사항 내용 | 적용 방식 |
| :--- | :--- | :--- |
| **NFR-PTNT-001** | 모든 환자 관련 API는 최대 3초 이내에 로직을 처리하고 응답하도록 한다. | DB 인덱싱 최적화 및 비동기 ORM 쿼리 적용 |
| **NFR-MDR-001** | 모든 진료기록 관련 API는 최대 3초 이내에 로직을 처리하고 응답하도록 한다. | 대용량 바이너리 파일 처리 최적화 및 비동기 I/O 적용 |

---

## 📑 상세 API 명세

### REQ-PTNT-001. 환자 정보 등록 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 환자 정보 등록 API |
| **설명** | 사내 의료인 역할을 가진 유저가 신규 환자의 정보를 시스템 상에 등록하는 API |
| **엔드포인트** | `/api/v1/patients` |
| **메서드** | `POST` |
| **인증 필요** | Y (의료인 권한: `STAFF` / `ADMIN` 중 `MEDICAL` 부서 소속 유저 권장) |

#### 2. 요청 (Request)

* **Headers**
  * `Content-Type: application/json`
  * `Authorization: Bearer <access_token>`

* **본문 예시 (JSON)**

```json
{
  "name": "홍길동",
  "age": 45,
  "gender": "M",
  "phone": "01012345678"
}
```

* **본문 필드 설명**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **name** | string | Y | 환자 이름 |
| **age** | integer | Y | 환자 나이 |
| **gender** | string | Y | 환자 성별 (`M` / `F` 규격 통일) |
| **phone** | string | Y | 환자 연락처 (하이픈 없이 숫자만 입력) |

#### 3. 응답 (Response)

* **성공 (201 Created)**

```json
{
  "id": 1,
  "name": "홍길동",
  "age": 45,
  "gender": "M",
  "phone": "01012345678",
  "created_at": "2026-06-09T16:00:00"
}
```

---

### REQ-PTNT-002. 환자 목록 조회 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 환자 목록 조회 API |
| **설명** | 로그인된 유저가 등록된 환자 정보를 검색어 및 필터 조건을 적용하여 목록으로 조회하는 API |
| **엔드포인트** | `/api/v1/patients` |
| **메서드** | `GET` |
| **인증 필요** | Y |

#### 2. 요청 (Request)

* **Headers**
  * `Authorization: Bearer <access_token>`

* **쿼리 파라미터 (Query Parameters)**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **search** | string | N | 환자 이름 기준 검색어 |
| **gender** | string | N | 성별 필터링 (`M` / `F`) |
| **age_min** | integer | N | 최소 나이 범위 필터 |
| **age_max** | integer | N | 최대 나이 범위 필터 |

#### 3. 응답 (Response)

* **성공 (200 OK)**

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "age": 45,
    "gender": "M",
    "phone": "01012345678",
    "created_at": "2026-06-09T16:00:00",
    "updated_at": "2026-06-09T16:10:00"
  }
]
```

---

### REQ-PTNT-003. 환자 정보 상세 조회 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 환자 정보 상세 조회 API |
| **설명** | 지정한 환자 고유 ID의 상세 인적 정보를 확인하는 API |
| **엔드포인트** | `/api/v1/patients/{patient_id}` |
| **메서드** | `GET` |
| **인증 필요** | Y |

#### 2. 응답 (Response)

* **성공 (200 OK)**

```json
{
  "name": "홍길동",
  "gender": "M",
  "phone": "01012345678",
  "age": 45
}
```

---

### REQ-PTNT-004. 환자 정보 수정 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 환자 정보 수정 API |
| **설명** | 특정 환자의 이름 또는 연락처 정보를 부분 수정(Partial Update)하는 API |
| **엔드포인트** | `/api/v1/patients/{patient_id}` |
| **메서드** | `PATCH` |
| **인증 필요** | Y |

#### 2. 요청 (Request)

* **Headers**
  * `Content-Type: application/json`
  * `Authorization: Bearer <access_token>`

* **본문 예시 (JSON)**

```json
{
  "name": "홍길순",
  "phone": "01099998888"
}
```

* **본문 필드 설명 (선택적 입력)**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **name** | string | N | 수정 적용할 새로운 환자 이름 |
| **phone** | string | N | 수정 적용할 새로운 환자 연락처 |

#### 3. 응답 (Response)

* **성공 (200 OK)**

```json
{
  "id": 1,
  "name": "홍길순",
  "age": 45,
  "gender": "M",
  "phone": "01099998888",
  "created_at": "2026-06-09T16:00:00",
  "updated_at": "2026-06-09T16:30:00"
}
```

---

### REQ-PTNT-005. 환자 정보 삭제 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 환자 정보 삭제 API |
| **설명** | 특정 환자 및 그와 연계된 모든 데이터(진료기록, 촬영된 X-Ray 파일 등)를 영구 삭제하는 API |
| **엔드포인트** | `/api/v1/patients/{patient_id}` |
| **메서드** | `DELETE` |
| **인증 필요** | Y |

#### 2. 응답 (Response)

* **성공 (204 No Content)**

  * *성공적으로 삭제 완료 시 RESTful 표준 규격에 부합하게 별도의 바디 없이 반환됩니다.*

---

### REQ-MDR-001. 진료기록 등록 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 진료기록 등록 API |
| **설명** | 환자의 진료내용과 촬영한 흉부 X-Ray 이미지 파일을 함께 실시간 등록하는 API |
| **엔드포인트** | `/api/v1/medical-records` |
| **메서드** | `POST` |
| **인증 필요** | Y (의료인 권한: `STAFF` / `ADMIN`) |

#### 2. 요청 (Request)

* **Headers**
  * `Content-Type: multipart/form-data`
  * `Authorization: Bearer <access_token>`

* **Form-Data 매개변수 정의**

| 필드명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **patient_id** | integer | Y | 대상 환자 고유 ID |
| **chart_number** | string | Y | 진료 차트 넘버 (고유 식별값) |
| **symptoms** | string | Y | 진료된 상세 증상 내용 |
| **xray_image** | file | Y | 촬영된 흉부 X-Ray 이미지 파일 바이너리 |

#### 3. 응답 (Response)

* **성공 (201 Created)**

```json
{
  "record_id": 10,
  "patient_id": 1,
  "chart_number": "CHART-2026-0089",
  "symptoms": "지속적인 기침 및 발열 증세 확인.",
  "xray_image_url": "/media/xray/CHART-2026-0089.png",
  "created_at": "2026-06-09T16:45:00"
}
```

#### 4. 비고

* 업로드된 이미지 파일(`xray_image`)은 백엔드 서버 실행 환경의 로컬 미디어 저장소 경로(`/media/xray/`)에 안전하게 동기화 저장됩니다.

---

### REQ-MDR-002. 진료기록 목록 조회 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 진료기록 목록 조회 API |
| **설명** | 특정 환자가 지닌 모든 진료기록들을 목록 형태로 요약 확인하는 API |
| **엔드포인트** | `/api/v1/patients/{patient_id}/medical-records` |
| **메서드** | `GET` |
| **인증 필요** | Y |

#### 2. 응답 (Response)

* **성공 (200 OK)**

```json
[
  {
    "id": 10,
    "chart_number": "CHART-2026-0089",
    "symptoms": "지속적인 기침 및 발열 증세 확인...",
    "created_at": "2026-06-09T16:45:00"
  }
]
```
* *증상(`symptoms`) 필드는 100자 초과 기입 시, 꼬리 부분이 생략 형태(`...`)로 가공되어 목록에 전달됩니다.*

---

### REQ-MDR-003. 진료기록 상세 조회 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 진료기록 상세 조회 API |
| **설명** | 진료 기록의 상세 내역과 흉부 X-Ray 원본 이미지 URL 경로를 함께 개별 조회하는 API |
| **엔드포인트** | `/api/v1/medical-records/{record_id}` |
| **메서드** | `GET` |
| **인증 필요** | Y |

#### 2. 응답 (Response)

* **성공 (200 OK)**

```json
{
  "id": 10,
  "chart_number": "CHART-2026-0089",
  "symptoms": "지속적인 기침 및 발열 증세가 확인되어 흉부 X-Ray 검사를 진행함. 왼쪽 하엽 폐 침윤 소견 관찰됨.",
  "xray_image_url": "/media/xray/CHART-2026-0089.png",
  "created_at": "2026-06-09T16:45:00"
}
```