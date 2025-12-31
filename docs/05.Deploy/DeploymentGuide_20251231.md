# RedArrow - 배포 가이드

## 문서 정보
- **작성일**: 2025-12-31
- **최종 수정일**: 2025-12-31
- **버전**: 1.0
- **작성자**: RedArrow Team

---

## 1. 개요

본 문서는 RedArrow 시스템을 다양한 환경에 배포하는 방법을 안내합니다.

### 1.1 배포 방법 종류
- 로컬 개발 환경 배포
- Docker 컨테이너 배포
- 클라우드 배포 (AWS, GCP, Azure)
- 리눅스 서버 배포

---

## 2. 사전 준비사항

### 2.1 필수 소프트웨어

#### 2.1.1 Python 3.11+
```bash
# macOS
brew install python@3.11

# Ubuntu/Linux
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# 버전 확인
python3.11 --version
```

#### 2.1.2 PostgreSQL 15+
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Linux
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 생성
createdb redarrow_db
```

#### 2.1.3 Redis 7+
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Linux
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# 연결 테스트
redis-cli ping
# 응답: PONG
```

#### 2.1.4 TA-Lib
```bash
# macOS
brew install ta-lib

# Ubuntu/Linux
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

### 2.2 증권사 API 준비
- 한국투자증권/키움증권/이베스트투자증권 중 선택
- API 키 발급
- 계좌 개설

---

## 3. 로컬 개발 환경 배포

### 3.1 프로젝트 클론

```bash
# Git 저장소 클론
git clone https://github.com/yourusername/RedArrow.git
cd RedArrow
```

### 3.2 가상환경 생성

```bash
# 가상환경 생성
python3.11 -m venv venv

# 가상환경 활성화
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 가상환경 활성화 확인
which python
# 출력: /path/to/RedArrow/venv/bin/python
```

### 3.3 의존성 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list
```

### 3.4 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 vim, code 등
```

**.env 파일 예시**:
```env
# 증권사 API 설정
BROKER_TYPE=koreainvestment
TRADING_MODE=simulation
APP_KEY=your_app_key_here
APP_SECRET=your_app_secret_here
ACCOUNT_NUMBER=your_account_number

# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_NAME=redarrow_db
DB_USER=postgres
DB_PASSWORD=your_password

# Redis 설정
REDIS_HOST=localhost
REDIS_PORT=6379

# 리스크 관리
STOP_LOSS_PERCENT=2.5
MAX_POSITION_SIZE=1000000
```

### 3.5 데이터베이스 초기화

```bash
# PostgreSQL 접속
psql -U postgres

# 데이터베이스 확인
\l

# 사용자 생성 (필요 시)
CREATE USER redarrow WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE redarrow_db TO redarrow;

# 종료
\q
```

### 3.6 프로그램 실행

```bash
# 설정 확인
python src/config/settings.py

# 메인 프로그램 실행
python src/main.py
```

### 3.7 로그 확인

```bash
# 로그 디렉토리 이동
cd logs

# 최신 로그 확인
tail -f redarrow_$(date +%Y%m%d).log
```

---

## 4. Docker 컨테이너 배포

### 4.1 Dockerfile 작성

**Dockerfile**:
```dockerfile
# Base image
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# TA-Lib 설치
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p logs

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 실행 권한 부여
RUN chmod +x src/main.py

# 실행 명령
CMD ["python", "src/main.py"]
```

### 4.2 docker-compose.yml 작성

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:15-alpine
    container_name: redarrow-postgres
    environment:
      POSTGRES_DB: redarrow_db
      POSTGRES_USER: redarrow
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - redarrow-network

  # Redis 캐시
  redis:
    image: redis:7-alpine
    container_name: redarrow-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - redarrow-network

  # RedArrow 애플리케이션
  redarrow:
    build: .
    container_name: redarrow-app
    depends_on:
      - postgres
      - redis
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=redarrow_db
      - DB_USER=redarrow
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - BROKER_TYPE=${BROKER_TYPE}
      - APP_KEY=${APP_KEY}
      - APP_SECRET=${APP_SECRET}
      - ACCOUNT_NUMBER=${ACCOUNT_NUMBER}
      - TRADING_MODE=${TRADING_MODE}
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    networks:
      - redarrow-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  redarrow-network:
    driver: bridge
```

