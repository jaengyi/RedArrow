# 데이터베이스 가이드

## 📌 중요 안내

**현재 RedArrow 시스템에서는 PostgreSQL과 Redis를 사용하지 않습니다!**

데이터베이스 설치는 **선택사항**이며, 지금 당장 설치하지 않아도 프로그램이 정상 작동합니다.

---

## 🔍 현재 상황

### ✅ 설치하지 않아도 되는 것들

1. **PostgreSQL** - 설치 불필요
2. **Redis** - 설치 불필요
3. **InfluxDB** - 설치 불필요

### 💡 왜 문서에 나와있나요?

문서에 데이터베이스가 언급된 이유:
- **장기 개발 계획**에 포함되어 있습니다
- 추후 기능 확장 시 필요할 수 있습니다
- 전체 시스템 설계의 일부입니다

하지만 **현재 구현된 코드에서는 사용하지 않습니다!**

---

## 📊 데이터베이스 사용 계획 (미래)

### PostgreSQL이 필요한 경우

다음 기능을 추가할 때 설치가 필요합니다:

#### 1. 백테스팅 기능
```
목적: 과거 데이터로 전략 성과 검증
저장 데이터:
- 과거 주가 데이터 (일봉, 분봉)
- 거래량 데이터
- 기술적 지표 계산 결과
```

#### 2. 거래 이력 관리
```
목적: 모든 거래 기록 보관 및 분석
저장 데이터:
- 주문 내역 (매수/매도)
- 체결 내역
- 손익 계산 결과
- 일일/월간 성과 리포트
```

#### 3. 종목 분석 히스토리
```
목적: 종목 선정 기록 추적
저장 데이터:
- 일별 선정 종목 목록
- 선정 점수 기록
- 기술적 지표 스냅샷
```

### Redis가 필요한 경우

다음 최적화를 수행할 때 설치가 필요합니다:

#### 1. API 호출 캐싱
```
목적: 증권사 API 호출 횟수 절감
캐싱 데이터:
- 실시간 시세 (짧은 TTL)
- 종목 정보
- 거래소 영업일 캘린더
```

#### 2. 세션 관리
```
목적: API 인증 토큰 관리
캐싱 데이터:
- Access Token (만료 전까지)
- API 호출 제한 카운터
```

#### 3. 성능 최적화
```
목적: 계산 결과 재사용
캐싱 데이터:
- 기술적 지표 계산 결과
- 종목 스크리닝 중간 결과
```

---

## 🚀 현재 시스템 동작 방식

### 데이터 흐름 (DB 없이)

```
1. 프로그램 시작
   ↓
2. 한국투자증권 API 호출
   ↓
3. 실시간 데이터 수신
   ↓
4. 메모리에서 기술적 지표 계산
   ↓
5. 종목 선정 및 거래 실행
   ↓
6. 종료 (데이터 저장 안 함)
```

**모든 데이터는 메모리에서만 처리되고 프로그램 종료 시 사라집니다.**

---

## 📅 데이터베이스가 필요해지는 시점

### Phase 1: 현재 (DB 불필요)
- ✅ 실시간 종목 선정
- ✅ 자동 매매 실행
- ✅ 리스크 관리

### Phase 2: 거래 이력 기록 (PostgreSQL 필요)
- 매일의 거래 내역 저장
- 월간 성과 리포트
- 손익 추이 분석

### Phase 3: 백테스팅 (PostgreSQL 필요)
- 과거 데이터로 전략 검증
- 최적 파라미터 찾기
- 성과 시뮬레이션

### Phase 4: 성능 최적화 (Redis 필요)
- API 호출 캐싱
- 빠른 데이터 조회
- 다중 인스턴스 운영

---

## 🛠️ 미래에 DB 설치가 필요하다면

### PostgreSQL 설치 방법

**macOS:**
```bash
# Homebrew로 설치
brew install postgresql@15

# 시작
brew services start postgresql@15

# 데이터베이스 생성
createdb redarrow_db

# 사용자 생성
psql -d postgres
CREATE USER redarrow WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE redarrow_db TO redarrow;
```

**Ubuntu/Linux:**
```bash
# 설치
sudo apt update
sudo apt install postgresql-15

# 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 및 사용자 생성
sudo -u postgres psql
CREATE DATABASE redarrow_db;
CREATE USER redarrow WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE redarrow_db TO redarrow;
```

### Redis 설치 방법

**macOS:**
```bash
# Homebrew로 설치
brew install redis

# 시작
brew services start redis

# 확인
redis-cli ping
# 응답: PONG
```

**Ubuntu/Linux:**
```bash
# 설치
sudo apt update
sudo apt install redis-server

# 시작
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 확인
redis-cli ping
# 응답: PONG
```

### .env 파일 업데이트

DB 설치 후 `.env` 파일 수정:

```env
# PostgreSQL 설정
DB_HOST=localhost
DB_PORT=5432
DB_NAME=redarrow_db
DB_USER=redarrow
DB_PASSWORD=your_actual_password

# Redis 설정
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # 로컬 개발 시 비밀번호 불필요
```

---

## ❓ FAQ

### Q1. 지금 바로 PostgreSQL을 설치해야 하나요?
**A:** 아니요! 현재는 필요하지 않습니다. 프로그램이 DB 없이도 정상 작동합니다.

### Q2. 검증(validate) 실패 메시지가 나와요!
**A:** 수정했습니다! 이제 DB 설정이 없어도 경고만 표시되고 정상 실행됩니다:
```
⚠️ 경고:
  - 데이터베이스 미설정 (현재는 사용하지 않음)

✅ 설정 검증 성공
```

### Q3. requirements.txt에 psycopg2가 있는데요?
**A:** 미래를 위한 의존성입니다. 설치는 해도 되고 안 해도 됩니다:
```bash
# PostgreSQL 라이브러리만 제외하고 설치
grep -v psycopg2 requirements.txt > requirements_minimal.txt
pip install -r requirements_minimal.txt
```

### Q4. 언제 DB를 설치해야 하나요?
**A:** 다음 기능이 필요할 때 설치하세요:
- 거래 이력을 장기 보관하고 싶을 때
- 백테스팅 기능을 사용하고 싶을 때
- 월간/연간 성과 리포트가 필요할 때

### Q5. DB 없이 거래 이력은 어떻게 보나요?
**A:** 현재는 로그 파일(`logs/` 디렉토리)에 기록됩니다:
```bash
# 로그 확인
tail -f logs/redarrow.log

# 거래 이력 검색
grep "매수\|매도" logs/redarrow.log
```

---

## 📝 체크리스트: DB 설치가 필요한가?

다음 중 하나라도 해당되면 DB 설치를 고려하세요:

- [ ] 과거 거래 데이터를 분석하고 싶다
- [ ] 백테스팅으로 전략을 검증하고 싶다
- [ ] 월간/연간 성과 리포트가 필요하다
- [ ] 여러 서버에서 동시 운영하고 싶다
- [ ] API 호출 횟수를 줄이고 싶다

**모두 체크 안 됨** → DB 설치 불필요! 지금 그대로 사용하세요.

---

## 🔗 관련 문서

- [APIKeyManagement.md](./APIKeyManagement.md) - API 키 관리 (필수)
- [DeploymentGuide_20251231.md](../05.Deploy/DeploymentGuide_20251231.md) - 배포 가이드
- [TechnicalAnalysis_20251231.md](../02.Analysis/TechnicalAnalysis_20251231.md) - 기술 스택

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 데이터베이스 가이드 초안 작성 | - |
