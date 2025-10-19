import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional

# .env 파일 로드 (있는 경우)
try:
    from dotenv import load_dotenv
    load_dotenv()
    # .env 파일 로드 완료 (로그 출력 제거)
except ImportError:
    # python-dotenv가 설치되지 않음 (로그 출력 제거)
    pass
except Exception as e:
    # .env 파일 로드 실패 (로그 출력 제거)
    pass

class SupabaseConfig:
    def __init__(self):
        self._client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """인증 토큰이 포함된 Supabase 클라이언트 반환"""
        if not self._client:
            # Streamlit secrets에서 먼저 가져오기 시도
            url = None
            key = None
            
            try:
                url = st.secrets["supabase"]["url"]
                key = st.secrets["supabase"]["anon_key"]
                # Streamlit secrets에서 Supabase 설정 로드됨
            except Exception as e:
                # Streamlit secrets에서 가져오기 실패시 환경 변수에서 가져오기
                url = os.getenv("SUPABASE_URL")
                key = os.getenv("SUPABASE_ANON_KEY")
                
                if not url or not key:
                    raise Exception(f"Supabase 설정을 찾을 수 없습니다. Streamlit secrets나 환경 변수를 확인하세요. 에러: {str(e)}")
            
            # URL 유효성 검사
            if not url or not url.startswith('https://'):
                raise Exception(f"Invalid Supabase URL: {url}. URL은 https://로 시작해야 합니다.")
            
            if not key or len(key) < 10:
                raise Exception(f"Invalid Supabase Key: {key[:10]}... (너무 짧음)")
            
            # Supabase 클라이언트 생성
            self._client = create_client(url, key)
            # Supabase 클라이언트 생성 완료 (로그 출력 제거)
        
        
        return self._client
    

# 전역 인스턴스
supabase_config = SupabaseConfig()
