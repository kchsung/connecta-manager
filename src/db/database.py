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
            # datetime 객체를 ISO 형식 문자열로 변환
            campaign_data = campaign.dict()
            if 'start_date' in campaign_data and campaign_data['start_date']:
                campaign_data['start_date'] = campaign_data['start_date'].isoformat()
            if 'end_date' in campaign_data and campaign_data['end_date']:
                campaign_data['end_date'] = campaign_data['end_date'].isoformat()
            
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
    def get_campaign_participations(self, campaign_id: str, page: int = 1, page_size: int = 5, search_sns_id: str = None) -> Dict[str, Any]:
        """캠페인 참여자 목록 조회 (페이징 지원, SNS ID 검색 지원)"""
        try:
            return simple_client.get_campaign_participations(campaign_id=campaign_id, page=page, page_size=page_size, search_sns_id=search_sns_id)
        except Exception as e:
            self._handle_error(e, "캠페인 참여자 조회")
            return {"data": [], "total_count": 0, "total_pages": 0, "current_page": page, "page_size": page_size}
    
    def get_all_campaign_participations(self, campaign_id: str) -> List[Dict[str, Any]]:
        """캠페인 참여자 목록 조회 (모든 데이터, 페이징 없음)"""
        try:
            # 큰 page_size로 설정하여 모든 데이터를 가져옴
            result = simple_client.get_campaign_participations(campaign_id=campaign_id, page=1, page_size=1000)
            return result.get('data', []) if isinstance(result, dict) else result
        except Exception as e:
            self._handle_error(e, "캠페인 참여자 조회")
            return []
    
    def get_all_participated_influencer_ids(self) -> set:
        """모든 캠페인에 참여한 인플루언서 ID 목록 조회"""
        try:
            # 모든 캠페인 참여 정보를 한 번에 조회
            campaigns = self.get_campaigns()
            all_participations = []
            for campaign in campaigns:
                participations = self.get_all_campaign_participations(campaign['id'])
                all_participations.extend(participations)
            
            # 참여한 인플루언서 ID 목록 추출
            participated_influencer_ids = set()
            for participation in all_participations:
                influencer_id = participation.get('influencer_id')
                if influencer_id:
                    participated_influencer_ids.add(influencer_id)
            
            return participated_influencer_ids
        except Exception as e:
            self._handle_error(e, "참여 인플루언서 ID 조회")
            return set()
    
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
    
    def get_participation_by_campaign_and_influencer(self, campaign_id: str, influencer_id: str) -> Dict[str, Any]:
        """특정 캠페인과 인플루언서의 참여 정보 조회"""
        try:
            result = simple_client.get_participation_by_campaign_and_influencer(campaign_id, influencer_id)
            return result
        except Exception as e:
            return self._handle_error(e, "참여 정보 조회")
    
    # 성과 지표 관련 메서드들
    def get_campaign_influencer_contents(self, participation_id: str) -> List[Dict[str, Any]]:
        """캠페인 인플루언서 콘텐츠 조회"""
        try:
            return simple_client.get_campaign_influencer_contents(participation_id)
        except Exception as e:
            self._handle_error(e, "캠페인 콘텐츠 조회")
            return []
    
    def get_performance_data_by_participation(self, participation_id: str) -> List[Dict[str, Any]]:
        """참여별 성과 데이터 조회 (campaign_influencer_contents 테이블 기반)"""
        try:
            return simple_client.get_campaign_influencer_contents(participation_id)
        except Exception as e:
            self._handle_error(e, "성과 데이터 조회")
            return []
    
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
        try:
            metric_data = metric.dict()
            result = simple_client.create_performance_metric(metric_data)
            return result
        except Exception as e:
            return self._handle_error(e, "성과 지표 생성")
    
    def get_performance_metrics_by_influencer(self, influencer_id: str) -> List[Dict[str, Any]]:
        """인플루언서별 성과 지표 조회"""
        try:
            return simple_client.get_performance_metrics_by_influencer(influencer_id)
        except Exception as e:
            self._handle_error(e, "성과 지표 조회")
            return []
    
    def get_performance_metrics_by_participation(self, participation_id: str) -> List[Dict[str, Any]]:
        """참여별 성과 지표 조회"""
        try:
            return simple_client.get_performance_metrics_by_participation(participation_id)
        except Exception as e:
            self._handle_error(e, "성과 지표 조회")
            return []
    
    def update_performance_metric(self, metric_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """성과 지표 업데이트"""
        try:
            result = simple_client.update_performance_metric(metric_id, update_data)
            return result
        except Exception as e:
            return self._handle_error(e, "성과 지표 업데이트")
    
    def delete_performance_metric(self, metric_id: str) -> Dict[str, Any]:
        """성과 지표 삭제"""
        try:
            result = simple_client.delete_performance_metric(metric_id)
            return result
        except Exception as e:
            return self._handle_error(e, "성과 지표 삭제")
    
    def get_user_stats(self) -> Dict[str, Any]:
        """사용자 통계 조회"""
        try:
            return simple_client.get_user_stats()
        except Exception as e:
            return self._handle_error(e, "사용자 통계 조회")

# 전역 인스턴스
db_manager = DatabaseManager()
