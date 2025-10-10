import streamlit as st
import requests
import json
from typing import Dict, Any, List, Optional
from .auth import supabase_auth

class EdgeFunctionClient:
    def __init__(self):
        self.base_url = None
        self._setup_base_url()
    
    def _setup_base_url(self):
        """Supabase URL에서 Edge Function URL 설정"""
        try:
            # Streamlit secrets에서 Supabase URL 가져오기
            supabase_url = st.secrets["supabase"]["url"]
            # URL에서 프로젝트 참조 추출
            # 예: https://abcdefghijklmnop.supabase.co -> https://abcdefghijklmnop.supabase.co
            self.base_url = f"{supabase_url}/functions/v1/connecta-manager-api"
        except Exception as e:
            print(f"Supabase URL 설정 실패: {e}")
            # 환경 변수에서 시도
            import os
            supabase_url = os.getenv("SUPABASE_URL")
            if supabase_url:
                self.base_url = f"{supabase_url}/functions/v1/connecta-manager-api"
    
    def _get_headers(self) -> Dict[str, str]:
        """인증 헤더 생성"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        # JWT 토큰 추가
        if 'auth_token' in st.session_state and st.session_state.auth_token:
            headers['Authorization'] = f"Bearer {st.session_state.auth_token}"
            print(f"🔑 토큰 전달됨: {st.session_state.auth_token[:20]}...")
        else:
            print("❌ 토큰이 없습니다. session_state:", list(st.session_state.keys()))
            # 세션에서 토큰을 다시 가져오기 시도
            try:
                from .auth import supabase_auth
                current_user = supabase_auth.get_current_user()
                if current_user:
                    # Supabase 클라이언트에서 현재 세션 가져오기
                    client = supabase_auth.get_client()
                    session = client.auth.get_session()
                    if session and session.access_token:
                        st.session_state.auth_token = session.access_token
                        st.session_state.refresh_token = session.refresh_token
                        headers['Authorization'] = f"Bearer {session.access_token}"
                        print(f"🔄 토큰 재설정됨: {session.access_token[:20]}...")
            except Exception as e:
                print(f"토큰 재설정 실패: {e}")
        
        return headers
    
    def _make_request(self, method: str, path: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Edge Function에 요청 보내기"""
        try:
            if not self.base_url:
                return {
                    "success": False,
                    "error": "BASE_URL_NOT_SET",
                    "message": "Supabase URL이 설정되지 않았습니다."
                }
            
            # URL 구성
            url = f"{self.base_url}?path={path}"
            if params:
                for key, value in params.items():
                    if value is not None:
                        url += f"&{key}={value}"
            
            headers = self._get_headers()
            
            # 요청 보내기
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return {
                    "success": False,
                    "error": "INVALID_METHOD",
                    "message": f"지원하지 않는 HTTP 메서드: {method}"
                }
            
            # 응답 처리
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", "UNKNOWN_ERROR"),
                        "message": error_data.get("message", "알 수 없는 오류가 발생했습니다.")
                    }
                except:
                    return {
                        "success": False,
                        "error": "HTTP_ERROR",
                        "message": f"HTTP {response.status_code}: {response.text}"
                    }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": "REQUEST_ERROR",
                "message": f"요청 중 오류가 발생했습니다: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "UNKNOWN_ERROR",
                "message": f"알 수 없는 오류가 발생했습니다: {str(e)}"
            }
    
    # 캠페인 관련 메서드들
    def get_campaigns(self, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """캠페인 목록 조회"""
        params = {}
        if campaign_id:
            params['id'] = campaign_id
        
        return self._make_request('GET', 'campaigns', params=params)
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 캠페인 생성"""
        return self._make_request('POST', 'campaigns', data=campaign_data)
    
    def update_campaign(self, campaign_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 업데이트"""
        params = {'id': campaign_id}
        return self._make_request('PUT', 'campaigns', params=params, data=update_data)
    
    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """캠페인 삭제"""
        params = {'id': campaign_id}
        return self._make_request('DELETE', 'campaigns', params=params)
    
    # 인플루언서 관련 메서드들
    def get_influencers(self, influencer_id: Optional[str] = None, platform: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """인플루언서 목록 조회"""
        params = {}
        if influencer_id:
            params['id'] = influencer_id
        if platform:
            params['platform'] = platform
        if search:
            params['search'] = search
        
        return self._make_request('GET', 'influencers', params=params)
    
    def create_influencer(self, influencer_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 인플루언서 생성"""
        return self._make_request('POST', 'influencers', data=influencer_data)
    
    def update_influencer(self, influencer_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """인플루언서 업데이트"""
        params = {'id': influencer_id}
        return self._make_request('PUT', 'influencers', params=params, data=update_data)
    
    def delete_influencer(self, influencer_id: str) -> Dict[str, Any]:
        """인플루언서 삭제"""
        params = {'id': influencer_id}
        return self._make_request('DELETE', 'influencers', params=params)
    
    # 분석 및 통계
    def get_analytics(self, type: str = 'overview') -> Dict[str, Any]:
        """분석 및 통계 조회"""
        params = {'type': type}
        return self._make_request('GET', 'analytics', params=params)

# 전역 인스턴스
edge_function_client = EdgeFunctionClient()
