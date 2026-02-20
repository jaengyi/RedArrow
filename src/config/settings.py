"""
설정 관리 모듈

환경 변수와 YAML 설정 파일을 로드하고 관리합니다.

===============================================================================
[학습 가이드] - 이 파일을 읽기 전에
===============================================================================

📚 이 파일의 역할:
    - 프로그램의 모든 설정값을 중앙에서 관리합니다
    - .env 파일(민감 정보)과 config.yaml(전략 설정)을 로드합니다
    - 다른 모듈에서 settings.app_key처럼 쉽게 설정값에 접근할 수 있게 합니다

🎯 학습 목표:
    1. @property 데코레이터의 사용법과 장점 이해하기
    2. os.getenv()로 환경 변수 읽는 방법 배우기
    3. yaml.safe_load()로 YAML 설정 파일 파싱하기
    4. pathlib.Path로 파일 경로를 다루는 현대적인 방법 익히기

📖 사전 지식:
    - Python 기본 문법 (클래스, 메서드)
    - 딕셔너리(Dict) 자료형

🔗 관련 파일:
    - .env: API 키 등 민감한 설정 (Git에 올리지 않음)
    - config/config.yaml: 거래 전략 관련 설정
    - src/main.py: 이 Settings 클래스를 사용하는 메인 파일

💡 핵심 개념:
    - 환경 변수(Environment Variable): 운영체제에서 프로그램에 전달하는 설정값
    - YAML: 사람이 읽기 쉬운 설정 파일 형식 (JSON보다 간결함)
    - Property: 메서드를 변수처럼 사용할 수 있게 해주는 Python 기능

===============================================================================
"""

# ============================================================================
# [학습 포인트] 모듈 임포트
# ============================================================================
# Python에서는 필요한 기능을 다른 모듈에서 가져와서 사용합니다.
# 표준 라이브러리(Python 설치 시 포함)와 외부 라이브러리를 구분합니다.
# ============================================================================

import os  # 운영체제 기능 (환경 변수 읽기 등) - 표준 라이브러리
import yaml  # YAML 파일 파싱 - 외부 라이브러리 (pip install pyyaml)
from pathlib import Path  # 파일 경로를 객체로 다루는 현대적 방법 - 표준 라이브러리
from typing import Dict, Any  # 타입 힌트를 위한 모듈 - 표준 라이브러리
from dotenv import load_dotenv  # .env 파일 로드 - 외부 라이브러리 (pip install python-dotenv)


# ============================================================================
# [학습 포인트] 클래스 정의
# ============================================================================
# 클래스(Class)는 관련된 데이터와 기능을 하나로 묶는 틀입니다.
# Settings 클래스는 모든 설정값을 관리하는 "설정 관리자" 역할을 합니다.
#
# 클래스 사용 예시:
#   settings = Settings()          # 인스턴스 생성 (__init__ 호출됨)
#   print(settings.app_key)        # @property 메서드 호출
#   settings.validate()            # 일반 메서드 호출
# ============================================================================

