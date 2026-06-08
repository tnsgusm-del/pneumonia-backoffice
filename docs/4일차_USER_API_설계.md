# 4일차 User API 설계

---

## 비기능 요구사항 (공통 적용)

| ID | 내용 |
| --- | --- |
| NFR-USER-001 | 로그인 시 JWT 발급. access_token 만료 30분, refresh_token 만료 7일. refresh_token은 http_only 쿠키로 전달. JWT 페이로드에는 user_id만 저장. |
| NFR-USER-002 | 모든 비밀번호 입력란은 마스킹 처리. 비밀번호 보기 아이콘으로 확인 가능. |
| NFR-USER-003 | 모든 유저 API는 최대 3초 이내에 응답해야 한다. |

---

## REQ-USER-001. 회원가입 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원가입 API |
| 설명 | 사내 의료인, 개발 실무진이 회원가입을 통해 서비스를 이용할 수 있도록 하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/signup` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

---

### 2. 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |

#### 본문 예시
```json
{
  "email": "example@example.com",
  "password": "securePassword1!",
  "name": "홍길동",
  "department": "MEDICAL",
  "gender": "M",
  "phone_number": "01012345678"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 사용자 이메일 |
| password | string | Y | 사용자 비밀번호 (마스킹 처리) |
| name | string | Y | 사용자 이름 |
| department | string | Y | 부서 (MEDICAL / DEV / RESEARCH) |
| gender | string | Y | 성별 (M / F) |
| phone_number | string | Y | 휴대폰 번호 |

#### 쿼리 파라미터 (GET 요청시)
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
  "email": "example@example.com",
  "name": "홍길동",
  "department": "MEDICAL",
  "gender": "M",
  "phone_number": "01012345678",
  "role": "PENDING",
  "is_active": true
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 고유 ID |
| email | string | 이메일 |
| name | string | 이름 |
| department | string | 부서 (MEDICAL / DEV / RESEARCH) |
| gender | string | 성별 (M / F) |
| phone_number | string | 휴대폰 번호 |
| role | string | 권한 (기본값: PENDING) |
| is_active | boolean | 계정 활성화 여부 |

#### 실패
- 400 Bad Request
```json
{
  "detail": "이미 사용중인 이메일입니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - duplicate_email: 이메일 중복 / invalid_fields: 필드 유효성 오류 |

---

### 4. 비고
- 회원가입 직후 권한은 PENDING(대기자)으로 설정되며, 관리자가 권한을 변경해야 서비스 이용 가능
- 비밀번호는 평문이 아닌 암호화된 형태로 저장

---

## REQ-USER-002 / NFR-USER-001. 로그인 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 로그인 API |
| 설명 | 이메일과 비밀번호를 통해 로그인하고 JWT 토큰을 발급하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/login` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

---

### 2. 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |

#### 본문 예시
```json
{
  "email": "example@example.com",
  "password": "securePassword1!"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 사용자 이메일 |
| password | string | Y | 사용자 비밀번호 (마스킹 처리) |

#### 쿼리 파라미터 (GET 요청시)
| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공
- 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| access_token | string | JWT 액세스 토큰 (만료: 30분) |
| token_type | string | 토큰 타입 (bearer) |

#### 실패
- 400 Bad Request
```json
{
  "detail": "이메일 또는 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - invalid_email_or_password: 이메일 혹은 비밀번호가 잘못된 경우 / empty_fields: 필수 필드가 비어있는 경우 |

---

### 4. 비고
- refresh_token은 http_only 쿠키로 전달 (만료: 7일)
- JWT 페이로드에는 user_id만 저장
- 비밀번호는 암호화된 형태로 저장

---

## NFR-USER-001. 액세스 토큰 재발급 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 액세스 토큰 재발급 API |
| 설명 | 리프레시 토큰을 통해 액세스 토큰을 재발급하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/token/refresh` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |

#### 본문 예시
```json
{}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | refresh_token은 http_only 쿠키로 자동 전달 |

#### 쿼리 파라미터 (GET 요청시)
| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공
- 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| access_token | string | 새로 발급된 JWT 액세스 토큰 |
| token_type | string | 토큰 타입 (bearer) |

#### 실패
- 401 Unauthorized
```json
{
  "detail": "리프레시 토큰이 만료되었습니다. 다시 로그인해주세요."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - token_expired: 리프레시 토큰 만료 |

---

### 4. 비고
- refresh_token도 만료된 경우 재로그인 유도

---

## REQ-USER-003. 로그아웃 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 로그아웃 API |
| 설명 | 로그인된 유저가 로그아웃하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/logout` |
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
{}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터 (GET 요청시)
| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공
- 200 OK
```json
{
  "message": "로그아웃 되었습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| message | string | 로그아웃 완료 메시지 |

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

---

### 4. 비고
- 로그아웃 시 http_only 쿠키의 refresh_token 삭제
- 로그아웃 후 로그인 페이지로 전환

---

## REQ-USER-004. 회원 목록 조회 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 목록 조회 API |
| 설명 | 관리자(Admin) 권한 유저가 전체 회원 목록을 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시
```
해당 없음
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터 (GET 요청시)
| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| search | string | N | 이메일 또는 이름으로 검색 |
| department | string | N | 부서 필터 (MEDICAL / DEV / RESEARCH) |

---

### 3. 응답(Response)

#### 성공
- 200 OK
```json
[
  {
    "id": 1,
    "email": "example@example.com",
    "name": "홍길동",
    "department": "MEDICAL",
    "gender": "M",
    "phone_number": "01012345678",
    "is_active": true
  }
]
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 고유 ID |
| email | string | 이메일 |
| name | string | 이름 |
| department | string | 부서 (MEDICAL / DEV / RESEARCH) |
| gender | string | 성별 (M / F) |
| phone_number | string | 휴대폰 번호 |
| is_active | boolean | 계정 활성화 여부 |

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
| detail | string | - no_permission: Admin 권한이 없는 경우 |

---

### 4. 비고
- Admin 권한을 가진 유저만 접근 가능

---

## REQ-USER-005. 회원 권한 변경 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 권한 변경 API |
| 설명 | 관리자(Admin) 권한 유저가 특정 회원의 권한을 변경하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/{user_id}/role` |
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
  "role": "STAFF"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| role | string | Y | 변경할 권한 (PENDING / STAFF / ADMIN) |

#### 쿼리 파라미터 (GET 요청시)
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
  "email": "example@example.com",
  "role": "STAFF"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 고유 ID |
| email | string | 이메일 |
| role | string | 변경된 권한 |

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
| detail | string | - no_permission: Admin 권한이 없는 경우 |

- 404 Not Found
```json
{
  "detail": "해당 유저를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - user_not_found: 해당 유저가 존재하지 않는 경우 |

---

### 4. 비고
- PENDING: 마이페이지 외 모든 서비스 접근 불가
- STAFF: 흉부 X-ray 관련 모든 읽기, 쓰기, 수정 작업 가능
- ADMIN: 모든 항목에 대한 데이터 액세스 가능

---

## REQ-USER-006. 마이페이지 조회 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 마이페이지 조회 API |
| 설명 | 로그인한 유저가 본인의 정보를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시
```
해당 없음
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터 (GET 요청시)
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
  "email": "example@example.com",
  "department": "MEDICAL",
  "gender": "M",
  "phone_number": "01012345678",
  "role": "STAFF"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 고유 ID |
| name | string | 이름 |
| email | string | 이메일 |
| department | string | 부서 (MEDICAL / DEV / RESEARCH) |
| gender | string | 성별 (M / F) |
| phone_number | string | 휴대폰 번호 |
| role | string | 권한 (PENDING / STAFF / ADMIN) |

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

---

### 4. 비고
- 모든 로그인 유저 접근 가능

---

## REQ-USER-007. 회원 정보 수정 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 정보 수정 API |
| 설명 | 로그인한 유저가 본인의 부서 및 휴대폰 번호를 수정하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me` |
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
  "department": "DEV",
  "phone_number": "01098765432"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| department | string | N | 부서 (MEDICAL / DEV / RESEARCH) |
| phone_number | string | N | 휴대폰 번호 |

#### 쿼리 파라미터 (GET 요청시)
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
  "email": "example@example.com",
  "department": "DEV",
  "phone_number": "01098765432"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 고유 ID |
| name | string | 이름 |
| email | string | 이메일 |
| department | string | 수정된 부서 |
| phone_number | string | 수정된 휴대폰 번호 |

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

---

### 4. 비고
- 두 항목 중 하나만 수정해도 정상 처리 (Partial Update)

---

## REQ-USER-008. 비밀번호 변경 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 비밀번호 변경 API |
| 설명 | 로그인한 유저가 기존 비밀번호 확인 후 새 비밀번호로 변경하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/password` |
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
  "current_password": "oldPassword1!",
  "new_password": "newPassword1!"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| current_password | string | Y | 기존 비밀번호 (마스킹 처리) |
| new_password | string | Y | 새로운 비밀번호 (마스킹 처리) |

#### 쿼리 파라미터 (GET 요청시)
| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

---

### 3. 응답(Response)

#### 성공
- 200 OK
```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| message | string | 비밀번호 변경 완료 메시지 |

#### 실패
- 400 Bad Request
```json
{
  "detail": "기존 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - invalid_current_password: 기존 비밀번호 불일치 |

- 401 Unauthorized
```json
{
  "detail": "인증이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | - unauthorized: 인증되지 않은 사용자 |

---

### 4. 비고
- 비밀번호는 암호화된 형태로 저장

---

## REQ-USER-009. 회원 탈퇴 API

### 1. API 개요
| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 탈퇴 API |
| 설명 | 로그인한 유저가 본인 계정을 삭제하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me` |
| 메서드(Method) | `DELETE` |
| 인증 필요 여부 | Y |

---

### 2. 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer \<access_token\> | JWT 액세스 토큰 |

#### 본문 예시
```
해당 없음
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 ( Y / N ) | 설명 |
| --- | --- | --- | --- |
| - | - | - | 해당 없음 |

#### 쿼리 파라미터 (GET 요청시)
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

---

### 4. 비고
- 회원 탈퇴 시 DB에서 회원과 관련된 모든 정보 즉시 삭제
