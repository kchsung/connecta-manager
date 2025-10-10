import streamlit as st
from typing import Dict, Any, List, Optional
from .config import supabase_config
from .auth import supabase_auth

class DirectSupabaseClient:
    """직접 Supabase 클라이언트를 사용하는 클래스 (RLS 적용)"""
    
    def __init__(self):
        self.client = None
    
    def get_client(self):
        """인증된 Supabase 클라이언트 반환"""
        try:
            # 먼저 일반 클라이언트를 가져오고, 인증 상태를 확인
            client = supabase_config.get_client()
            
            # 현재 사용자 확인
            current_user = supabase_auth.get_current_user()
            if not current_user:
                st.warning("로그인이 필요합니다. 먼저 로그인해주세요.")
                return None
            
            # 세션 확인
            session = client.auth.get_session()
            if not session or not session.access_token:
                st.warning("세션이 만료되었습니다. 다시 로그인해주세요.")
                return None
            
            return client
        except Exception as e:
            st.error(f"데이터베이스 연결 실패: {str(e)}")
            return None
    
    def _handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """에러 처리 공통 함수"""
        error_msg = str(error)
        print(f"데이터베이스 오류 ({operation}): {error_msg}")
        
        # RLS 관련 오류인지 확인
        if "row-level security" in error_msg.lower() or "permission denied" in error_msg.lower():
            return {
                "success": False,
                "error": "RLS_ERROR",
                "message": "데이터 접근 권한이 없습니다. 로그인 상태를 확인해주세요."
            }
        
        return {
            "success": False,
            "error": error_msg,
            "message": f"{operation} 중 오류가 발생했습니다: {error_msg}"
        }
    
    # 캠페인 관련 메서드들
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """사용자의 캠페인 목록 조회"""
        try:
            client = self.get_client()
            if not client:
                return []
            
            response = client.table("campaigns").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            self._handle_error(e, "캠페인 조회")
            return []
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 캠페인 생성"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            # 현재 사용자 ID 추가
            current_user = supabase_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "로그인이 필요합니다"}
            
            campaign_data["created_by"] = current_user.id
            
            response = client.table("campaigns").insert(campaign_data).execute()
            
            if response.data:
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": "캠페인이 성공적으로 생성되었습니다."
                }
            else:
                return {"success": False, "message": "캠페인 생성에 실패했습니다."}
        except Exception as e:
            return self._handle_error(e, "캠페인 생성")
    
    def update_campaign(self, campaign_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 정보 업데이트"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            response = client.table("campaigns").update(update_data).eq("id", campaign_id).execute()
            
            if response.data:
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": "캠페인이 성공적으로 업데이트되었습니다."
                }
            else:
                return {"success": False, "message": "캠페인 업데이트에 실패했습니다."}
        except Exception as e:
            return self._handle_error(e, "캠페인 업데이트")
    
    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """캠페인 삭제"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            response = client.table("campaigns").delete().eq("id", campaign_id).execute()
            
            return {
                "success": True,
                "message": "캠페인이 성공적으로 삭제되었습니다."
            }
        except Exception as e:
            return self._handle_error(e, "캠페인 삭제")
    
    # 인플루언서 관련 메서드들
    def get_influencers(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """인플루언서 목록 조회"""
        try:
            client = self.get_client()
            if not client:
                return []
            
            query = client.table("connecta_influencers").select("*")
            
            if platform:
                query = query.eq("platform", platform)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            self._handle_error(e, "인플루언서 조회")
            return []
    
    def get_influencer_info(self, platform: str, sns_id: str) -> Dict[str, Any]:
        """특정 인플루언서 정보 조회"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "exists": False}
            
            response = client.table("connecta_influencers")\
                .select("*")\
                .eq("platform", platform)\
                .eq("sns_id", sns_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return {
                    "success": True,
                    "exists": True,
                    "data": response.data[0]
                }
            else:
                return {
                    "success": True,
                    "exists": False,
                    "data": None
                }
        except Exception as e:
            return self._handle_error(e, "인플루언서 정보 조회")
    
    def create_influencer(self, influencer_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 인플루언서 생성"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            # 현재 사용자 ID 추가
            current_user = supabase_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "로그인이 필요합니다"}
            
            influencer_data["created_by"] = current_user.id
            
            response = client.table("connecta_influencers").insert(influencer_data).execute()
            
            if response.data:
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": "인플루언서가 성공적으로 생성되었습니다."
                }
            else:
                return {"success": False, "message": "인플루언서 생성에 실패했습니다."}
        except Exception as e:
            return self._handle_error(e, "인플루언서 생성")
    
    def update_influencer(self, influencer_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """인플루언서 정보 업데이트"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            response = client.table("connecta_influencers").update(update_data).eq("id", influencer_id).execute()
            
            if response.data:
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": "인플루언서가 성공적으로 업데이트되었습니다."
                }
            else:
                return {"success": False, "message": "인플루언서 업데이트에 실패했습니다."}
        except Exception as e:
            return self._handle_error(e, "인플루언서 업데이트")
    
    def delete_influencer(self, influencer_id: str) -> Dict[str, Any]:
        """인플루언서 삭제"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            response = client.table("connecta_influencers").delete().eq("id", influencer_id).execute()
            
            return {
                "success": True,
                "message": "인플루언서가 성공적으로 삭제되었습니다."
            }
        except Exception as e:
            return self._handle_error(e, "인플루언서 삭제")
    
    def get_user_stats(self) -> Dict[str, Any]:
        """사용자 통계 조회"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            current_user = supabase_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "로그인이 필요합니다"}
            
            # 간단한 통계 조회
            campaigns_response = client.table("campaigns").select("id").eq("created_by", current_user.id).execute()
            influencers_response = client.table("connecta_influencers").select("id").eq("created_by", current_user.id).execute()
            
            return {
                "success": True,
                "data": {
                    "user_id": current_user.id,
                    "email": current_user.email,
                    "total_campaigns": len(campaigns_response.data) if campaigns_response.data else 0,
                    "total_influencers": len(influencers_response.data) if influencers_response.data else 0
                }
            }
        except Exception as e:
            return self._handle_error(e, "사용자 통계 조회")

# 전역 인스턴스
direct_client = DirectSupabaseClient()
