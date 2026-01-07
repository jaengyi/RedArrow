#!/bin/bash
# RedArrow 시스템 상태 확인 스크립트

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# PID 파일 및 로그
PID_FILE="$PROJECT_ROOT/.redarrow.pid"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/redarrow_$(date +%Y%m%d).log"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  RedArrow 시스템 상태${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# PID 파일 확인
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}✗ 상태: 중지됨${NC}"
    echo -e "${YELLOW}  시작하려면: ./scripts/start.sh${NC}"
    exit 1
fi

# PID 읽기
PID=$(cat "$PID_FILE")

# 프로세스 확인
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${RED}✗ 상태: 중지됨 (PID 파일만 존재)${NC}"
    echo -e "${YELLOW}  오래된 PID 파일: $PID_FILE${NC}"
    echo -e "${YELLOW}  정리하려면: rm $PID_FILE${NC}"
    exit 1
fi

# 프로세스 정보
PROCESS_INFO=$(ps -p "$PID" -o pid,etime,%cpu,%mem,cmd --no-headers)
ELAPSED_TIME=$(ps -p "$PID" -o etime --no-headers | xargs)
CPU_USAGE=$(ps -p "$PID" -o %cpu --no-headers | xargs)
MEM_USAGE=$(ps -p "$PID" -o %mem --no-headers | xargs)
CMD=$(ps -p "$PID" -o cmd --no-headers)

echo -e "${GREEN}✓ 상태: 실행 중${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  프로세스 정보${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  PID:           ${GREEN}$PID${NC}"
echo -e "  실행 시간:     ${GREEN}$ELAPSED_TIME${NC}"
echo -e "  CPU 사용률:    ${GREEN}$CPU_USAGE%${NC}"
echo -e "  메모리 사용률: ${GREEN}$MEM_USAGE%${NC}"
echo -e "  명령어:        ${GREEN}$CMD${NC}"

# 로그 파일 확인
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  로그 정보${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    LOG_LINES=$(wc -l < "$LOG_FILE")
    echo -e "  로그 파일:   ${GREEN}$LOG_FILE${NC}"
    echo -e "  파일 크기:   ${GREEN}$LOG_SIZE${NC}"
    echo -e "  라인 수:     ${GREEN}$LOG_LINES${NC}"

    # 최근 로그 (마지막 5줄)
    echo ""
    echo -e "${BLUE}  최근 로그 (마지막 5줄):${NC}"
    echo -e "${YELLOW}  ─────────────────────────────────────────${NC}"
    tail -n 5 "$LOG_FILE" | sed 's/^/  /'
    echo -e "${YELLOW}  ─────────────────────────────────────────${NC}"
else
    echo -e "${YELLOW}  로그 파일 없음: $LOG_FILE${NC}"
fi

# 환경 설정 정보
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  환경 설정${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$PROJECT_ROOT/.env" ]; then
    TRADING_MODE=$(grep "^TRADING_MODE=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d '"' | tr -d "'" | xargs)

    if [ -n "$TRADING_MODE" ]; then
        if [ "$TRADING_MODE" = "simulation" ]; then
            echo -e "  거래 모드:   ${GREEN}$TRADING_MODE (모의투자)${NC}"
        else
            echo -e "  거래 모드:   ${RED}$TRADING_MODE (실전투자)${NC} ${YELLOW}⚠ 실제 거래${NC}"
        fi
    else
        echo -e "  거래 모드:   ${YELLOW}설정되지 않음${NC}"
    fi
else
    echo -e "${RED}  .env 파일 없음${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  관리 명령어${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  로그 실시간:  ${GREEN}tail -f $LOG_FILE${NC}"
echo -e "  중지:         ${GREEN}./scripts/stop.sh${NC}"
echo -e "  재시작:       ${GREEN}./scripts/restart.sh${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
