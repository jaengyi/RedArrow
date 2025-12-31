# RedArrow 문제 해결 가이드

## 📌 개요

RedArrow 사용 중 발생할 수 있는 일반적인 문제와 해결 방법을 안내합니다.

---

## 목차

1. [설치 및 설정 문제](#1-설치-및-설정-문제)
2. [API 연결 문제](#2-api-연결-문제)
3. [실행 중 오류](#3-실행-중-오류)
4. [거래 관련 문제](#4-거래-관련-문제)
5. [성능 문제](#5-성능-문제)
6. [로그 분석](#6-로그-분석)

---

## 1. 설치 및 설정 문제

### 1.1 Python 버전 오류

**증상:**
```bash
$ python3 --version
Python 3.9.7
```

**문제**: Python 3.11 이상 필요

**해결책:**

**macOS:**
```bash
# Homebrew로 최신 Python 설치
brew install python@3.11

# 설치 확인
python3.11 --version

# 가상환경 재생성
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Ubuntu/Linux:**
```bash
# Python 3.11 저장소 추가
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 설치
sudo apt install python3.11 python3.11-venv

# 가상환경 생성
python3.11 -m venv venv
```

---

### 1.2 패키지 설치 실패

**증상:**
```bash
$ pip install -r requirements.txt
ERROR: Could not find a version that satisfies the requirement...
```

**해결책 1: pip 업그레이드**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**해결책 2: 개별 설치**
```bash
# 실패하는 패키지 제외하고 설치
pip install pandas numpy pyyaml python-dotenv requests

# 선택적 패키지는 나중에
pip install TA-Lib  # 실패 시 건너뛰기
```

**해결책 3: TA-Lib 설치 문제**

TA-Lib는 C 라이브러리 의존성이 있어 설치가 까다로울 수 있습니다.

**macOS:**
```bash
# Homebrew로 먼저 설치
brew install ta-lib

# Python 패키지 설치
pip install TA-Lib
```

**Ubuntu/Linux:**
```bash
# 의존성 설치
sudo apt-get install build-essential wget

# TA-Lib C 라이브러리 설치
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Python 패키지 설치
pip install TA-Lib
```

**Windows:**
- 사전 컴파일된 wheel 파일 다운로드
- https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

---

### 1.3 .env 파일 문제

**증상:**
```
⚠️  .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성하세요.
```

**해결책:**
```bash
# .env.example 복사
cp .env.example .env

# 편집
nano .env
```

**증상:**
```
❌ 설정 검증 실패:
  - APP_KEY가 설정되지 않았습니다.
```

**원인:**
- API 키가 입력되지 않음
- 공백이나 따옴표가 잘못 입력됨

**해결책:**
```env
# ❌ 잘못된 예
SIMULATION_APP_KEY="PSxkN3fH..."  # 따옴표 제거 필요
SIMULATION_APP_KEY = PSxkN3fH...  # 공백 제거 필요

# ✅ 올바른 예
SIMULATION_APP_KEY=PSxkN3fH8Gp2Lm9Rq4Tv7Yw1Zb5Cd8Ef
```

---

## 2. API 연결 문제

### 2.1 API 인증 실패

**증상:**
```
[ERROR] API 인증 실패: 401 Unauthorized
```

**원인:**
1. API 키가 잘못됨
2. API 키가 만료됨
3. 모의투자/실전투자 키가 바뀜

**해결책:**

1. **API 키 재확인**
   ```bash
   # .env 파일 확인
   cat .env | grep "APP_KEY\|APP_SECRET"
   ```

2. **모드 확인**
   ```env
   # .env에서 확인
   TRADING_MODE=simulation  # 또는 real

   # simulation이면 SIMULATION_APP_KEY 사용
   # real이면 REAL_APP_KEY 사용
   ```

3. **API 키 재발급**
   - https://apiportal.koreainvestment.com/ 접속
   - 기존 키 폐기 후 재발급

---

### 2.2 네트워크 연결 오류

**증상:**
```
[ERROR] Connection timeout
[ERROR] Failed to connect to API server
```

**해결책:**

1. **인터넷 연결 확인**
   ```bash
   ping 8.8.8.8
   curl https://www.google.com
   ```

2. **방화벽 확인**
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

   # Linux
   sudo ufw status
   ```

3. **프록시 설정 확인**
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

4. **DNS 문제**
   ```bash
   # DNS 캐시 초기화 (macOS)
   sudo dscacheutil -flushcache

   # DNS 캐시 초기화 (Linux)
   sudo systemd-resolve --flush-caches
   ```

---

### 2.3 API Rate Limit 초과

**증상:**
```
[ERROR] API rate limit exceeded
[ERROR] 429 Too Many Requests
```

**해결책:**

1. **대기 후 재시도**
   - 1-5분 대기 후 재실행

2. **호출 빈도 조정**
   ```yaml
   # config/config.yaml
   data_collection:
     update_interval: 10  # 10초로 늘림 (기본 5초)
   ```

3. **캐싱 활용** (향후 구현 예정)

---

## 3. 실행 중 오류

### 3.1 프로그램이 즉시 종료됨

**증상:**
```
[INFO] RedArrow 시스템 시작
[WARNING] 시장 운영 시간이 아닙니다
[INFO] 프로그램을 종료합니다
```

**원인**: 시장 운영 시간 외 실행

**해결책:**

1. **시간 확인**
   - 평일 09:00 - 15:30에만 실행

2. **테스트를 위해 시간 제한 임시 해제**
   ```python
   # src/main.py에서 수정 (개발/테스트용)
   def is_market_open(self):
       # return True  # 항상 True 반환 (테스트용)
       ...
   ```

---

### 3.2 ModuleNotFoundError

**증상:**
```bash
$ python src/main.py
ModuleNotFoundError: No module named 'pandas'
```

**원인**: 가상환경 미활성화 또는 패키지 미설치

**해결책:**

1. **가상환경 활성화 확인**
   ```bash
   # 프롬프트에 (venv) 있는지 확인
   source venv/bin/activate
   ```

2. **패키지 재설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **Python 경로 확인**
   ```bash
   which python
   # 출력: .../RedArrow/venv/bin/python 이어야 함
   ```

---

### 3.3 Permission Denied

**증상:**
```bash
$ python src/main.py
PermissionError: [Errno 13] Permission denied: 'logs/redarrow.log'
```

**해결책:**

1. **로그 디렉토리 권한 확인**
   ```bash
   ls -la logs/
   ```

2. **권한 부여**
   ```bash
   chmod 755 logs/
   chmod 644 logs/*.log
   ```

3. **로그 디렉토리 생성**
   ```bash
   mkdir -p logs
   ```

---

### 3.4 YAML 파싱 오류

**증상:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**원인**: config.yaml 파일 문법 오류

**해결책:**

1. **YAML 문법 검증**
   ```bash
   # Python으로 확인
   python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
   ```

2. **들여쓰기 확인**
   - YAML은 공백으로 들여쓰기 (탭 사용 금지)
   - 일관된 들여쓰기 (2칸 또는 4칸)

3. **백업에서 복원**
   ```bash
   git checkout config/config.yaml
   ```

---

## 4. 거래 관련 문제

### 4.1 종목이 선정되지 않음

**증상:**
```
[INFO] 거래대금 상위 30개 종목 필터링 완료
[INFO] 조건 만족 종목: 0개
```

**원인:**
- 선정 기준이 너무 엄격함
- 시장 상황이 조건에 맞지 않음

**해결책:**

1. **선정 기준 완화**
   ```yaml
   # config/config.yaml
   stock_selector:
     min_score: 3  # 5에서 3으로 낮춤
     volume_surge_threshold: 1.5  # 2.0에서 1.5로 낮춤
   ```

2. **로그에서 점수 확인**
   ```bash
   grep "점수" logs/redarrow.log
   ```

3. **수동으로 조건 확인**
   - 거래량이 충분한지
   - 기술적 지표가 신호를 주는지

---

### 4.2 주문이 체결되지 않음

**증상:**
```
[INFO] 매수 주문: 삼성전자 10주 @ 70,000원
[WARNING] 주문 미체결: 타임아웃
```

**원인:**
1. 호가가 맞지 않음
2. 시장가가 아닌 지정가로 주문
3. 거래량 부족

**해결책:**

1. **주문 타입 확인**
   ```python
   # 시장가 주문 사용 (즉시 체결)
   order_type = "market"  # 또는 "limit"
   ```

2. **수동으로 확인**
   - 한국투자증권 앱/웹에서 미체결 주문 확인
   - 필요시 수동 취소/재주문

---

### 4.3 잔고 부족 오류

**증상:**
```
[ERROR] 주문 실패: 잔고 부족
```

**해결책:**

1. **계좌 잔고 확인**
   - 한국투자증권 앱/웹에서 확인

2. **투자금액 조정**
   ```env
   # .env 파일
   MAX_POSITION_SIZE=500000  # 100만원에서 50만원으로 줄임
   ```

3. **모의투자 계좌 확인**
   - 모의투자 계좌도 초기 자금이 설정되어 있음
   - 부족 시 리셋 필요

---

## 5. 성능 문제

### 5.1 프로그램이 느림

**증상:**
- 종목 분석에 5분 이상 소요
- CPU 사용률 100%

**해결책:**

1. **분석 대상 종목 수 줄이기**
   ```yaml
   # config/config.yaml
   stock_selector:
     top_volume_count: 20  # 30에서 20으로 줄임
   ```

2. **지표 계산 최적화**
   - 불필요한 지표 계산 비활성화

3. **시스템 리소스 확인**
   ```bash
   # CPU/메모리 사용량 확인
   top
   htop
   ```

---

### 5.2 메모리 부족

**증상:**
```
MemoryError: Unable to allocate array
```

**해결책:**

1. **데이터 크기 확인**
   ```python
   import pandas as pd
   df.memory_usage(deep=True).sum() / 1024**2  # MB 단위
   ```

2. **데이터 타입 최적화**
   ```python
   # float64 → float32로 변경
   df = df.astype('float32')
   ```

3. **분할 처리**
   - 한 번에 모든 종목 처리하지 않고 배치로 나눔

---

## 6. 로그 분석

### 6.1 로그 레벨 변경

**디버그 로그 활성화:**
```env
# .env 파일
LOG_LEVEL=DEBUG  # INFO에서 DEBUG로 변경
```

**로그 레벨:**
- `DEBUG`: 모든 상세 정보
- `INFO`: 일반 정보
- `WARNING`: 경고
- `ERROR`: 오류만
- `CRITICAL`: 치명적 오류만

---

### 6.2 로그 파일이 너무 큼

**증상:**
```bash
$ ls -lh logs/
-rw-r--r-- 1 user 5.2G redarrow.log
```

**해결책:**

1. **로그 로테이션 설정**
   ```bash
   # logrotate 설정 (Linux)
   sudo nano /etc/logrotate.d/redarrow
   ```

   ```
   /path/to/RedArrow/logs/*.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

2. **수동 정리**
   ```bash
   # 7일 이전 로그 삭제
   find logs/ -name "*.log" -mtime +7 -delete

   # 압축
   gzip logs/redarrow_old.log
   ```

---

### 6.3 주요 로그 패턴

**정상 실행:**
```
[INFO] RedArrow 시스템 시작
[INFO] 한국투자증권 API 연결 성공
[INFO] 시장 데이터 수집 중...
[INFO] 종목 선정: 삼성전자 (점수: 7점)
[INFO] 매수 주문: 삼성전자 10주 @ 70,000원
[INFO] 주문 체결 완료
```

**주의 필요:**
```
[WARNING] 시장 변동성 높음
[WARNING] 일일 손실률 -3% 도달
[WARNING] API 호출 제한 근접
```

**즉시 확인 필요:**
```
[ERROR] API 연결 실패
[ERROR] 주문 실패: 잔고 부족
[ERROR] 예상치 못한 오류 발생
```

---

## 7. 긴급 상황 대응

### 7.1 시스템 오작동

**증상:**
- 의도하지 않은 주문 발생
- 손실이 급격히 증가

**즉시 조치:**

1. **프로그램 즉시 중지**
   ```bash
   Ctrl + C
   # 또는
   kill -9 $(pgrep -f "python src/main.py")
   ```

2. **한국투자증권 앱/웹에서 확인**
   - 미체결 주문 모두 취소
   - 보유 포지션 확인

3. **필요 시 수동 청산**

4. **로그 확인**
   ```bash
   tail -100 logs/redarrow.log > emergency_log.txt
   ```

---

### 7.2 계정 잠김

**증상:**
```
[ERROR] Account locked
```

**조치:**
- 한국투자증권 고객센터 연락
- API 키 재발급

---

### 7.3 데이터 불일치

**증상:**
- 프로그램의 포지션과 실제 계좌가 다름

**조치:**

1. **프로그램 중지**

2. **실제 계좌 확인**
   - 한국투자증권 앱/웹

3. **로그 분석**
   ```bash
   grep "체결\|취소" logs/redarrow.log
   ```

4. **불일치 원인 파악**
   - 수동 개입 여부
   - 프로그램 재시작 여부

---

## 8. 도움 받기

### 8.1 버그 리포트

GitHub Issues에 리포트 시 포함할 정보:

```markdown
## 환경
- OS: macOS 13.0
- Python: 3.11.5
- RedArrow 버전: commit hash

## 문제 설명
간단한 설명...

## 재현 방법
1. ...
2. ...
3. ...

## 예상 동작
...

## 실제 동작
...

## 로그
\`\`\`
[에러 로그 복사]
\`\`\`

## 추가 정보
...
```

### 8.2 자주 확인할 문서

- **API 키 관리**: `docs/06.Security/APIKeyManagement.md`
- **데이터베이스**: `docs/06.Security/DatabaseGuide.md`
- **실행 가이드**: `docs/07.Manual/ExecutionGuide.md`
- **시스템 설계**: `docs/03.Design/SystemDesign_20251231.md`

---

## 9. 예방 조치

### 9.1 정기 점검 항목

**매일:**
- [ ] API 키 유효성 확인
- [ ] 로그 파일 크기 확인
- [ ] 디스크 공간 확인

**매주:**
- [ ] 성과 분석
- [ ] 설정 최적화
- [ ] 로그 백업

**매월:**
- [ ] API 키 갱신 (필요시)
- [ ] 의존성 패키지 업데이트
- [ ] 시스템 업데이트

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 문제 해결 가이드 초안 작성 | - |
