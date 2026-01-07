# RedArrow 스크립트 모음

RedArrow 자동 매매 시스템을 쉽게 관리할 수 있는 스크립트 모음입니다.

## 📁 스크립트 목록

### 관리 스크립트

#### start.sh
**용도**: RedArrow 시스템 시작 (백그라운드)

**실행 방법**:
```bash
./scripts/start.sh
```

**수행 작업**:
- 가상환경 자동 활성화
- 의존성 패키지 확인 및 설치
- 백그라운드 프로세스로 실행
- PID 파일 생성 (`.redarrow.pid`)
- 로그 파일 자동 생성

#### stop.sh
**용도**: RedArrow 시스템 안전 중지

**실행 방법**:
```bash
./scripts/stop.sh
```

**수행 작업**:
- SIGTERM 신호로 정상 종료 시도 (최대 10초 대기)
- 정상 종료 실패 시 SIGKILL로 강제 종료
- PID 파일 자동 삭제

#### restart.sh
**용도**: RedArrow 시스템 재시작

**실행 방법**:
```bash
./scripts/restart.sh
```

**수행 작업**:
- 기존 프로세스 중지
- 2초 대기
- 새 프로세스 시작

#### status.sh
**용도**: RedArrow 시스템 상태 확인

**실행 방법**:
```bash
./scripts/status.sh
```

**표시 정보**:
- 실행 상태 (실행 중/중지)
- PID, 실행 시간, CPU/메모리 사용률
- 로그 파일 정보
- 거래 모드 (모의투자/실전투자)
- 최근 로그 (마지막 5줄)

---

### 배포 스크립트

#### oci_setup.sh

**용도**: OCI 인스턴스 자동 설정

**지원 OS**:
- Oracle Linux 8
- Ubuntu 22.04 LTS

**실행 방법**:
```bash
# OCI 인스턴스에서 실행
wget https://raw.githubusercontent.com/jaengyi/RedArrow/main/scripts/oci_setup.sh
chmod +x oci_setup.sh
bash oci_setup.sh
```

**수행 작업**:
1. 시스템 업데이트
2. 개발 도구 설치
3. Python 3.11 설치
4. Git 설정
5. 프로젝트 클론
6. Python 가상환경 생성
7. 의존성 패키지 설치
8. .env 파일 생성
9. Systemd 서비스 설정
10. 백업 스크립트 생성
11. Logrotate 설정
12. 방화벽 설정

**소요 시간**: 약 15-20분

---

## 📖 사용 가이드

### 일반적인 작업 흐름

```bash
# 1. 시스템 시작
./scripts/start.sh

# 2. 상태 확인
./scripts/status.sh

# 3. 로그 실시간 모니터링
tail -f logs/redarrow_$(date +%Y%m%d).log

# 4. 설정 변경 후 재시작
vim .env
./scripts/restart.sh

# 5. 시스템 중지
./scripts/stop.sh
```

### 트러블슈팅

**문제: "RedArrow가 이미 실행 중입니다" 오류**
```bash
# PID 파일 삭제 후 재시작
rm .redarrow.pid
./scripts/start.sh
```

**문제: 시작은 되지만 바로 종료됨**
```bash
# 로그 확인
tail -n 50 logs/redarrow_$(date +%Y%m%d).log
# .env 파일 확인
cat .env
```

**문제: 프로세스가 종료되지 않음**
```bash
# 강제 종료
cat .redarrow.pid  # PID 확인
kill -9 <PID>
rm .redarrow.pid
```

---

### OCI 배포

자세한 내용은 [OCI 배포 가이드](../docs/05.Deploy/OCIDeployment.md)를 참고하세요.

**빠른 시작**:
1. OCI 인스턴스 생성
2. SSH 접속
3. `oci_setup.sh` 실행
4. .env 파일 편집
5. 서비스 시작

---

## 🔧 수동 설치

스크립트 없이 수동으로 설치하려면:

```bash
# 1. 시스템 업데이트
sudo dnf update -y  # Oracle Linux
# sudo apt update && sudo apt upgrade -y  # Ubuntu

# 2. Python 3.11 설치
sudo dnf install -y python3.11  # Oracle Linux
# sudo apt install -y python3.11  # Ubuntu

# 3. 프로젝트 클론
mkdir -p ~/trading
cd ~/trading
git clone https://github.com/jaengyi/RedArrow.git
cd RedArrow

# 4. 가상환경 및 패키지 설치
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. 환경 설정
cp .env.example .env
vi .env

# 6. Systemd 서비스 생성
sudo vi /etc/systemd/system/redarrow.service
# (서비스 파일 내용은 OCIDeployment.md 참고)

# 7. 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable redarrow
sudo systemctl start redarrow
```

---

## 📝 참고 문서

- [OCI 배포 가이드](../docs/05.Deploy/OCIDeployment.md) - 전체 가이드
- [OCI 빠른 시작](../docs/05.Deploy/OCI-QuickStart.md) - 5단계 빠른 시작
- [실행 가이드](../docs/07.Manual/ExecutionGuide.md) - 로컬 실행 방법

---

## ⚠️ 주의사항

1. **거래 모드 확인**: 스크립트 실행 전 `.env` 파일에서 `TRADING_MODE`를 확인하세요
   - `simulation`: 모의투자 (안전)
   - `real`: 실전투자 (실제 돈 사용)

2. **로그 모니터링**: 실행 후 반드시 로그를 확인하여 정상 동작 여부를 체크하세요

3. **시장 시간**: 한국 주식 시장 운영 시간 (09:00-15:30 KST)에만 거래가 실행됩니다

4. **백업**: 중요한 설정 변경 전 `.env` 파일을 백업하세요

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-01-07 | 1.1 | 관리 스크립트 추가 (start, stop, restart, status) |
| 2025-12-31 | 1.0 | 스크립트 디렉토리 README 작성 |
