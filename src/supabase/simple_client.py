import streamlit as st
import os
from typing import Dict, Any, List, Optional
from .config import supabase_config

class SimpleSupabaseClient:
    """간단한 Supabase 클라이언트 (인증 상태 확인 포함)"""
    
    def __init__(self):
        self.client = None
    
    def get_client(self):
        """Supabase 클라이언트 반환 (인증 상태 확인)"""
        try:
            # 일반 모드: 기본 클라이언트 사용 (RLS 정책 적용)
            client = supabase_config.get_client()
            
            return client
        except Exception as e:
            st.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            return None
    
    def _set_dev_user_session(self, client):
        """개발 모드에서 가상 사용자 세션 설정 (anon key 사용)"""
        try:
            # 개발 모드용 가상 사용자 정보
            dev_user_id = "dev-user-123"
            dev_email = "dev@example.com"
            
            self._debug_print(f"🔧 개발 모드: anon key 사용하여 가상 사용자 세션 설정")
            
            # session_state에 가상 사용자 정보 설정
            st.session_state.user = {
                "id": dev_user_id,
                "email": dev_email
            }
            
            # anon key를 사용하므로 RLS 정책이 적용됨
            # 하지만 개발 모드에서는 가상 사용자로 데이터 접근
            self._debug_print(f"✅ 개발 모드: 가상 사용자 세션 설정 완료 ({dev_user_id})")
            
        except Exception as e:
            self._debug_print(f"❌ 개발 모드 세션 설정 실패: {e}")
    
    def _get_service_role_client(self):
        """Service Role Key를 사용한 클라이언트 (RLS 우회) - 사용하지 않음"""
        # 이 메서드는 더 이상 사용하지 않음 (RLS 정책을 적용하기 위해)
        pass
    
    def _is_dev_mode(self) -> bool:
        """개발 모드 체크 공통 함수"""
        return (
            os.getenv("DEV_MODE", "false").lower() == "true" or
            st.session_state.get("dev_mode", False) or
            st.secrets.get("dev_mode", False)
        )
    
    def _debug_print(self, message: str):
        """개발 모드일 때만 디버깅 메시지 출력"""
        if self._is_dev_mode():
            print(message)
    
    def _handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """에러 처리 공통 함수"""
        error_msg = str(error)
        self._debug_print(f"데이터베이스 오류 ({operation}): {error_msg}")
        
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
            client = self.get_client()
            if not client:
                return []
            
            # 개발 모드일 때만 디버깅 메시지 표시
            self._debug_print("🔍 캠페인 조회 시도...")
            response = client.table("campaigns").select("*").execute()
            self._debug_print(f"✅ 캠페인 조회 성공: {len(response.data) if response.data else 0}개")
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
            
            # 개발 모드 체크
            is_dev_mode = (
                os.getenv("DEV_MODE", "false").lower() == "true" or
                st.session_state.get("dev_mode", False) or
                st.secrets.get("dev_mode", False)
            )
            
            # created_by 필드는 null로 설정하여 데이터베이스 기본값(auth.uid()) 사용
            # UUID 형식이 아닌 문자열을 전달하면 오류가 발생하므로 null 사용
            if "created_by" in campaign_data:
                del campaign_data["created_by"]  # 필드를 완전히 제거
            self._debug_print("🔧 created_by 필드를 제거하여 데이터베이스 기본값 사용")
            
            self._debug_print("🔍 캠페인 생성 시도...")
            response = client.table("campaigns").insert(campaign_data).execute()
            self._debug_print(f"✅ 캠페인 생성 성공: {response.data[0]['id'] if response.data else 'None'}")
            
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
            
            self._debug_print(f"🔍 캠페인 업데이트 시도: {campaign_id}")
            response = client.table("campaigns").update(update_data).eq("id", campaign_id).execute()
            self._debug_print(f"✅ 캠페인 업데이트 성공")
            
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
            
            self._debug_print(f"🔍 캠페인 삭제 시도: {campaign_id}")
            response = client.table("campaigns").delete().eq("id", campaign_id).execute()
            self._debug_print(f"✅ 캠페인 삭제 성공")
            
            return {
                "success": True,
                "message": "캠페인이 성공적으로 삭제되었습니다."
            }
        except Exception as e:
            return self._handle_error(e, "캠페인 삭제")
    
    # 인플루언서 관련 메서드들
    def get_influencers(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """인플루언서 목록 조회 (페이지네이션 적용)"""
        try:
            client = self.get_client()
            if not client:
                return []
            
            self._debug_print(f"🔍 인플루언서 조회 시도 (platform: {platform})")
            
            # 페이지네이션으로 모든 데이터 조회
            all_influencers = []
            page_size = 1000  # 한 번에 1000개씩 조회
            offset = 0
            
            while True:
                self._debug_print(f"  조회 중... offset: {offset}, limit: {page_size}")
                query = client.table("connecta_influencers").select("*")
                
                if platform:
                    query = query.eq("platform", platform)
                
                response = query.range(offset, offset + page_size - 1).execute()
                
                if not response.data or len(response.data) == 0:
                    break
                    
                all_influencers.extend(response.data)
                self._debug_print(f"  조회된 레코드: {len(response.data)}개 (총 누적: {len(all_influencers)}개)")
                
                # 마지막 페이지인지 확인
                if len(response.data) < page_size:
                    break
                    
                offset += page_size
            
            self._debug_print(f"✅ 인플루언서 조회 성공: 총 {len(all_influencers)}개")
            
            return all_influencers
        except Exception as e:
            self._handle_error(e, "인플루언서 조회")
            return []
    
    def get_influencer_info(self, platform: str, sns_id: str) -> Dict[str, Any]:
        """특정 인플루언서 정보 조회"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "exists": False}
            
            self._debug_print(f"🔍 인플루언서 정보 조회: {platform}/{sns_id}")
            response = client.table("connecta_influencers")\
                .select("*")\
                .eq("platform", platform)\
                .eq("sns_id", sns_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                self._debug_print(f"✅ 인플루언서 찾음: {response.data[0]['influencer_name']}")
                return {
                    "success": True,
                    "exists": True,
                    "data": response.data[0]
                }
            else:
                self._debug_print(f"❌ 인플루언서 없음: {platform}/{sns_id}")
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
            
            # 개발 모드 체크
            is_dev_mode = (
                os.getenv("DEV_MODE", "false").lower() == "true" or
                st.session_state.get("dev_mode", False) or
                st.secrets.get("dev_mode", False)
            )
            
            # created_by 필드는 모델에서 제거되어 데이터베이스 기본값(auth.uid()) 사용
            self._debug_print("🔧 created_by 필드는 모델에서 제거되어 데이터베이스 기본값 사용")
            
            self._debug_print(f"🔍 인플루언서 생성 시도: {influencer_data.get('sns_id')}")
            self._debug_print(f"🔍 전달되는 데이터: {influencer_data}")
            response = client.table("connecta_influencers").insert(influencer_data).execute()
            self._debug_print(f"✅ 인플루언서 생성 성공: {response.data[0]['id'] if response.data else 'None'}")
            
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
            
            self._debug_print(f"🔍 인플루언서 업데이트 시도: {influencer_id}")
            response = client.table("connecta_influencers").update(update_data).eq("id", influencer_id).execute()
            self._debug_print(f"✅ 인플루언서 업데이트 성공")
            
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
            
            self._debug_print(f"🔍 인플루언서 삭제 시도: {influencer_id}")
            response = client.table("connecta_influencers").delete().eq("id", influencer_id).execute()
            self._debug_print(f"✅ 인플루언서 삭제 성공")
            
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
            
            # 개발 모드 체크
            is_dev_mode = (
                os.getenv("DEV_MODE", "false").lower() == "true" or
                st.session_state.get("dev_mode", False) or
                st.secrets.get("dev_mode", False)
            )
            
            # 사용자 정보 설정 (로그인 없이 기본 사용자 사용)
            if is_dev_mode:
                # 개발 모드에서는 session_state에서 사용자 정보 가져오기
                if 'user' in st.session_state:
                    user = st.session_state.user
                    user_id = user.get('id', 'dev-user-123') if isinstance(user, dict) else user.id
                    user_email = user.get('email', 'dev@example.com') if isinstance(user, dict) else user.email
                    self._debug_print(f"🔧 개발 모드: 세션 사용자 정보 사용 ({user_id})")
                else:
                    user_id = "dev-user-123"
                    user_email = "dev@example.com"
                    self._debug_print("🔧 개발 모드: 기본 사용자 정보 사용")
            else:
                # 일반 모드: 기본 사용자 정보 사용
                user_id = "default-user-123"
                user_email = "default@example.com"
            
            self._debug_print("🔍 사용자 통계 조회 시도...")
            # 간단한 통계 조회
            campaigns_response = client.table("campaigns").select("id").eq("created_by", user_id).execute()
            influencers_response = client.table("connecta_influencers").select("id").eq("created_by", user_id).execute()
            
            stats = {
                "user_id": user_id,
                "email": user_email,
                "total_campaigns": len(campaigns_response.data) if campaigns_response.data else 0,
                "total_influencers": len(influencers_response.data) if influencers_response.data else 0
            }
            
            self._debug_print(f"✅ 사용자 통계 조회 성공: {stats}")
            return {
                "success": True,
                "data": stats
            }
        except Exception as e:
            return self._handle_error(e, "사용자 통계 조회")
    
    # 캠페인 참여 관련 메서드들
    def get_campaign_participations(self, campaign_id: str = None, participation_id: str = None) -> List[Dict[str, Any]]:
        """캠페인 참여 목록 조회"""
        try:
            client = self.get_client()
            if not client:
                return []
            
            # 직접 Supabase 클라이언트 사용 (Edge Function 우회)
            query = client.table('campaign_influencer_participations').select("""
                *,
                campaigns!inner(id, campaign_name, created_by),
                connecta_influencers!inner(id, influencer_name, sns_id, platform, followers_count, phone_number, shipping_address, email, kakao_channel_id)
            """)
            
            # 사용자 필터링 (RLS 정책 적용)
            if hasattr(self, '_get_current_user_id'):
                user_id = self._get_current_user_id()
                if user_id:
                    query = query.eq('campaigns.created_by', user_id)
            
            # 특정 참여 조회
            if participation_id:
                query = query.eq('id', participation_id)
            
            # 특정 캠페인의 참여자들 조회
            if campaign_id:
                query = query.eq('campaign_id', campaign_id)
            
            result = query.order('created_at', desc=True).execute()
            
            if result.data:
                # 데이터 구조 디버깅
                print(f"🔍 참여 데이터 구조 (첫 번째 항목): {result.data[0] if result.data else 'None'}")
                
                # 데이터 평면화
                flattened_data = []
                for item in result.data:
                    # sample_status 값은 이미 DB enum과 UI가 동일하므로 그대로 사용
                    db_sample_status = item.get('sample_status')
                    ui_sample_status = db_sample_status
                    
                    flattened_item = {
                        # 참여 기본 정보
                        'id': item.get('id'),
                        'campaign_id': item.get('campaign_id'),
                        'influencer_id': item.get('influencer_id'),
                        'manager_comment': item.get('manager_comment'),
                        'influencer_requests': item.get('influencer_requests'),
                        'memo': item.get('memo'),
                        'sample_status': ui_sample_status,  # UI 값으로 변환
                        'influencer_feedback': item.get('influencer_feedback'),
                        'content_uploaded': item.get('content_uploaded'),
                        'cost_krw': item.get('cost_krw'),
                        'content_links': item.get('content_links', []),
                        'created_by': item.get('created_by'),
                        'created_at': item.get('created_at'),
                        'updated_at': item.get('updated_at'),
                        
                        # 캠페인 정보 (평면화)
                        'campaign_name': item.get('campaigns', {}).get('campaign_name'),
                        
                        # 인플루언서 정보 (평면화)
                        'influencer_name': item.get('connecta_influencers', {}).get('influencer_name'),
                        'sns_id': item.get('connecta_influencers', {}).get('sns_id'),
                        'platform': item.get('connecta_influencers', {}).get('platform'),
                        'followers_count': item.get('connecta_influencers', {}).get('followers_count'),
                        'phone_number': item.get('connecta_influencers', {}).get('phone_number'),
                        'shipping_address': item.get('connecta_influencers', {}).get('shipping_address'),
                        'email': item.get('connecta_influencers', {}).get('email'),
                        'kakao_channel_id': item.get('connecta_influencers', {}).get('kakao_channel_id'),
                    }
                    flattened_data.append(flattened_item)
                
                return flattened_data
            else:
                return []
                
        except Exception as e:
            self._debug_print(f"❌ 참여 조회 오류: {str(e)}")
            return []
    
    def create_campaign_participation(self, participation_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 참여 생성"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            # 자동 생성되는 필드들 제거 (데이터베이스에서 자동 설정)
            auto_generated_fields = ['id', 'created_at', 'updated_at']
            for field in auto_generated_fields:
                if field in participation_data and (participation_data[field] is None or participation_data[field] == ''):
                    del participation_data[field]
            
            # sample_status 값 검증 (DB enum 값과 일치하는지 확인)
            if 'sample_status' in participation_data:
                valid_statuses = ['요청', '발송준비', '발송완료', '수령']
                original_status = participation_data['sample_status']
                if original_status not in valid_statuses:
                    participation_data['sample_status'] = '요청'  # 기본값
            
            # content_links가 빈 리스트인 경우 빈 배열로 설정
            if 'content_links' in participation_data and not participation_data['content_links']:
                participation_data['content_links'] = []
            
            # 직접 Supabase 클라이언트 사용 (Edge Function 우회)
            result = client.table('campaign_influencer_participations').insert([participation_data]).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "인플루언서가 캠페인에 성공적으로 추가되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": "참여 생성 실패"
                }
                
        except Exception as e:
            return self._handle_error(e, "참여 생성")
    
    def update_campaign_participation(self, participation_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 참여 업데이트"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            # 자동 생성되는 필드들 제거 (데이터베이스에서 자동 설정)
            auto_generated_fields = ['id', 'created_at', 'updated_at']
            for field in auto_generated_fields:
                if field in update_data:
                    del update_data[field]
            
            # sample_status 값 검증 (DB enum 값과 일치하는지 확인)
            if 'sample_status' in update_data:
                valid_statuses = ['요청', '발송준비', '발송완료', '수령']
                original_status = update_data['sample_status']
                if original_status not in valid_statuses:
                    update_data['sample_status'] = '요청'  # 기본값
            
            # content_links가 빈 리스트인 경우 빈 배열로 설정
            if 'content_links' in update_data and not update_data['content_links']:
                update_data['content_links'] = []
            
            # 직접 Supabase 클라이언트 사용 (Edge Function 우회)
            result = client.table('campaign_influencer_participations').update(update_data).eq('id', participation_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "참여 정보가 성공적으로 업데이트되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": "참여 업데이트 실패"
                }
                
        except Exception as e:
            return self._handle_error(e, "참여 업데이트")
    
    def delete_campaign_participation(self, participation_id: str) -> Dict[str, Any]:
        """캠페인 참여 삭제"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            # 직접 Supabase 클라이언트 사용 (Edge Function 우회)
            result = client.table('campaign_influencer_participations').delete().eq('id', participation_id).execute()
            
            return {
                "success": True,
                "message": "참여가 성공적으로 삭제되었습니다."
            }
                
        except Exception as e:
            return self._handle_error(e, "참여 삭제")
    
    # 캠페인 콘텐츠 관련 메서드들
    def get_campaign_influencer_contents(self, participation_id: str) -> List[Dict[str, Any]]:
        """캠페인 인플루언서 콘텐츠 조회"""
        try:
            client = self.get_client()
            if not client:
                return []
            
            self._debug_print(f"🔍 캠페인 콘텐츠 조회 시도: {participation_id}")
            
            # campaign_influencer_contents 테이블에서 조회
            response = client.table("campaign_influencer_contents")\
                .select("*")\
                .eq("participation_id", participation_id)\
                .order("created_at", desc=True)\
                .execute()
            
            if response.data:
                self._debug_print(f"✅ 캠페인 콘텐츠 조회 성공: {len(response.data)}개")
                return response.data
            else:
                self._debug_print("❌ 캠페인 콘텐츠 없음")
                return []
                
        except Exception as e:
            self._debug_print(f"❌ 캠페인 콘텐츠 조회 오류: {str(e)}")
            return []
    
    def create_campaign_influencer_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 인플루언서 콘텐츠 생성"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            self._debug_print(f"🔍 캠페인 콘텐츠 생성 시도: {content_data.get('content_url')}")
            
            # created_by 필드는 null로 설정하여 데이터베이스 기본값(auth.uid()) 사용
            if "created_by" in content_data:
                del content_data["created_by"]
            
            response = client.table("campaign_influencer_contents").insert(content_data).execute()
            
            if response.data:
                self._debug_print(f"✅ 캠페인 콘텐츠 생성 성공: {response.data[0]['id']}")
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": "콘텐츠가 성공적으로 추가되었습니다."
                }
            else:
                return {"success": False, "message": "콘텐츠 생성에 실패했습니다."}
                
        except Exception as e:
            return self._handle_error(e, "콘텐츠 생성")
    
    def update_campaign_influencer_content(self, content_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """캠페인 인플루언서 콘텐츠 업데이트"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            self._debug_print(f"🔍 캠페인 콘텐츠 업데이트 시도: {content_id}")
            
            response = client.table("campaign_influencer_contents").update(update_data).eq("id", content_id).execute()
            
            if response.data:
                self._debug_print(f"✅ 캠페인 콘텐츠 업데이트 성공")
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": "콘텐츠가 성공적으로 업데이트되었습니다."
                }
            else:
                return {"success": False, "message": "콘텐츠 업데이트에 실패했습니다."}
                
        except Exception as e:
            return self._handle_error(e, "콘텐츠 업데이트")
    
    def delete_campaign_influencer_content(self, content_id: str) -> Dict[str, Any]:
        """캠페인 인플루언서 콘텐츠 삭제"""
        try:
            client = self.get_client()
            if not client:
                return {"success": False, "message": "데이터베이스 연결 실패"}
            
            self._debug_print(f"🔍 캠페인 콘텐츠 삭제 시도: {content_id}")
            
            response = client.table("campaign_influencer_contents").delete().eq("id", content_id).execute()
            
            return {
                "success": True,
                "message": "콘텐츠가 성공적으로 삭제되었습니다."
            }
                
        except Exception as e:
            return self._handle_error(e, "콘텐츠 삭제")

# 전역 인스턴스
simple_client = SimpleSupabaseClient()
