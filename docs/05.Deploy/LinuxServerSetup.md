# RedArrow 리눅스 서버 설정 가이드

> 현재 서버 환경에 구성된 RedArrow 시스템의 설정 내용을 정리한 문서입니다.

## 서버 환경 정보

### 시스템 사양
- **OS**: Ubuntu 24.04.3 LTS (Noble Numbat)
- **Kernel**: Linux 6.8.0-90-generic
- **Architecture**: x86_64
- **Python Version**: 3.12.3
- **pip Version**: 25.3

### 프로젝트 설정
- **프로젝트 경로**: `/app/RedArrow`
- **실행 사용자**: `jaengyi`
- **로그 디렉토리**: `/app/RedArrow/logs`

---

## 설치 및 구성 내역

### 1. Python 가상 환경 (venv)

가상 환경이 프로젝트 루트에 생성되어 있습니다.

```bash
# 가상 환경 경로
/app/RedArrow/venv

# 활성화 방법
source /app/RedArrow/venv/bin/activate
```

### 2. 설치된 주요 패키지

현재 설치된 핵심 패키지 목록:

| 패키지 | 버전 | 용도 |
|--------|------|------|
| numpy | 2.4.0 | 수치 계산 |
| pandas | 2.3.3 | 데이터 처리 |
| python-dotenv | 1.2.1 | 환경 변수 관리 |
| requests | 2.32.5 | HTTP 통신 |

```bash
# 전체 패키지 확인
pip list

# 추가 설치가 필요한 경우
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (.env)

환경 변수 파일이 구성되어 있습니다:
- **파일 경로**: `/app/RedArrow/.env`
- **권한**: `-rw-------` (600) - 소유자만 읽기/쓰기 가능
- **템플릿**: `.env.example` 파일 참조

#### 주요 설정 항목

```bash
# 증권사 및 거래 모드
BROKER_TYPE=koreainvestment
TRADING_MODE=simulation

# API 키 (모의투자)
SIMULATION_APP_KEY=your_simulation_app_key_here
SIMULATION_APP_SECRET=your_simulation_app_secret_here
SIMULATION_ACCOUNT_NUMBER=your_simulation_account_number_here

# 리스크 관리
STOP_LOSS_PERCENT=2.5
TAKE_PROFIT_PERCENT=5.0
MAX_POSITION_SIZE=1000000
MAX_POSITIONS=5
DAILY_LOSS_LIMIT=-5.0

# 로그 레벨
LOG_LEVEL=INFO
TIMEZONE=Asia/Seoul
```

⚠️ **보안 주의사항**: `.env` 파일에는 API 키와 계좌 정보가 포함되어 있으므로 절대 Git에 커밋하지 마세요.

### 4. 로그 파일

시스템 로그가 자동으로 생성됩니다:
- **디렉토리**: `/app/RedArrow/logs`
- **파일명 형식**: `redarrow_YYYYMMDD.log`
- **현재 로그**: `redarrow_20260103.log`

```bash
# 실시간 로그 모니터링
tail -f /app/RedArrow/logs/redarrow_$(date +%Y%m%d).log

# 최근 로그 확인
cat /app/RedArrow/logs/redarrow_$(date +%Y%m%d).log | tail -50
```

---

## 실행 방법

### 기본 실행

```bash
# 1. 프로젝트 디렉토리로 이동
cd /app/RedArrow

# 2. 가상 환경 활성화
source venv/bin/activate

# 3. 프로그램 실행
python src/main.py
```

### 시장 시간 확인

프로그램은 한국 증시 개장 시간에만 실행됩니다:
- **개장 시간**: 09:00 - 15:30 (KST)
- **시간외 실행 시**: "시장이 개장하지 않았습니다. 대기 중..." 메시지 출력 후 종료

### 설정 검증

```bash
# 설정 파일 검증
python -m src.config.settings

# 출력 예시:
# ✅ 설정 검증 성공
# 증권사: koreainvestment
# 거래 모드: simulation
# 모의투자: True
```

---

## 프로그램 실행 결과 예시

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  RedArrow Trading System                  ║
║                  단기투자 종목 선정 시스템                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

2026-01-03 04:49:09,728 - __main__ - INFO - ============================================================
2026-01-03 04:49:09,728 - __main__ - INFO - RedArrow 시스템 시작
2026-01-03 04:49:09,728 - __main__ - INFO - ============================================================

⚠️  경고:
  - 데이터베이스 미설정 (현재는 사용하지 않음)
✅ 설정 검증 성공

==================================================
RedArrow 설정 요약
==================================================
증권사: koreainvestment
거래 모드: simulation
모의투자: True
계좌번호: 50158954

손절률: 2.5%
익절률: 5.0%
최대 포지션: 5개
단일 종목 최대 투자금: 1,000,000원
==================================================

2026-01-03 04:49:09,728 - __main__ - INFO - 모든 모듈 초기화 완료
2026-01-03 04:49:09,728 - __main__ - INFO - 시장이 개장하지 않았습니다. 대기 중...
```

