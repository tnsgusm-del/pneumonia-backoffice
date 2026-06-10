import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt

from app.core.db.databases import Base, get_db
from app.models.user import User, GenderEnum, DepartmentEnum, RoleEnum

# ==========================================
# 🗺️ API 라우터 선언 (인증용과 유저용 분리)
# ==========================================
# 인증 관련 라우터 (/api/v1/auth)
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# 유저 정보 조작 라우터 (/api/v1/users)
user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# ==========================================
# 🔒 보안 및 JWT 설정 (NFR-USER-001)
# ==========================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_password_hash(password: str) -> str:
    """비밀번호 해싱 암호화 함수"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증 함수"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Access Token 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Refresh Token 생성"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================
# 📋 Pydantic DTO 스키마 정의
# ==========================================
class UserRegister(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="Password123@!")
    name: str = Field(..., max_length=100, example="박종현")
    department: DepartmentEnum = Field(..., example=DepartmentEnum.MEDICAL)
    gender: GenderEnum = Field(..., example=GenderEnum.M)
    phone_number: str = Field(..., example="01012345678")

class UserLogin(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="Password123@!")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: Optional[str]
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    role: RoleEnum = Field(..., example=RoleEnum.STAFF)

class UserUpdate(BaseModel):
    department: Optional[DepartmentEnum] = Field(None, example=DepartmentEnum.DEV)
    phone_number: Optional[str] = Field(None, example="01099998888")

class PasswordUpdate(BaseModel):
    current_password: str = Field(..., example="OldPassword123@!")
    new_password: str = Field(..., min_length=8, example="NewPassword123@!")


# ==========================================
# 🚀 인증 라우터 구현체 (/api/v1/auth)
# ==========================================

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """[REQ-USER-001] 신규 회원가입 등록"""
    exist_email = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
    if exist_email:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    
    exist_phone = db.execute(select(User).where(User.phone_number == user_data.phone_number)).scalars().first()
    if exist_phone:
        raise HTTPException(status_code=400, detail="이미 사용 중인 휴대폰 번호입니다.")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        name=user_data.name,
        department=user_data.department,
        gender=user_data.gender,
        phone_number=user_data.phone_number,
        role=RoleEnum.PENDING,  # 최초 가입 시 승인 대기자 상태
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth_router.post("/login", response_model=TokenResponse)
def login_user(response: Response, login_data: UserLogin, db: Session = Depends(get_db)):
    """[REQ-USER-002 / NFR-USER-001] 로그인 및 JWT 발급"""
    user = db.execute(select(User).where(User.email == login_data.email)).scalars().first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="비활성화된 계정입니다. 관리자에게 문의하세요.")
        
    if user.role == RoleEnum.PENDING:
        raise HTTPException(status_code=401, detail="관리자의 가입 승인을 기다리는 대기자 상태입니다.")

    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    # HTTP-Only 쿠키 설정
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="strict",
        secure=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/token/refresh", response_model=TokenResponse)
def refresh_token_endpoint(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """[NFR-USER-001] 리프레시 토큰을 이용한 엑세스 토큰 갱신"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 쿠키에 존재하지 않습니다.")
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="인증 토큰 정보가 올바르지 않습니다.")
    except JWTError:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다. 다시 로그인해 주세요.")

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="유효하지 않은 계정 세션입니다.")

    new_access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": new_access_token, "token_type": "bearer"}


@auth_router.post("/logout")
def logout_user(response: Response):
    """[REQ-USER-003] 쿠키 비우기 및 로그아웃"""
    response.delete_cookie(key="refresh_token", httponly=True, samesite="strict")
    return {"message": "로그아웃 되었습니다."}


# ==========================================
# 🚀 유저 정보 조작 라우터 구현체 (/api/v1/users)
# ==========================================

@user_router.get("", response_model=List[UserResponse])
def get_user_list(
    search: Optional[str] = None,
    department: Optional[DepartmentEnum] = None,
    db: Session = Depends(get_db)
):
    """[REQ-USER-004] 관리자 전용 전체 회원 목록 조회"""
    query = select(User)
    
    if search:
        query = query.where(
            or_(
                User.email.contains(search),
                User.name.contains(search)
            )
        )
    if department:
        query = query.where(User.department == department)
        
    result = db.execute(query).scalars().all()
    return result


@user_router.patch("/{user_id}/role")
def change_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-005] 관리자 전용 특정 회원 역할(권한) 변경"""
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="지정한 사용자를 찾을 수 없습니다.")
    
    user.role = role_data.role
    db.commit()
    return {
        "message": "회원 권한이 성공적으로 변경되었습니다.",
        "user_id": user.id,
        "changed_role": user.role
    }


@user_router.get("/me", response_model=UserResponse)
def get_my_profile(db: Session = Depends(get_db)):
    """[REQ-USER-006] 내 마이페이지 프로필 조회"""
    dummy_user = db.execute(select(User)).scalars().first()
    if not dummy_user:
        raise HTTPException(status_code=404, detail="사용자 정보가 존재하지 않습니다.")
    return dummy_user


@user_router.patch("/me", response_model=UserResponse)
def update_my_profile(update_data: UserUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-007] 마이페이지 일부 정보(부서, 전화번호) 수정"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="수정할 사용자 정보가 존재하지 않습니다.")

    if update_data.department is not None:
        user.department = update_data.department
    if update_data.phone_number is not None:
        exist_phone = db.execute(
            select(User).where(User.phone_number == update_data.phone_number, User.id != user.id)
        ).scalars().first()
        if exist_phone:
            raise HTTPException(status_code=400, detail="이미 다른 사용자가 등록한 휴대폰 번호입니다.")
        user.phone_number = update_data.phone_number

    db.commit()
    db.refresh(user)
    return user


@user_router.patch("/me/password")
def change_my_password(pwd_data: PasswordUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-008] 기존 비밀번호 검증 후 비밀번호 변경"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    if not verify_password(pwd_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="현재 사용 중인 비밀번호가 일치하지 않습니다.")

    user.hashed_password = get_password_hash(pwd_data.new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_my_account(db: Session = Depends(get_db)):
    """[REQ-USER-009] 본인 회원 탈퇴 (CASCADE 삭제 보장)"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="탈퇴할 회원 정보가 존재하지 않습니다.")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)