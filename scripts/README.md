# RedArrow 배포 스크립트

## 📁 스크립트 목록

### oci_setup.sh

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

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2025-12-31 | 1.0 | 스크립트 디렉토리 README 작성 |
