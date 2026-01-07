#!/bin/bash
# RedArrow 시스템 재시작 스크립트

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  RedArrow 자동 매매 시스템 재시작${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 중지
echo -e "${GREEN}[1/2] 기존 프로세스 중지${NC}"
"$PROJECT_ROOT/scripts/stop.sh"

STOP_RESULT=$?

if [ $STOP_RESULT -ne 0 ] && [ $STOP_RESULT -ne 1 ]; then
    echo -e "${RED}✗ 중지 중 오류 발생${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 2초 대기
sleep 2

# 시작
echo -e "${GREEN}[2/2] RedArrow 시작${NC}"
"$PROJECT_ROOT/scripts/start.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 재시작 완료${NC}"
else
    echo -e "${RED}✗ 재시작 실패${NC}"
    exit 1
fi
