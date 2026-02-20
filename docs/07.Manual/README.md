# RedArrow 사용자 매뉴얼

## 📚 개요

이 디렉토리는 RedArrow 자동매매 시스템의 실행 및 운영을 위한 사용자 매뉴얼을 포함합니다.

---

## 📖 문서 구성

### 1. [QuickStart.md](./QuickStart.md)
**대상**: 경험 있는 사용자
**목적**: 5분 안에 빠르게 시작하기
**내용**:
- 빠른 설치 및 실행
- 주요 명령어
- 체크리스트
- 일일 운영 루틴

**이런 분께 추천:**
- Python과 거래 시스템에 익숙한 사용자
- 빠르게 시작하고 싶은 사용자
- 레퍼런스가 필요한 사용자

### 2. [ExecutionGuide.md](./ExecutionGuide.md)
**대상**: 모든 사용자 (초급자 포함)
**목적**: 단계별 상세 실행 가이드
**내용**:
- 사전 준비사항
- 환경 설정 (상세)
- API 키 설정
- 설정 파일 조정
- 프로그램 실행 및 모니터링
- 자동 실행 설정
- 모드 전환 가이드

**이런 분께 추천:**
- 처음 사용하는 사용자
- 자세한 설명이 필요한 사용자
- 자동 실행 설정을 원하는 사용자

### 3. [TroubleShooting.md](./TroubleShooting.md)
**대상**: 문제를 겪고 있는 사용자
**목적**: 일반적인 문제 해결
**내용**:
- 설치 및 설정 문제
- API 연결 문제
- 실행 중 오류
- 거래 관련 문제
- 성능 문제
- 로그 분석
- 긴급 상황 대응

**이런 분께 추천:**
- 오류가 발생한 사용자
- 예상대로 동작하지 않는 경우
- 긴급 상황에 대응이 필요한 사용자

---

## 🎯 사용 흐름도

```
처음 사용하시나요?
    ↓
    [YES] → ExecutionGuide.md 정독
             ↓
             QuickStart.md를 레퍼런스로 사용

    [NO, 경험 있음] → QuickStart.md로 빠르게 시작
                      ↓
                      필요시 ExecutionGuide.md 참고

문제가 발생했나요?
    ↓
    TroubleShooting.md 확인
    ↓
    해결 안 됨?
    ↓
    GitHub Issues 또는 관련 문서 참고
```

---

## ⚡ 빠른 링크

### 처음 사용하는 경우

