import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..supabase.simple_client import simple_client
from ..supabase.auth import supabase_auth
from .models import Campaign, Influencer, CampaignInfluencer, CampaignInfluencerParticipation, PerformanceMetric

class DatabaseManager:
    def __init__(self):
        self.client = None
    
    def get_client(self):
        """간단한 Supabase 클라이언트 반환 (호환성을 위해 유지)"""
        return simple_client
    
    def _handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """에러 처리 공통 함수"""
        error_msg = str(error)
        print(f"데이터베이스 오류 ({operation}): {error_msg}")
        
        # 중복 제약조건 오류 감지
        if "duplicate key value violates unique constraint" in error_msg and "uq_platform_sns" in error_msg:
            return {
                "success": False,
                "error": "DUPLICATE_INFLUENCER",
                "message": "중복된 사용자가 있습니다. 같은 플랫폼의 동일한 SNS ID는 이미 등록되어 있습니다."
            }
        
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
            return simple_client.get_campaigns()
        except Exception as e:
            self._handle_error(e, "캠페인 조회")
            return []
    
    def create_campaign(self, campaign: Campaign) -> Dict[str, Any]:
        """새 캠페인 생성"""
        try:
            campaign_data = campaign.dict()
            result = simple_client.create_campaign(campaign_data)
            return result
        except Exception as e:
            return self._handle_error(e, "캠페인 생성")
    
    def update_campaign(self, campaign_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 정보 업데이트"""
        try:
            result = simple_client.update_campaign(campaign_id, update_data)
            return result
        except Exception as e:
            return self._handle_error(e, "캠페인 업데이트")
    
    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """캠페인 삭제"""
        try:
            result = simple_client.delete_campaign(campaign_id)
            return result
        except Exception as e:
            return self._handle_error(e, "캠페인 삭제")
    
    # 인플루언서 관련 메서드들
    def get_influencers(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """인플루언서 목록 조회"""
        try:
            return simple_client.get_influencers(platform=platform)
        except Exception as e:
            self._handle_error(e, "인플루언서 조회")
            return []
    
    def get_influencer_info(self, platform: str, sns_id: str) -> Dict[str, Any]:
        """특정 인플루언서 정보 조회"""
        try:
            return simple_client.get_influencer_info(platform, sns_id)
        except Exception as e:
            return self._handle_error(e, "인플루언서 정보 조회")
    
    def create_influencer(self, influencer: Influencer) -> Dict[str, Any]:
        """새 인플루언서 생성 (직접 Supabase 클라이언트 사용)"""
        try:
            influencer_data = influencer.dict()
            result = simple_client.create_influencer(influencer_data)
            return result
        except Exception as e:
            return self._handle_error(e, "인플루언서 생성")
    
    def update_influencer(self, influencer_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """인플루언서 정보 업데이트"""
        try:
            result = simple_client.update_influencer(influencer_id, update_data)
            return result
        except Exception as e:
            return self._handle_error(e, "인플루언서 업데이트")
    
    def delete_influencer(self, influencer_id: str) -> Dict[str, Any]:
        """인플루언서 삭제"""
        try:
            result = simple_client.delete_influencer(influencer_id)
            return result
        except Exception as e:
            return self._handle_error(e, "인플루언서 삭제")
    
    # 캠페인 참여 관련 메서드들
    def get_campaign_participations(self, campaign_id: str) -> List[Dict[str, Any]]:
        """캠페인 참여자 목록 조회"""
        try:
            return simple_client.get_campaign_participations(campaign_id=campaign_id)
        except Exception as e:
            self._handle_error(e, "캠페인 참여자 조회")
            return []
    
    def add_influencer_to_campaign(self, participation: CampaignInfluencerParticipation) -> Dict[str, Any]:
        """캠페인에 인플루언서 추가"""
        try:
            participation_data = participation.dict()
            result = simple_client.create_campaign_participation(participation_data)
            return result
        except Exception as e:
            return self._handle_error(e, "캠페인 참여 추가")
    
    def remove_influencer_from_campaign(self, participation_id: str) -> Dict[str, Any]:
        """캠페인에서 인플루언서 제거"""
        try:
            result = simple_client.delete_campaign_participation(participation_id)
            return result
        except Exception as e:
            return self._handle_error(e, "캠페인 참여 제거")
    
    def update_campaign_participation(self, participation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 참여 정보 업데이트"""
        try:
            result = simple_client.update_campaign_participation(participation_id, updates)
            return result
        except Exception as e:
            return self._handle_error(e, "캠페인 참여 업데이트")
    
    # 성과 지표 관련 메서드들
    def get_campaign_influencer_contents(self, participation_id: str) -> List[Dict[str, Any]]:
        """캠페인 인플루언서 콘텐츠 조회"""
        try:
            return simple_client.get_campaign_influencer_contents(participation_id)
        except Exception as e:
            return self._handle_error(e, "캠페인 콘텐츠 조회")
    
    def create_campaign_influencer_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 인플루언서 콘텐츠 생성"""
        try:
            return simple_client.create_campaign_influencer_content(content_data)
        except Exception as e:
            return self._handle_error(e, "캠페인 콘텐츠 생성")
    
    def update_campaign_influencer_content(self, content_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 인플루언서 콘텐츠 업데이트"""
        try:
            return simple_client.update_campaign_influencer_content(content_id, update_data)
        except Exception as e:
            return self._handle_error(e, "캠페인 콘텐츠 업데이트")
    
    def delete_campaign_influencer_content(self, content_id: str) -> Dict[str, Any]:
        """캠페인 인플루언서 콘텐츠 삭제"""
        try:
            return simple_client.delete_campaign_influencer_content(content_id)
        except Exception as e:
            return self._handle_error(e, "캠페인 콘텐츠 삭제")
    
    def create_performance_metric(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """성과 지표 생성"""
        # TODO: Edge Function에서 campaign-contents 구현 후 연결
        return {"success": False, "message": "성과 지표 기능은 아직 구현 중입니다."}
    
    def get_user_stats(self) -> Dict[str, Any]:
        """사용자 통계 조회"""
        try:
            return simple_client.get_user_stats()
        except Exception as e:
            return self._handle_error(e, "사용자 통계 조회")

# 전역 인스턴스
db_manager = DatabaseManager()
