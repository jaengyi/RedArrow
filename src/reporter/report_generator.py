import os
import re
from datetime import datetime
from loguru import logger

# Constants
LOG_DIR = "logs"
REPORT_DIR = "docs/08.Report"
LOG_FILE_FORMAT = "redarrow_{}.log"
REPORT_FILE_FORMAT = "{}_투자결과.md"


def setup_reporter():
    """Ensure the report directory exists."""
    os.makedirs(REPORT_DIR, exist_ok=True)


def parse_log_file(date_str: str):
    """
    Parses the log file for a specific date to extract trading activities.

    Args:
        date_str (str): The date in YYYYMMDD format.

    Returns:
        A tuple containing two lists: (buy_events, sell_events)
    """
    log_file_path = os.path.join(LOG_DIR, LOG_FILE_FORMAT.format(date_str))
    buy_events = []
    sell_events = []

    if not os.path.exists(log_file_path):
        logger.warning(f"로그 파일을 찾을 수 없습니다: {log_file_path}")
        return buy_events, sell_events

    # Example log patterns (to be adjusted based on actual log format)
    # INFO | ... | 매수 신호: ... 이유: ...
    # INFO | ... | 매도 신호: ... 이유: ...
    buy_pattern = re.compile(r".*매수.*")
    sell_pattern = re.compile(r".*매도.*")

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if buy_pattern.search(line):
                buy_events.append(line.strip())
            elif sell_pattern.search(line):
                sell_events.append(line.strip())

    return buy_events, sell_events


def generate_report_content(date_str: str, buy_events: list, sell_events: list) -> str:
    """
    Generates the Markdown content for the daily report.

    Args:
        date_str (str): The date of the report.
        buy_events (list): A list of buy event log lines.
        sell_events (list): A list of sell event log lines.

    Returns:
        str: The generated Markdown report as a string.
    """
    content = []
    content.append(f"# {date_str} 투자 결과 리포트")
    content.append("\n---\n")

    # 매수 기록
    content.append("## 📝 매수 기록\n")
    if buy_events:
        for event in buy_events:
            # Extracting reason needs a more specific log format.
            # For now, we'll just list the log entry.
            content.append(f"- {event}\n")
    else:
        content.append("- 해당일에 매수 기록이 없습니다.\n")
    content.append("\n")

    # 매도 기록
    content.append("## 📈 매도 기록\n")
    if sell_events:
        for event in sell_events:
            content.append(f"- {event}\n")
    else:
        content.append("- 해당일에 매도 기록이 없습니다.\n")
    content.append("\n")

    # 총평 및 결과
    content.append("## 📊 총평 및 결과\n")
    total_trades = len(buy_events) + len(sell_events)
    summary = f"총 {total_trades}건의 거래가 발생했습니다. (매수: {len(buy_events)}건, 매도: {len(sell_events)}건)"
    # TODO: 실제 수익률 계산 로직 추가 필요
    result = "수익률 계산은 현재 구현되지 않았습니다."

    content.append(f"{summary}\n\n")
    content.append(f"{result}\n")

    return "".join(content)


def generate_daily_report():
    """
    The main function to generate the daily trading report.
    It reads today's log, creates the report content, and saves it to a file.
    """
    logger.info("일일 투자 결과 리포트 생성을 시작합니다.")
    setup_reporter()

    now = datetime.now()
    # 리포트 파일명 및 내용에 사용할 날짜 형식 (YYYY-MM-DD)
    date_str_for_report = now.strftime("%Y-%m-%d")
    # 로그 파일 검색에 사용할 날짜 형식 (YYYYMMDD)
    date_str_for_log = now.strftime("%Y%m%d")

    report_file_path = os.path.join(REPORT_DIR, REPORT_FILE_FORMAT.format(date_str_for_report))

    try:
        buy_events, sell_events = parse_log_file(date_str_for_log)
        report_content = generate_report_content(date_str_for_report, buy_events, sell_events)

        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"일일 투자 결과 리포트가 성공적으로 생성되었습니다: {report_file_path}")

    except Exception as e:
        logger.error(f"리포트 생성 중 오류 발생: {e}")


if __name__ == "__main__":
    # For direct testing
    generate_daily_report()