---

## 트러블슈팅

### 1. 권한 오류

```bash
# .env 파일 권한 설정
chmod 600 /app/RedArrow/.env

# 로그 디렉토리 권한 설정
chmod 755 /app/RedArrow/logs
```

### 2. 패키지 누락 오류

```bash
# 가상 환경 활성화 확인
which python
# 출력: /app/RedArrow/venv/bin/python

# 패키지 재설치
pip install -r requirements.txt
```

### 3. API 키 오류

```bash
# .env 파일 확인
cat /app/RedArrow/.env | grep -E "(APP_KEY|APP_SECRET|ACCOUNT_NUMBER)"

# 설정 검증
python -m src.config.settings
```

### 4. 로그 확인

```bash
# 최근 에러 로그 확인
grep "ERROR" /app/RedArrow/logs/redarrow_$(date +%Y%m%d).log

# 특정 키워드 검색
grep "매수\|매도" /app/RedArrow/logs/redarrow_*.log
```

---

## 자동 실행 설정 (옵션)

### systemd 서비스 등록

시장 개장 시간에 자동으로 실행되도록 설정:

```bash
# 1. 서비스 파일 생성
sudo nano /etc/systemd/system/redarrow.service
```

```ini
[Unit]
Description=RedArrow Trading System
After=network.target

[Service]
Type=simple
User=jaengyi
WorkingDirectory=/app/RedArrow
Environment="PATH=/app/RedArrow/venv/bin"
ExecStart=/app/RedArrow/venv/bin/python /app/RedArrow/src/main.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

```bash
# 2. 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable redarrow
sudo systemctl start redarrow

# 3. 상태 확인
sudo systemctl status redarrow

# 4. 로그 확인
sudo journalctl -u redarrow -f
```

### Cron 스케줄링

특정 시간에 자동 실행:

```bash
# crontab 편집
crontab -e

# 평일 오전 9시에 실행 (예시)
0 9 * * 1-5 cd /app/RedArrow && source venv/bin/activate && python src/main.py >> /app/RedArrow/logs/cron.log 2>&1
```

---

## 모니터링

### 실시간 로그 모니터링

```bash
# 로그 실시간 추적
tail -f /app/RedArrow/logs/redarrow_$(date +%Y%m%d).log

# 매매 신호만 확인
tail -f /app/RedArrow/logs/redarrow_$(date +%Y%m%d).log | grep -E "매수|매도|선정"
```

### 프로세스 확인

```bash
# Python 프로세스 확인
ps aux | grep "python.*main.py"

# 포트 사용 확인 (API 연결 시)
netstat -tuln | grep ESTABLISHED
```

---

## 업데이트 및 유지보수

### 코드 업데이트

```bash
# Git pull
cd /app/RedArrow
git pull origin main

# 패키지 업데이트
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 로그 정리

```bash
# 30일 이전 로그 삭제
find /app/RedArrow/logs -name "redarrow_*.log" -mtime +30 -delete

# 로그 압축 보관
tar -czf /app/RedArrow/logs/archive_$(date +%Y%m).tar.gz /app/RedArrow/logs/redarrow_*.log
```

---

## 보안 권장사항

1. **.env 파일 보안**
   ```bash
   chmod 600 /app/RedArrow/.env
   chown jaengyi:jaengyi /app/RedArrow/.env
   ```

2. **API 키 주기적 갱신**
   - 한국투자증권 API 포털에서 3개월마다 키 재발급 권장

3. **로그 파일 접근 제한**
   ```bash
   chmod 640 /app/RedArrow/logs/*.log
   ```

4. **방화벽 설정** (필요시)
   ```bash
   # API 통신 포트만 허용
   sudo ufw allow out 443/tcp
   sudo ufw enable
   ```

---

## 관련 문서

- [OCI 배포 가이드](./OCIDeployment.md)
- [OCI 빠른 시작](./OCI-QuickStart.md)
- [프로젝트 구조](../01.Requirements/ProjectScope.md)
- [사용자 매뉴얼](../07.Manual/UserManual.md)

---

## 변경 이력

| 날짜 | 작성자 | 내용 |
|------|--------|------|
| 2026-01-03 | Claude | 초기 문서 작성 - 현재 서버 환경 기준 |

---

**문서 작성일**: 2026-01-03
**서버 환경**: Ubuntu 24.04.3 LTS, Python 3.12.3
**프로젝트 경로**: /app/RedArrow
