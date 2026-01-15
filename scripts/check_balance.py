#!/usr/bin/env python3
"""
RedArrow 모의계좌 현황 조회 스크립트

API를 통해 직접 계좌의 잔고와 보유 종목 현황을 조회합니다.
"""

import sys
from pathlib import Path
import logging

# 프로젝트 루트를 Python 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    from src.config import Settings
    from src.data_collectors.broker_api import create_broker_api
except ImportError as e:
    print(f"Error: {e}")
    print("Please ensure the script is run from the project's root directory or that the src path is correct.")
    sys.exit(1)

# 기본 로깅 설정 (API 모듈 내 로거가 사용)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_account_status():
    """계좌 현황을 조회하고 출력합니다."""
    print("="*60)
    print("RedArrow 계좌 현황 조회 시스템")
    print("="*60)

    try:
        # 1. 설정 로드
        print("1. 설정 파일 로드 중...")
        settings = Settings()
        
        # TRADING_MODE가 'simulation'인지 확인
        if settings.trading_mode != 'simulation':
            print(f"오류: 이 스크립트는 모의투자(simulation) 모드에서만 실행 가능합니다.")
            print(f"현재 TRADING_MODE: {settings.trading_mode}")
            sys.exit(1)

        print(f"   - 거래 모드: {settings.trading_mode}")
        print(f"   - 계좌 번호: {settings.account_number}")

        # 2. Broker API 초기화
        print("\n2. 증권사 API 초기화...")
        broker_config = {
            'app_key': settings.app_key,
            'app_secret': settings.app_secret,
            'account_number': settings.account_number,
            'trading_mode': settings.trading_mode
        }
        api = create_broker_api(settings.broker_type, broker_config)

        # 3. API 연결
        print("\n3. API 서버에 연결 중...")
        if not api.connect():
            print("\n❌ API 연결에 실패했습니다. 설정을 확인하세요.")
            return

        print("   - API 연결 성공")

        # 4. 계좌 잔고 조회
        print("\n4. 계좌 잔고 조회 중...")
        balance = api.get_account_balance()

        if not balance:
            print("\n❌ 계좌 잔고 조회에 실패했습니다.")
        else:
            print("\n" + "-"*25 + " 계좌 잔고 " + "-"*25)
            print(f"   - 총 평가금액 (순자산): {balance.get('total_assets', 0):,}원")
            print(f"   - 주식 평가금액: {balance.get('stock_eval_amount', 0):,}원")
            print(f"   - 평가 손익: {balance.get('profit_loss', 0):,}원")
            print(f"   - 예수금 (현금): {balance.get('total_amount', 0):,}원")
            print(f"   - ✨ 주문 가능 현금: {balance.get('available_amount', 0):,}원")
            print("-" * 60)

        # 5. 보유 종목 조회
        print("\n5. 보유 종목 조회 중...")
        positions = api.get_positions()

        if not positions:
            print("\nℹ️  현재 보유 중인 종목이 없습니다.")
        else:
            print("\n" + "-"*25 + " 보유 종목 " + "-"*25)
            total_profit_loss = 0
            for pos in positions:
                profit_loss = pos.get('profit_loss', 0)
                total_profit_loss += profit_loss
                print(f"   - {pos.get('name', 'N/A')} ({pos.get('code', 'N/A')})")
                print(f"     - 보유 수량: {pos.get('quantity', 0):,}주")
                print(f"     - 평균 단가: {pos.get('avg_price', 0):,.0f}원")
                print(f"     - 현재가: {pos.get('current_price', 0):,.0f}원")
                print(f"     - 평가 손익: {profit_loss:,.0f}원 ({pos.get('profit_rate', 0):.2f}%)")
                print()
            print("-" * 60)
            print(f"   - 총 보유 종목: {len(positions)}개")
            print(f"   - 총 평가 손익: {total_profit_loss:,.0f}원")


    except FileNotFoundError:
        print("\n❌ 오류: 'config/config.yaml' 또는 '.env' 파일을 찾을 수 없습니다.")
        print("   - 스크립트를 프로젝트의 루트 디렉토리에서 실행하고 있는지 확인하세요.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n" + "="*60)
        print("조회가 완료되었습니다.")
        print("="*60)


if __name__ == "__main__":
    check_account_status()
