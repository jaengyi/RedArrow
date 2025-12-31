#!/bin/bash

###############################################################################
# RedArrow OCI 자동 설정 스크립트
#
# 사용법: bash oci_setup.sh
# 실행 위치: OCI 인스턴스에서 실행
###############################################################################

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 배너 출력
echo "============================================================"
echo "  RedArrow OCI 자동 설정 스크립트"
echo "============================================================"
echo ""

# OS 확인
if [ -f /etc/oracle-release ]; then
    OS="oracle"
    log_info "Oracle Linux 감지"
elif [ -f /etc/lsb-release ]; then
    OS="ubuntu"
    log_info "Ubuntu 감지"
else
    log_error "지원하지 않는 OS입니다."
    exit 1
fi

# 1. 시스템 업데이트
log_info "시스템 업데이트 중..."
if [ "$OS" = "oracle" ]; then
    sudo dnf update -y
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y git wget curl vim
else
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y git wget curl vim build-essential
fi

# 2. Python 3.11 설치
log_info "Python 3.11 설치 중..."
if [ "$OS" = "oracle" ]; then
    sudo dnf install -y python3.11 python3.11-devel python3.11-pip
    sudo alternatives --set python3 /usr/bin/python3.11 2>/dev/null || true
else
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi

# Python 버전 확인
PYTHON_VERSION=$(python3 --version)
log_info "설치된 Python: $PYTHON_VERSION"

# 3. 프로젝트 디렉토리 생성
log_info "프로젝트 디렉토리 생성 중..."
mkdir -p ~/trading
cd ~/trading

# 4. Git 설정
log_info "Git 설정..."
read -p "Git 사용자 이름: " GIT_USER
read -p "Git 이메일: " GIT_EMAIL
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"

# 5. 저장소 클론 여부 확인
echo ""
read -p "GitHub에서 프로젝트를 클론하시겠습니까? (y/n): " CLONE_REPO

if [ "$CLONE_REPO" = "y" ] || [ "$CLONE_REPO" = "Y" ]; then
    read -p "GitHub Repository URL: " REPO_URL
    log_info "저장소 클론 중..."
    git clone "$REPO_URL" RedArrow
else
    log_warn "수동으로 프로젝트 파일을 업로드해야 합니다."
    log_warn "scp -i ~/.ssh/key.pem RedArrow.tar.gz opc@YOUR_IP:~/trading/"
    exit 0
fi

cd RedArrow

# 6. Python 가상환경 설정
log_info "Python 가상환경 생성 중..."
python3 -m venv venv
source venv/bin/activate

# 7. 의존성 패키지 설치
log_info "의존성 패키지 설치 중..."
pip install --upgrade pip
pip install numpy pandas python-dateutil requests \
            websocket-client aiohttp PyYAML python-dotenv \
            loguru APScheduler pytz

# 8. .env 파일 설정
log_info ".env 파일 생성 중..."
if [ ! -f .env ]; then
    cp .env.example .env
    log_warn ".env 파일을 편집해야 합니다: vi ~/trading/RedArrow/.env"
else
    log_info ".env 파일이 이미 존재합니다."
fi

# 9. 로그 디렉토리 생성
log_info "로그 디렉토리 생성 중..."
mkdir -p logs

# 10. Systemd 서비스 생성
log_info "Systemd 서비스 생성 중..."

# 현재 사용자 확인
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

sudo tee /etc/systemd/system/redarrow.service > /dev/null <<EOF
[Unit]
Description=RedArrow Trading System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"

ExecStart=$PROJECT_DIR/venv/bin/python src/main.py

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=redarrow

MemoryLimit=800M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

# 11. Systemd 서비스 등록
log_info "Systemd 서비스 등록 중..."
sudo systemctl daemon-reload
sudo systemctl enable redarrow

# 12. 백업 스크립트 생성
log_info "백업 스크립트 생성 중..."
cat > ~/backup_redarrow.sh <<'EOF'
#!/bin/bash

BACKUP_DIR="$HOME/backups"
PROJECT_DIR="$HOME/trading/RedArrow"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

cp $PROJECT_DIR/.env $BACKUP_DIR/.env_$DATE
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz $PROJECT_DIR/logs/

find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name ".env_*" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x ~/backup_redarrow.sh

# 13. Logrotate 설정
log_info "Logrotate 설정 중..."
sudo tee /etc/logrotate.d/redarrow > /dev/null <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $CURRENT_USER $CURRENT_USER
}
EOF

# 14. 방화벽 설정 (Oracle Linux만)
if [ "$OS" = "oracle" ]; then
    log_info "방화벽 설정 중..."
    sudo firewall-cmd --permanent --add-service=ssh 2>/dev/null || true
    sudo firewall-cmd --reload 2>/dev/null || true
fi

# 15. 완료
echo ""
echo "============================================================"
echo -e "${GREEN}설치 완료!${NC}"
echo "============================================================"
echo ""
echo "다음 단계:"
echo "1. .env 파일 편집:"
echo "   vi ~/trading/RedArrow/.env"
echo ""
echo "2. API 키 입력 후 설정 검증:"
echo "   cd ~/trading/RedArrow"
echo "   source venv/bin/activate"
echo "   python -m src.config.settings"
echo ""
echo "3. 서비스 시작:"
echo "   sudo systemctl start redarrow"
echo ""
echo "4. 상태 확인:"
echo "   sudo systemctl status redarrow"
echo ""
echo "5. 로그 확인:"
echo "   sudo journalctl -u redarrow -f"
echo ""
echo "============================================================"
