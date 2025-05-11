import os
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class ChatService:
    print(f"🩷3 서비스 진입")
    def __init__(self):
        # 환경 변수 로드
        load_dotenv()
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if not self.hf_token:
            raise ValueError("HUGGINGFACE_TOKEN이 설정되지 않았습니다.")

        # 모델 및 토크나이저 로드
        self.model_name = "lcw99/ko-dialoGPT-korean-chit-chat"
        logger.info(f"모델 로딩 시작: {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            token=self.hf_token
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            token=self.hf_token
        )
        logger.info("모델 로딩 완료")

    async def chat(self, message: str):
        try:
            # 입력 메시지 전처리
            input_text = f"User: {message}\nAssistant:"
            logger.info(f"입력 텍스트: {input_text}")
            
            # 입력 메시지 토크나이징
            inputs = self.tokenizer.encode(
                input_text,
                return_tensors='pt',
                add_special_tokens=True
            )
            
            # 응답 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=200,  # 최대 길이 증가
                    min_length=10,   # 최소 길이 설정
                    num_return_sequences=1,
                    no_repeat_ngram_size=3,
                    temperature=0.8,  # 약간 더 창의적인 응답을 위해 온도 상승
                    top_k=50,
                    top_p=0.95,
                    do_sample=True,  # 샘플링 활성화
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2  # 반복 패널티 추가
                )
            
            # 응답 디코딩
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"전체 응답: {response}")
            
            # Assistant: 이후의 텍스트만 추출
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
            else:
                response = response.replace(input_text, "").strip()
            
            logger.info(f"최종 응답: {response}")
            
            if not response:
                response = "죄송합니다. 응답을 생성하지 못했습니다. 다시 시도해주세요."
            
            return {
                "response": response,
                "metadata": {
                    "model": self.model_name,
                    "temperature": 0.8
                }
            }
            
        except Exception as e:
            logger.error(f"응답 생성 중 오류 발생: {str(e)}")
            raise Exception(f"응답 생성 실패: {str(e)}")
