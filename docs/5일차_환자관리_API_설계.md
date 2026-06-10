# 5일차 환자 관리 및 진료기록 API 설계 명세서

---

## 비기능 요구사항 (공통 적용)

| ID | 내용 |
| --- | --- |
| NFR-PTNT-001 | 모든 환자/진료기록 API는 최대 3초 이내에 응답해야 한다. |
| NFR-PTNT-002 | 모든 환자/진료기록 API는 인증된 사용자(STAFF, ADMIN)만 접근 가능하다. |
| NFR-PTNT-003 | PENDING 권한 사용자는 모든 환자/진료기록 API에 접근할 수 없다. |

---

## API 목록 요약

| 요구사항 ID | 기능 요약 | Method | Endpoint | 권한 |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-PTNT-001** | 환자 등록 | `POST` | `/api/v1/patients` | STAFF, ADMIN |
| **REQ-PTNT-002** | 환자 목록 조회 | `GET` | `/api/v1/patients` | STAFF, ADMIN |
| **REQ-PTNT-003** | 환자 상세 조회 | `GET` | `/api/v1/patients/{patient_id}` | STAFF, ADMIN |
| **REQ-PTNT-004** | 환자 정보 수정 | `PATCH` | `/api/v1/patients/{patient_id}` | STAFF, ADMIN |
| **REQ-PTNT-005** | 환자 삭제 | `DELETE` | `/api/v1/patients/{patient_id}` | STAFF, ADMIN |
| **REQ-MDR-001** | 진료기록 등록 | `POST` | `/api/v1/patients/{patient_id}/medical-records` | STAFF, ADMIN |
| **REQ-MDR-002** | 진료기록 목록 조회 | `GET` | `/api/v1/patients/{patient_id}/medical-records` | STAFF, ADMIN |
| **REQ-MDR-003** | 진료기록 상세 조회 | `GET` | `/api/v1/patients/{patient_id}/medical-records/{record_id}` | STAFF, ADMIN |

---

## 📑 상세 API 명세

---

## REQ-PTNT-001. 환자 등록 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 등록 API |
| 설명 | 사내 의료인 역할을 가진 유저가 새로운 환자 정보를 등록하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "name": "홍길동",
  "age": 45,
  "gender": "M",
  "phone_number": "01012345678"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| name | string | Y | 환자 이름 |
| age | integer | Y | 환자 나이 |
| gender | string | Y | 환자 성별 (M / F) |
| phone_number | string | Y | 환자 연락처 (숫자만, 최대 11자리) |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 201 Created

```json
{
  "id": 1,
  "name": "홍길동",
  "age": 45,
  "gender": "M",
  "phone_number": "01012345678",
  "created_at": "2026-06-09T10:00:00",
  "updated_at": "2026-06-09T10:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 (M / F) |
| phone_number | string | 환자 연락처 |
| created_at | string | 등록 일시 |
| updated_at | string | 수정 일시 |

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: STAFF 또는 ADMIN 권한이 없는 경우 |

- 422 Unprocessable Entity

```json
{
  "detail": "입력값이 올바르지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - invalid_fields: 필드 유효성 오류 |

---

### 4. 비고

- 환자 등록은 STAFF, ADMIN 권한을 가진 유저만 가능

---

## REQ-PTNT-002. 환자 목록 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 목록 조회 API |
| 설명 | 로그인된 사용자가 전체 환자 목록을 조회하는 API. 이름 검색 및 성별, 나이 범위 필터링 가능 |
| 엔드포인트(Endpoint) | `/api/v1/patients` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

해당 없음

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| name | string | N | 환자 이름으로 검색 (부분 일치) |
| gender | string | N | 성별 필터 (M / F) |
| min_age | integer | N | 최소 나이 필터 |
| max_age | integer | N | 최대 나이 필터 |

---

### 3. 응답(Response)

#### 성공

- 200 OK

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "age": 45,
    "gender": "M",
    "phone_number": "01012345678",
    "created_at": "2026-06-09T10:00:00",
    "updated_at": "2026-06-09T10:00:00"
  },
  {
    "id": 2,
    "name": "김영희",
    "age": 32,
    "gender": "F",
    "phone_number": "01098765432",
    "created_at": "2026-06-09T11:00:00",
    "updated_at": "2026-06-09T11:00:00"
  }
]
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 (M / F) |
| phone_number | string | 환자 연락처 |
| created_at | string | 등록 일시 |
| updated_at | string | 수정 일시 |

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: PENDING 권한인 경우 |

---

### 4. 비고

- 필터 미적용 시 전체 환자 목록 반환
- 검색 결과가 없을 경우 빈 배열 `[]` 반환

---

## REQ-PTNT-003. 환자 상세 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 상세 조회 API |
| 설명 | 특정 환자의 상세 정보를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

해당 없음

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 200 OK