### 4.3 Docker 빌드 및 실행

```bash
# Docker 이미지 빌드
docker-compose build

# 컨테이너 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f redarrow

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 중지
docker-compose down

# 볼륨까지 삭제 (주의!)
docker-compose down -v
```

### 4.4 Docker 관리 명령어

```bash
# 컨테이너 내부 접속
docker exec -it redarrow-app bash

# PostgreSQL 접속
docker exec -it redarrow-postgres psql -U redarrow -d redarrow_db

# Redis 접속
docker exec -it redarrow-redis redis-cli

# 리소스 사용량 확인
docker stats
```

---

## 5. 리눅스 서버 배포 (Ubuntu 22.04)

### 5.1 시스템 업데이트

```bash
# 시스템 업데이트
sudo apt update
sudo apt upgrade -y
```

### 5.2 사용자 생성

```bash
# 전용 사용자 생성
sudo useradd -m -s /bin/bash redarrow
sudo passwd redarrow

# 사용자 전환
sudo su - redarrow
```

### 5.3 프로젝트 배포

```bash
# 홈 디렉토리로 이동
cd ~

# 프로젝트 클론
git clone https://github.com/yourusername/RedArrow.git
cd RedArrow

# 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
nano .env
```

### 5.4 systemd 서비스 설정

**/etc/systemd/system/redarrow.service**:
```ini
[Unit]
Description=RedArrow Trading System
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=redarrow
Group=redarrow
WorkingDirectory=/home/redarrow/RedArrow
Environment="PATH=/home/redarrow/RedArrow/venv/bin"
ExecStart=/home/redarrow/RedArrow/venv/bin/python /home/redarrow/RedArrow/src/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/redarrow/RedArrow/logs/service.log
StandardError=append:/home/redarrow/RedArrow/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

### 5.5 서비스 관리

```bash
# 서비스 파일 권한 설정
sudo chmod 644 /etc/systemd/system/redarrow.service

# systemd 재로드
sudo systemctl daemon-reload

# 서비스 활성화
sudo systemctl enable redarrow

# 서비스 시작
sudo systemctl start redarrow

# 서비스 상태 확인
sudo systemctl status redarrow

# 로그 확인
journalctl -u redarrow -f

# 서비스 중지
sudo systemctl stop redarrow

# 서비스 재시작
sudo systemctl restart redarrow
```

---

## 6. 클라우드 배포

### 6.1 AWS 배포

#### 6.1.1 EC2 인스턴스 생성
1. AWS Console 접속
2. EC2 서비스 선택
3. "Launch Instance" 클릭
4. AMI 선택: Ubuntu Server 22.04 LTS
5. 인스턴스 타입: t3.medium 이상 권장
6. 스토리지: 30GB 이상
7. 보안 그룹 설정:
   - SSH (22): My IP
   - Custom TCP (5432): PostgreSQL (필요 시)
   - Custom TCP (6379): Redis (필요 시)

#### 6.1.2 Elastic IP 할당
```bash
# Elastic IP 할당
# AWS Console > EC2 > Elastic IPs > Allocate
# 생성된 IP를 인스턴스에 연결
```

#### 6.1.3 배포
```bash
# SSH 접속
ssh -i your-key.pem ubuntu@your-elastic-ip

# 위의 "리눅스 서버 배포" 섹션 참고하여 배포
```

#### 6.1.4 RDS 사용 (선택사항)
```bash
# AWS Console > RDS > Create database
# Engine: PostgreSQL 15
# Template: Free tier / Production
# DB instance identifier: redarrow-db
# Master username: redarrow
# Master password: [설정]
# VPC: 기본값 또는 EC2와 동일한 VPC

