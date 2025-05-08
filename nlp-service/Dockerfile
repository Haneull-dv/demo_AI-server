FROM python:3.11.9-slim

# 환경변수 설정 - Python 출력 버퍼링 비활성화 및 한글 인코딩 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    PYTHONTRACEMALLOC=1 \
    PYTHONFAULTHANDLER=1 \
    LOG_LEVEL=DEBUG

# 필수 시스템 패키지 설치 (apt-get)
RUN apt-get update && \
    # Java 설치 (KoNLPy의 OKT 형태소 분석기가 JVM 필요)
    # default-jdk는 시스템에 맞는 기본 JDK를 설치해줌 (python:3.11-slim에서는 openjdk-11-jdk 패키지를 직접 찾을 수 없음)
    apt-get install -y --no-install-recommends \
    default-jdk \
    # 기타 필요한 시스템 의존성 
    build-essential \
    g++ \
    gcc \
    # 디버깅용 도구 추가
    procps \
    curl \
    nano \
    && \
    # 캐시 정리 및 불필요한 파일 제거로 이미지 크기 최적화
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일 복사
COPY requirements.txt .

# 모든 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# NLTK 데이터 다운로드 (punkt 데이터셋은 tokenize에 필요)
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt

# 애플리케이션 코드 복사
COPY app ./app

# 필요한 디렉토리 생성 및 권한 설정
RUN mkdir -p output original && \
    chmod -R 777 output original

# 디버깅: 디렉토리 구조 출력
RUN ls -la /app && \
    ls -la /app/original && \
    ls -la /app/output && \
    ls -la /app/app && \
    echo "Java version:" && \
    java -version && \
    echo "Python version:" && \
    python --version && \
    echo "NLTK data path:" && \
    python -c "import nltk; print(nltk.data.path)"

# 포트 노출
EXPOSE 9004

# 애플리케이션 실행 명령
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9004", "--reload"]