class Settings:
    """설정 관리 클래스"""

    def __init__(self, config_path: str = None):
        """
        초기화

        Args:
            config_path: 설정 파일 경로 (기본: config/config.yaml)
        """
        # ====================================================================
        # [학습 포인트] __init__ 메서드
        # ====================================================================
        # __init__은 클래스의 인스턴스가 생성될 때 자동으로 호출되는 특별한 메서드입니다.
        # "초기화 메서드" 또는 "생성자(Constructor)"라고도 합니다.
        #
        # 사용 예: settings = Settings()  # 이때 __init__이 자동 호출됨
        #
        # self는 생성되는 인스턴스 자신을 가리킵니다.
        # self.root_dir처럼 self.변수명으로 인스턴스 변수를 만들 수 있습니다.
        # ====================================================================

        # ====================================================================
        # [학습 포인트] Path 객체로 경로 다루기
        # ====================================================================
        # Path(__file__)는 현재 파일(settings.py)의 경로를 Path 객체로 만듭니다.
        # .parent는 부모 디렉토리를 반환합니다.
        # .parent.parent.parent는 3단계 위 폴더를 의미합니다:
        #   settings.py → config/ → src/ → RedArrow/ (프로젝트 루트)
        #
        # 전통적인 방법(os.path)과 비교:
        #   전통: os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        #   현대: Path(__file__).parent.parent.parent  ← 더 읽기 쉬움!
        # ====================================================================
        # 프로젝트 루트 디렉토리
        self.root_dir = Path(__file__).parent.parent.parent

        # ====================================================================
        # [학습 포인트] .env 파일 로드
        # ====================================================================
        # .env 파일은 API 키, 비밀번호 등 민감한 정보를 저장합니다.
        # load_dotenv()를 호출하면 .env 파일의 내용이 환경 변수로 로드됩니다.
        #
        # .env 파일 예시:
        #   SIMULATION_APP_KEY=PS12345abcdef
        #   SIMULATION_APP_SECRET=xyz789...
        #
        # 로드 후 os.getenv('SIMULATION_APP_KEY')로 값을 읽을 수 있습니다.
        #
        # Path 객체의 / 연산자: 경로를 직관적으로 연결
        #   self.root_dir / '.env'  →  /app/RedArrow/.env
        # ====================================================================
        # .env 파일 로드
        env_path = self.root_dir / '.env'
        if env_path.exists():  # 파일 존재 여부 확인
            load_dotenv(env_path)  # 환경 변수로 로드
        else:
            print("⚠️  .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성하세요.")

        # config.yaml 파일 로드
        if config_path is None:
            config_path = self.root_dir / 'config' / 'config.yaml'
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        # ====================================================================
        # [학습 포인트] YAML 파일 읽기
        # ====================================================================
        # with open() as f: 구문은 파일을 안전하게 열고 닫습니다.
        # - with 블록이 끝나면 자동으로 파일이 닫힘 (close() 불필요)
        # - 에러가 발생해도 파일이 안전하게 닫힘
        #
        # yaml.safe_load()는 YAML 텍스트를 Python 딕셔너리로 변환합니다.
        # safe_load를 사용하는 이유: 보안 취약점 방지 (임의 코드 실행 차단)
        #
        # YAML 예시 → Python 변환:
        #   stock_selector:        →  {'stock_selector': {
        #     top_volume_count: 30           'top_volume_count': 30,
        #     k_value: 0.5                   'k_value': 0.5
        #                               }}
        # ====================================================================
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)  # YAML → Python 딕셔너리

    # ========================================
    # 증권사 API 설정
    # ========================================

    # ========================================================================
    # [학습 포인트] @property 데코레이터
    # ========================================================================
    # @property는 메서드를 변수처럼 사용할 수 있게 해주는 데코레이터입니다.
    #
    # 데코레이터 없이:
    #   def get_broker_type(self):
    #       return os.getenv('BROKER_TYPE', 'koreainvestment')
    #   사용: settings.get_broker_type()  # 괄호 필요
    #
    # @property 사용:
    #   @property
    #   def broker_type(self):
    #       return os.getenv('BROKER_TYPE', 'koreainvestment')
    #   사용: settings.broker_type  # 괄호 불필요, 변수처럼 사용
    #
    # 장점:
    #   1. 사용이 간결함 (settings.broker_type vs settings.get_broker_type())
    #   2. 내부 구현을 숨김 (사용자는 어떻게 값을 가져오는지 몰라도 됨)
    #   3. 나중에 로직 변경이 쉬움 (호출하는 코드 수정 불필요)
    # ========================================================================

    @property
    def broker_type(self) -> str:
        """증권사 타입"""
        # os.getenv(이름, 기본값): 환경 변수 읽기. 없으면 기본값 반환
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
        # ====================================================================
        # [학습 포인트] 조건에 따른 환경 변수 선택
        # ====================================================================
        # 이 패턴은 "설정 자동 선택"입니다.
        # 사용자가 TRADING_MODE만 바꾸면 연관된 모든 설정이 자동으로 바뀝니다.
        #
        # 왜 이렇게 설계했나?
        #   - 실수 방지: 모의투자 모드에서 실전 키를 사용하는 실수를 막음
        #   - 편의성: 여러 설정을 일일이 바꿀 필요 없음
        #   - 확장성: 나중에 다른 모드(예: 'backtest')를 추가하기 쉬움
        # ====================================================================
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
        # ====================================================================
        # [학습 포인트] 딕셔너리의 .get() 메서드
        # ====================================================================
        # dict.get(key, default)는 key가 없을 때 에러 대신 default를 반환합니다.
        #
        # 비교:
        #   self.config['stock_selector']     # 키가 없으면 KeyError 발생!
        #   self.config.get('stock_selector', {})  # 키가 없으면 빈 딕셔너리 반환
        #
        # 이 패턴은 설정 파일에 해당 섹션이 없어도 프로그램이 죽지 않게 합니다.
        # ====================================================================
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
        # ====================================================================
        # [학습 포인트] 검증(Validation) 패턴
        # ====================================================================
        # 프로그램 시작 전에 필수 설정이 올바른지 확인합니다.
        # "빨리 실패하기(Fail-Fast)" 원칙: 문제를 일찍 발견하면 디버깅이 쉬움
        #
        # 이 메서드의 동작:
        #   1. 에러 목록(errors)과 경고 목록(warnings)을 수집
        #   2. 에러가 있으면 False 반환 (프로그램 시작 불가)
        #   3. 경고만 있으면 True 반환 (프로그램 시작 가능, 주의 필요)
        #
        # 왜 리스트에 모았다가 한번에 출력하나?
        #   - 사용자가 모든 문제를 한눈에 볼 수 있음
        #   - 하나 고치고 실행 → 또 에러 → 또 고치는 반복을 줄임
        # ====================================================================
        errors = []  # 치명적 문제 (프로그램 실행 불가)
        warnings = []  # 경고 (실행 가능하지만 주의 필요)

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


# ============================================================================
# [학습 포인트] if __name__ == "__main__": 패턴
# ============================================================================
# 이 조건은 "이 파일이 직접 실행될 때만" 아래 코드를 실행합니다.
# 다른 파일에서 import될 때는 실행되지 않습니다.
#
# 사용 예:
#   $ python src/config/settings.py   → if 블록 실행됨 (직접 실행)
#   from src.config import Settings   → if 블록 실행 안 됨 (import)
#
# 이 패턴의 용도:
#   1. 모듈 테스트: 개발 중 모듈 단독 실행하여 동작 확인
#   2. 사용 예시 제공: 다른 개발자에게 사용법 시연
#   3. 유틸리티 기능: 설정 검증, 정보 출력 등
#
# __name__은 Python 내장 변수입니다:
#   - 직접 실행 시: __name__ == "__main__"
#   - import 시: __name__ == 모듈 이름 (예: "src.config.settings")
# ============================================================================
if __name__ == "__main__":
    # 이 파일을 직접 실행하면 설정 요약과 검증 결과를 보여줍니다.
    # 사용법: python -m src.config.settings
    settings = Settings()
    settings.print_summary()
    settings.validate()
