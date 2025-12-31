# Oracle Cloud Infrastructure (OCI) 배포 가이드

## 📌 개요

RedArrow 자동매매 시스템을 Oracle Cloud Infrastructure의 Compute Instance에 배포하여 24/7 운영하는 방법을 설명합니다.

**대상**: 개발 PC를 계속 켜둘 수 없는 환경
**목표**: OCI에서 안정적으로 자동 실행
**소요 시간**: 약 60분

---

## 목차

1. [OCI 계정 준비](#1-oci-계정-준비)
2. [Compute Instance 생성](#2-compute-instance-생성)
3. [네트워크 및 보안 설정](#3-네트워크-및-보안-설정)
4. [인스턴스 접속 및 초기 설정](#4-인스턴스-접속-및-초기-설정)
5. [애플리케이션 배포](#5-애플리케이션-배포)
6. [Systemd 서비스 설정](#6-systemd-서비스-설정)
7. [자동 시작 설정](#7-자동-시작-설정)
8. [모니터링 및 로그 관리](#8-모니터링-및-로그-관리)
9. [백업 및 복구](#9-백업-및-복구)
10. [비용 최적화](#10-비용-최적화)

---

## 1. OCI 계정 준비

### 1.1 OCI 계정 생성

1. **Oracle Cloud 가입**
   - URL: https://www.oracle.com/cloud/free/
   - 무료 티어 제공 (Always Free)
   - 신용카드 등록 필요 (무료 사용 시 과금 안 됨)

2. **무료 티어 스펙**
   ```
   - VM.Standard.E2.1.Micro (AMD)
   - 1 OCPU (2 vCPU)
   - 1GB RAM
   - 월 750시간 무료 (항상 켜둘 수 있음)
   - 스토리지: 100GB 블록 볼륨
   ```

3. **리전 선택**
   - 권장: **Seoul (ap-seoul-1)** 또는 **Tokyo (ap-tokyo-1)**
   - 한국에서 가장 빠른 응답 속도

### 1.2 필수 정보 준비

- [ ] OCI 계정 생성 완료
- [ ] 리전 선택 완료
- [ ] SSH 키페어 준비 (없으면 생성 예정)

---

## 2. Compute Instance 생성

### 2.1 인스턴스 생성 시작

1. **OCI Console 접속**
   - https://cloud.oracle.com/ 로그인

2. **Compute > Instances 메뉴**
   - 좌측 메뉴: "Compute" → "Instances"
   - "Create Instance" 버튼 클릭

### 2.2 기본 정보 설정

**Name (인스턴스 이름):**
```
redarrow-trading-system
```

**Compartment:**
```
(root) 또는 원하는 compartment 선택
```

**Availability Domain:**
```
Seoul: AD-1 (또는 사용 가능한 AD)
```

### 2.3 Image and Shape 설정

**Image (운영체제):**
```
- Oracle Linux 8 (권장)
또는
- Ubuntu 22.04 LTS

✅ Oracle Linux 8 선택 권장 (OCI 최적화)
```

**Shape (인스턴스 타입):**

**무료 티어 사용:**
```
Shape: VM.Standard.E2.1.Micro
- 1 OCPU
- 1GB RAM
- Always Free 대상
```

**더 높은 성능 필요 시 (유료):**
```
Shape: VM.Standard.E4.Flex
- 1-64 OCPU (선택)
- 1-1024 GB RAM (선택)
권장: 2 OCPU, 8GB RAM (월 약 $30)
```

### 2.4 네트워킹 설정

**Virtual Cloud Network (VCN):**
```
- "Create new virtual cloud network" 선택
또는
- 기존 VCN이 있으면 선택
```

**Subnet:**
```
- "Create new public subnet" 선택
- Public IP 할당: ✅ 체크
```

### 2.5 SSH 키 설정

**SSH Key Pair:**

**방법 1: 자동 생성 (권장)**
```
1. "Generate a key pair for me" 선택
2. "Save Private Key" 클릭 → 다운로드
3. "Save Public Key" 클릭 → 다운로드

저장 위치 예시:
~/Downloads/ssh-key-YYYY-MM-DD.key (Private)
~/Downloads/ssh-key-YYYY-MM-DD.key.pub (Public)
```

**방법 2: 기존 키 사용**
```bash
# 로컬에서 키 생성
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oci_redarrow

# Public Key 내용을 OCI에 붙여넣기
cat ~/.ssh/oci_redarrow.pub
```

### 2.6 Boot Volume 설정

```
Boot Volume Size: 50 GB (기본값으로 충분)
Encryption: Oracle-managed keys (기본값)
```

### 2.7 인스턴스 생성

```
"Create" 버튼 클릭
```

**대기 시간**: 약 2-3분
**상태 확인**: "Running" 상태가 되면 완료

### 2.8 Public IP 확인

```
Instance Details 페이지에서:
- Public IP Address: XXX.XXX.XXX.XXX 복사
```

⚠️ **중요**: 이 IP 주소를 잘 기록해두세요!

---

## 3. 네트워크 및 보안 설정

### 3.1 Security List 설정

**경로:**
```
Networking → Virtual Cloud Networks → 생성한 VCN → Security Lists
```

**Ingress Rules (인바운드) 추가:**

1. **SSH 접속 허용 (필수)**
   ```
   Source CIDR: 0.0.0.0/0 (모든 IP) 또는 내 IP만
   IP Protocol: TCP
   Destination Port: 22
   Description: SSH access
   ```

2. **HTTPS 허용 (선택 - 모니터링용)**
   ```
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port: 443
   Description: HTTPS for monitoring
   ```

**Egress Rules (아웃바운드):**
```
기본 설정 유지 (모든 트래픽 허용)
```

### 3.2 OS 방화벽 설정 (나중에 SSH 접속 후)

**Oracle Linux 8:**
```bash
# SSH 포트 허용 확인
sudo firewall-cmd --list-all

# 필요시 포트 추가
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

**Ubuntu:**
```bash
# UFW 방화벽 설정
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 4. 인스턴스 접속 및 초기 설정

### 4.1 SSH 키 권한 설정 (로컬)

```bash
# Private Key 권한 변경 (필수!)
chmod 600 ~/Downloads/ssh-key-YYYY-MM-DD.key

# 또는 ~/.ssh로 이동
mv ~/Downloads/ssh-key-YYYY-MM-DD.key ~/.ssh/oci_redarrow.key
chmod 600 ~/.ssh/oci_redarrow.key
```

### 4.2 SSH 접속

**Oracle Linux:**
```bash
ssh -i ~/.ssh/oci_redarrow.key opc@YOUR_PUBLIC_IP
```

**Ubuntu:**
```bash
ssh -i ~/.ssh/oci_redarrow.key ubuntu@YOUR_PUBLIC_IP
```

**첫 접속 시 메시지:**
```
The authenticity of host 'XXX.XXX.XXX.XXX' can't be established.
Are you sure you want to continue connecting (yes/no)? yes
```

**접속 성공:**
```
[opc@redarrow-trading-system ~]$
```

### 4.3 시스템 업데이트

**Oracle Linux 8:**
```bash
# 시스템 업데이트
sudo dnf update -y

# 개발 도구 설치
sudo dnf groupinstall -y "Development Tools"

# 필수 패키지 설치
sudo dnf install -y git wget curl vim
```

**Ubuntu 22.04:**
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y git wget curl vim build-essential
```

### 4.4 Python 3.11 설치

**Oracle Linux 8:**
```bash
# Python 3.11 설치
sudo dnf install -y python3.11 python3.11-devel python3.11-pip

# 기본 python3 링크 설정
sudo alternatives --set python3 /usr/bin/python3.11

# 확인
python3 --version
# 출력: Python 3.11.x
```

**Ubuntu 22.04:**
```bash
# Python 3.11 설치
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 확인
python3.11 --version
```

### 4.5 Git 설정

```bash
# Git 사용자 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 5. 애플리케이션 배포

### 5.1 프로젝트 디렉토리 생성

```bash
# 홈 디렉토리에 프로젝트용 폴더 생성
mkdir -p ~/trading
cd ~/trading
```

### 5.2 소스 코드 배포

**방법 1: Git Clone (권장)**

```bash
# Private Repository인 경우
git clone https://github.com/jaengyi/RedArrow.git
cd RedArrow

# Public Repository인 경우 (토큰 없이)
git clone https://github.com/jaengyi/RedArrow.git
cd RedArrow
```

**방법 2: 파일 직접 업로드**

**로컬 PC에서:**
```bash
# 프로젝트 전체를 tar로 압축
cd ~/projects
tar -czf RedArrow.tar.gz RedArrow/

# OCI로 전송
scp -i ~/.ssh/oci_redarrow.key RedArrow.tar.gz opc@YOUR_PUBLIC_IP:~/trading/
```

**OCI 인스턴스에서:**
```bash
cd ~/trading
tar -xzf RedArrow.tar.gz
cd RedArrow
```

### 5.3 Python 가상환경 설정

```bash
cd ~/trading/RedArrow

# 가상환경 생성
python3.11 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

### 5.4 의존성 패키지 설치

```bash
# 필수 패키지 설치 (TA-Lib 제외)
pip install numpy pandas python-dateutil requests \
            websocket-client aiohttp PyYAML python-dotenv \
            loguru APScheduler pytz

# 설치 확인
pip list
```

### 5.5 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
vi .env
```

**vi 에디터 사용법:**
```
i → 입력 모드
Esc → 명령 모드
:wq → 저장하고 종료
:q! → 저장 안 하고 종료
```

**.env 파일 내용 (필수 수정):**
```env
# 거래 모드
TRADING_MODE=simulation

# 모의투자 API 키
SIMULATION_APP_KEY=실제_API_KEY_입력
SIMULATION_APP_SECRET=실제_API_SECRET_입력
SIMULATION_ACCOUNT_NUMBER=실제_계좌번호_입력

# 실전투자 API 키 (나중에)
REAL_APP_KEY=
REAL_APP_SECRET=
REAL_ACCOUNT_NUMBER=

# 데이터베이스 (현재 미사용)
DB_USER=
DB_PASSWORD=

# 로그 레벨
LOG_LEVEL=INFO
```

### 5.6 설정 검증

```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 설정 검증
python -m src.config.settings
```

**성공 시 출력:**
```
✅ 설정 검증 성공
```

### 5.7 수동 테스트 실행

```bash
# 프로그램 실행 테스트
python src/main.py
```

**예상 출력:**
```
RedArrow 시스템 시작
시장이 개장하지 않았습니다. 대기 중...
RedArrow 시스템 종료
```

✅ 정상 작동 확인!

---

## 6. Systemd 서비스 설정

### 6.1 서비스 파일 생성

```bash
# systemd 서비스 파일 생성
sudo vi /etc/systemd/system/redarrow.service
```

**서비스 파일 내용:**

```ini
[Unit]
Description=RedArrow Trading System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=opc
Group=opc
WorkingDirectory=/home/opc/trading/RedArrow
Environment="PATH=/home/opc/trading/RedArrow/venv/bin:/usr/local/bin:/usr/bin:/bin"

# 실행 명령
ExecStart=/home/opc/trading/RedArrow/venv/bin/python src/main.py

# 재시작 정책
Restart=always
RestartSec=10

# 로그 설정
StandardOutput=journal
StandardError=journal
SyslogIdentifier=redarrow

# 리소스 제한
MemoryLimit=800M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
```

**Ubuntu 사용 시 User/Group 변경:**
```ini
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/trading/RedArrow
```

### 6.2 서비스 등록 및 시작

```bash
# systemd 설정 리로드
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable redarrow

# 서비스 시작
sudo systemctl start redarrow

# 상태 확인
sudo systemctl status redarrow
```

**성공 시 출력:**
```
● redarrow.service - RedArrow Trading System
   Loaded: loaded (/etc/systemd/system/redarrow.service; enabled)
   Active: active (running) since ...
   Main PID: 12345
```

### 6.3 서비스 관리 명령어

```bash
# 서비스 시작
sudo systemctl start redarrow

# 서비스 중지
sudo systemctl stop redarrow

# 서비스 재시작
sudo systemctl restart redarrow

# 상태 확인
sudo systemctl status redarrow

# 로그 확인 (실시간)
sudo journalctl -u redarrow -f

# 최근 100줄 로그
sudo journalctl -u redarrow -n 100

# 오늘 로그만
sudo journalctl -u redarrow --since today
```

---

## 7. 자동 시작 설정

### 7.1 타이머 서비스 생성 (선택)

매일 장 시작 전에만 실행하려면:

```bash
# 타이머 파일 생성
sudo vi /etc/systemd/system/redarrow.timer
```

**타이머 파일 내용:**
```ini
[Unit]
Description=RedArrow Trading System Timer
Requires=redarrow.service

[Timer]
# 평일 오전 8시 55분에 실행
OnCalendar=Mon-Fri 08:55:00
Persistent=true

[Install]
WantedBy=timers.target
```

**타이머 활성화:**
```bash
# 타이머 활성화
sudo systemctl enable redarrow.timer
sudo systemctl start redarrow.timer

# 타이머 상태 확인
sudo systemctl list-timers --all | grep redarrow
```

### 7.2 24/7 실행 (권장)

서비스가 항상 실행되도록 설정 (이미 완료):
```bash
sudo systemctl enable redarrow
sudo systemctl start redarrow
```

프로그램 내부에서 시장 시간을 체크하므로 계속 실행해도 안전합니다.

---

## 8. 모니터링 및 로그 관리

### 8.1 실시간 로그 모니터링

**Systemd 로그:**
```bash
# 실시간 로그 확인
sudo journalctl -u redarrow -f

# 최근 50줄
sudo journalctl -u redarrow -n 50

# 오늘 로그
sudo journalctl -u redarrow --since today
```

**애플리케이션 로그:**
```bash
# 프로그램 로그 파일
cd ~/trading/RedArrow/logs

# 실시간 확인
tail -f redarrow_$(date +%Y%m%d).log

# 매수/매도만 확인
tail -f redarrow_$(date +%Y%m%d).log | grep "매수\|매도"
```

### 8.2 시스템 리소스 모니터링

**CPU 및 메모리 사용량:**
```bash
# 실시간 모니터링
top

# 프로세스별 리소스
htop  # 설치: sudo dnf install -y htop

# 메모리 확인
free -h

# 디스크 사용량
df -h
```

**RedArrow 프로세스만 확인:**
```bash
# 프로세스 찾기
ps aux | grep "python src/main.py"

# 리소스 사용량
top -p $(pgrep -f "python src/main.py")
```

### 8.3 로그 로테이션 설정

```bash
# logrotate 설정 파일 생성
sudo vi /etc/logrotate.d/redarrow
```

**내용:**
```
/home/opc/trading/RedArrow/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 opc opc
}
```

**수동 실행 테스트:**
```bash
sudo logrotate -f /etc/logrotate.d/redarrow
```

### 8.4 알림 설정 (선택)

**이메일 알림:**

`.env`에 추가:
```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECEIVER=your-email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

## 9. 백업 및 복구

### 9.1 자동 백업 스크립트

```bash
# 백업 스크립트 생성
vi ~/backup_redarrow.sh
```

**스크립트 내용:**
```bash
#!/bin/bash

BACKUP_DIR="/home/opc/backups"
PROJECT_DIR="/home/opc/trading/RedArrow"
DATE=$(date +%Y%m%d_%H%M%S)

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# .env 파일 백업
cp $PROJECT_DIR/.env $BACKUP_DIR/.env_$DATE

# 로그 백업
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz $PROJECT_DIR/logs/

# 7일 이전 백업 삭제
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name ".env_*" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**실행 권한 부여:**
```bash
chmod +x ~/backup_redarrow.sh
```

### 9.2 Cron 자동 백업 설정

```bash
# crontab 편집
crontab -e
```

**매일 자정에 백업:**
```cron
0 0 * * * /home/opc/backup_redarrow.sh >> /home/opc/backup.log 2>&1
```

### 9.3 복구 방법

**설정 파일 복구:**
```bash
# 백업에서 .env 복구
cp ~/backups/.env_20251231_120000 ~/trading/RedArrow/.env
```

**로그 복구:**
```bash
# 백업 압축 해제
cd ~/backups
tar -xzf logs_20251231_120000.tar.gz
```

---

## 10. 비용 최적화

### 10.1 무료 티어 최대 활용

**Always Free 인스턴스:**
- VM.Standard.E2.1.Micro: 1GB RAM
- 월 750시간 (24/7 가능)
- 영구 무료

**확인 방법:**
```
OCI Console → Governance → Limits, Quotas and Usage
→ "Always Free-Eligible Resources" 확인
```

### 10.2 비용 절감 팁

1. **불필요한 리소스 제거**
   ```bash
   # 사용하지 않는 Block Volume 삭제
   # 사용하지 않는 VCN 삭제
   ```

2. **로그 파일 정리**
   ```bash
   # 오래된 로그 삭제 (30일 이상)
   find ~/trading/RedArrow/logs -name "*.log" -mtime +30 -delete
   ```

3. **모니터링 알림 설정**
   ```
   OCI Console → Monitoring → Alarms
   → 비용 임계값 알림 설정
   ```

### 10.3 비용 모니터링

```bash
# OCI CLI 설치 (선택)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# 비용 확인
oci usage-api usage-summary summarize-usage-carbon-emissions \
  --tenant-id <your-tenant-id> \
  --time-usage-started 2025-01-01T00:00:00.000Z \
  --time-usage-ended 2025-01-31T23:59:59.999Z \
  --granularity DAILY
```

---

## 11. 문제 해결

### 11.1 서비스가 시작되지 않음

**증상:**
```bash
$ sudo systemctl status redarrow
Failed to start redarrow.service
```

**해결:**
```bash
# 로그 확인
sudo journalctl -u redarrow -n 100

# 권한 확인
ls -la /home/opc/trading/RedArrow/src/main.py

# Python 경로 확인
which python
/home/opc/trading/RedArrow/venv/bin/python --version
```

### 11.2 API 연결 실패

**증상:**
```
[ERROR] API 연결 실패
```

**해결:**
```bash
# 인터넷 연결 확인
ping -c 3 8.8.8.8

# DNS 확인
nslookup google.com

# 방화벽 확인
sudo firewall-cmd --list-all

# API 키 확인
grep "APP_KEY" ~/trading/RedArrow/.env
```

### 11.3 메모리 부족

**증상:**
```
OOM killer terminated process
```

**해결:**
```bash
# Swap 메모리 추가
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 적용
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 11.4 디스크 공간 부족

**증상:**
```bash
$ df -h
/dev/sda1  50G  48G  2G  96% /
```

**해결:**
```bash
# 로그 정리
find ~/trading/RedArrow/logs -name "*.log" -mtime +7 -delete

# 패키지 캐시 정리
sudo dnf clean all  # Oracle Linux
sudo apt clean      # Ubuntu

# 불필요한 패키지 제거
pip cache purge
```

---

## 12. 보안 강화

### 12.1 SSH 보안 설정

```bash
# SSH 설정 편집
sudo vi /etc/ssh/sshd_config
```

**권장 설정:**
```
# 비밀번호 로그인 비활성화
PasswordAuthentication no

# Root 로그인 비활성화
PermitRootLogin no

# SSH 포트 변경 (선택)
Port 2222
```

**SSH 재시작:**
```bash
sudo systemctl restart sshd
```

### 12.2 자동 보안 업데이트

**Oracle Linux:**
```bash
# dnf-automatic 설치
sudo dnf install -y dnf-automatic

# 자동 업데이트 활성화
sudo systemctl enable --now dnf-automatic.timer
```

**Ubuntu:**
```bash
# unattended-upgrades 설치
sudo apt install -y unattended-upgrades

# 활성화
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 12.3 fail2ban 설치

```bash
# fail2ban 설치 (무차별 대입 공격 방어)
sudo dnf install -y fail2ban  # Oracle Linux
sudo apt install -y fail2ban  # Ubuntu

# 활성화
sudo systemctl enable --now fail2ban
```

---

## 13. 운영 체크리스트

### 13.1 일일 체크 (자동화 권장)

- [ ] 서비스 상태 확인: `sudo systemctl status redarrow`
- [ ] 로그 확인: `tail -100 ~/trading/RedArrow/logs/redarrow_*.log`
- [ ] 거래 내역 확인
- [ ] 디스크 사용량: `df -h`
- [ ] 메모리 사용량: `free -h`

### 13.2 주간 체크

- [ ] 전체 로그 리뷰
- [ ] 백업 상태 확인
- [ ] 성과 분석
- [ ] 시스템 업데이트: `sudo dnf update -y`

### 13.3 월간 체크

- [ ] 비용 확인 (OCI Console)
- [ ] API 키 만료 확인
- [ ] 로그 아카이빙
- [ ] 보안 패치 적용

---

## 14. 참고 자료

### 14.1 OCI 문서

- OCI Free Tier: https://www.oracle.com/cloud/free/
- Compute 문서: https://docs.oracle.com/en-us/iaas/Content/Compute/home.htm
- 네트워킹 가이드: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

### 14.2 관련 프로젝트 문서

- [ExecutionGuide](../07.Manual/ExecutionGuide.md) - 로컬 실행 가이드
- [TroubleShooting](../07.Manual/TroubleShooting.md) - 문제 해결
- [APIKeyManagement](../06.Security/APIKeyManagement.md) - API 키 관리

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | OCI 배포 가이드 초안 작성 | - |
