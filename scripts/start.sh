#!/bin/bash
# RedArrow 시스템 시작 스크립트

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# PID 파일 및 로그 디렉토리
PID_FILE="$PROJECT_ROOT/.redarrow.pid"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/redarrow_$(date +%Y%m%d).log"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  RedArrow 자동 매매 시스템 시작${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${RED}✗ RedArrow가 이미 실행 중입니다 (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}  중지하려면: ./scripts/stop.sh${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠ 이전 PID 파일 발견 (프로세스 없음) - 정리 중...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# .env 파일 확인
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}✗ .env 파일이 없습니다${NC}"
    echo -e "${YELLOW}  cp .env.example .env 후 설정을 입력하세요${NC}"
    exit 1
fi

# 가상환경 확인 및 활성화
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}⚠ 가상환경이 없습니다. 생성 중...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 가상환경 생성 실패${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}→ 가상환경 활성화${NC}"
source "$PROJECT_ROOT/venv/bin/activate"

# 의존성 확인
if [ ! -f "$PROJECT_ROOT/venv/bin/pip" ]; then
    echo -e "${RED}✗ pip이 설치되어 있지 않습니다${NC}"
    exit 1
fi

# requirements.txt가 변경되었는지 확인 (선택적)
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${GREEN}→ 의존성 패키지 확인${NC}"
    pip install -q -r "$REQUIREMENTS_FILE"
fi

# Python 경로 확인
PYTHON_PATH="$PROJECT_ROOT/venv/bin/python"
if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}✗ Python 실행 파일을 찾을 수 없습니다${NC}"
    exit 1
fi

# 시작 시간 기록
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")

# RedArrow 시작 (백그라운드)
echo -e "${GREEN}→ RedArrow 시작 중...${NC}"
echo -e "${GREEN}  로그 파일: $LOG_FILE${NC}"

nohup "$PYTHON_PATH" "$PROJECT_ROOT/src/main.py" >> "$LOG_FILE" 2>&1 &
PID=$!

# PID 저장
echo "$PID" > "$PID_FILE"

# 프로세스 시작 확인 (2초 대기)
sleep 2

if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RedArrow 시작 완료 (PID: $PID)${NC}"
    echo -e "${GREEN}  시작 시간: $START_TIME${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  유용한 명령어:${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  상태 확인:  ${GREEN}./scripts/status.sh${NC}"
    echo -e "  로그 보기:  ${GREEN}tail -f $LOG_FILE${NC}"
    echo -e "  중지:       ${GREEN}./scripts/stop.sh${NC}"
    echo -e "  재시작:     ${GREEN}./scripts/restart.sh${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}✗ RedArrow 시작 실패${NC}"
    echo -e "${YELLOW}  로그 확인: tail -n 50 $LOG_FILE${NC}"
    rm -f "$PID_FILE"
    exit 1
fi
