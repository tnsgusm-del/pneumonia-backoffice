import sys
from urllib.parse import quote_plus
from sqlalchemy import create_engine

print("=== 🔍 데이터베이스 연결 진단 스크립트 시작 ===")

# 1. 설정 정보 임포트 테스트
try:
    from app.core.config import settings
    print("✅ 1. app.core.config.settings 임포트 성공")
    print(f"   - DB_USER: {settings.DB_USER}")
    print(f"   - DB_HOST: {settings.DB_HOST}")
    print(f"   - DB_PORT: {settings.DB_PORT}")
    print(f"   - DB_NAME: {settings.DB_NAME}")
except Exception as e:
    print(f"❌ 1. 설정파일 임포트 실패: {e}")
    sys.exit(1)

# 2. 비밀번호 인코딩 및 URL 조립
try:
    encoded_password = quote_plus(settings.DB_PASSWORD)
    DATABASE_URL_SYNC = f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    print("✅ 2. DB 연결 URL 조립 성공")
except Exception as e:
    print(f"❌ 2. URL 조립 실패: {e}")
    sys.exit(1)

# 3. 실제 DB 접속 테스트 (제한 시간 5초 설정)
print(f"\n⚡ 3. {settings.DB_HOST}:{settings.DB_PORT} 서버로 5초간 연결 시도 중...")
try:
    # connect_timeout을 5초로 제한하여 무한 대기를 방지합니다.
    engine = create_engine(
        DATABASE_URL_SYNC, 
        connect_args={"connect_timeout": 5}
    )
    with engine.connect() as conn:
        print("🎉 [성공] MySQL 데이터베이스 연결에 완전히 성공했습니다!")
except Exception as e:
    print("\n❌ 3. 데이터베이스 연결 최종 실패!")
    print("=== 에러 원인 상세 내용 ===")
    print(e)
    print("==========================")
    print("\n💡 [해결 조치 팁]")
    print("1. 로컬 컴퓨터의 MySQL 서비스가 '실행 중(Running)'인지 확인하세요.")
    print("   (윈도우 검색창 -> '서비스(Services)' 검색 -> 'MySQL' 또는 'MySQL80' 서비스 우클릭 후 '시작')")
    print("2. Workbench나 DBeaver 등의 툴로 동일한 계정 정보 접속이 가능한지 확인해 보세요.")