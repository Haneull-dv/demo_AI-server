# ML 모델 API 서버

FastAPI를 이용한 머신러닝 모델 서빙 API 서버입니다.

## 프로젝트 구조

```
📁 app/
├── 📁 controller/         ← API 라우터 정의
│   └── predict_controller.py
├── 📁 service/            ← 비즈니스 로직
│   └── predict_service.py
├── main.py               ← FastAPI 앱 실행
├── model.pkl             ← 저장된 ML 모델
📄 Dockerfile              ← 도커 이미지 정의
📄 requirements.txt        ← 의존 패키지 리스트
📄 .dockerignore           ← 도커 빌드시 제외할 파일 목록
```

## 사용 방법

### 로컬에서 실행하기

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
uvicorn app.main:app --reload
```

### Docker로 실행하기

1. Docker 이미지 빌드
```bash
docker build -t ml-api-server .
```

2. Docker 컨테이너 실행
```bash
docker run -p 8000:8000 ml-api-server
```

## API 사용법

### 예측 API

- **엔드포인트**: `/api/predict`
- **메서드**: POST
- **입력 형식**:
```json
{
  "features": [0.1, 0.2, 0.3, 0.4]
}
```
- **출력 형식**:
```json
{
  "prediction": "class_label",
  "probability": {
    "class_1": 0.1,
    "class_2": 0.9
  }
}
```

## 주의사항

- 실제 모델 파일(model.pkl)은 직접 추가해야 합니다. 