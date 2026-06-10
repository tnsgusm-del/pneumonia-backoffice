
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

# 기본 제공 데이터
user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!"
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!"
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@"
    }
]

# Request Body를 위한 Pydantic 모델 정의
class UserCreate(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    age: int
    email: EmailStr

# 1. 모든 회원의 정보를 목록으로 조회하는 API
@router.get("/users")
def get_all_users():
    return user_list

# 2. 특정 회원의 정보를 조회하는 API (ID 기준)

import re
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/practice_api", tags=["Practice User API"])

user_list = [
	{"id": 1, "name": "홍길동", "age": 24, "email": "gildong24@example.com", "password": "Password1234!!"},
	{"id": 2, "name": "장문복", "age": 21, "email": "moonluck12@example.com", "password": "Check1321!"},
	{"id": 3, "name": "임우진", "age": 31, "email": "limousine33@example.com", "password": "lwsPAssword12@"}
]

def validate_email_format(email: str):
    if len(email) > 30:
        raise HTTPException(status_code=400, detail="이메일은 최대 30자까지 가능합니다.")
    regex = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(regex, email):
        raise HTTPException(status_code=400, detail="올바른 이메일 형식이 아닙니다.")

def validate_password_format(password: str):
    if not (8 <= len(password) <= 20):
        raise HTTPException(status_code=400, detail="비밀번호는 8자 이상 20자 이하로 입력해주세요.")
    if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="비밀번호에는 대소문자와 특수문자가 각각 1개 이상 포함되어야 합니다.")

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=10)
    age: int = Field(..., ge=14)
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    age: int | None = Field(None, ge=14)
    email: str | None = None
    password: str | None = None

# 1. 모든 회원 정보 목록 조회
@router.get("/users")
def get_all_users():
    return [{"id": u["id"], "name": u["name"], "age": u["age"], "email": u["email"]} for u in user_list]

# 2. 특정 회원 정보 조회

@router.get("/users/{user_id}")
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:

            return user
    raise HTTPException(status_code=404, detail="User not found")

# 3. 회원의 정보를 입력받아 추가하는 API
@router.post("/users")
def create_user(user: UserCreate):
    # 중복 ID 체크 (선택)
    for existing_user in user_list:
        if existing_user["id"] == user.id:
            raise HTTPException(status_code=400, detail="ID already exists")
    
    new_user = user.model_dump() # Pydantic 모델을 딕셔너리로 변환
    user_list.append(new_user)
    return {"message": "User created successfully", "user": new_user}

# 4. 특정 회원의 나이와 이메일을 수정하는 API
@router.put("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdate):
    for user in user_list:
        if user["id"] == user_id:
            user["age"] = update_data.age
            user["email"] = update_data.email
            return {"message": "User updated successfully", "user": user}
    raise HTTPException(status_code=404, detail="User not found")

# 5. 특정 회원의 정보를 삭제하는 API
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for idx, user in enumerate(user_list):
        if user["id"] == user_id:
            deleted_user = user_list.pop(idx)
            return {"message": "User deleted successfully", "user": deleted_user}
    raise HTTPException(status_code=404, detail="User not found")

# 2단계: 깃 충돌 해결 과정에서 꼬여서 지워졌던 회원 조회 API 복구
@router.get("/{user_id}")  # (혹은 기존에 작성하셨던 데코레이터)
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return {"id": user["id"], "name": user["name"], "age": user["age"], "email": user["email"]}
    raise HTTPException(status_code=404, detail="해당 ID의 회원을 찾을 수 없습니다.")

# 3. 회원 정보 추가
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreateRequest):
    validate_email_format(user_data.email)
    validate_password_format(user_data.password)
    
    if any(u["email"] == user_data.email for u in user_list):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        
    next_id = max(u["id"] for u in user_list) + 1 if user_list else 1
    new_user = {
        "id": next_id, "name": user_data.name, "age": user_data.age, "email": user_data.email, "password": user_data.password
    }
    user_list.append(new_user)
    return {"message": "회원이 성공적으로 등록되었습니다.", "user_id": next_id}

# 4. 회원 정보 수정
@router.put("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdateRequest):
    if update_data.age is None and update_data.email is None and update_data.password is None:
        raise HTTPException(status_code=400, detail="수정할 항목을 최소 하나 이상 입력해주세요.")
        
    target_user = None
    for user in user_list:
        if user["id"] == user_id:
            target_user = user
            break
            
    if not target_user:
        raise HTTPException(status_code=404, detail="해당 ID의 회원을 찾을 수 없습니다.")
        
    if update_data.age is not None:
        target_user["age"] = update_data.age
    if update_data.email is not None:
        validate_email_format(update_data.email)
        target_user["email"] = update_data.email
    if update_data.password is not None:
        validate_password_format(update_data.password)
        target_user["password"] = update_data.password
        
    return {"message": "회원 정보가 수정되었습니다."}

# 5. 특정 회원 정보 삭제
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(user_list):
        if user["id"] == user_id:
            del user_list[i]
            return {"message": "회원 정보가 삭제되었습니다."}
    raise HTTPException(status_code=404, detail="해당 ID의 회원을 찾을 수 없습니다.")