```json
{
  "id": 1,
  "name": "홍길동",
  "age": 45,
  "gender": "M",
  "phone_number": "01012345678",
  "created_at": "2026-06-09T10:00:00",
  "updated_at": "2026-06-09T10:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 (M / F) |
| phone_number | string | 환자 연락처 |
| created_at | string | 등록 일시 |
| updated_at | string | 수정 일시 |

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: PENDING 권한인 경우 |

- 404 Not Found

```json
{
  "detail": "해당 환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - patient_not_found: 해당 환자가 존재하지 않는 경우 |

---

### 4. 비고

- 없음

---

## REQ-PTNT-004. 환자 정보 수정 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 정보 수정 API |
| 설명 | 특정 환자의 이름 및 연락처를 수정하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "name": "홍길순",
  "phone_number": "01099998888"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| name | string | N | 수정할 환자 이름 |
| phone_number | string | N | 수정할 환자 연락처 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 200 OK

```json
{
  "id": 1,
  "name": "홍길순",
  "age": 45,
  "gender": "M",
  "phone_number": "01099998888",
  "created_at": "2026-06-09T10:00:00",
  "updated_at": "2026-06-09T11:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 (M / F) |
| phone_number | string | 수정된 환자 연락처 |
| created_at | string | 등록 일시 |
| updated_at | string | 수정 일시 |

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: PENDING 권한인 경우 |

- 404 Not Found

```json
{
  "detail": "해당 환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - patient_not_found: 해당 환자가 존재하지 않는 경우 |

---

### 4. 비고

- 두 항목 중 하나만 수정해도 정상 처리 (Partial Update)

---

## REQ-PTNT-005. 환자 삭제 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 삭제 API |
| 설명 | 특정 환자 정보 및 관련된 모든 진료기록, X-Ray 이미지를 삭제하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}` |
| 메서드(Method) | `DELETE` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

해당 없음

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 204 No Content

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: PENDING 권한인 경우 |

- 404 Not Found

```json
{
  "detail": "해당 환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - patient_not_found: 해당 환자가 존재하지 않는 경우 |

---

### 4. 비고

- 환자 삭제 시 해당 환자의 모든 진료기록, X-Ray 이미지, AI 분석 결과가 연쇄 삭제됨 (CASCADE)

---

## REQ-MDR-001. 진료기록 등록 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 진료기록 등록 API |
| 설명 | 사내 의료인 역할을 가진 유저가 특정 환자의 진료기록을 등록하는 API. X-Ray 이미지 파일 포함 |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | multipart/form-data | 파일 업로드 포함 요청 |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

```
patient_id: 1
chart_number: "CHART-2026-001"
symptoms: "기침, 발열, 호흡 곤란"
xray_image: (파일)
```

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| chart_number | string | Y | 진료 차트 번호 (중복 불가) |
| symptoms | string | Y | 환자 증상 기록 |
| xray_image | file | Y | 흉부 X-Ray 이미지 파일 (이미지 형식만 허용) |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 201 Created

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-2026-001",
  "symptoms": "기침, 발열, 호흡 곤란",
  "xray_image_url": "/media/xray/2026/06/09/image.jpg",
  "created_at": "2026-06-09T10:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 진료기록 고유 ID |
| patient_id | integer | 환자 ID |
| chart_number | string | 진료 차트 번호 |
| symptoms | string | 환자 증상 기록 |
| xray_image_url | string | 업로드된 X-Ray 이미지 접근 경로 |
| created_at | string | 진료기록 등록 일시 |

#### 실패

- 400 Bad Request

```json
{
  "detail": "이미 존재하는 차트 번호입니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - duplicate_chart_number: 차트 번호 중복 |

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: STAFF 또는 ADMIN 권한이 없는 경우 |

- 404 Not Found

```json
{
  "detail": "해당 환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - patient_not_found: 해당 환자가 존재하지 않는 경우 |

---

### 4. 비고

- X-Ray 이미지는 서버의 /media 폴더에 저장
- 진료기록 등록은 STAFF, ADMIN 권한을 가진 유저만 가능

---

## REQ-MDR-002. 진료기록 목록 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 진료기록 목록 조회 API |
| 설명 | 특정 환자의 전체 진료기록 목록을 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

해당 없음

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 200 OK

```json
[
  {
    "id": 1,
    "chart_number": "CHART-2026-001",
    "symptoms": "기침, 발열, 호흡 곤란",
    "created_at": "2026-06-09T10:00:00"
  }
]
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 진료기록 고유 ID |
| chart_number | string | 진료 차트 번호 |
| symptoms | string | 환자 증상 기록 (100자 초과 시 `...` 생략) |
| created_at | string | 진료기록 등록 일시 |

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: PENDING 권한인 경우 |

- 404 Not Found

```json
{
  "detail": "해당 환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - patient_not_found: 해당 환자가 존재하지 않는 경우 |

---

### 4. 비고

- 진료기록이 없을 경우 빈 배열 `[]` 반환
- 증상(symptoms)은 100자 초과 시 `...` 생략 형태로 반환

---

## REQ-MDR-003. 진료기록 상세 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 진료기록 상세 조회 API |
| 설명 | 특정 진료기록의 상세 내용을 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/{record_id}` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시

해당 없음

#### 본문 필드

| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공

- 200 OK

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-2026-001",
  "symptoms": "기침, 발열, 호흡 곤란",
  "xray_image_url": "/media/xray/2026/06/09/image.jpg",
  "created_at": "2026-06-09T10:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 진료기록 고유 ID |
| patient_id | integer | 환자 ID |
| chart_number | string | 진료 차트 번호 |
| symptoms | string | 환자 증상 기록 |
| xray_image_url | string | X-Ray 이미지 접근 경로 |
| created_at | string | 진료기록 등록 일시 |

#### 실패

- 401 Unauthorized

```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

- 403 Forbidden

```json
{
  "detail": "접근 권한이 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - no_permission: PENDING 권한인 경우 |

- 404 Not Found

```json
{
  "detail": "해당 진료기록을 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - record_not_found: 해당 진료기록이 존재하지 않는 경우 |

---

### 4. 비고

- 없음
