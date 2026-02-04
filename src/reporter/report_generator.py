import re
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# 프로젝트 루트 기준 절대 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "docs" / "08.Report"

LOG_FILE_FORMAT = "redarrow_{}.log"
SUMMARY_FILE_FORMAT = "summary_{}.json"
REPORT_FILE_FORMAT = "{}_투자결과.md"

# 로그 파싱 패턴 (실제 거래 이벤트만 매칭)
# 매수: "✅ 매수 주문 접수 성공: {종목명} {수량}주 @ {가격}원 (주문번호: {번호})"
BUY_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - .+ - INFO - "
    r"✅ 매수 주문 접수 성공: (.+?) (\d+)주 @ ([\d,]+)원"
)

# 매도: "✅ 매도 주문 체결 성공: {종목명} {수량}주 @ {가격}원 (주문번호: {번호})"
SELL_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - .+ - INFO - "
    r"✅ 매도 주문 체결 성공: (.+?) (\d+)주 @ ([\d,]+)원"
)

# 청산: "✅ 청산 주문 체결 성공: {종목명} {수량}주, 진입가 {가격}원, 청산가 {가격}원"
LIQUIDATION_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - .+ - INFO - "
    r"✅ 청산 주문 체결 성공: (.+?) (\d+)주, 진입가 ([\d,]+)원, 청산가 ([\d,]+)원"
)

# 손익: "💰 청산 손익: {금액}원 ({비율}%)"
PNL_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - .+ - INFO - "
    r"💰 청산 손익: ([\d,.-]+)원 \(([\d.+-]+)%\)"
)