1. **[환경 설정](./ExecutionGuide.md#2-환경-설정)** - Python, Git 설치
2. **[API 키 설정](./ExecutionGuide.md#3-api-키-설정)** - 필수!
3. **[프로그램 실행](./ExecutionGuide.md#5-프로그램-실행)** - 첫 실행
4. **[모니터링](./ExecutionGuide.md#6-모니터링-및-관리)** - 실행 중 확인

### 자주 찾는 항목

- **[빠른 시작 체크리스트](./QuickStart.md#-체크리스트)**
- **[일일 운영 루틴](./QuickStart.md#-일일-운영-루틴)**
- **[모드 전환 (모의↔실전)](./ExecutionGuide.md#101-모의투자--실전투자-전환)**
- **[긴급 상황 대응](./TroubleShooting.md#7-긴급-상황-대응)**

### 문제 해결

- **[설치 문제](./TroubleShooting.md#1-설치-및-설정-문제)**
- **[API 연결 문제](./TroubleShooting.md#2-api-연결-문제)**
- **[거래 문제](./TroubleShooting.md#4-거래-관련-문제)**
- **[성능 문제](./TroubleShooting.md#5-성능-문제)**

---

## 📋 시작 전 체크리스트

### 필수 준비물

- [ ] Python 3.11 이상 설치
- [ ] 한국투자증권 계좌 (모의투자 또는 실전투자)
- [ ] API 키 발급 완료 (APP_KEY, APP_SECRET, 계좌번호)
- [ ] 안정적인 인터넷 연결
- [ ] 충분한 디스크 공간 (최소 1GB)

### 권장 사항

- [ ] Git 설치 (코드 업데이트 용이)
- [ ] 텍스트 에디터 (VS Code, nano 등)
- [ ] 기본적인 Python 지식
- [ ] 주식 거래 경험
- [ ] 기술적 분석 기초 지식

---

## 🔧 핵심 명령어 요약

### 프로그램 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 프로그램 실행
python src/main.py

# 로그 모니터링 (다른 터미널)
tail -f logs/redarrow.log
```

### 설정 관리

```bash
# 설정 검증
python -m src.config.settings

# .env 파일 편집
nano .env

# config.yaml 편집
nano config/config.yaml
```

### 모니터링

```bash
# 당일 거래 내역
grep "$(date +%Y-%m-%d)" logs/redarrow.log | grep "매수\|매도"

# 에러 확인
grep "ERROR" logs/redarrow.log

# 실시간 로그
tail -f logs/redarrow.log | grep "매수\|매도\|체결"
```

---

## ⚠️ 주의사항

### 보안

1. **API 키 보호**
   - `.env` 파일 절대 공유 금지
   - Git에 업로드되지 않도록 주의
   - 정기적인 키 갱신 권장

2. **계정 보안**
   - 2단계 인증 활성화
   - 비밀번호 정기 변경
   - 의심스러운 활동 즉시 확인

### 거래 리스크

1. **모의투자로 시작**
   - 최소 1주일 테스트 후 실전 전환
   - 전략 검증 필수
   - 리스크 관리 확인

2. **실전투자 주의**
   - 실제 돈이 거래됩니다
   - 손실 가능성 항상 존재
   - 투자는 본인 책임

3. **긴급 대응 준비**
   - 수동 개입 방법 숙지
   - 한국투자증권 앱 접근 가능 상태 유지
   - 긴급 연락처 저장

---

## 📞 추가 도움말

### 관련 문서

**보안:**
- [API 키 관리](../06.Security/APIKeyManagement.md)
- [데이터베이스 가이드](../06.Security/DatabaseGuide.md)

**설계:**
- [시스템 설계](../03.Design/SystemDesign_20251231.md)

**구현:**
- [프로그램 목록](../04.Implement/ProgramList_20251231.md)
- [프로그램 사양서](../04.Implement/ProgramSpecification_20251231.md)

**배포:**
- [배포 가이드](../05.Deploy/DeploymentGuide_20251231.md)

**기술:**
- [Python 기초](../10.Technical/PythonBasics_20251231.md)
- [기술 분석](../02.Analysis/TechnicalAnalysis_20251231.md)

### 지원

- **GitHub Issues**: https://github.com/jaengyi/RedArrow/issues
- **문서 피드백**: GitHub Issues 또는 Pull Request

---

## 🗺️ 학습 경로

### 초급 사용자

1. **1일차**: [ExecutionGuide.md](./ExecutionGuide.md) 정독
2. **2일차**: API 키 설정 및 환경 구축
3. **3일차**: 모의투자로 첫 실행
4. **4-7일차**: 모니터링 및 로그 분석 학습
5. **2주차**: 설정 최적화 시도

### 중급 사용자

1. **자동 실행 설정**: [ExecutionGuide.md#8-자동-실행-설정](./ExecutionGuide.md#8-자동-실행-설정)
2. **성능 최적화**: [TroubleShooting.md#5-성능-문제](./TroubleShooting.md#5-성능-문제)
3. **코드 커스터마이징**: 프로그램 사양서 참고

### 고급 사용자

1. **시스템 확장**: 새로운 지표 추가
2. **전략 개발**: 선정 알고리즘 수정
3. **모니터링 개선**: 대시보드 구축
4. **기여**: GitHub Pull Request

### 📖 소스 코드 학습 (개발자용)

Python과 자동매매 시스템을 소스 코드를 통해 학습하고 싶다면:

1. **[소스 코드 학습 로드맵](../10.Technical/SourceCodeLearningRoadmap.md)** - 단계별 학습 가이드
2. **[라이브러리 사용 가이드](../10.Technical/LibraryGuide.md)** - pandas, requests 등 핵심 라이브러리

**추천 학습 순서**:
```
[초급] settings.py → main.py(개요) → technical_indicators.py
         ↓
[중급] selector.py → risk_control.py → report_generator.py
         ↓
[고급] broker_api.py → main.py(전체)
```

---

## 🎓 FAQ

### Q: 프로그래밍 경험이 없는데 사용할 수 있나요?
**A**: [ExecutionGuide.md](./ExecutionGuide.md)를 따라하면 기본 사용이 가능합니다. 하지만 Python과 터미널 기초 지식이 있으면 더 좋습니다. [Python 기초 문서](../10.Technical/PythonBasics_20251231.md)를 참고하세요.

### Q: 얼마의 자금이 필요한가요?
**A**: 모의투자는 무료입니다. 실전투자는 최소 100만원 이상 권장합니다.

### Q: 하루에 몇 시간 관리해야 하나요?
**A**: 자동매매이므로 최소 관리만 필요합니다. 장 시작 전 10분, 장 중 확인 2-3회, 장 마감 후 10분 정도면 충분합니다.

### Q: Mac에서만 사용할 수 있나요?
**A**: Linux, macOS, Windows 모두 가능합니다. 이 문서는 macOS/Linux 기준이지만 Windows도 유사합니다.

### Q: 수익을 보장하나요?
**A**: 아니요. 투자는 항상 리스크가 있으며, 손실 가능성이 있습니다. 이 시스템은 도구일 뿐이며, 투자 결과는 본인 책임입니다.

---

## 📝 피드백

이 매뉴얼에 대한 피드백은 언제나 환영합니다!

- **오타/오류**: GitHub Issues
- **개선 제안**: GitHub Issues 또는 Pull Request
- **추가 문서 요청**: GitHub Issues

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 사용자 매뉴얼 디렉토리 README 작성 | - |
