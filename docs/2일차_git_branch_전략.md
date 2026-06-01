# Git Branch 전략 정리

## 1. Git Flow

### 개념
Git Flow는 Vincent Driessen이 제안한 브랜치 전략으로, 제품 출시 주기가 명확한 프로젝트에 적합합니다.

### 브랜치 구성

| 브랜치 | 역할 |
|--------|------|
| `main` | 실제 배포되는 안정적인 코드 |
| `develop` | 개발 통합 브랜치, 다음 배포를 위한 코드 |
| `feature/기능명` | 새로운 기능 개발 브랜치 |
| `release/버전` | 배포 준비 브랜치 (QA, 버그 수정) |
| `hotfix/이슈` | 배포 중인 버전의 긴급 버그 수정 |

### 흐름
```
main
 └── develop
       ├── feature/login
       ├── feature/signup
       └── release/1.0.0
             └── hotfix/bug-fix
```

### 작업 순서
1. `develop` 브랜치에서 `feature` 브랜치 생성
2. 기능 개발 완료 후 `develop` 으로 merge
3. 배포 준비가 되면 `release` 브랜치 생성
4. 테스트 완료 후 `main` 과 `develop` 에 merge
5. 배포 후 긴급 버그 발생 시 `hotfix` 브랜치 생성

### 장점
- 브랜치 역할이 명확하게 분리됨
- 대규모 팀 프로젝트에 적합
- 버전 관리가 체계적

### 단점
- 브랜치가 많아 복잡함
- 소규모 프로젝트에는 오버스펙

---

## 2. GitHub Flow

### 개념
GitHub Flow는 Git Flow보다 단순한 전략으로, main 브랜치와 feature 브랜치 두 가지만 사용합니다. CI/CD 환경에 적합합니다.

### 브랜치 구성

| 브랜치 | 역할 |
|--------|------|
| `main` | 항상 배포 가능한 안정적인 코드 |
| `feature/기능명` | 새로운 기능 개발 브랜치 |

### 흐름
```
main
 ├── feature/login
 ├── feature/signup
 └── feature/dashboard
```

### 작업 순서
1. `main` 브랜치에서 `feature` 브랜치 생성
2. 기능 개발 및 커밋
3. Pull Request(PR) 생성
4. 코드 리뷰 진행
5. 리뷰 승인 후 `main` 으로 merge
6. 즉시 배포

### 장점
- 구조가 단순하고 이해하기 쉬움
- 빠른 배포 가능
- 소규모 팀에 적합

### 단점
- 브랜치 역할 구분이 부족
- 대규모 프로젝트에는 관리가 어려울 수 있음

---

## 3. Git Flow vs GitHub Flow 비교

| 항목 | Git Flow | GitHub Flow |
|------|----------|-------------|
| 브랜치 수 | 많음 (5종류) | 적음 (2종류) |
| 복잡도 | 높음 | 낮음 |
| 배포 주기 | 주기적 배포 | 수시 배포 |
| 팀 규모 | 대규모 | 소규모 |
| 버전 관리 | 명확 | 단순 |

---

## 4. 우리 팀 브랜치 전략

본 프로젝트에서는 **GitHub Flow** 전략을 채택합니다.

### 이유
- 소규모 팀 프로젝트에 적합
- 브랜치 구조가 단순하여 협업이 용이
- PR을 통한 코드 리뷰 문화 정착 가능

### 브랜치 네이밍 규칙
```
feature/기능명
예) feature/patient-list
    feature/xray-upload
    feature/dashboard
```

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷 변경
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드 설정 변경
```

### 작업 흐름
```
1. main에서 feature 브랜치 생성
   git checkout -b feature/기능명

2. 작업 후 commit
   git add .
   git commit -m "feat: 기능 설명"

3. 원격 저장소에 push
   git push origin feature/기능명

4. GitHub에서 Pull Request 생성

5. 팀원 코드 리뷰

6. 승인 후 main에 merge
```
