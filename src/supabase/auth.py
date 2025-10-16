import streamlit as st
from supabase import Client
from .config import supabase_config
from typing import Optional, Dict, Any
import json
import base64
import time

class SupabaseAuth:
    def __init__(self):
        self.client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """Supabase 클라이언트 반환"""
        if not self.client:
            self.client = supabase_config.get_client()
        
        # 현재 인증 토큰이 있다면 클라이언트에 설정
        if 'auth_token' in st.session_state:
            try:
                self.client.auth.set_session(
                    access_token=st.session_state.auth_token,
                    refresh_token=st.session_state.get('refresh_token', '')
                )
            except Exception as e:
                # 토큰 설정 실패 (로그 출력 제거)
                pass
        
        return self.client
    
    def _save_token_to_browser(self, token: str, refresh_token: str = None):
        """브라우저에 토큰 저장"""
        # Streamlit의 session state를 사용하여 토큰 저장
        st.session_state.auth_token = token
        if refresh_token:
            st.session_state.refresh_token = refresh_token
        st.session_state.token_saved = True
        st.session_state.token_timestamp = time.time()
    
    def _get_token_from_browser(self) -> Optional[str]:
        """브라우저에서 토큰 가져오기"""
        # session state에서 토큰 확인
        if 'auth_token' in st.session_state:
            return st.session_state.auth_token
        return None
    
    def _get_refresh_token_from_browser(self) -> Optional[str]:
        """브라우저에서 리프레시 토큰 가져오기"""
        if 'refresh_token' in st.session_state:
            return st.session_state.refresh_token
        return None
    
    def _clear_token_from_browser(self):
        """브라우저에서 토큰 제거"""
        if 'auth_token' in st.session_state:
            del st.session_state.auth_token
        if 'refresh_token' in st.session_state:
            del st.session_state.refresh_token
        if 'token_saved' in st.session_state:
            del st.session_state.token_saved
        if 'token_timestamp' in st.session_state:
            del st.session_state.token_timestamp
    
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
                    self._save_token_to_browser(
                        response.session.access_token,
                        response.session.refresh_token
                    )
                
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
                    self._save_token_to_browser(
                        response.session.access_token,
                        response.session.refresh_token
                    )
                
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
            # 토큰이 있는지 확인하고 유효성 검사
            token = self._get_token_from_browser()
            if token:
                # 토큰 만료 시간 확인 (1시간 = 3600초)
                token_timestamp = st.session_state.get('token_timestamp', 0)
                if time.time() - token_timestamp < 3600:
                    return True
                else:
                    # 토큰이 만료된 경우 리프레시 시도
                    return self._try_refresh_session()
            return True
        
        # Supabase 클라이언트에서 현재 세션 확인
        try:
            client = self.get_client()
            session = client.auth.get_session()
            if session and session.user:
                # 세션이 유효한 경우 session state 업데이트
                st.session_state.user = session.user
                st.session_state.authenticated = True
                if session.access_token:
                    self._save_token_to_browser(
                        session.access_token,
                        session.refresh_token
                    )
                return True
        except Exception as e:
            # 세션 확인 실패 (로그 출력 제거)
            pass
        
        # 저장된 토큰으로 세션 복원 시도
        return self._try_restore_session()
    
    def _try_refresh_session(self) -> bool:
        """리프레시 토큰으로 세션 갱신 시도"""
        try:
            refresh_token = self._get_refresh_token_from_browser()
            if not refresh_token:
                return False
            
            client = self.get_client()
            response = client.auth.refresh_session(refresh_token)
            
            if response.session and response.user:
                # 새로운 세션 정보 저장
                st.session_state.user = response.user
                st.session_state.authenticated = True
                self._save_token_to_browser(
                    response.session.access_token,
                    response.session.refresh_token
                )
                return True
        except Exception as e:
            # 세션 갱신 실패 (로그 출력 제거)
            # 갱신 실패 시 토큰 제거
            self._clear_token_from_browser()
            if 'user' in st.session_state:
                del st.session_state.user
            if 'authenticated' in st.session_state:
                del st.session_state.authenticated
        
        return False
    
    def _try_restore_session(self) -> bool:
        """저장된 토큰으로 세션 복원 시도"""
        try:
            token = self._get_token_from_browser()
            if not token:
                return False
            
            client = self.get_client()
            # 토큰으로 사용자 정보 확인
            response = client.auth.get_user(token)
            
            if response.user:
                # 세션 복원 성공
                st.session_state.user = response.user
                st.session_state.authenticated = True
                return True
        except Exception as e:
            # 세션 복원 실패 (로그 출력 제거)
            # 복원 실패 시 토큰 제거
            self._clear_token_from_browser()
        
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
    
    def refresh_session_if_needed(self) -> bool:
        """필요한 경우 세션 갱신"""
        token_timestamp = st.session_state.get('token_timestamp', 0)
        # 토큰이 50분(3000초) 이상 지났으면 갱신
        if time.time() - token_timestamp > 3000:
            return self._try_refresh_session()
        return True

# 전역 인스턴스
supabase_auth = SupabaseAuth()
