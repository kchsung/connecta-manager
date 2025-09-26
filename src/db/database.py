import streamlit as st
import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import UserStats
from ..supabase.config import supabase_config

class DatabaseManager:
    def __init__(self):
        self.client = None
        
    def get_client(self):
        """Supabase 클라이언트 반환"""
        if not self.client:
            self.client = supabase_config.get_client()
        return self.client
    
    def get_current_user_id(self) -> Optional[str]:
        """현재 로그인된 사용자 ID 반환 (비로그인시 None)"""
        if 'user' in st.session_state and st.session_state.authenticated:
            return st.session_state.user.id
        return None
    
    def get_or_create_anonymous_user_id(self) -> str:
        """비로그인 사용자를 위한 임시 사용자 ID 생성"""
        if 'anonymous_user_id' not in st.session_state:
            import uuid
            st.session_state.anonymous_user_id = str(uuid.uuid4())
        return st.session_state.anonymous_user_id
    
    # 크롤링 관련 메서드들이 제거되었습니다.
    
    # 사용자 통계 관련 메서드
    def get_user_stats(self) -> Optional[Dict[str, Any]]:
        """사용자 통계 조회 - 크롤링 기능이 제거되어 빈 통계를 반환합니다."""
        return {
            "total_sessions": 0,
            "total_posts": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "total_likes": 0,
            "total_comments": 0
        }
    
    # 캠페인 관리 관련 메서드
    def create_campaign(self, campaign) -> Dict[str, Any]:
        """캠페인 생성"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            # 로그인하지 않은 경우 임시 사용자 ID 사용
            if not user_id:
                user_id = self.get_or_create_anonymous_user_id()
            
            campaign_data = {
                "created_by": user_id,
                "campaign_name": campaign.campaign_name,
                "campaign_description": campaign.campaign_description,
                "campaign_type": campaign.campaign_type,
                "start_date": campaign.start_date.strftime('%Y-%m-%d'),
                "end_date": campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
                "status": campaign.status,
                "campaign_instructions": campaign.campaign_instructions,
                "tags": campaign.tags if campaign.tags else ""
            }
            
            response = client.table("campaigns")\
                .insert(campaign_data)\
                .execute()
            
            return {"success": True, "data": response.data, "message": "캠페인이 생성되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"캠페인 생성 중 오류가 발생했습니다: {str(e)}"}
    
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """캠페인 목록 조회 (모든 캠페인 표시)"""
        try:
            client = self.get_client()
            
            # 모든 캠페인 조회 (생성자와 상관없이)
            response = client.table("campaigns")\
                .select("*")\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data
        except Exception as e:
            st.error(f"캠페인 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 정보 업데이트"""
        try:
            client = self.get_client()
            
            # 업데이트할 데이터 준비
            update_data = {
                "campaign_name": campaign_data.get("campaign_name"),
                "campaign_description": campaign_data.get("campaign_description"),
                "campaign_type": campaign_data.get("campaign_type"),
                "start_date": campaign_data.get("start_date"),
                "end_date": campaign_data.get("end_date"),
                "status": campaign_data.get("status"),
                "campaign_instructions": campaign_data.get("campaign_instructions"),
                "tags": campaign_data.get("tags") if campaign_data.get("tags") else "",
                "updated_at": datetime.now().isoformat()
            }
            
            # None 값 제거
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            response = client.table("campaigns")\
                .update(update_data)\
                .eq("id", campaign_id)\
                .execute()
            
            if response.data:
                return {"success": True, "data": response.data, "message": "캠페인이 수정되었습니다."}
            else:
                return {"success": False, "message": "캠페인을 찾을 수 없습니다."}
        except Exception as e:
            return {"success": False, "message": f"캠페인 수정 중 오류가 발생했습니다: {str(e)}"}
    
    def get_all_campaigns(self) -> List[Dict[str, Any]]:
        """모든 캠페인 목록 조회 (RLS 정책 우회용 - 개발/디버깅용)"""
        try:
            client = self.get_client()
            
            response = client.table("campaigns")\
                .select("*")\
                .order("created_at", desc=True)\
                .execute()
            
            print(f"DEBUG - get_all_campaigns: Found {len(response.data) if response.data else 0} campaigns")
            return response.data
        except Exception as e:
            st.error(f"모든 캠페인 조회 중 오류가 발생했습니다: {str(e)}")
            print(f"DEBUG - Exception in get_all_campaigns: {e}")
            return []
    
    def update_campaign_ownership(self, campaign_id: str, new_owner_id: str) -> Dict[str, Any]:
        """캠페인 소유권 변경"""
        try:
            client = self.get_client()
            
            response = client.table("campaigns")\
                .update({"created_by": new_owner_id})\
                .eq("id", campaign_id)\
                .execute()
            
            if response.data:
                return {"success": True, "message": "캠페인 소유권이 변경되었습니다."}
            else:
                return {"success": False, "message": "캠페인을 찾을 수 없습니다."}
        except Exception as e:
            return {"success": False, "message": f"캠페인 소유권 변경 중 오류가 발생했습니다: {str(e)}"}
    
    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """캠페인 삭제"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            # 로그인하지 않은 경우 임시 사용자 ID 사용
            if not user_id:
                user_id = self.get_or_create_anonymous_user_id()
            
            response = client.table("campaigns")\
                .delete()\
                .eq("id", campaign_id)\
                .eq("created_by", user_id)\
                .execute()
            
            return {"success": True, "message": "캠페인이 삭제되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"캠페인 삭제 중 오류가 발생했습니다: {str(e)}"}
    
    # 인플루언서 관리 관련 메서드
    def create_influencer(self, influencer) -> Dict[str, Any]:
        """인플루언서 생성 - connecta_influencers 테이블 사용"""
        try:
            client = self.get_client()
            
            # influencer_name이 비어있으면 sns_id를 사용
            influencer_name = influencer.influencer_name.strip() if influencer.influencer_name else influencer.sns_id
            
            influencer_data = {
                "platform": influencer.platform,
                "sns_id": influencer.sns_id,
                "sns_url": influencer.sns_url,
                "influencer_name": influencer_name,
                "owner_comment": influencer.owner_comment,
                "content_category": influencer.content_category,
                "active": True
            }
            
            response = client.table("connecta_influencers")\
                .insert(influencer_data)\
                .execute()
            
            return {"success": True, "data": response.data, "message": "인플루언서가 등록되었습니다."}
        except Exception as e:
            error_str = str(e)
            
            # 중복 오류 처리
            if "duplicate key" in error_str.lower() or "unique constraint" in error_str.lower():
                return {"success": False, "message": "중복된 인플루언서가 있어 등록할 수 없습니다."}
            
            # 기타 오류는 일반적인 메시지로 처리
            return {"success": False, "message": "인플루언서 등록 중 오류가 발생했습니다."}
    
    def get_influencers(self, platform: Optional[str] = None, first_crawled_only: bool = False) -> List[Dict[str, Any]]:
        """인플루언서 목록 조회 - connecta_influencers 테이블 사용 (모든 데이터 가져오기)"""
        try:
            client = self.get_client()
            
            all_data = []
            page_size = 1000
            offset = 0
            
            while True:
                query = client.table("connecta_influencers")\
                    .select("id, sns_id, influencer_name, platform, content_category, followers_count, post_count, profile_image_url, sns_url, owner_comment, profile_text, tags, contact_method, preferred_mode, created_at, updated_at")\
                    .order("created_at", desc=True)\
                    .range(offset, offset + page_size - 1)
                
                if platform:
                    query = query.eq("platform", platform)
                
                response = query.execute()
                
                if not response.data:
                    break
                
                all_data.extend(response.data)
                
                # 가져온 데이터가 페이지 크기보다 적으면 마지막 페이지
                if len(response.data) < page_size:
                    break
                
                offset += page_size
            
            return all_data
        except Exception as e:
            st.error(f"인플루언서 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    def get_influencers_with_update_filter(self, platform: Optional[str] = None, 
                                         update_filter_type: str = "전체", 
                                         update_date: Optional[datetime] = None,
                                         first_crawled_only: bool = False) -> List[Dict[str, Any]]:
        """업데이트 필터를 적용한 인플루언서 목록 조회 (모든 데이터 가져오기)"""
        try:
            client = self.get_client()
            
            all_data = []
            page_size = 1000
            offset = 0
            
            while True:
                query = client.table("connecta_influencers")\
                    .select("id, sns_id, influencer_name, platform, content_category, followers_count, post_count, profile_image_url, sns_url, owner_comment, profile_text, tags, contact_method, preferred_mode, created_at, updated_at")\
                    .order("created_at", desc=True)\
                    .range(offset, offset + page_size - 1)
                
                # 플랫폼 필터 적용
                if platform:
                    query = query.eq("platform", platform)
                
                # 업데이트 필터 적용
                if update_filter_type != "전체" and update_date:
                    update_datetime = datetime.combine(update_date, datetime.min.time())
                    
                    if update_filter_type == "마지막 업데이트 이후":
                        query = query.gte("updated_at", update_datetime.isoformat())
                    elif update_filter_type == "마지막 업데이트 이전":
                        query = query.lt("updated_at", update_datetime.isoformat())
                
                response = query.execute()
                
                if not response.data:
                    break
                
                all_data.extend(response.data)
                
                # 가져온 데이터가 페이지 크기보다 적으면 마지막 페이지
                if len(response.data) < page_size:
                    break
                
                offset += page_size
            
            return all_data
        except Exception as e:
            st.error(f"인플루언서 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    def update_influencer(self, influencer_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """인플루언서 정보 업데이트 - connecta_influencers 테이블 사용"""
        try:
            client = self.get_client()
            
            # 업데이트할 데이터 준비
            data = {
                "updated_at": datetime.now().isoformat()
            }
            
            # 기존 필드들
            if "influencer_name" in update_data and update_data["influencer_name"]:
                data["influencer_name"] = update_data["influencer_name"]
            
            if "platform" in update_data:
                data["platform"] = update_data["platform"]
            
            if "sns_id" in update_data and update_data["sns_id"]:
                data["sns_id"] = update_data["sns_id"]
            
            if "followers_count" in update_data:
                data["followers_count"] = update_data["followers_count"]
            
            if "sns_url" in update_data:
                data["sns_url"] = update_data["sns_url"]
            
            if "profile_text" in update_data:
                data["profile_text"] = update_data["profile_text"]
            
            # 새로운 필드들
            if "owner_comment" in update_data:
                data["owner_comment"] = update_data["owner_comment"]
            
            if "content_category" in update_data:
                data["content_category"] = update_data["content_category"]
            
            if "tags" in update_data:
                # tags를 텍스트로 처리 (text 타입)
                tags = update_data["tags"]
                print(f"DEBUG - tags in update_data: {tags}, type: {type(tags)}")
                
                if tags is None or tags == "":
                    data["tags"] = ""  # 빈 문자열로 처리
                    print(f"DEBUG - setting tags to empty string: '{data['tags']}'")
                else:
                    # 문자열 그대로 저장
                    data["tags"] = str(tags)
                    print(f"DEBUG - setting tags as text: '{data['tags']}'")
            
            if "contact_method" in update_data:
                data["contact_method"] = update_data["contact_method"]
            
            if "preferred_mode" in update_data:
                data["preferred_mode"] = update_data["preferred_mode"]
            
            if "price_krw" in update_data:
                data["price_krw"] = update_data["price_krw"]
            
            if "manager_rating" in update_data:
                data["manager_rating"] = update_data["manager_rating"]
            
            if "interested_products" in update_data:
                data["interested_products"] = update_data["interested_products"]
            
            if "shipping_address" in update_data:
                data["shipping_address"] = update_data["shipping_address"]
            
            if "phone_number" in update_data:
                data["phone_number"] = update_data["phone_number"]
            
            if "email" in update_data:
                data["email"] = update_data["email"]
            
            if "kakao_channel_id" in update_data:
                data["kakao_channel_id"] = update_data["kakao_channel_id"]
            
            print(f"DEBUG - Final data to send to Supabase: {data}")
            
            # Supabase에 전달되는 데이터를 반환하여 UI에서 확인할 수 있도록 함
            debug_info = {
                "final_data": data,
                "tags_in_data": data.get("tags"),
                "tags_type": type(data.get("tags"))
            }
            
            response = client.table("connecta_influencers")\
                .update(data)\
                .eq("id", influencer_id)\
                .execute()
            
            if response.data:
                return {"success": True, "data": response.data, "message": "인플루언서 정보가 업데이트되었습니다."}
            else:
                return {"success": False, "message": "인플루언서를 찾을 수 없습니다."}
        except Exception as e:
            return {"success": False, "message": f"인플루언서 업데이트 중 오류가 발생했습니다: {str(e)}"}
    
    def delete_influencer(self, influencer_id: str) -> Dict[str, Any]:
        """인플루언서 삭제 - connecta_influencers 테이블 사용"""
        try:
            client = self.get_client()
            
            response = client.table("connecta_influencers")\
                .delete()\
                .eq("id", influencer_id)\
                .execute()
            
            return {"success": True, "message": "인플루언서가 삭제되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"인플루언서 삭제 중 오류가 발생했습니다: {str(e)}"}
    
    # 캠페인-인플루언서 연결 관련 메서드
    def assign_influencer_to_campaign(self, campaign_id: str, influencer_id: str) -> Dict[str, Any]:
        """캠페인에 인플루언서 할당"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            # 로그인하지 않은 경우 임시 사용자 ID 사용
            if not user_id:
                user_id = self.get_or_create_anonymous_user_id()
            
            assignment_data = {
                "campaign_id": campaign_id,
                "influencer_id": influencer_id,
                "status": "assigned"
            }
            
            response = client.table("campaign_influencers")\
                .insert(assignment_data)\
                .execute()
            
            return {"success": True, "data": response.data, "message": "인플루언서가 할당되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"인플루언서 할당 중 오류가 발생했습니다: {str(e)}"}
    
    def get_campaign_influencers(self, campaign_id: str) -> List[Dict[str, Any]]:
        """캠페인에 할당된 인플루언서 목록 조회"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            if not user_id:
                return []
            
            response = client.table("campaign_influencers")\
                .select("""
                    *,
                    influencers (
                        id,
                        platform,
                        sns_id,
                        display_name,
                        follower_count,
                        engagement_rate
                    )
                """)\
                .eq("campaign_id", campaign_id)\
                .execute()
            
            # 데이터 구조 정리
            result = []
            for item in response.data:
                if item.get('influencers'):
                    influencer_data = item['influencers']
                    result.append({
                        'id': item['id'],
                        'campaign_id': item['campaign_id'],
                        'influencer_id': item['influencer_id'],
                        'status': item['status'],
                        'final_output_url': item['final_output_url'],
                        'notes': item['notes'],
                        'assigned_at': item['assigned_at'],
                        'completed_at': item['completed_at'],
                        'platform': influencer_data['platform'],
                        'sns_id': influencer_data['sns_id'],
                        'display_name': influencer_data['display_name'],
                        'follower_count': influencer_data['follower_count'],
                        'engagement_rate': influencer_data['engagement_rate']
                    })
            
            return result
        except Exception as e:
            st.error(f"캠페인 인플루언서 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    # 캠페인 참여 관리 관련 메서드
    def add_influencer_to_campaign(self, participation) -> Dict[str, Any]:
        """캠페인에 인플루언서 참여 추가"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            # 로그인하지 않은 경우 임시 사용자 ID 사용
            if not user_id:
                user_id = self.get_or_create_anonymous_user_id()
            
            # 디버깅 로그
            print(f"DEBUG - add_influencer_to_campaign: user_id = {user_id}")
            print(f"DEBUG - campaign_id = {participation.campaign_id}")
            print(f"DEBUG - influencer_id = {participation.influencer_id}")
            
            participation_data = {
                "campaign_id": participation.campaign_id,
                "influencer_id": participation.influencer_id,
                "manager_comment": participation.manager_comment,
                "influencer_requests": participation.influencer_requests,
                "memo": participation.memo,
                "sample_status": participation.sample_status,
                "influencer_feedback": participation.influencer_feedback,
                "content_uploaded": participation.content_uploaded,
                "cost_krw": participation.cost_krw,
                "content_links": participation.content_links,
                "created_by": user_id
            }
            
            print(f"DEBUG - participation_data = {participation_data}")
            
            response = client.table("campaign_influencer_participations")\
                .insert(participation_data)\
                .execute()
            
            print(f"DEBUG - Insert response: {response.data}")
            
            return {"success": True, "data": response.data, "message": "인플루언서가 캠페인에 참여로 추가되었습니다."}
        except Exception as e:
            print(f"DEBUG - Exception in add_influencer_to_campaign: {e}")
            return {"success": False, "message": f"인플루언서 참여 추가 중 오류가 발생했습니다: {str(e)}"}
    
    def get_campaign_participations(self, campaign_id: str) -> List[Dict[str, Any]]:
        """캠페인 참여 인플루언서 목록 조회"""
        try:
            client = self.get_client()
            
            response = client.table("campaign_influencer_participations")\
                .select("""
                    *,
                    connecta_influencers (
                        id,
                        platform,
                        sns_id,
                        influencer_name,
                        followers_count,
                        post_count,
                        profile_image_url
                    )
                """)\
                .eq("campaign_id", campaign_id)\
                .execute()
            
            # 데이터 구조 정리
            result = []
            for item in response.data:
                if item.get('connecta_influencers'):
                    influencer_data = item['connecta_influencers']
                    result.append({
                        'id': item['id'],
                        'campaign_id': item['campaign_id'],
                        'influencer_id': item['influencer_id'],
                        'manager_comment': item['manager_comment'],
                        'influencer_requests': item['influencer_requests'],
                        'memo': item['memo'],
                        'sample_status': item['sample_status'],
                        'influencer_feedback': item['influencer_feedback'],
                        'content_uploaded': item['content_uploaded'],
                        'cost_krw': item['cost_krw'],
                        'content_links': item['content_links'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at'],
                        'platform': influencer_data['platform'],
                        'sns_id': influencer_data['sns_id'],
                        'influencer_name': influencer_data['influencer_name'],
                        'followers_count': influencer_data['followers_count'],
                        'post_count': influencer_data['post_count'],
                        'profile_image_url': influencer_data['profile_image_url']
                    })
            
            return result
        except Exception as e:
            st.error(f"캠페인 참여자 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    def update_campaign_participation(self, participation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 참여 정보 업데이트"""
        try:
            client = self.get_client()
            
            response = client.table("campaign_influencer_participations")\
                .update(updates)\
                .eq("id", participation_id)\
                .execute()
            
            return {"success": True, "data": response.data, "message": "참여 정보가 업데이트되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"참여 정보 업데이트 중 오류가 발생했습니다: {str(e)}"}
    
    def remove_influencer_from_campaign(self, participation_id: str) -> Dict[str, Any]:
        """캠페인에서 인플루언서 참여 제거"""
        try:
            client = self.get_client()
            
            response = client.table("campaign_influencer_participations")\
                .delete()\
                .eq("id", participation_id)\
                .execute()
            
            return {"success": True, "message": "인플루언서 참여가 제거되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"참여 제거 중 오류가 발생했습니다: {str(e)}"}

    # 성과 관리 관련 메서드
    def create_performance_metric(self, metric) -> Dict[str, Any]:
        """성과 지표 생성 (campaign_influencer_contents 테이블 사용)"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            # 로그인하지 않은 경우 임시 사용자 ID 사용
            if not user_id:
                user_id = self.get_or_create_anonymous_user_id()
            
            # campaign_influencer_contents 테이블에 데이터 삽입
            content_data = {
                "participation_id": metric.participation_id,
                "content_url": metric.content_link,
                "likes": metric.metric_value if metric.metric_type == 'likes' else 0,
                "comments": metric.metric_value if metric.metric_type == 'comments' else 0,
                "views": metric.metric_value if metric.metric_type == 'views' else 0,
                "shares": metric.metric_value if metric.metric_type == 'shares' else 0,
                "clicks": metric.metric_value if metric.metric_type == 'clicks' else 0,
                "conversions": metric.metric_value if metric.metric_type == 'conversions' else 0,
                "qualitative_note": metric.qualitative_evaluation,
                "posted_at": metric.measurement_date.isoformat() if metric.measurement_date else None
            }
            
            response = client.table("campaign_influencer_contents")\
                .insert(content_data)\
                .execute()
            
            return {"success": True, "data": response.data, "message": "성과 지표가 저장되었습니다."}
        except Exception as e:
            return {"success": False, "message": f"성과 지표 저장 중 오류가 발생했습니다: {str(e)}"}
    
    def get_performance_metrics(self, campaign_id: str, influencer_id: str) -> List[Dict[str, Any]]:
        """성과 지표 조회"""
        try:
            client = self.get_client()
            user_id = self.get_current_user_id()
            
            if not user_id:
                return []
            
            response = client.table("performance_metrics")\
                .select("*")\
                .eq("campaign_id", campaign_id)\
                .eq("influencer_id", influencer_id)\
                .order("measurement_date", desc=True)\
                .execute()
            
            return response.data
        except Exception as e:
            st.error(f"성과 지표 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    def get_campaign_influencer_contents(self, participation_id: str) -> List[Dict[str, Any]]:
        """캠페인 인플루언서 컨텐츠 성과 조회"""
        try:
            client = self.get_client()
            
            # campaign_influencer_contents 테이블에서 해당 participation_id의 성과 데이터 조회
            response = client.table("campaign_influencer_contents")\
                .select("*")\
                .eq("participation_id", participation_id)\
                .execute()
            
            return response.data
        except Exception as e:
            st.error(f"컨텐츠 성과 조회 중 오류가 발생했습니다: {str(e)}")
            return []
    
    # 인플루언서 크롤링 관련 메서드
    def check_influencer_exists(self, platform: str, sns_id: str) -> Optional[Dict[str, Any]]:
        """인플루언서가 데이터베이스에 존재하는지 확인 - connecta_influencers 테이블 사용"""
        try:
            client = self.get_client()
            
            # connecta_influencers 테이블에서 sns_id로만 검색
            response = client.table("connecta_influencers")\
                .select("*")\
                .eq("platform", platform)\
                .eq("sns_id", sns_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"인플루언서 존재 확인 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def update_influencer_data(self, influencer_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """인플루언서 데이터 업데이트 - 크롤링 기능이 제거되었습니다."""
        return {"success": False, "message": "크롤링 기능이 제거되었습니다."}
    
    def create_influencer_from_crawl(self, platform: str, sns_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """크롤링 결과로부터 인플루언서 생성 - 크롤링 기능이 제거되었습니다."""
        return {"success": False, "message": "크롤링 기능이 제거되었습니다."}
    
    def save_crawl_raw_data(self, influencer_id: str, platform: str, sns_id: str, 
                           page_source: str, profile_data: Dict[str, Any], 
                           debug_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """크롤링 원시 데이터 저장 - 크롤링 기능이 제거되었습니다."""
        return {"success": False, "message": "크롤링 기능이 제거되었습니다."}
    
    def _extract_meaningful_content(self, page_source: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """HTML에서 유효한 정보만 추출 - 크롤링 기능이 제거되었습니다."""
        return {"error": "크롤링 기능이 제거되었습니다."}
    
    def get_influencer_info(self, platform: str, sns_id: str) -> Dict[str, Any]:
        """인플루언서 정보 조회 (DB 확인용) - connecta_influencers 테이블 사용"""
        try:
            client = self.get_client()
            
            # 디버깅 정보
            debug_info = {
                "platform": platform,
                "sns_id": sns_id,
                "table": "connecta_influencers"
            }
            
            # connecta_influencers 테이블에서 sns_id로만 검색
            # 먼저 정확한 매칭 시도
            response = client.table("connecta_influencers")\
                .select("id, sns_id, influencer_name, content_category, followers_count, post_count, profile_text, profile_image_url, sns_url, kakao_channel_id, created_at")\
                .eq("platform", platform)\
                .eq("sns_id", sns_id)\
                .execute()
            
            # 정확한 매칭이 실패하면 대소문자 구분 없이 검색
            if not response.data:
                all_influencers = client.table("connecta_influencers")\
                    .select("id, sns_id, influencer_name, content_category, followers_count, post_count, profile_text, profile_image_url, sns_url, kakao_channel_id, created_at")\
                    .eq("platform", platform)\
                    .execute()
                
                # 대소문자 구분 없이 매칭
                for inf in all_influencers.data:
                    if inf.get("sns_id", "").lower() == sns_id.lower():
                        response.data = [inf]
                        break
            
            debug_info["query_conditions"] = f"platform={platform}, sns_id={sns_id}"
            debug_info["case_insensitive_search"] = True
            debug_info["response_count"] = len(response.data) if response.data else 0
            debug_info["response_data"] = response.data
            
            # 모든 인플루언서 조회 (디버깅용)
            all_influencers = client.table("connecta_influencers")\
                .select("id, sns_id, influencer_name, platform")\
                .eq("platform", platform)\
                .execute()
            
            debug_info["all_influencers"] = all_influencers.data
            
            if response.data:
                influencer = response.data[0]
                return {
                    "success": True,
                    "exists": True,
                    "data": {
                        "id": influencer["id"],
                        "sns_id": influencer["sns_id"],
                        "influencer_name": influencer.get("influencer_name", ""),
                        "content_category": influencer.get("content_category", "일반"),
                        "followers_count": influencer.get("followers_count", 0),
                        "post_count": influencer.get("post_count", 0),
                        "profile_text": influencer.get("profile_text", ""),
                        "profile_image_url": influencer.get("profile_image_url", ""),
                        "sns_url": influencer.get("sns_url", ""),
                        "kakao_channel_id": influencer.get("kakao_channel_id", ""),
                        "created_at": influencer.get("created_at", "")
                    },
                    "message": "인플루언서 정보를 찾았습니다.",
                    "debug_info": debug_info
                }
            else:
                return {
                    "success": True,
                    "exists": False,
                    "data": None,
                    "message": f"데이터베이스에 해당 인플루언서가 없습니다. (디버그: {debug_info})",
                    "debug_info": debug_info
                }
        except Exception as e:
            return {
                "success": False,
                "exists": False,
                "data": None,
                "message": f"인플루언서 정보 조회 중 오류가 발생했습니다: {str(e)}",
                "debug_info": {"error": str(e), "platform": platform, "sns_id": sns_id}
            }

# 전역 인스턴스
db_manager = DatabaseManager()
