# OCI 배포 빠른 시작 가이드

## 🚀 5단계로 OCI에 배포하기

**소요 시간**: 약 30분

---

## Step 1: OCI 인스턴스 생성 (10분)

### 1.1 OCI Console 접속
```
https://cloud.oracle.com/
```

### 1.2 Compute Instance 생성

**필수 설정:**
```
Name: redarrow-trading-system
Shape: VM.Standard.E2.1.Micro (무료)
Image: Oracle Linux 8
Public IP: 할당
SSH Key: 자동 생성 (다운로드!)
```

### 1.3 Public IP 기록
```
Instance Details → Public IP: XXX.XXX.XXX.XXX
```

---

## Step 2: SSH 접속 (2분)

### 2.1 SSH 키 권한 설정 (로컬)
```bash
chmod 600 ~/Downloads/ssh-key-*.key
```

### 2.2 접속
```bash
ssh -i ~/Downloads/ssh-key-*.key opc@YOUR_PUBLIC_IP
```

---

## Step 3: 자동 설치 스크립트 실행 (15분)

### 3.1 스크립트 다운로드
```bash
cd ~
wget https://raw.githubusercontent.com/jaengyi/RedArrow/main/scripts/oci_setup.sh
chmod +x oci_setup.sh
```

### 3.2 스크립트 실행
```bash
bash oci_setup.sh
```

**입력 정보:**
- Git 사용자 이름
- Git 이메일
- GitHub Repository URL

---

## Step 4: 환경 설정 (3분)

### 4.1 .env 파일 편집
```bash
cd ~/trading/RedArrow
vi .env
```

### 4.2 API 키 입력
```env
TRADING_MODE=simulation
SIMULATION_APP_KEY=여기에_입력
SIMULATION_APP_SECRET=여기에_입력
SIMULATION_ACCOUNT_NUMBER=여기에_입력
```

**저장**: `Esc` → `:wq` → `Enter`

### 4.3 설정 검증
```bash
source venv/bin/activate
python -m src.config.settings
```

**성공 시**: `✅ 설정 검증 성공`

---

## Step 5: 서비스 시작 (1분)

### 5.1 서비스 시작
```bash
sudo systemctl start redarrow
```

### 5.2 상태 확인
```bash
sudo systemctl status redarrow
```

### 5.3 로그 확인
```bash
sudo journalctl -u redarrow -f
```

---

## ✅ 완료!

이제 프로그램이 OCI에서 24/7 실행됩니다!

### 📊 일일 모니터링

**로그 확인:**
```bash
# SSH 접속
ssh -i ~/.ssh/key.pem opc@YOUR_PUBLIC_IP

# 로그 확인
sudo journalctl -u redarrow -n 100

# 거래 내역
sudo journalctl -u redarrow | grep "매수\|매도"
```

---

## 🔧 주요 명령어

### 서비스 관리
```bash
sudo systemctl start redarrow    # 시작
sudo systemctl stop redarrow     # 중지
sudo systemctl restart redarrow  # 재시작
sudo systemctl status redarrow   # 상태 확인
```

### 로그 확인
```bash
sudo journalctl -u redarrow -f           # 실시간 로그
sudo journalctl -u redarrow -n 100       # 최근 100줄
sudo journalctl -u redarrow --since today # 오늘 로그
```

### 프로그램 업데이트
```bash
cd ~/trading/RedArrow
git pull
sudo systemctl restart redarrow
```

---

## 🚨 문제 해결

### 서비스가 시작되지 않음

```bash
# 로그 확인
sudo journalctl -u redarrow -n 50

# Python 확인
source ~/trading/RedArrow/venv/bin/activate
python --version

# 설정 검증
python -m src.config.settings
```

### API 연결 실패

```bash
# .env 파일 확인
cat ~/trading/RedArrow/.env | grep "APP_KEY"

# 인터넷 연결 확인
ping -c 3 8.8.8.8
```

---

## 📚 상세 가이드

더 자세한 내용은 다음 문서를 참고하세요:

- **전체 가이드**: [OCIDeployment.md](./OCIDeployment.md)
- **실행 매뉴얼**: [ExecutionGuide.md](../07.Manual/ExecutionGuide.md)
- **문제 해결**: [TroubleShooting.md](../07.Manual/TroubleShooting.md)

---

## 💰 비용

**무료 티어 사용 시**: $0
- VM.Standard.E2.1.Micro
- 월 750시간 (24/7 가능)
- 영구 무료

---

## 📞 지원

- **GitHub Issues**: https://github.com/jaengyi/RedArrow/issues
- **OCI 문서**: https://docs.oracle.com/en-us/iaas/

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2025-12-31 | 1.0 | OCI 빠른 시작 가이드 작성 |