# .env 파일 수정
DB_HOST=redarrow-db.xxxxxxxx.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=redarrow_db
DB_USER=redarrow
DB_PASSWORD=your_password
```

#### 6.1.5 ElastiCache (Redis) 사용 (선택사항)
```bash
# AWS Console > ElastiCache > Create cluster
# Engine: Redis
# Name: redarrow-redis
# Node type: cache.t3.micro 이상
# VPC: EC2와 동일한 VPC

# .env 파일 수정
REDIS_HOST=redarrow-redis.xxxxxx.0001.use1.cache.amazonaws.com
REDIS_PORT=6379
```

### 6.2 GCP 배포

#### 6.2.1 Compute Engine 인스턴스 생성
```bash
# gcloud CLI 설치 및 인증
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 인스턴스 생성
gcloud compute instances create redarrow-instance \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB

# SSH 접속
gcloud compute ssh redarrow-instance --zone=us-central1-a
```

#### 6.2.2 Cloud SQL (PostgreSQL) 사용
```bash
# Cloud SQL 인스턴스 생성
gcloud sql instances create redarrow-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# 데이터베이스 생성
gcloud sql databases create redarrow_db \
    --instance=redarrow-db

# 사용자 생성
gcloud sql users create redarrow \
    --instance=redarrow-db \
    --password=your_password
```

### 6.3 Azure 배포

#### 6.3.1 Virtual Machine 생성
```bash
# Azure CLI 설치 및 로그인
az login

# 리소스 그룹 생성
az group create --name redarrow-rg --location eastus

# VM 생성
az vm create \
    --resource-group redarrow-rg \
    --name redarrow-vm \
    --image UbuntuLTS \
    --size Standard_B2s \
    --admin-username azureuser \
    --generate-ssh-keys

# SSH 접속
ssh azureuser@<PUBLIC_IP>
```

---

## 7. 자동 시작 설정

### 7.1 cron을 이용한 스케줄링

```bash
# crontab 편집
crontab -e

# 평일 오전 8시 50분에 시작 (장 시작 10분 전)
50 8 * * 1-5 cd /home/redarrow/RedArrow && /home/redarrow/RedArrow/venv/bin/python src/main.py >> logs/cron.log 2>&1

# 평일 오후 3시 40분에 종료 (장 마감 10분 후)
40 15 * * 1-5 pkill -f "python src/main.py"
```

### 7.2 APScheduler를 이용한 스케줄링 (프로그램 내부)

프로그램이 이미 APScheduler를 사용할 수 있도록 설계되어 있습니다.

---

## 8. 모니터링 및 관리

### 8.1 로그 모니터링

```bash
# 실시간 로그 확인
tail -f logs/redarrow_$(date +%Y%m%d).log

# 오류 로그만 확인
grep ERROR logs/redarrow_$(date +%Y%m%d).log

# 최근 100줄 확인
tail -n 100 logs/redarrow_$(date +%Y%m%d).log
```

### 8.2 리소스 모니터링

```bash
# CPU, 메모리 확인
htop

# 디스크 사용량
df -h

# 프로세스 확인
ps aux | grep python

# 네트워크 연결 확인
netstat -tuln | grep python
```

### 8.3 데이터베이스 백업

```bash
# PostgreSQL 백업
pg_dump -U redarrow redarrow_db > backup_$(date +%Y%m%d).sql

# 백업 복원
psql -U redarrow redarrow_db < backup_20251231.sql

# 자동 백업 (cron)
# crontab -e
0 2 * * * pg_dump -U redarrow redarrow_db > /home/redarrow/backups/redarrow_db_$(date +\%Y\%m\%d).sql
```

---

## 9. 보안 설정

### 9.1 방화벽 설정

```bash
# UFW 활성화 (Ubuntu)
sudo ufw enable

# SSH 허용
sudo ufw allow 22/tcp

# PostgreSQL 외부 접근 차단 (로컬만 허용)
sudo ufw deny 5432/tcp

# Redis 외부 접근 차단
sudo ufw deny 6379/tcp

