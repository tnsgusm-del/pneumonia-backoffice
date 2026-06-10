
---

### 📝 docs/4일차_USER_API_설계.md 

```markdown
# 4일차 과제: User 사용자 API 설계 명세서

본 문서는 4일차 User 사용자 요구사항 정의서(REQ-USER-001 ~ NFR-USER-003)에 기반하여 설계된 RESTful API 명세서입니다. 모든 API는 비동기 처리(FastAPI 표준) 및 적절한 상태 코드를 반환하도록 설계되었습니다.

---

## 🗺️ API 요약 가이드

| 요구사항 ID | 기능 요약 | Method | Endpoint | 권한 |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-USER-001** | 회원가입 신청 | `POST` | `/api/v1/users/register` | 비회원 (공개) |
| **REQ-USER-002**<br>**NFR-USER-001** | 로그인 (JWT 발급) | `POST` | `/api/v1/users/login` | 비회원 (공개) |
| **NFR-USER-001** | 토큰 재발급 | `POST` | `/api/v1/users/refresh` | 비회원 (쿠키 검증) |
| **REQ-USER-003** | 로그아웃 | `POST` | `/api/v1/users/logout` | 로그인 유저 |
| **REQ-USER-004** | 회원 목록 조회 (검색/필터) | `GET` | `/api/v1/users` | 어드민 (`ADMIN`) |
| **REQ-USER-005** | 회원 권한 변경 | `PATCH` | `/api/v1/users/{user_id}/role` | 어드민 (`ADMIN`) |
| **REQ-USER-006** | 마이페이지 조회 | `GET` | `/api/v1/users/me` | 로그인 유저 |
| **REQ-USER-007** | 회원 정보 수정 (Partial) | `PATCH` | `/api/v1/users/me` | 로그인 유저 |
| **REQ-USER-008** | 비밀번호 변경 | `PUT` | `/api/v1/users/me/password` | 로그인 유저 |
| **REQ-USER-009** | 회원 탈퇴 (즉시 삭제) | `DELETE` | `/api/v1/users/me` | 로그인 유저 |

---

## 📑 상세 API 명세

### 1. 회원가입 신청 (REQ-USER-001)
- **Method**: `POST`
- **Endpoint**: `/api/v1/users/register`
- **Request Body (JSON)**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123@!",
    "name": "박종현",
    "department": "의료", // 연구, 의료, 개발 중 택1
    "gender": "M",        // M / F 중 택1
    "phone_number": "01012345678"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "message": "회원가입 신청이 완료되었습니다. 관리자 승인 대기 상태입니다.",
    "user_id": 1,
    "email": "user@example.com"
  }
  ```

---

### 2. 로그인 및 토큰 발급 (REQ-USER-002 / NFR-USER-001)
- **Method**: `POST`
- **Endpoint**: `/api/v1/users/login`
- **Request Body (JSON)**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123@!"
  }
  ```
- **Response Headers**:
  - `Set-Cookie`: `refresh_token=ey...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800` (7일 만료, 클라이언트 접근 불가)
- **Response Body (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ...",
    "token_type": "bearer"
  }
  ```

---

### 3. 토큰 재발급 (NFR-USER-001)
- **Method**: `POST`
- **Endpoint**: `/api/v1/users/refresh`
- **Request (Cookie)**: `refresh_token` 필수 포함
- **Response Body (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer"
  }
  ```

---

### 4. 로그아웃 (REQ-USER-003)
- **Method**: `POST`
- **Endpoint**: `/api/v1/users/logout`
- **Response Headers**:
  - `Set-Cookie`: `refresh_token=; HttpOnly; Max-Age=0` (쿠키 파기)
- **Response Body (200 OK)**:
  ```json
  { 
    "message": "로그아웃 되었습니다." 
  }
  ```

---

### 5. 회원 목록 조회 (REQ-USER-004)
- **Method**: `GET`
- **Endpoint**: `/api/v1/users`
- **Query Parameters**: `search` (이메일/이름 검색), `department` (부서 필터)
- **Response Body (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "박종현",
      "department": "의료",
      "gender": "M",
      "phone_number": "01012345678",
      "is_active": true
    }
  ]
  ```

---

### 6. 회원 권한 변경 (REQ-USER-005)
- **Method**: `PATCH`
- **Endpoint**: `/api/v1/users/{user_id}/role`
- **Request Body (JSON)**:
  ```json
  {
    "role": "스태프" // 대기자, 스태프, 어드민 중 택1
  }
  ```
- **Response Body (200 OK)**:
  ```json
  {
    "message": "회원 권한이 성공적으로 변경되었습니다.",
    "user_id": 1,
    "changed_role": "스태프"
  }
  ```

---

### 7. 마이페이지 조회 (REQ-USER-006)
- **Method**: `GET`
- **Endpoint**: `/api/v1/users/me`
- **Response Body (200 OK)**:
  ```json
  {
    "name": "박종현",
    "email": "user@example.com",
    "department": "의료",
    "gender": "M",
    "phone_number": "01012345678",
    "role": "스태프"
  }
  ```

---

### 8. 회원 정보 수정 (REQ-USER-007)
- **Method**: `PATCH` (Partial Update)
- **Endpoint**: `/api/v1/users/me`
- **Request Body (JSON)**:
  ```json
  {
    "department": "개발",
    "phone_number": "01099998888"
  }
  ```
- **Response Body (200 OK)**:
  ```json
  {
    "message": "회원 정보가 성공적으로 수정되었습니다.",
    "updated_fields": {
      "department": "개발",
      "phone_number": "01099998888"
    }
  }
  ```

---

### 9. 비밀번호 변경 (REQ-USER-008)
- **Method**: `PUT`
- **Endpoint**: `/api/v1/users/me/password`
- **Request Body (JSON)**:
  ```json
  {
    "current_password": "OldPassword123@!",
    "new_password": "NewPassword123@!"
  }
  ```
- **Response Body (200 OK)**:
  ```json
  { 
    "message": "비밀번호가 성공적으로 변경되었습니다." 
  }
  ```

---

### 10. 회원 탈퇴 (REQ-USER-009)
- **Method**: `DELETE`
- **Endpoint**: `/api/v1/users/me`
- **Response Body (200 OK)**:
  ```json
  { 
    "message": "회원 탈퇴가 완료되었으며 모든 데이터가 영구 삭제되었습니다." 
  }
  ```

---

## ⚡ 비기능적 요구사항 정의 검증 (NFR)
- **NFR-USER-002 (비밀번호 입력 보안)**: 프론트엔드 인풋 마스킹 정책 기반 설계를 지원하며 백엔드는 모든 비밀번호를 평문 저장 없이 단방향 암호화 해시화하여 처리함.
- **NFR-USER-003 (API 성능)**: 인덱스 최적화 및 비동기 ORM(`asyncmy`)을 활용하여 모든 유저 API의 로직 처리 및 응답 속도를 최대 3초 이내로 보장하도록 설계함.


