#!/bin/bash
# RedArrow 시스템 중지 스크립트

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# PID 파일
PID_FILE="$PROJECT_ROOT/.redarrow.pid"

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  RedArrow 자동 매매 시스템 중지${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# PID 파일 확인
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}✗ RedArrow가 실행 중이지 않습니다${NC}"
    echo -e "${YELLOW}  (PID 파일을 찾을 수 없음)${NC}"
    exit 1
fi

# PID 읽기
PID=$(cat "$PID_FILE")

# 프로세스 확인
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${RED}✗ PID $PID 프로세스가 실행 중이지 않습니다${NC}"
    echo -e "${YELLOW}  (오래된 PID 파일 삭제 중...)${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

# 프로세스 정보 표시
PROCESS_INFO=$(ps -p "$PID" -o pid,etime,cmd --no-headers)
echo -e "${GREEN}→ 실행 중인 프로세스:${NC}"
echo -e "  $PROCESS_INFO"
echo ""

# 정상 종료 시도 (SIGTERM)
echo -e "${GREEN}→ RedArrow 중지 중... (SIGTERM)${NC}"
kill -TERM "$PID" 2>/dev/null

# 최대 10초 대기
WAIT_COUNT=0
MAX_WAIT=10

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ RedArrow 정상 종료 완료 (PID: $PID)${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -ne "${YELLOW}  대기 중... ($WAIT_COUNT/$MAX_WAIT 초)\r${NC}"
done

echo ""

# 정상 종료 실패 시 강제 종료 (SIGKILL)
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 정상 종료 실패 - 강제 종료 시도 (SIGKILL)${NC}"
    kill -9 "$PID" 2>/dev/null
    sleep 1

    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ RedArrow 강제 종료 완료 (PID: $PID)${NC}"
        rm -f "$PID_FILE"
        exit 0
    else
        echo -e "${RED}✗ 프로세스 종료 실패${NC}"
        exit 1
    fi
fi
