from enum import Enum
import os

# ✅ 서비스 타입 정의
class ServiceType(str, Enum):
    TITANIC = "titanic"
    CRIME = "crime"
    MATZIP = "matzip"
    NLP = "nlp"
    TF = "tf"
    CHAT = "chat"

# ✅ 환경 변수에서 서비스 URL 가져오기
DOMAIN = os.getenv("DOMAIN")

TITANIC_SERVICE_URL = os.getenv("TITANIC_SERVICE_URL")
CRIME_SERVICE_URL = os.getenv("CRIME_SERVICE_URL")
MATZIP_SERVICE_URL = os.getenv("MATZIP_SERVICE_URL")
NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL")
TF_SERVICE_URL = os.getenv("TF_SERVICE_URL")
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL")

# ✅ 서비스 URL 매핑
SERVICE_URLS = {
    ServiceType.TITANIC: TITANIC_SERVICE_URL,
    ServiceType.CRIME: CRIME_SERVICE_URL,
    ServiceType.MATZIP: MATZIP_SERVICE_URL,
    ServiceType.NLP: NLP_SERVICE_URL,
    ServiceType.TF: TF_SERVICE_URL,
    ServiceType.CHAT: CHAT_SERVICE_URL,
}

# (선택) 필요하다면 도메인도 별도로 활용 가능
# 예시
print(f"도메인: {DOMAIN}")
print(f"TITANIC 서비스 URL: {SERVICE_URLS[ServiceType.TITANIC]}")
print(f"CRIME 서비스 URL: {SERVICE_URLS[ServiceType.CRIME]}")
print(f"MATZIP 서비스 URL: {SERVICE_URLS[ServiceType.MATZIP]}")
print(f"NLP 서비스 URL: {SERVICE_URLS[ServiceType.NLP]}")
print(f"TF 서비스 URL: {SERVICE_URLS[ServiceType.TF]}")
print(f"CHAT 서비스 URL: {SERVICE_URLS[ServiceType.CHAT]}")