# 방화벽 상태 확인
sudo ufw status
```

### 9.2 SSL/TLS 설정 (선택사항)

API 통신 시 HTTPS를 사용하도록 설정합니다. 증권사 API는 대부분 HTTPS를 기본으로 사용합니다.

### 9.3 환경 변수 암호화

```bash
# .env 파일 권한 제한
chmod 600 .env

# .env 파일 소유자 확인
ls -la .env
```

---

## 10. 트러블슈팅

### 10.1 일반적인 문제

#### 문제 1: TA-Lib 설치 실패
**증상**: `pip install TA-Lib` 실패
**해결**:
```bash
# macOS
brew install ta-lib

# Ubuntu/Linux
# 위의 "사전 준비사항" 섹션 참고하여 소스 컴파일
```

#### 문제 2: PostgreSQL 연결 실패
**증상**: `could not connect to server`
**해결**:
```bash
# PostgreSQL 실행 확인
sudo systemctl status postgresql

# 연결 테스트
psql -U redarrow -d redarrow_db

# 비밀번호 재설정 (필요 시)
sudo -u postgres psql
ALTER USER redarrow WITH PASSWORD 'new_password';
```

#### 문제 3: Redis 연결 실패
**증상**: `Error connecting to Redis`
**해결**:
```bash
# Redis 실행 확인
sudo systemctl status redis

# 연결 테스트
redis-cli ping

# Redis 재시작
sudo systemctl restart redis
```

#### 문제 4: 포트 충돌
**증상**: `Address already in use`
**해결**:
```bash
# 포트 사용 확인
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# 프로세스 종료 (PID 확인 후)
sudo kill -9 <PID>
```

### 10.2 성능 문제

#### CPU 사용률이 높을 때
- 데이터 수집 주기 조정 (config.yaml)
- 동시 모니터링 종목 수 감소
- 로그 레벨 INFO 이상으로 변경

#### 메모리 부족
- 가상환경 메모리 확인
- 불필요한 프로세스 종료
- 서버 업그레이드 고려

---

## 11. 업데이트 및 유지보수

### 11.1 코드 업데이트

```bash
# Git pull
cd /home/redarrow/RedArrow
git pull origin main

# 의존성 업데이트 확인
pip install -r requirements.txt --upgrade

# 서비스 재시작
sudo systemctl restart redarrow
```

### 11.2 데이터베이스 마이그레이션

현재 버전은 데이터베이스 스키마를 사용하지 않지만, 향후 필요 시:

```bash
# 스키마 백업
pg_dump -s -U redarrow redarrow_db > schema_backup.sql

# 마이그레이션 스크립트 실행
psql -U redarrow redarrow_db < migration_v1.1.sql
```

---

## 12. 배포 체크리스트

### 12.1 배포 전 체크리스트
- [ ] Python 3.11+ 설치 완료
- [ ] PostgreSQL 설치 및 데이터베이스 생성
- [ ] Redis 설치 및 실행
- [ ] TA-Lib 설치
- [ ] 증권사 API 키 발급
- [ ] .env 파일 작성 및 검증
- [ ] config.yaml 파일 확인
- [ ] 의존성 설치 (requirements.txt)

### 12.2 배포 후 체크리스트
- [ ] 프로그램 정상 실행 확인
- [ ] 로그 파일 생성 확인
- [ ] 데이터베이스 연결 확인
- [ ] Redis 연결 확인
- [ ] API 연동 확인 (증권사)
- [ ] 자동 시작 설정 (systemd 또는 cron)
- [ ] 모니터링 도구 설정
- [ ] 백업 설정

---

## 13. 참고 자료

### 13.1 공식 문서
- Python: https://docs.python.org/3.11/
- Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/documentation

### 13.2 클라우드 문서
- AWS EC2: https://docs.aws.amazon.com/ec2/
- Google Cloud: https://cloud.google.com/docs
- Azure: https://docs.microsoft.com/azure/

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 초기 배포 가이드 작성 | RedArrow Team |

---

**문서 끝**
