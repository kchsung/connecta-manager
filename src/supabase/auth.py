import streamlit as st
from supabase import Client
from .config import supabase_config
from typing import Optional, Dict, Any
import json
import base64

class SupabaseAuth:
    def __init__(self):
        self.client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """Supabase 클라이언트 반환"""
        if not self.client:
            self.client = supabase_config.get_client()
        return self.client
    
    def _save_token_to_browser(self, token: str):
        """브라우저에 토큰 저장"""
        # Streamlit의 session state를 사용하여 토큰 저장
        st.session_state.auth_token = token
        st.session_state.token_saved = True
    
    def _get_token_from_browser(self) -> Optional[str]:
        """브라우저에서 토큰 가져오기"""
        # session state에서 토큰 확인
        if 'auth_token' in st.session_state:
            return st.session_state.auth_token
        return None
    
    def _clear_token_from_browser(self):
        """브라우저에서 토큰 제거"""
        if 'auth_token' in st.session_state:
            del st.session_state.auth_token
        if 'token_saved' in st.session_state:
            del st.session_state.token_saved
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """회원가입"""
        try:
            client = self.get_client()
            response = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": "http://localhost:8501"
                }
            })
            
            # 회원가입 성공 시 자동으로 로그인 처리
            if response.user and response.session:
                # 세션 정보를 Streamlit 세션 상태에 저장
                st.session_state.user = response.user
                st.session_state.authenticated = True
                
                # 토큰을 브라우저에 저장
                if response.session.access_token:
                    self._save_token_to_browser(response.session.access_token)
                
                return {
                    "success": True,
                    "data": response,
                    "message": "회원가입이 완료되었습니다! 자동으로 로그인되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": "회원가입에 실패했습니다."
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"
            }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """로그인"""
        try:
            client = self.get_client()
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # 세션 정보를 Streamlit 세션 상태에 저장
            if response.user and response.session:
                st.session_state.user = response.user
                st.session_state.authenticated = True
                
                # 토큰을 브라우저에 저장
                if response.session.access_token:
                    self._save_token_to_browser(response.session.access_token)
                
            return {
                "success": True,
                "data": response,
                "message": "로그인에 성공했습니다."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"로그인 중 오류가 발생했습니다: {str(e)}"
            }
    
    def sign_out(self) -> Dict[str, Any]:
        """로그아웃"""
        try:
            client = self.get_client()
            client.auth.sign_out()
            
            # 세션 상태 초기화
            if 'user' in st.session_state:
                del st.session_state.user
            if 'authenticated' in st.session_state:
                del st.session_state.authenticated
            
            # 브라우저에서 토큰 제거
            self._clear_token_from_browser()
                
            return {
                "success": True,
                "message": "로그아웃되었습니다."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"로그아웃 중 오류가 발생했습니다: {str(e)}"
            }
    
    def get_current_user(self):
        """현재 로그인된 사용자 정보 반환"""
        if 'user' in st.session_state and st.session_state.authenticated:
            return st.session_state.user
        return None
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        # 먼저 session state에서 확인
        if st.session_state.get('authenticated', False):
            return True
        
        # Supabase 클라이언트에서 현재 세션 확인
        try:
            client = self.get_client()
            session = client.auth.get_session()
            if session and session.user:
                # 세션이 유효한 경우 session state 업데이트
                st.session_state.user = session.user
                st.session_state.authenticated = True
                return True
        except Exception as e:
            print(f"세션 확인 실패: {e}")
        
        return False
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """비밀번호 재설정 이메일 발송"""
        try:
            client = self.get_client()
            response = client.auth.reset_password_email(email)
            return {
                "success": True,
                "data": response,
                "message": "비밀번호 재설정 이메일이 발송되었습니다."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"비밀번호 재설정 중 오류가 발생했습니다: {str(e)}"
            }

# 전역 인스턴스
supabase_auth = SupabaseAuth()
