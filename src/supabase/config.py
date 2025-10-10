import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional

# .env 파일 로드 (있는 경우)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] .env 파일 로드됨")
except ImportError:
    print("[WARNING] python-dotenv가 설치되지 않음. 환경 변수를 직접 설정하세요.")
except Exception as e:
    print(f"[WARNING] .env 파일 로드 실패: {e}")

class SupabaseConfig:
    def __init__(self):
        self._client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """인증 토큰이 포함된 Supabase 클라이언트 반환"""
        if not self._client:
            # 환경 변수에서 Supabase 설정 가져오기
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_ANON_KEY")
            
            print(f"🔍 환경 변수 확인:")
            print(f"  - SUPABASE_URL: {'설정됨' if url else '없음'}")
            print(f"  - SUPABASE_ANON_KEY: {'설정됨' if key else '없음'}")
            
            if not url or not key:
                # Streamlit secrets에서 가져오기 시도
                try:
                    url = st.secrets["supabase"]["url"]
                    key = st.secrets["supabase"]["anon_key"]
                    print("✅ Streamlit secrets에서 Supabase 설정 로드됨")
                except Exception as e:
                    print(f"❌ Streamlit secrets 로드 실패: {e}")
                    raise Exception("Supabase 설정을 찾을 수 없습니다. 환경 변수나 Streamlit secrets를 확인하세요.")
            else:
                print("✅ 환경 변수에서 Supabase 설정 로드됨")
            
            self._client = create_client(url, key)
            print("✅ Supabase 클라이언트 생성 완료")
        
        
        return self._client
    

# 전역 인스턴스
supabase_config = SupabaseConfig()
