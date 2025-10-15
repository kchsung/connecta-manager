"""
공통으로 사용되는 함수들을 모아놓은 모듈
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager
from ..db.models import Campaign, Influencer, CampaignInfluencer, CampaignInfluencerParticipation, PerformanceMetric

def check_database_for_influencer(platform: str, sns_id: str) -> Dict[str, Any]:
    """데이터베이스에서 인플루언서 정보 확인"""
    try:
        # SNS ID에서 @ 제거
        clean_sns_id = sns_id.replace('@', '') if sns_id else ''
        
        # 데이터베이스에서 인플루언서 정보 조회
        result = db_manager.get_influencer_info(platform, clean_sns_id)
        
        if result["success"] and result["exists"]:
            return {
                "success": True,
                "exists": True,
                "data": result["data"],
                "message": f"✅ 데이터베이스에서 인플루언서를 찾았습니다: {result['data']['influencer_name'] or clean_sns_id}"
            }
        else:
            return {
                "success": True,
                "exists": False,
                "data": None,
                "message": "❌ 데이터베이스에 해당 인플루언서가 없습니다."
            }
    except Exception as e:
        return {
            "success": False,
            "exists": False,
            "data": None,
            "message": f"❌ DB 확인 중 오류가 발생했습니다: {str(e)}"
        }

def perform_crawling(platform: str, url: str, sns_id: str, debug_mode: bool, save_to_db: bool) -> Dict[str, Any]:
    """크롤링 기능이 제거되었습니다."""
    return {
        "success": False,
        "message": "크롤링 기능이 제거되었습니다.",
        "data": None
    }

def search_single_influencer(search_term: str):
    """단일 인플루언서 검색 - 개선된 검색 로직 (전체 플랫폼)"""
    try:
        if not search_term or not search_term.strip():
            return {
                "success": False,
                "message": "검색어를 입력해주세요.",
                "data": None
            }
        
        # Supabase에서 직접 검색 (페이징 없이)
        simple_client_instance = db_manager.get_client()
        client = simple_client_instance.get_client()
        
        if not client:
            return {
                "success": False,
                "message": "데이터베이스 연결에 실패했습니다.",
                "data": None
            }
        
        # 서버 코드와 동일한 검색 로직 사용
        search_response = client.table("connecta_influencers")\
            .select("*")\
            .order("created_at", desc=True)\
            .or_(f"influencer_name.ilike.%{search_term}%,sns_id.ilike.%{search_term}%")\
            .execute()
        
        if search_response.data:
            return {
                "success": True,
                "message": f"✅ 검색 결과: {len(search_response.data)}명의 인플루언서를 찾았습니다.",
                "data": search_response.data
            }
        
        return {
            "success": True,
            "message": "❌ 검색 결과가 없습니다.",
            "data": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 검색 중 오류가 발생했습니다: {str(e)}",
            "data": None
        }

def search_single_influencer_by_platform(search_term: str, platform: str):
    """특정 플랫폼에서 단일 인플루언서 검색"""
    try:
        if not search_term or not search_term.strip():
            return {
                "success": False,
                "message": "검색어를 입력해주세요.",
                "data": None
            }
        
        # Supabase에서 직접 검색 (특정 플랫폼)
        simple_client_instance = db_manager.get_client()
        client = simple_client_instance.get_client()
        
        if not client:
            return {
                "success": False,
                "message": "데이터베이스 연결에 실패했습니다.",
                "data": None
            }
        
        # 서버 코드와 동일한 검색 로직 사용 (플랫폼 필터 포함)
        search_response = client.table("connecta_influencers")\
            .select("*")\
            .order("created_at", desc=True)\
            .eq("platform", platform)\
            .or_(f"influencer_name.ilike.%{search_term}%,sns_id.ilike.%{search_term}%")\
            .execute()
        
        if search_response.data:
            return {
                "success": True,
                "message": f"✅ {platform}에서 {len(search_response.data)}명의 인플루언서를 찾았습니다.",
                "data": search_response.data
            }
        
        return {
            "success": True,
            "message": f"❌ {platform}에서 검색 결과가 없습니다.",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 검색 중 오류가 발생했습니다: {str(e)}",
            "data": None
        }

def render_influencer_info_inline(influencer):
    """인라인 인플루언서 정보 표시 (폼 내에서 사용)"""
    # 정보 카드 형태로 표시 (이미지 제거로 전체 폭 사용)
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"**이름:** {influencer.get('influencer_name') or 'N/A'}")
        st.markdown(f"**플랫폼:** {influencer.get('platform', 'N/A')}")
        st.markdown(f"**SNS ID:** {influencer.get('sns_id', 'N/A')}")
    
    with col2:
        st.markdown(f"**팔로워:** {influencer.get('followers_count', 0):,}명")
        st.markdown(f"**카테고리:** {influencer.get('content_category', 'N/A')}")
        contact_method = influencer.get('contact_method', 'N/A')
        contacts_method_etc = influencer.get('contacts_method_etc', '')
        if contact_method == 'other' and contacts_method_etc:
            st.markdown(f"**연락방법:** 기타 ({contacts_method_etc})")
        else:
            st.markdown(f"**연락방법:** {contact_method}")
    
    with col3:
        st.markdown(f"**평점:** {influencer.get('manager_rating', 'N/A')}/5")
        st.markdown(f"**활성:** {'✅' if influencer.get('active', True) else '❌'}")
        st.markdown(f"**등록일:** {influencer.get('created_at', 'N/A')}")

def format_campaign_type(campaign_type: str) -> str:
    """캠페인 타입을 한글로 변환"""
    type_mapping = {
        "seeding": "🌱 시딩",
        "promotion": "📢 홍보", 
        "sales": "💰 판매"
    }
    return type_mapping.get(campaign_type, campaign_type)

def format_campaign_status(status) -> str:
    """캠페인 상태를 한글로 변환"""
    if status is None:
        return "📋 계획"  # 기본값
    
    status_mapping = {
        "planned": "📋 계획",
        "active": "🟢 진행중",
        "paused": "⏸️ 일시정지",
        "completed": "✅ 완료",
        "cancelled": "❌ 취소"
    }
    return status_mapping.get(str(status), str(status))

def format_participation_status(status) -> str:
    """참여 상태를 한글로 변환"""
    if status is None:
        return "📋 배정"  # 기본값
    
    status_mapping = {
        "assigned": "📋 배정",
        "in_progress": "🟢 진행중",
        "completed": "✅ 완료",
        "cancelled": "❌ 취소"
    }
    return status_mapping.get(str(status), str(status))

def format_sample_status(status) -> str:
    """샘플 상태를 한글로 변환"""
    if status is None:
        return "📋 요청"  # 기본값
    
    status_mapping = {
        "요청": "📋 요청",
        "발송준비": "📦 발송준비",
        "발송완료": "🚚 발송완료",
        "수령": "✅ 수령"
    }
    return status_mapping.get(str(status), str(status))

def get_platform_emoji(platform: str) -> str:
    """플랫폼별 이모지 반환"""
    platform_emojis = {
        "instagram": "📷",
        "youtube": "📺",
        "tiktok": "🎵",
        "twitter": "🐦"
    }
    return platform_emojis.get(platform, "📱")

def validate_campaign_data(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """캠페인 데이터 유효성 검사"""
    errors = []
    
    if not campaign_data.get('campaign_name'):
        errors.append("캠페인 이름은 필수입니다.")
    
    if not campaign_data.get('campaign_type'):
        errors.append("캠페인 유형은 필수입니다.")
    
    if not campaign_data.get('start_date'):
        errors.append("시작 날짜는 필수입니다.")
    
    if campaign_data.get('end_date') and campaign_data.get('start_date'):
        if campaign_data['end_date'] < campaign_data['start_date']:
            errors.append("종료 날짜는 시작 날짜보다 늦어야 합니다.")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_influencer_data(influencer_data: Dict[str, Any]) -> Dict[str, Any]:
    """인플루언서 데이터 유효성 검사"""
    errors = []
    
    if not influencer_data.get('platform'):
        errors.append("플랫폼은 필수입니다.")
    
    if not influencer_data.get('sns_id'):
        errors.append("SNS ID는 필수입니다.")
    
    if not influencer_data.get('content_category'):
        errors.append("콘텐츠 카테고리는 필수입니다.")
    
    if influencer_data.get('manager_rating') and not (1 <= influencer_data['manager_rating'] <= 5):
        errors.append("매니저 평점은 1-5 사이여야 합니다.")
    
    if influencer_data.get('content_rating') and not (1 <= influencer_data['content_rating'] <= 5):
        errors.append("콘텐츠 평점은 1-5 사이여야 합니다.")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def format_number_with_comma(number: int) -> str:
    """숫자를 콤마가 포함된 문자열로 변환"""
    if number is None:
        return "0"
    return f"{number:,}"

def get_date_range_options():
    """날짜 범위 옵션 반환"""
    return {
        "전체": None,
        "오늘": 0,
        "최근 7일": 7,
        "최근 30일": 30,
        "최근 90일": 90,
        "최근 1년": 365
    }

def calculate_date_range(days: Optional[int]) -> tuple:
    """날짜 범위 계산"""
    if days is None:
        return None, None
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def show_success_message(message: str):
    """성공 메시지 표시"""
    st.success(message)

def show_error_message(message: str):
    """에러 메시지 표시"""
    st.error(message)

def show_warning_message(message: str):
    """경고 메시지 표시"""
    st.warning(message)

def show_info_message(message: str):
    """정보 메시지 표시"""
    st.info(message)