def setup_reporter():
    """리포트 디렉토리가 없으면 생성합니다."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def parse_summary_file(date_str: str):
    """
    해당 날짜의 요약 JSON 파일을 파싱합니다.

    Args:
        date_str: YYYYMMDD 형식의 날짜 문자열

    Returns:
        요약 데이터 딕셔너리 또는 None
    """
    summary_file_path = LOG_DIR / SUMMARY_FILE_FORMAT.format(date_str)
    if not summary_file_path.exists():
        logger.warning(f"요약 파일을 찾을 수 없습니다: {summary_file_path}")
        return None

    try:
        with open(summary_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"요약 파일 파싱 중 오류 발생: {e}")
        return None


def parse_log_file(date_str: str):
    """
    해당 날짜의 로그 파일에서 실제 거래 이벤트만 추출합니다.

    Args:
        date_str: YYYYMMDD 형식의 날짜 문자열

    Returns:
        (buy_events, sell_events, pnl_events) 튜플
        - buy_events: [{'time': str, 'name': str, 'quantity': int, 'price': str}, ...]
        - sell_events: [{'time': str, 'name': str, 'quantity': int, 'price': str, 'type': str}, ...]
        - pnl_events: [{'time': str, 'amount': str, 'percent': str}, ...]
    """
    log_file_path = LOG_DIR / LOG_FILE_FORMAT.format(date_str)
    buy_events = []
    sell_events = []
    pnl_events = []

    if not log_file_path.exists():
        logger.warning(f"로그 파일을 찾을 수 없습니다: {log_file_path}")
        return buy_events, sell_events, pnl_events

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 매수 주문 접수 성공
            m = BUY_PATTERN.search(line)
            if m:
                buy_events.append({
                    'time': m.group(1).split(' ')[1],
                    'name': m.group(2),
                    'quantity': int(m.group(3)),
                    'price': m.group(4),
                })
                continue

            # 매도 주문 체결 성공
            m = SELL_PATTERN.search(line)
            if m:
                sell_events.append({
                    'time': m.group(1).split(' ')[1],
                    'name': m.group(2),
                    'quantity': int(m.group(3)),
                    'price': m.group(4),
                    'type': '매도',
                })
                continue

            # 청산 주문 체결 성공
            m = LIQUIDATION_PATTERN.search(line)
            if m:
                sell_events.append({
                    'time': m.group(1).split(' ')[1],
                    'name': m.group(2),
                    'quantity': int(m.group(3)),
                    'price': m.group(5),  # 청산가
                    'type': '청산',
                    'entry_price': m.group(4),
                })
                continue

            # 청산 손익
            m = PNL_PATTERN.search(line)
            if m:
                pnl_events.append({
                    'time': m.group(1).split(' ')[1],
                    'amount': m.group(2),
                    'percent': m.group(3),
                })

    return buy_events, sell_events, pnl_events


def generate_report_content(date_str: str, buy_events: list, sell_events: list,
                            pnl_events: list, summary_data: dict) -> str:
    """
    마크다운 형식의 일일 리포트 내용을 생성합니다.

    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        buy_events: 매수 이벤트 리스트
        sell_events: 매도/청산 이벤트 리스트
        pnl_events: 손익 이벤트 리스트
        summary_data: 요약 JSON 데이터

    Returns:
        마크다운 리포트 문자열
    """
    lines = []
    lines.append(f"# {date_str} 투자 결과 리포트\n")
    lines.append("---\n")

    # 매수 기록
    lines.append("## 매수 기록\n")
    if buy_events:
        lines.append("| 시간 | 종목 | 수량 | 주문가 |")
        lines.append("|------|------|-----:|-------:|")
        for e in buy_events:
            lines.append(f"| {e['time']} | {e['name']} | {e['quantity']}주 | {e['price']}원 |")
        lines.append("")
    else:
        lines.append("해당일에 매수 기록이 없습니다.\n")

    # 매도/청산 기록
    lines.append("## 매도/청산 기록\n")
    if sell_events:
        lines.append("| 시간 | 종목 | 유형 | 수량 | 체결가 |")
        lines.append("|------|------|------|-----:|-------:|")
        for e in sell_events:
            lines.append(f"| {e['time']} | {e['name']} | {e['type']} | {e['quantity']}주 | {e['price']}원 |")
        lines.append("")
    else:
        lines.append("해당일에 매도/청산 기록이 없습니다.\n")

    # 손익 기록
    lines.append("## 손익 기록\n")
    if pnl_events:
        lines.append("| 시간 | 손익 | 수익률 |")
        lines.append("|------|-----:|-------:|")
        for e in pnl_events:
            lines.append(f"| {e['time']} | {e['amount']}원 | {e['percent']}% |")
        lines.append("")
    else:
        lines.append("해당일에 손익 기록이 없습니다.\n")

    # 총평 및 결과
    lines.append("## 총평 및 결과\n")
    lines.append(f"- **매수 건수**: {len(buy_events)}건")
    lines.append(f"- **매도/청산 건수**: {len(sell_events)}건")

    if summary_data:
        pnl = summary_data.get('daily_pnl', 0)
        final_balance = summary_data.get('final_balance', 0)
        lines.append(f"- **당일 실현 손익**: {pnl:,.0f}원")
        lines.append(f"- **최종 계좌 잔고**: {final_balance:,.0f}원")
    else:
        lines.append("- **당일 실현 손익**: 요약 데이터 없음")
        lines.append("- **최종 계좌 잔고**: 요약 데이터 없음")

    lines.append("")
    return "\n".join(lines)


def generate_daily_report():
    """
    일일 투자 결과 리포트를 생성합니다.
    오늘 날짜의 로그 파일과 요약 파일을 읽어 마크다운 리포트를 작성합니다.
    """
    logger.info("일일 투자 결과 리포트 생성을 시작합니다.")
    setup_reporter()

    now = datetime.now()
    date_str_for_report = now.strftime("%Y-%m-%d")
    date_str_for_log = now.strftime("%Y%m%d")

    report_file_path = REPORT_DIR / REPORT_FILE_FORMAT.format(date_str_for_report)

    try:
        buy_events, sell_events, pnl_events = parse_log_file(date_str_for_log)
        summary_data = parse_summary_file(date_str_for_log)

        report_content = generate_report_content(
            date_str_for_report, buy_events, sell_events, pnl_events, summary_data
        )

        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"일일 투자 결과 리포트가 성공적으로 생성되었습니다: {report_file_path}")

    except Exception as e:
        logger.error(f"리포트 생성 중 오류 발생: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    generate_daily_report()
