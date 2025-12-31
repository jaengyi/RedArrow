"""
설정 관리 모듈

환경 변수와 YAML 설정 파일을 로드하고 관리합니다.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Settings:
    """설정 관리 클래스"""

    def __init__(self, config_path: str = None):
        """
        초기화

        Args:
            config_path: 설정 파일 경로 (기본: config/config.yaml)
        """
        # 프로젝트 루트 디렉토리
        self.root_dir = Path(__file__).parent.parent.parent

        # .env 파일 로드
        env_path = self.root_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print("⚠️  .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성하세요.")

        # config.yaml 파일 로드
        if config_path is None:
            config_path = self.root_dir / 'config' / 'config.yaml'
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    # ========================================
    # 증권사 API 설정
    # ========================================

    @property
    def broker_type(self) -> str:
        """증권사 타입"""
        return os.getenv('BROKER_TYPE', 'koreainvestment')

    @property
    def trading_mode(self) -> str:
        """거래 모드: simulation 또는 real"""
        return os.getenv('TRADING_MODE', 'simulation')

    @property
    def app_key(self) -> str:
        """
        API 앱 키

        TRADING_MODE에 따라 자동으로 실전/모의투자 키를 선택합니다.
        - simulation: SIMULATION_APP_KEY
        - real: REAL_APP_KEY
        """
        if self.trading_mode == 'simulation':
            return os.getenv('SIMULATION_APP_KEY', '')
        else:
            return os.getenv('REAL_APP_KEY', '')

    @property
    def app_secret(self) -> str:
        """
        API 앱 시크릿

        TRADING_MODE에 따라 자동으로 실전/모의투자 시크릿을 선택합니다.
        - simulation: SIMULATION_APP_SECRET
        - real: REAL_APP_SECRET
        """
        if self.trading_mode == 'simulation':
            return os.getenv('SIMULATION_APP_SECRET', '')
        else:
            return os.getenv('REAL_APP_SECRET', '')

    @property
    def account_number(self) -> str:
        """
        계좌번호

        TRADING_MODE에 따라 자동으로 실전/모의투자 계좌번호를 선택합니다.
        - simulation: SIMULATION_ACCOUNT_NUMBER
        - real: REAL_ACCOUNT_NUMBER
        """
        if self.trading_mode == 'simulation':
            return os.getenv('SIMULATION_ACCOUNT_NUMBER', '')
        else:
            return os.getenv('REAL_ACCOUNT_NUMBER', '')

    @property
    def is_paper_trading(self) -> bool:
        """
        모의투자 여부

        TRADING_MODE가 'simulation'이면 True를 반환합니다.
        """
        return self.trading_mode == 'simulation'

    # ========================================
    # 데이터베이스 설정
    # ========================================

    @property
    def db_config(self) -> Dict[str, str]:
        """PostgreSQL 데이터베이스 설정"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'redarrow_db'),
            'user': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', '')
        }

    @property
    def redis_config(self) -> Dict[str, Any]:
        """Redis 설정"""
        return {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'password': os.getenv('REDIS_PASSWORD', None),
            'decode_responses': True
        }

    # ========================================
    # 종목 선정 설정
    # ========================================

    @property
    def stock_selector_config(self) -> Dict[str, Any]:
        """종목 선정 설정"""
        return self.config.get('stock_selector', {})

    # ========================================
    # 기술적 지표 설정
    # ========================================

    @property
    def indicators_config(self) -> Dict[str, Any]:
        """기술적 지표 설정"""
        return self.config.get('indicators', {})

    # ========================================
    # 리스크 관리 설정
    # ========================================

    @property
    def risk_management_config(self) -> Dict[str, Any]:
        """리스크 관리 설정"""
        config = self.config.get('risk_management', {})

        # 환경 변수가 있으면 우선 적용
        if os.getenv('STOP_LOSS_PERCENT'):
            config['stop_loss_percent'] = float(os.getenv('STOP_LOSS_PERCENT'))

        if os.getenv('TAKE_PROFIT_PERCENT'):
            config['take_profit_percent'] = float(os.getenv('TAKE_PROFIT_PERCENT'))

        if os.getenv('MAX_POSITION_SIZE'):
            config['max_position_size'] = int(os.getenv('MAX_POSITION_SIZE'))

        if os.getenv('MAX_POSITIONS'):
            config['max_positions'] = int(os.getenv('MAX_POSITIONS'))

        if os.getenv('DAILY_LOSS_LIMIT'):
            config['daily_loss_limit'] = float(os.getenv('DAILY_LOSS_LIMIT'))

        return config

    # ========================================
    # 시장 운영 시간 설정
    # ========================================

    @property
    def market_hours(self) -> Dict[str, str]:
        """시장 운영 시간"""
        return self.config.get('market_hours', {})

    # ========================================
    # 데이터 수집 설정
    # ========================================

    @property
    def data_collection_config(self) -> Dict[str, Any]:
        """데이터 수집 설정"""
        return self.config.get('data_collection', {})

    # ========================================
    # 로깅 설정
    # ========================================

    @property
    def logging_config(self) -> Dict[str, Any]:
        """로깅 설정"""
        config = self.config.get('logging', {})

        # 환경 변수가 있으면 우선 적용
        if os.getenv('LOG_LEVEL'):
            config['level'] = os.getenv('LOG_LEVEL')

        return config

    # ========================================
    # 알림 설정
    # ========================================

    @property
    def notifications_config(self) -> Dict[str, Any]:
        """알림 설정"""
        config = self.config.get('notifications', {})

        # 외부 서비스 설정 추가
        config['slack_webhook_url'] = os.getenv('SLACK_WEBHOOK_URL', '')
        config['telegram_bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN', '')
        config['telegram_chat_id'] = os.getenv('TELEGRAM_CHAT_ID', '')

        return config

    # ========================================
    # 검증 메서드
    # ========================================

    def validate(self, require_db: bool = False) -> bool:
        """
        필수 설정 검증

        Args:
            require_db: 데이터베이스 설정 필수 여부 (기본: False)

        Returns:
            검증 성공 여부
        """
        errors = []
        warnings = []

        # API 키 확인
        if not self.app_key:
            errors.append("APP_KEY가 설정되지 않았습니다.")

        if not self.app_secret:
            errors.append("APP_SECRET이 설정되지 않았습니다.")

        if not self.account_number:
            errors.append("ACCOUNT_NUMBER가 설정되지 않았습니다.")

        # 데이터베이스 설정 확인 (선택사항)
        if require_db:
            if not self.db_config['user']:
                errors.append("DB_USER가 설정되지 않았습니다.")

            if not self.db_config['password']:
                errors.append("DB_PASSWORD가 설정되지 않았습니다.")
        else:
            if not self.db_config['user'] or not self.db_config['password']:
                warnings.append("데이터베이스 미설정 (현재는 사용하지 않음)")

        if errors:
            print("\n❌ 설정 검증 실패:")
            for error in errors:
                print(f"  - {error}")
            print("\n💡 .env 파일을 확인하고 필수 값을 입력하세요.\n")
            return False

        if warnings:
            print("\n⚠️  경고:")
            for warning in warnings:
                print(f"  - {warning}")

        print("✅ 설정 검증 성공")
        return True

    def print_summary(self):
        """설정 요약 출력"""
        print("\n" + "="*50)
        print("RedArrow 설정 요약")
        print("="*50)
        print(f"증권사: {self.broker_type}")
        print(f"거래 모드: {self.trading_mode}")
        print(f"모의투자: {self.is_paper_trading}")
        print(f"계좌번호: {self.account_number}")
        print(f"\n손절률: {self.risk_management_config.get('stop_loss_percent')}%")
        print(f"익절률: {self.risk_management_config.get('take_profit_percent')}%")
        print(f"최대 포지션: {self.risk_management_config.get('max_positions')}개")
        print(f"단일 종목 최대 투자금: {self.risk_management_config.get('max_position_size'):,}원")
        print("="*50 + "\n")


# 사용 예시
if __name__ == "__main__":
    settings = Settings()
    settings.print_summary()
    settings.validate()
