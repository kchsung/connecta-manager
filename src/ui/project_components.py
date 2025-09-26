import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager
from ..db.models import Campaign, Influencer, CampaignInfluencer, CampaignInfluencerParticipation, PerformanceMetric
from ..supabase.auth import supabase_auth

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

def render_single_url_crawl():
    """단일 URL 크롤링 컴포넌트 - 크롤링 기능이 제거되었습니다."""
    st.subheader("🔍 단일 URL 크롤링")
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")

def render_batch_url_crawl():
    """복수 URL 크롤링 컴포넌트 - 크롤링 기능이 제거되었습니다."""
    st.subheader("📊 복수 URL 크롤링")
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")

def render_campaign_management():
    """캠페인 관리 컴포넌트"""
    st.subheader("📋 캠페인 관리")
    st.markdown("시딩, 홍보, 판매 캠페인을 생성하고 참여 인플루언서를 관리합니다.")
    
    # 탭으로 캠페인 관리와 참여 인플루언서 관리 구분
    tab1, tab2 = st.tabs(["📁 캠페인 관리", "👥 참여 인플루언서 관리"])
    
    with tab1:
        render_campaign_tab()
    
    with tab2:
        render_campaign_participation_tab()

def render_campaign_tab():
    """캠페인 탭"""
    st.subheader("📁 캠페인 관리")
    
    # 새 캠페인 생성
    with st.expander("➕ 새 캠페인 생성", expanded=True):
        with st.form("create_campaign_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                campaign_name = st.text_input("캠페인 이름", placeholder="예: 2024 봄 시즌 시딩")
                campaign_type = st.selectbox(
                    "캠페인 유형",
                    ["seeding", "promotion", "sales"],
                    key="create_campaign_type",
                    format_func=lambda x: {
                        "seeding": "🌱 시딩",
                        "promotion": "📢 홍보", 
                        "sales": "💰 판매"
                    }[x]
                )
                start_date = st.date_input("캠페인 시작날짜", value=datetime.now().date())
            
            with col2:
                campaign_description = st.text_area("캠페인 설명", placeholder="캠페인에 대한 상세 설명을 입력하세요")
                status = st.selectbox(
                    "캠페인 상태",
                    ["planned", "active", "paused", "completed", "canceled"],
                    key="create_campaign_status",
                    format_func=lambda x: {
                        "planned": "📅 계획됨",
                        "active": "🟢 진행중",
                        "paused": "⏸️ 일시정지",
                        "completed": "✅ 완료",
                        "canceled": "❌ 취소"
                    }[x]
                )
                end_date = st.date_input("캠페인 종료일", value=None)
            
            # 추가 필드들
            campaign_instructions = st.text_area("캠페인 지시사항", placeholder="인플루언서에게 전달할 구체적인 지시사항을 입력하세요")
            
            # 태그 입력
            tags_input = st.text_input("태그", placeholder="태그를 쉼표로 구분하여 입력하세요 (예: 봄시즌, 뷰티, 신제품)")
            # 태그 처리 - 빈 문자열이나 None인 경우 빈 문자열로 처리 (text 타입)
            if tags_input and tags_input.strip():
                tags = tags_input.strip()
            else:
                tags = ""
            
            if st.form_submit_button("캠페인 생성", type="primary"):
                if not campaign_name:
                    st.error("캠페인 이름을 입력해주세요.")
                elif not start_date:
                    st.error("캠페인 시작날짜를 선택해주세요.")
                elif end_date and end_date < start_date:
                    st.error("종료일은 시작일보다 늦어야 합니다.")
                else:
                    campaign = Campaign(
                        campaign_name=campaign_name,
                        campaign_description=campaign_description,
                        campaign_type=campaign_type,
                        start_date=start_date,
                        end_date=end_date,
                        status=status,
                        campaign_instructions=campaign_instructions,
                        tags=tags
                    )
                    
                    result = db_manager.create_campaign(campaign)
                    if result["success"]:
                        st.success("캠페인이 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error(f"캠페인 생성 실패: {result['message']}")
    
    # 기존 캠페인 목록
    st.subheader("📋 캠페인 목록")
    
    # 캠페인 목록
    
    # 필터링 옵션
    st.markdown("### 🔍 필터링 옵션")
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
    
    with filter_col1:
        # 캠페인 유형 필터
        campaign_type_filter = st.selectbox(
            "캠페인 유형",
            options=["전체", "seeding", "promotion", "sales"],
            index=0 if "campaign_type_filter" not in st.session_state else ["전체", "seeding", "promotion", "sales"].index(st.session_state.get("campaign_type_filter", "전체")),
            key="campaign_type_filter",
            help="캠페인 유형으로 필터링합니다"
        )
    
    with filter_col2:
        # 캠페인 상태 필터
        campaign_status_filter = st.selectbox(
            "캠페인 상태",
            options=["전체", "planned", "active", "paused", "completed", "canceled"],
            index=0 if "campaign_status_filter" not in st.session_state else ["전체", "planned", "active", "paused", "completed", "canceled"].index(st.session_state.get("campaign_status_filter", "전체")),
            key="campaign_status_filter",
            help="캠페인 상태로 필터링합니다"
        )
    
    with filter_col3:
        st.markdown("")  # 공간 확보
        st.markdown("")  # 공간 확보
        if st.button("🔄 새로고침", key="refresh_campaigns", help="캠페인 목록을 새로 불러옵니다"):
            st.rerun()
    
    # 모든 캠페인 조회 (생성자와 상관없이)
    campaigns = db_manager.get_campaigns()
    
    # 필터링 적용
    filtered_campaigns = campaigns
    if campaign_type_filter != "전체":
        filtered_campaigns = [c for c in filtered_campaigns if c['campaign_type'] == campaign_type_filter]
    
    if campaign_status_filter != "전체":
        filtered_campaigns = [c for c in filtered_campaigns if c['status'] == campaign_status_filter]
    
    if filtered_campaigns:
        # 필터링 결과 표시
        if len(filtered_campaigns) != len(campaigns):
            st.info(f"🔍 필터링 결과: {len(filtered_campaigns)}개 (전체 {len(campaigns)}개 중)")
        else:
            st.success(f"✅ {len(filtered_campaigns)}개의 캠페인을 찾았습니다.")
        
        for i, campaign in enumerate(filtered_campaigns):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{campaign['campaign_name']}**")
                    st.caption(f"유형: {campaign['campaign_type']} | 상태: {campaign['status']}")
                    st.caption(f"기간: {campaign['start_date']} ~ {campaign['end_date'] or '미정'}")
                    if campaign['campaign_description']:
                        st.caption(campaign['campaign_description'])
                    if campaign.get('campaign_instructions'):
                        st.caption(f"📋 지시사항: {campaign['campaign_instructions']}")
                    if campaign.get('tags') and campaign['tags'].strip():
                        st.caption(f"🏷️ 태그: {campaign['tags']}")
                
                with col2:
                    if st.button("✏️ 수정", key=f"edit_{campaign['id']}_{i}", help="캠페인 정보를 수정합니다"):
                        st.session_state[f"editing_campaign_{campaign['id']}"] = True
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ 삭제", key=f"delete_{campaign['id']}_{i}", help="캠페인을 삭제합니다"):
                        result = db_manager.delete_campaign(campaign['id'])
                        if result["success"]:
                            st.success("캠페인이 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.error(f"삭제 실패: {result['message']}")
                
                st.divider()
                
                # 캠페인 수정 폼 (수정 버튼이 클릭된 경우)
                if st.session_state.get(f"editing_campaign_{campaign['id']}", False):
                    render_campaign_edit_form(campaign)
    else:
        if campaigns:
            st.warning("🔍 선택한 필터 조건에 맞는 캠페인이 없습니다.")
        else:
            st.info("생성된 캠페인이 없습니다.")

def render_campaign_edit_form(campaign):
    """캠페인 수정 폼"""
    st.markdown("---")
    st.subheader(f"✏️ 캠페인 수정: {campaign['campaign_name']}")
    
    with st.form(f"edit_campaign_form_{campaign['id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 기존 값으로 폼 초기화
            campaign_name = st.text_input(
                "캠페인 이름", 
                value=campaign['campaign_name'],
                key=f"edit_name_{campaign['id']}"
            )
            
            campaign_type = st.selectbox(
                "캠페인 유형",
                ["seeding", "promotion", "sales"],
                index=["seeding", "promotion", "sales"].index(campaign['campaign_type']),
                key=f"edit_type_{campaign['id']}",
                format_func=lambda x: {
                    "seeding": "🌱 시딩",
                    "promotion": "📢 홍보", 
                    "sales": "💰 판매"
                }[x]
            )
            
            # 날짜 변환
            start_date = st.date_input(
                "캠페인 시작날짜", 
                value=datetime.strptime(campaign['start_date'], '%Y-%m-%d').date(),
                key=f"edit_start_{campaign['id']}"
            )
        
        with col2:
            campaign_description = st.text_area(
                "캠페인 설명", 
                value=campaign.get('campaign_description', ''),
                key=f"edit_desc_{campaign['id']}"
            )
            
            status = st.selectbox(
                "캠페인 상태",
                ["planned", "active", "paused", "completed", "canceled"],
                index=["planned", "active", "paused", "completed", "canceled"].index(campaign['status']),
                key=f"edit_status_{campaign['id']}",
                format_func=lambda x: {
                    "planned": "📅 계획됨",
                    "active": "🟢 진행중",
                    "paused": "⏸️ 일시정지",
                    "completed": "✅ 완료",
                    "canceled": "❌ 취소"
                }[x]
            )
            
            # 종료일 처리
            end_date_value = None
            if campaign.get('end_date'):
                end_date_value = datetime.strptime(campaign['end_date'], '%Y-%m-%d').date()
            
            end_date = st.date_input(
                "캠페인 종료일", 
                value=end_date_value,
                key=f"edit_end_{campaign['id']}"
            )
        
        # 추가 필드들
        campaign_instructions = st.text_area(
            "캠페인 지시사항", 
            value=campaign.get('campaign_instructions', ''),
            key=f"edit_instructions_{campaign['id']}"
        )
        
        # 태그 처리
        tags_input = st.text_input(
            "태그", 
            value=campaign.get('tags', '') if campaign.get('tags') else "",
            key=f"edit_tags_{campaign['id']}",
            placeholder="태그를 쉼표로 구분하여 입력하세요 (예: 봄시즌, 뷰티, 신제품)"
        )
        # 태그 처리 - 빈 문자열이나 None인 경우 빈 문자열로 처리
        if tags_input and tags_input.strip():
            tags = tags_input.strip()
        else:
            tags = ""
        
        # 버튼들
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.form_submit_button("💾 수정하기", type="primary"):
                if not campaign_name:
                    st.error("캠페인 이름을 입력해주세요.")
                elif not start_date:
                    st.error("캠페인 시작날짜를 선택해주세요.")
                elif end_date and end_date < start_date:
                    st.error("종료일은 시작일보다 늦어야 합니다.")
                else:
                    # 캠페인 데이터 준비
                    update_data = {
                        "campaign_name": campaign_name,
                        "campaign_description": campaign_description,
                        "campaign_type": campaign_type,
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d') if end_date else None,
                        "status": status,
                        "campaign_instructions": campaign_instructions,
                        "tags": tags
                    }
                    
                    result = db_manager.update_campaign(campaign['id'], update_data)
                    if result["success"]:
                        st.success("캠페인이 수정되었습니다!")
                        # 수정 모드 종료
                        st.session_state[f"editing_campaign_{campaign['id']}"] = False
                        st.rerun()
                    else:
                        st.error(f"캠페인 수정 실패: {result['message']}")
        
        with col2:
            if st.form_submit_button("❌ 취소"):
                # 수정 모드 종료
                st.session_state[f"editing_campaign_{campaign['id']}"] = False
                st.rerun()
    
    st.markdown("---")

def render_add_influencer_workflow(campaign_id):
    """인플루언서 추가 워크플로우 (검색 → 정보 확인 → 추가)"""
    st.subheader("➕ 인플루언서 추가")
    
    # 1단계: 인플루언서 검색 (별도 폼)
    st.markdown("### 1️⃣ 인플루언서 검색")
    with st.form("search_influencer_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            platform = st.selectbox(
                "플랫폼",
                ["instagram", "youtube", "tiktok", "twitter"],
                key="search_platform",
                format_func=lambda x: {
                    "instagram": "📸 Instagram",
                    "youtube": "📺 YouTube",
                    "tiktok": "🎵 TikTok",
                    "twitter": "🐦 Twitter"
                }[x]
            )
        
        with col2:
            sns_id = st.text_input("SNS ID", placeholder="@username 또는 username", key="search_sns_id")
        
        search_clicked = st.form_submit_button("🔍 인플루언서 검색", type="primary")
    
    # 검색 결과 처리
    selected_influencer = None
    if search_clicked:
        if not sns_id:
            st.error("SNS ID를 입력해주세요.")
        else:
            # SNS ID에서 @ 제거
            clean_sns_id = sns_id.replace('@', '')
            
            # 인플루언서 검색
            influencer_info = db_manager.get_influencer_info(platform, clean_sns_id)
            
            if influencer_info["success"] and influencer_info["exists"]:
                selected_influencer = influencer_info["data"]
                st.session_state["selected_influencer_for_campaign"] = selected_influencer
                st.success("인플루언서를 찾았습니다!")
                st.rerun()
            else:
                st.error("해당 인플루언서를 찾을 수 없습니다. 먼저 인플루언서를 등록해주세요.")
    
    # 세션에서 선택된 인플루언서 가져오기
    if "selected_influencer_for_campaign" in st.session_state:
        selected_influencer = st.session_state["selected_influencer_for_campaign"]
    
    # 2단계: 검색된 인플루언서 정보 표시
    if selected_influencer:
        st.markdown("### 2️⃣ 인플루언서 정보 확인")
        render_influencer_info_inline(selected_influencer)
        
        # 3단계: 담당자 의견 및 비용 입력 (별도 폼)
        st.markdown("### 3️⃣ 담당자 의견 및 비용 입력")
        with st.form("add_influencer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                manager_comment = st.text_area(
                    "담당자 의견", 
                    placeholder="인플루언서에 대한 담당자 메모나 지시사항을 입력하세요",
                    key="manager_comment_input"
                )
                
                influencer_requests = st.text_area(
                    "인플루언서 요청사항", 
                    placeholder="인플루언서에게 전달할 요청사항을 입력하세요",
                    key="influencer_requests_input"
                )
            
            with col2:
                cost_krw = st.number_input(
                    "비용 (원)", 
                    min_value=0, 
                    value=0, 
                    step=1000,
                    key="cost_input",
                    help="인플루언서에게 지급할 비용을 입력하세요"
                )
                
                sample_status = st.selectbox(
                    "샘플 상태",
                    ["요청", "발송준비", "발송완료", "수령"],
                    key="sample_status_input",
                    help="샘플 발송 상태를 선택하세요"
                )
                
                memo = st.text_area(
                    "메모", 
                    placeholder="추가 메모사항을 입력하세요",
                    key="memo_input"
                )
            
            # 버튼들
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.form_submit_button("✅ 인플루언서 추가", type="primary"):
                    # 디버깅 정보
                    st.write("🔍 디버깅 정보:")
                    st.write(f"- Campaign ID: {campaign_id}")
                    st.write(f"- Influencer ID: {selected_influencer['id']}")
                    st.write(f"- Manager Comment: {manager_comment}")
                    st.write(f"- Cost: {cost_krw}")
                    
                    # 참여 데이터 생성
                    participation = CampaignInfluencerParticipation(
                        campaign_id=campaign_id,
                        influencer_id=selected_influencer["id"],
                        manager_comment=manager_comment,
                        influencer_requests=influencer_requests,
                        memo=memo,
                        sample_status=sample_status,
                        cost_krw=cost_krw
                    )
                    
                    st.write("📝 Participation 객체 생성 완료")
                    
                    result = db_manager.add_influencer_to_campaign(participation)
                    
                    st.write(f"📊 DB 결과: {result}")
                    
                    if result["success"]:
                        st.success("인플루언서가 캠페인에 추가되었습니다!")
                        # 세션 정리
                        if "selected_influencer_for_campaign" in st.session_state:
                            del st.session_state["selected_influencer_for_campaign"]
                        st.rerun()
                    else:
                        st.error(f"추가 실패: {result['message']}")
            
            with col2:
                if st.form_submit_button("❌ 취소"):
                    # 세션 정리
                    if "selected_influencer_for_campaign" in st.session_state:
                        del st.session_state["selected_influencer_for_campaign"]
                    st.rerun()

def render_influencer_info_inline(influencer):
    """인라인 인플루언서 정보 표시 (폼 내에서 사용)"""
    # 정보 카드 형태로 표시
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 프로필 이미지 (가운데 정렬)
        profile_image_url = influencer.get('profile_image_url')
        if profile_image_url and profile_image_url.strip():
            try:
                # CSS를 사용하여 이미지 가운데 정렬
                st.markdown("""
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
                    <img src="{}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 50%; border: 2px solid #e0e0e0;">
                </div>
                """.format(profile_image_url), unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; font-size: 0.8em; color: #666;'>프로필 이미지</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"프로필 이미지를 불러올 수 없습니다: {profile_image_url}")
        else:
            # 프로필 이미지가 없을 때도 가운데 정렬
            st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
                <div style="width: 150px; height: 150px; background-color: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #e0e0e0;">
                    <span style="color: #999; font-size: 0.9em;">이미지 없음</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; font-size: 0.8em; color: #666;'>프로필 이미지</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**📱 SNS ID:** `{influencer['sns_id']}`")
        st.markdown(f"**👤 인플루언서 이름:** {influencer.get('influencer_name', 'N/A')}")
        st.markdown(f"**🌐 SNS URL:** {influencer.get('sns_url', 'N/A')}")
        st.markdown(f"**👥 팔로워 수:** {influencer.get('followers_count', 0):,}")
        st.markdown(f"**💬 카카오 채널 ID:** {influencer.get('kakao_channel_id', 'N/A')}")
        
        # 프로필 텍스트 (멀티라인으로 표시)
        profile_text = influencer.get('profile_text')
        if profile_text and profile_text.strip():
            st.markdown("**📝 프로필 텍스트:**")
            # 텍스트 영역으로 표시하여 멀티라인 지원
            st.text_area(
                "프로필 텍스트 내용",
                value=profile_text,
                height=100,
                disabled=True,
                key=f"profile_text_{influencer['sns_id']}",
                label_visibility="collapsed"
            )


def render_campaign_participation_tab():
    """캠페인 참여 인플루언서 관리 탭"""
    st.subheader("👥 참여 인플루언서 관리")
    st.markdown("캠페인별로 참여 인플루언서를 관리합니다.")
    
    # 캠페인 목록 새로고침 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 캠페인 목록 새로고침", key="refresh_campaigns_participation", help="캠페인 목록을 새로 불러옵니다"):
            st.rerun()
    
    with col2:
        st.caption("캠페인 목록을 새로고침하려면 새로고침 버튼을 클릭하세요.")
    
    # 캠페인 선택 (모든 캠페인 조회)
    campaigns = db_manager.get_campaigns()
    
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    campaign_options = {f"{c['campaign_name']} ({c['campaign_type']})": c['id'] for c in campaigns}
    selected_campaign_id = st.selectbox(
        "캠페인 선택",
        options=list(campaign_options.keys()),
        key="participation_campaign_select",
        help="참여 인플루언서를 관리할 캠페인을 선택하세요"
    )
    
    if not selected_campaign_id:
        st.warning("캠페인을 선택해주세요.")
        return
    
    campaign_id = campaign_options[selected_campaign_id]
    selected_campaign = next(c for c in campaigns if c['id'] == campaign_id)
    
    st.subheader(f"📊 {selected_campaign['campaign_name']} 참여 인플루언서")
    
    # 인플루언서 추가 섹션 (새로운 워크플로우)
    render_add_influencer_workflow(campaign_id)
    
    # 참여 인플루언서 목록
    st.subheader("📋 참여 인플루언서 목록")
    
    # 참여 인플루언서 목록 컴팩트 스타일
    st.markdown("""
    <style>
    /* 참여 인플루언서 목록 컴팩트 스타일 */
    div[data-testid="column"] .stButton > button {
        height: 1.5rem !important;
        min-height: 1.5rem !important;
        width: 100% !important;
        font-size: 0.75rem !important;
        padding: 0.1rem 0.3rem !important;
        margin: 0.1rem 0 !important;
    }
    
    /* 리스트 아이템 간격 줄이기 */
    .stContainer {
        margin: 0.1rem 0 !important;
        padding: 0.2rem 0 !important;
    }
    
    /* 텍스트 크기 줄이기 */
    .stMarkdown {
        margin: 0.05rem 0 !important;
        line-height: 1.2 !important;
    }
    
    /* 캡션 텍스트 크기 줄이기 */
    .stCaption {
        font-size: 0.7rem !important;
        margin: 0.02rem 0 !important;
        line-height: 1.1 !important;
    }
    
    /* 제목 텍스트 크기 조정 */
    .stMarkdown h3 {
        margin: 0.1rem 0 !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    participations = db_manager.get_campaign_participations(campaign_id)
    
    if participations:
        # 페이지네이션을 위한 설정
        items_per_page = 20
        total_pages = (len(participations) - 1) // items_per_page + 1
        
        # 페이지 선택
        if total_pages > 1:
            page = st.selectbox("페이지 선택", range(1, total_pages + 1), key="participation_page") - 1
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, len(participations))
            page_participations = participations[start_idx:end_idx]
            st.caption(f"페이지 {page + 1}/{total_pages} (총 {len(participations)}명)")
        else:
            page_participations = participations
        
        for i, participation in enumerate(page_participations):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    # 모든 필드 정보 표시 (컴팩트하게)
                    st.markdown(f"**{participation.get('influencer_name') or participation['sns_id']}**")
                    st.caption(f"📱 SNS ID: {participation['sns_id']} | 👥 팔로워: {participation.get('followers_count', 0):,}명")
                    st.caption(f"🌐 플랫폼: {participation['platform']} | 📦 샘플상태: {participation['sample_status']}")
                    st.caption(f"💰 비용: {participation['cost_krw']:,}원 | 📤 업로드: {'✅' if participation['content_uploaded'] else '❌'}")
                    
                    # 컨텐츠 링크 표시 (첫 번째 링크만)
                    content_links = participation.get('content_links', [])
                    if content_links and len(content_links) > 0:
                        first_link = content_links[0]
                        link_count = len(content_links)
                        if link_count > 1:
                            st.caption(f"🔗 컨텐츠 링크: {first_link} (+{link_count-1}개 더)")
                        else:
                            st.caption(f"🔗 컨텐츠 링크: {first_link}")
                    
                    if participation['manager_comment']:
                        st.caption(f"💬 담당자 의견: {participation['manager_comment']}")
                    if participation['influencer_requests']:
                        st.caption(f"📋 요청사항: {participation['influencer_requests']}")
                    if participation['memo']:
                        st.caption(f"📝 메모: {participation['memo']}")
                    if participation['influencer_feedback']:
                        st.caption(f"💭 피드백: {participation['influencer_feedback']}")
                
                with col2:
                    if st.button("상세보기", key=f"detail_participation_{participation['id']}_{i}"):
                        st.session_state.viewing_participation = participation
                        st.rerun()
                
                with col3:
                    if st.button("수정", key=f"edit_participation_{participation['id']}_{i}"):
                        st.session_state.editing_participation = participation
                        st.rerun()
                
                with col4:
                    if st.button("제거", key=f"remove_participation_{participation['id']}_{i}"):
                        result = db_manager.remove_influencer_from_campaign(participation['id'])
                        if result["success"]:
                            st.success("인플루언서가 제거되었습니다!")
                            st.rerun()
                        else:
                            st.error(f"제거 실패: {result['message']}")
                
                # 구분선을 더 얇게
                st.markdown("---")
    else:
        st.info("이 캠페인에 참여한 인플루언서가 없습니다.")
    
    # 참여 상세보기 모달
    if 'viewing_participation' in st.session_state:
        render_participation_detail_modal()
    
    # 참여 수정 모달
    if 'editing_participation' in st.session_state:
        render_participation_edit_modal()

def render_participation_detail_modal():
    """참여 상세보기 모달"""
    participation = st.session_state.viewing_participation
    
    with st.expander("📋 참여 상세 정보", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**인플루언서:** {participation.get('influencer_name') or participation['sns_id']}")
            st.markdown(f"**플랫폼:** {participation['platform']}")
            st.markdown(f"**SNS ID:** {participation['sns_id']}")
            st.markdown(f"**팔로워 수:** {participation.get('followers_count', 0):,}")
            st.markdown(f"**게시물 수:** {participation.get('post_count', 0):,}")
        
        with col2:
            st.markdown(f"**샘플 상태:** {participation['sample_status']}")
            st.markdown(f"**비용:** {participation['cost_krw']:,}원")
            st.markdown(f"**업로드 완료:** {'✅' if participation['content_uploaded'] else '❌'}")
            st.markdown(f"**참여일:** {participation['created_at'][:10] if participation['created_at'] else 'N/A'}")
        
        if participation['manager_comment']:
            st.markdown("**담당자 의견:**")
            st.info(participation['manager_comment'])
        
        if participation['influencer_requests']:
            st.markdown("**인플루언서 요청사항:**")
            st.info(participation['influencer_requests'])
        
        if participation['influencer_feedback']:
            st.markdown("**인플루언서 피드백:**")
            st.info(participation['influencer_feedback'])
        
        if participation['memo']:
            st.markdown("**메모:**")
            st.info(participation['memo'])
        
        content_links = participation.get('content_links', [])
        if content_links and len(content_links) > 0:
            st.markdown("**컨텐츠 링크:**")
            first_link = content_links[0]
            link_count = len(content_links)
            if link_count > 1:
                st.markdown(f"- {first_link}")
                st.caption(f"총 {link_count}개의 링크가 있습니다. (첫 번째 링크만 표시)")
            else:
                st.markdown(f"- {first_link}")
        
        if st.button("닫기", key="close_participation_detail"):
            del st.session_state.viewing_participation
            st.rerun()

def render_participation_edit_modal():
    """참여 수정 모달"""
    participation = st.session_state.editing_participation
    
    with st.expander("✏️ 참여 정보 수정", expanded=True):
        with st.form("edit_participation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sample_status = st.selectbox(
                    "샘플 상태",
                    ["요청", "발송준비", "발송완료", "수령"],
                    index=["요청", "발송준비", "발송완료", "수령"].index(participation['sample_status']),
                    key="edit_sample_status"
                )
                cost_krw = st.number_input(
                    "비용 (원)",
                    min_value=0,
                    value=int(participation['cost_krw']),
                    key="edit_cost_krw"
                )
                content_uploaded = st.checkbox(
                    "컨텐츠 업로드 완료",
                    value=participation['content_uploaded'],
                    key="edit_content_uploaded"
                )
            
            with col2:
                manager_comment = st.text_area(
                    "담당자 의견",
                    value=participation['manager_comment'] or "",
                    key="edit_manager_comment"
                )
                influencer_requests = st.text_area(
                    "인플루언서 요청사항",
                    value=participation['influencer_requests'] or "",
                    key="edit_influencer_requests"
                )
                memo = st.text_area(
                    "메모",
                    value=participation['memo'] or "",
                    key="edit_memo"
                )
            
            influencer_feedback = st.text_area(
                "인플루언서 피드백",
                value=participation['influencer_feedback'] or "",
                key="edit_influencer_feedback"
            )
            
            # 컨텐츠 링크 관리
            st.markdown("**컨텐츠 링크:**")
            
            # 버튼 정렬을 위한 CSS
            st.markdown("""
            <style>
            .stButton > button {
                height: 2.5rem !important;
                min-height: 2.5rem !important;
                align-self: flex-end !important;
            }
            .stColumns > div {
                display: flex !important;
                align-items: flex-end !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 세션 상태에서 링크 관리
            if f"content_links_{participation['id']}" not in st.session_state:
                st.session_state[f"content_links_{participation['id']}"] = participation['content_links'] or []
            
            content_links = st.session_state[f"content_links_{participation['id']}"]
            
            # 기존 링크 표시
            for i, link in enumerate(content_links):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text_input(f"링크 {i+1}", value=link, key=f"existing_link_{i}", disabled=True)
                with col2:
                    # 마이너스 버튼으로 삭제
                    if st.form_submit_button("➖", key=f"delete_link_{i}", help="링크 삭제"):
                        # 삭제할 링크를 None으로 표시
                        content_links[i] = None
                        # None 값 제거 (삭제된 링크들)
                        content_links = [link for link in content_links if link is not None]
                        st.session_state[f"content_links_{participation['id']}"] = content_links
                        st.rerun()
            
            # None 값 제거 (삭제된 링크들)
            content_links = [link for link in content_links if link is not None]
            st.session_state[f"content_links_{participation['id']}"] = content_links
            
            # 새 링크 추가
            col1, col2 = st.columns([4, 1])
            with col1:
                new_link = st.text_input("새 링크 추가", key="new_content_link", placeholder="https://...")
            with col2:
                if st.form_submit_button("➕", key="add_content_link", help="링크 추가"):
                    if new_link and new_link.strip():
                        content_links.append(new_link.strip())
                        st.session_state[f"content_links_{participation['id']}"] = content_links
                        st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("수정 완료", type="primary"):
                    updates = {
                        "sample_status": sample_status,
                        "cost_krw": cost_krw,
                        "content_uploaded": content_uploaded,
                        "manager_comment": manager_comment,
                        "influencer_requests": influencer_requests,
                        "memo": memo,
                        "influencer_feedback": influencer_feedback,
                        "content_links": content_links
                    }
                    
                    result = db_manager.update_campaign_participation(participation['id'], updates)
                    if result["success"]:
                        st.success("참여 정보가 수정되었습니다!")
                        # 세션 상태 정리
                        del st.session_state.editing_participation
                        if f"content_links_{participation['id']}" in st.session_state:
                            del st.session_state[f"content_links_{participation['id']}"]
                        st.rerun()
                    else:
                        st.error(f"수정 실패: {result['message']}")
            
            with col2:
                if st.form_submit_button("취소"):
                    # 세션 상태 정리
                    del st.session_state.editing_participation
                    if f"content_links_{participation['id']}" in st.session_state:
                        del st.session_state[f"content_links_{participation['id']}"]
                    st.rerun()

def render_influencer_management():
    """인플루언서 관리 메인 컴포넌트"""
    st.subheader("👥 인플루언서 관리")
    st.markdown("인플루언서 정보를 검색, 필터링하고 상세 정보를 관리합니다.")
    
    # 두 컬럼으로 분할
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_influencer_search_and_filter()
    
    with col2:
        render_influencer_detail_view()

def render_influencer_search_and_filter():
    """인플루언서 검색 및 필터링 (좌측)"""
    st.subheader("인플루언서 등록`")
    
    # 새 인플루언서 등록
    with st.expander("➕ 새 인플루언서 등록", expanded=False):
        with st.form("create_influencer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                platform = st.selectbox(
                    "플랫폼",
                    ["instagram", "youtube", "tiktok", "twitter"],
                    key="create_influencer_platform",
                    format_func=lambda x: {
                        "instagram": "📸 Instagram",
                        "youtube": "📺 YouTube",
                        "tiktok": "🎵 TikTok",
                        "twitter": "🐦 Twitter"
                    }[x]
                )
                sns_id = st.text_input("SNS ID", placeholder="@username 또는 username")
            
            with col2:
                influencer_name = st.text_input("별칭", placeholder="인플루언서의 별칭")
                sns_url = st.text_input("SNS URL", placeholder="https://...")
            
            # Owner Comment와 Content Category 추가
            owner_comment = st.text_area("Owner Comment", placeholder="인플루언서에 대한 담당자 코멘트")
            
            content_category = st.selectbox(
                "카테고리",
                ["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"],
                key="create_influencer_category",
                format_func=lambda x: {
                    "일반": "📝 일반",
                    "뷰티": "💄 뷰티",
                    "패션": "👗 패션",
                    "푸드": "🍽️ 푸드",
                    "여행": "✈️ 여행",
                    "라이프스타일": "🏠 라이프스타일",
                    "테크": "💻 테크",
                    "게임": "🎮 게임",
                    "스포츠": "⚽ 스포츠",
                    "애견": "🐕 애견",
                    "기타": "🔧 기타"
                }[x]
            )
            
            if st.form_submit_button("인플루언서 등록", type="primary"):
                if not sns_id:
                    st.error("SNS ID를 입력해주세요.")
                elif not sns_url:
                    st.error("SNS URL을 입력해주세요.")
                else:
                    # 별칭이 비어있으면 SNS ID를 사용
                    final_influencer_name = influencer_name.strip() if influencer_name else sns_id
                    
                    influencer = Influencer(
                        platform=platform,
                        sns_id=sns_id,
                        influencer_name=final_influencer_name,
                        sns_url=sns_url,
                        owner_comment=owner_comment,
                        content_category=content_category
                    )
                    
                    result = db_manager.create_influencer(influencer)
                    if result["success"]:
                        st.success("인플루언서가 등록되었습니다!")
                        # 캐시 초기화
                        if "influencers_data" in st.session_state:
                            del st.session_state["influencers_data"]
                        st.rerun()
                    else:
                        st.error(f"인플루언서 등록 실패: {result['message']}")
    
    # 1명 검색 기능
    st.markdown("### 🔍 인플루언서 검색")
    with st.form("search_influencer_form"):
        search_term = st.text_input("SNS ID 또는 이름", placeholder="정확한 SNS ID 또는 이름 입력", key="influencer_search_input")
        search_clicked = st.form_submit_button("🔍 검색", type="primary")
    
    if search_clicked:
        if not search_term:
            st.error("검색어를 입력해주세요.")
        else:
            # 단일 인플루언서 검색
            search_result = search_single_influencer(search_term)
            if search_result:
                st.session_state.selected_influencer = search_result
                st.success(f"인플루언서를 찾았습니다: {search_result.get('influencer_name') or search_result['sns_id']}")
                st.rerun()
            else:
                st.error("해당 인플루언서를 찾을 수 없습니다.")
    
    # 필터링 기능
    st.markdown("### 🎯 필터링")
    
    # 플랫폼 필터
    platform_filter = st.selectbox(
        "플랫폼",
        ["전체", "instagram", "youtube", "tiktok", "twitter"],
        key="influencer_platform_filter",
        format_func=lambda x: {
            "전체": "🌐 전체",
            "instagram": "📸 Instagram",
            "youtube": "📺 YouTube",
            "tiktok": "🎵 TikTok",
            "twitter": "🐦 Twitter"
        }[x]
    )
    
    # 콘텐츠 카테고리 필터
    content_category_filter = st.selectbox(
        "콘텐츠 카테고리",
        ["전체", "일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"],
        key="influencer_content_category_filter",
        format_func=lambda x: {
            "전체": "📂 전체",
            "일반": "📝 일반",
            "뷰티": "💄 뷰티",
            "패션": "👗 패션",
            "푸드": "🍽️ 푸드",
            "여행": "✈️ 여행",
            "라이프스타일": "🏠 라이프스타일",
            "테크": "💻 테크",
            "게임": "🎮 게임",
            "스포츠": "⚽ 스포츠",
            "애견": "🐕 애견",
            "기타": "🔧 기타"
        }[x]
    )
    
    # 팔로워 수 필터
    col1, col2 = st.columns(2)
    with col1:
        min_followers = st.number_input("최소 팔로워 수", min_value=0, value=0, key="min_followers")
    with col2:
        max_followers = st.number_input("최대 팔로워 수", min_value=0, value=10000000, key="max_followers")
    
    # 필터 적용 버튼
    if st.button("🔄 필터 적용", help="선택한 필터 조건으로 인플루언서를 조회합니다", key="apply_filter"):
        # 필터 조건을 세션에 저장
        st.session_state.filter_conditions = {
            "platform": platform_filter if platform_filter != "전체" else None,
            "content_category": content_category_filter if content_category_filter != "전체" else None,
            "min_followers": min_followers,
            "max_followers": max_followers
        }
        # 페이지 초기화
        st.session_state.influencer_current_page = 0
        # 필터링된 데이터 캐시 초기화
        for key in list(st.session_state.keys()):
            if key.startswith("filtered_influencers_"):
                del st.session_state[key]
        st.success("필터가 적용되었습니다!")
        st.rerun()
    
    # 인플루언서 목록 표시 (페이징)
    render_influencer_list_with_pagination()

def search_single_influencer(search_term: str):
    """단일 인플루언서 검색"""
    try:
        # 모든 인플루언서 조회
        all_influencers = db_manager.get_influencers()
        
        # 정확한 매칭 시도
        for influencer in all_influencers:
            sns_id = influencer.get('sns_id', '').lower()
            name = (influencer.get('influencer_name', '') or '').lower()
            search_lower = search_term.lower()
            
            if search_lower == sns_id or search_lower == name:
                return influencer
        
        # 부분 매칭 시도
        for influencer in all_influencers:
            sns_id = influencer.get('sns_id', '').lower()
            name = (influencer.get('influencer_name', '') or '').lower()
            search_lower = search_term.lower()
            
            if search_lower in sns_id or search_lower in name:
                return influencer
        
        return None
    except Exception as e:
        st.error(f"검색 중 오류가 발생했습니다: {str(e)}")
        return None

def render_influencer_list_with_pagination():
    """페이징이 적용된 인플루언서 목록 표시"""
    st.markdown("### 📊 인플루언서 목록")
    
    # 필터 조건 확인
    filter_conditions = st.session_state.get('filter_conditions', {})
    
    if not filter_conditions:
        st.info("필터 조건을 설정하고 '필터 적용' 버튼을 클릭해주세요.")
        return
    
    # 필터링된 인플루언서 조회
    cache_key = f"filtered_influencers_{hash(str(filter_conditions))}"
    
    if cache_key not in st.session_state:
        with st.spinner("필터링된 인플루언서를 불러오는 중..."):
            all_influencers = db_manager.get_influencers()
            
            # 필터링 적용
            filtered_influencers = all_influencers.copy()
            
            # 플랫폼 필터
            if filter_conditions.get("platform"):
                filtered_influencers = [inf for inf in filtered_influencers if inf['platform'] == filter_conditions["platform"]]
            
            # 콘텐츠 카테고리 필터 (LIKE 검색)
            if filter_conditions.get("content_category"):
                content_category = filter_conditions["content_category"]
                filtered_influencers = [
                    inf for inf in filtered_influencers 
                    if inf.get('content_category') and content_category.lower() in inf.get('content_category', '').lower()
                ]
            
            # 팔로워 수 필터
            min_followers = filter_conditions.get("min_followers", 0)
            max_followers = filter_conditions.get("max_followers", 10000000)
            filtered_influencers = [
                inf for inf in filtered_influencers 
                if min_followers <= inf.get('followers_count', 0) <= max_followers
            ]
            
            st.session_state[cache_key] = filtered_influencers
    
    filtered_influencers = st.session_state[cache_key]
    
    # 페이징 설정
    items_per_page = 10
    total_pages = (len(filtered_influencers) - 1) // items_per_page + 1
    current_page = st.session_state.get('influencer_current_page', 0)
    
    # 페이지 선택
    if total_pages > 1:
        page_options = list(range(total_pages))
        selected_page = st.selectbox(
            f"페이지 선택 (총 {total_pages}페이지, {len(filtered_influencers)}명)",
            page_options,
            index=current_page,
            key="page_selector"
        )
        
        if selected_page != current_page:
            st.session_state.influencer_current_page = selected_page
            st.rerun()
    
    # 현재 페이지의 인플루언서 표시
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_influencers))
    page_influencers = filtered_influencers[start_idx:end_idx]
    
    st.caption(f"페이지 {current_page + 1}/{total_pages} (총 {len(filtered_influencers)}명)")
    
    if page_influencers:
        # 인플루언서 목록 표시
        for i, influencer in enumerate(page_influencers):
            with st.container():
                # 인플루언서 정보를 잘 조합해서 표시
                render_influencer_list_item(influencer, i)
                st.divider()
    else:
        st.info("해당 조건에 맞는 인플루언서가 없습니다.")

def render_influencer_list_item(influencer, index):
    """인플루언서 리스트 아이템 표시"""
    # 인플루언서 정보 조합 표시
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # SNS ID와 팔로워 수
        st.markdown(f"**SNS ID:** `{influencer['sns_id']}`")
        st.caption(f"👥 팔로워: {influencer.get('followers_count', 0):,}명")
        
        # SNS URL - 링크로 표시
        if influencer.get('sns_url'):
            sns_url = influencer['sns_url']
            st.caption(f"🔗 URL: [{sns_url}]({sns_url})")
        
        # Owner Comment (있는 경우)
        if influencer.get('owner_comment'):
            st.caption(f"💬 코멘트: {influencer['owner_comment']}")
        
        # 프로필 텍스트 (간단히)
        if influencer.get('profile_text'):
            profile_text = influencer['profile_text'][:100] + "..." if len(influencer['profile_text']) > 100 else influencer['profile_text']
            st.caption(f"📝 프로필: {profile_text}")
    
    with col2:
        # 프로필 이미지 (작은 크기)
        if influencer.get('profile_image_url'):
            try:
                st.image(influencer['profile_image_url'], width=80, caption="프로필")
            except:
                st.caption("이미지 로드 실패")
        else:
            st.caption("이미지 없음")
    
    with col3:
        # 현재 선택된 인플루언서인지 확인
        is_selected = (st.session_state.get('selected_influencer', {}).get('id') == influencer['id'])
        
        # 선택 버튼 (editor 아이콘) - 선택된 경우 primary 타입으로 표시
        button_type = "primary" if is_selected else "secondary"
        if st.button("📝", key=f"select_{influencer['id']}_{index}", help="상세보기", type=button_type):
            st.session_state.selected_influencer = influencer
            st.rerun()
        
        # 편집 버튼
        if st.button("✏️", key=f"edit_{influencer['id']}_{index}", help="편집"):
            st.session_state.editing_influencer = influencer
            st.rerun()
        
        # 삭제 버튼
        if st.button("🗑️", key=f"delete_inf_{influencer['id']}_{index}", help="삭제"):
            result = db_manager.delete_influencer(influencer['id'])
            if result["success"]:
                st.success("인플루언서가 삭제되었습니다!")
                # 선택된 인플루언서가 삭제된 경우 선택 해제
                if is_selected:
                    del st.session_state.selected_influencer
                # 캐시 초기화
                for key in list(st.session_state.keys()):
                    if key.startswith("filtered_influencers_"):
                        del st.session_state[key]
                st.rerun()
            else:
                st.error(f"삭제 실패: {result['message']}")

def render_influencer_detail_view():
    """인플루언서 상세 정보 보기 (우측)"""
    st.subheader("📋 상세 정보")
    
    # 선택된 인플루언서가 있는지 확인
    if 'selected_influencer' in st.session_state:
        influencer = st.session_state.selected_influencer
        render_influencer_detail_form(influencer)
    else:
        st.info("좌측에서 📝 버튼을 클릭하여 인플루언서를 선택해주세요.")

def render_influencer_detail_form(influencer):
    """인플루언서 상세 정보 폼"""
    st.markdown(f"**{influencer.get('influencer_name') or influencer['sns_id']}**")
    
    # 프로필 이미지를 가장 상단에 표시
    if influencer.get('profile_image_url'):
        st.image(influencer['profile_image_url'], width=200, caption="프로필 이미지")
    
    # 기본 정보 표시
    col1, col2 = st.columns(2)
    with col1:
        # 플랫폼 아이콘화
        platform_icons = {
            "instagram": "📸 Instagram",
            "youtube": "📺 YouTube", 
            "tiktok": "🎵 TikTok",
            "twitter": "🐦 Twitter"
        }
        platform_display = platform_icons.get(influencer['platform'], f"🌐 {influencer['platform']}")
        st.metric("플랫폼", platform_display)
        st.metric("팔로워 수", f"{influencer.get('followers_count', 0):,}")
    with col2:
        st.metric("SNS ID", influencer['sns_id'])
        st.metric("게시물 수", f"{influencer.get('post_count', 0):,}")
    
    # 필수 정보 표시
    st.markdown("### 📋 필수 정보")
    
    # SNS URL (필수) - 링크로 표시
    sns_url = influencer.get('sns_url', 'N/A')
    if sns_url and sns_url != 'N/A':
        st.markdown(f"**🔗 SNS URL:** [{sns_url}]({sns_url})")
    else:
        st.markdown(f"**🔗 SNS URL:** {sns_url}")
    
    # Owner Comment (필수)
    owner_comment = influencer.get('owner_comment', 'N/A')
    st.markdown("**💬 Owner Comment:**")
    st.text_area("", value=owner_comment, height=80, disabled=True, key=f"owner_comment_{influencer['id']}")
    
    # 프로필 텍스트 표시
    if influencer.get('profile_text'):
        st.markdown("**프로필 텍스트:**")
        st.text_area("", value=influencer['profile_text'], height=100, disabled=True, key=f"profile_text_{influencer['id']}")
    
    # 추가 정보
    if influencer.get('kakao_channel_id'):
        st.markdown(f"**카카오 채널 ID:** {influencer['kakao_channel_id']}")
    
    # 등록일 정보
    if influencer.get('created_at'):
        st.caption(f"등록일: {influencer['created_at'][:10]}")
    
    # 수정 폼
    with st.expander("✏️ 정보 수정", expanded=True):
        with st.form(f"edit_influencer_form_{influencer['id']}"):
            st.markdown("**수정 가능 정보:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Owner Comment
                new_owner_comment = st.text_area(
                    "💬 Owner Comment", 
                    value=influencer.get('owner_comment', ''), 
                    key=f"edit_owner_comment_{influencer['id']}",
                    help="인플루언서에 대한 담당자 코멘트"
                )
                
                # Content Category
                category_options = ["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"]
                current_category = influencer.get('content_category', '일반')
                
                # 현재 카테고리가 리스트에 없으면 기본값(일반)으로 설정
                try:
                    category_index = category_options.index(current_category)
                except ValueError:
                    category_index = 0  # '일반'의 인덱스
                
                new_content_category = st.selectbox(
                    "📂 Content Category",
                    category_options,
                    index=category_index,
                    key=f"edit_content_category_{influencer['id']}"
                )
                
                # Tags
                # tags는 문자열로 처리
                existing_tags = influencer.get('tags', '')
                tags_display_value = existing_tags or ""
                
                tags_input = st.text_input(
                    "🏷️ Tags", 
                    value=tags_display_value,
                    key=f"edit_tags_{influencer['id']}",
                    help="태그를 쉼표로 구분하여 입력하세요"
                )
                
                # 디버깅: 태그 입력 필드 값 확인
                st.write(f"🔍 디버깅 - tags_input field value: '{tags_input}'")
                
                # Contact Method (enum: dm, email, kakao, phone, form, other)
                contact_method_options = ["dm", "email", "kakao", "phone", "form", "other"]
                current_contact_method = influencer.get('contact_method', 'dm')
                contact_method_index = contact_method_options.index(current_contact_method) if current_contact_method in contact_method_options else 0
                
                new_contact_method = st.selectbox(
                    "📱 연락 방식",
                    contact_method_options,
                    index=contact_method_index,
                    key=f"edit_contact_method_{influencer['id']}",
                    format_func=lambda x: {
                        "dm": "💬 DM",
                        "email": "📧 이메일",
                        "kakao": "💛 카카오톡",
                        "phone": "📞 전화",
                        "form": "📝 폼",
                        "other": "🔧 기타"
                    }[x]
                )
                
                # Preferred Mode (enum: seeding, promotion, sales)
                preferred_mode_options = ["seeding", "promotion", "sales"]
                current_preferred_mode = influencer.get('preferred_mode', 'seeding')
                preferred_mode_index = preferred_mode_options.index(current_preferred_mode) if current_preferred_mode in preferred_mode_options else 0
                
                new_preferred_mode = st.selectbox(
                    "🎯 선호 홍보/세일즈 방식",
                    preferred_mode_options,
                    index=preferred_mode_index,
                    key=f"edit_preferred_mode_{influencer['id']}",
                    format_func=lambda x: {
                        "seeding": "🌱 시딩",
                        "promotion": "📢 홍보",
                        "sales": "💰 세일즈"
                    }[x]
                )
            
            with col2:
                # Price KRW
                new_price_krw = st.number_input(
                    "💰 Price (KRW)", 
                    min_value=0, 
                    value=influencer.get('price_krw', 0),
                    key=f"edit_price_krw_{influencer['id']}",
                    help="인플루언서 협찬 비용"
                )
                
                # Manager Rating
                new_manager_rating = st.selectbox(
                    "⭐ Manager Rating",
                    ["1", "2", "3", "4", "5"],
                    index=["1", "2", "3", "4", "5"].index(str(influencer.get('manager_rating', '3'))),
                    key=f"edit_manager_rating_{influencer['id']}",
                    help="담당자 평가 (1-5점)"
                )
                
                # Interested Products
                new_interested_products = st.text_area(
                    "🛍️ Interested Products", 
                    value=influencer.get('interested_products', ''),
                    key=f"edit_interested_products_{influencer['id']}",
                    help="관심 있는 제품 카테고리",
                    height=80
                )
                
                # Shipping Address
                new_shipping_address = st.text_area(
                    "📦 Shipping Address", 
                    value=influencer.get('shipping_address', ''),
                    key=f"edit_shipping_address_{influencer['id']}",
                    help="배송 주소",
                    height=80
                )
            
            # 추가 연락처 정보 (새로운 행)
            st.markdown("**📞 연락처 정보**")
            col3, col4 = st.columns(2)
            
            with col3:
                # Phone Number
                new_phone_number = st.text_input(
                    "📱 Phone Number", 
                    value=influencer.get('phone_number', ''),
                    key=f"edit_phone_number_{influencer['id']}",
                    help="인플루언서 전화번호",
                    placeholder="010-1234-5678"
                )
                
                # Email
                new_email = st.text_input(
                    "📧 Email", 
                    value=influencer.get('email', ''),
                    key=f"edit_email_{influencer['id']}",
                    help="인플루언서 이메일 주소",
                    placeholder="influencer@example.com"
                )
            
            with col4:
                # Kakao Channel ID
                new_kakao_channel_id = st.text_input(
                    "💬 Kakao Channel ID", 
                    value=influencer.get('kakao_channel_id', ''),
                    key=f"edit_kakao_channel_id_{influencer['id']}",
                    help="카카오 채널 ID",
                    placeholder="@channel_id"
                )
            
            # 태그 처리 - 빈 문자열이나 None인 경우 빈 배열로 처리 (jsonb 타입)
            if tags_input and tags_input.strip():
                # 쉼표로 분리하고 각 태그의 앞뒤 공백 제거, 빈 문자열 제거
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                # 빈 리스트가 되면 빈 배열로 설정 (jsonb 타입)
                if not tags:
                    tags = []
            else:
                tags = []
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 수정하기", type="primary"):
                    # 폼 제출 시점에서 세션 상태에서 실제 값 가져오기
                    actual_tags_input = st.session_state.get(f"edit_tags_{influencer['id']}", "")
                    
                    # 디버깅: 태그 데이터 확인
                    st.write(f"🔍 디버깅 - tags_input (form variable): '{tags_input}'")
                    st.write(f"🔍 디버깅 - actual_tags_input (session state): '{actual_tags_input}'")
                    
                    # 실제 세션 상태 값으로 태그 처리
                    if actual_tags_input and actual_tags_input.strip():
                        # 문자열 그대로 저장
                        actual_tags = actual_tags_input.strip()
                    else:
                        actual_tags = ""
                    
                    st.write(f"🔍 디버깅 - actual_tags: {actual_tags}")
                    st.write(f"🔍 디버깅 - actual_tags type: {type(actual_tags)}")
                    
                    # 수정 데이터 준비
                    update_data = {
                        "owner_comment": new_owner_comment,
                        "content_category": new_content_category,
                        "tags": actual_tags,
                        "contact_method": new_contact_method,
                        "preferred_mode": new_preferred_mode,
                        "price_krw": new_price_krw,
                        "manager_rating": int(new_manager_rating),
                        "interested_products": new_interested_products,
                        "shipping_address": new_shipping_address,
                        "phone_number": new_phone_number,
                        "email": new_email,
                        "kakao_channel_id": new_kakao_channel_id
                    }
                    
                    st.write(f"🔍 디버깅 - update_data: {update_data}")
                    
                    # 데이터베이스 업데이트
                    result = db_manager.update_influencer(influencer['id'], update_data)
                    
                    # 디버깅: 데이터베이스 응답 확인
                    st.write(f"🔍 디버깅 - DB result: {result}")
                    
                    if result["success"]:
                        st.success("인플루언서 정보가 수정되었습니다!")
                        # 캐시 초기화
                        for key in list(st.session_state.keys()):
                            if key.startswith("filtered_influencers_"):
                                del st.session_state[key]
                        # 선택된 인플루언서 정보도 업데이트
                        if 'selected_influencer' in st.session_state:
                            st.session_state.selected_influencer.update(update_data)
                        st.rerun()
                    else:
                        st.error(f"수정 실패: {result['message']}")
            with col2:
                if st.form_submit_button("❌ 취소"):
                    st.rerun()
    
    # 선택 해제 버튼
    if st.button("🔄 선택 해제", key=f"clear_selection_{influencer['id']}"):
        del st.session_state.selected_influencer
        st.rerun()

def render_influencer_tab():
    """인플루언서 탭 - 기존 함수 유지 (호환성)"""
    render_influencer_management()

def render_performance_crawl():
    """성과관리 크롤링 컴포넌트 - 크롤링 기능이 제거되었습니다."""
    st.subheader("📈 성과관리 크롤링")
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")

def render_performance_management():
    """성과 관리 컴포넌트"""
    st.subheader("📈 성과 관리")
    st.markdown("캠페인별 성과를 확인하고 인플루언서의 성과를 관리합니다.")
    
    # 탭으로 성과 관리와 리포트 구분
    tab1, tab2 = st.tabs(["📊 성과 관리", "📋 리포트"])
    
    with tab1:
        render_performance_management_tab()
    
    with tab2:
        render_performance_report_tab()

def render_performance_management_tab():
    """성과 관리 탭"""
    # 캠페인 목록 새로고침 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 캠페인 목록 새로고침", key="refresh_campaigns_performance", help="캠페인 목록을 새로 불러옵니다"):
            # 세션 상태를 초기화하여 데이터를 새로 불러오도록 함
            if 'campaigns_cache' in st.session_state:
                del st.session_state['campaigns_cache']
            if 'participations_cache' in st.session_state:
                del st.session_state['participations_cache']
            st.success("캠페인 목록을 새로고침했습니다!")
            st.rerun()
    
    with col2:
        st.caption("캠페인 목록을 새로고침하려면 새로고침 버튼을 클릭하세요.")
    
    # 캠페인별로 참여 인플루언서 조회
    campaigns = db_manager.get_campaigns()
    
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    # 모든 캠페인의 참여 인플루언서를 가져와서 표시
    all_participations = []
    for campaign in campaigns:
        participations = db_manager.get_campaign_participations(campaign['id'])
        for participation in participations:
            participation['campaign_name'] = campaign['campaign_name']
            participation['campaign_type'] = campaign['campaign_type']
            all_participations.append(participation)
    
    if not all_participations:
        st.info("참여한 인플루언서가 없습니다.")
        return
    
    # 캠페인 선택 기능 추가
    campaign_names = list(set(p['campaign_name'] for p in all_participations))
    selected_campaign = st.selectbox(
        "캠페인을 선택하세요", 
        ["전체"] + campaign_names, 
        key="performance_campaign_select",
        help="특정 캠페인의 성과만 보고 싶다면 선택하세요"
    )
    
    # 선택된 캠페인에 따른 데이터 필터링
    if selected_campaign == "전체":
        filtered_participations = all_participations
    else:
        filtered_participations = [p for p in all_participations if p['campaign_name'] == selected_campaign]
    
    if not filtered_participations:
        st.info("선택된 캠페인에 참여자가 없습니다.")
        return
    
    # 좌/우 레이아웃으로 변경 (반응형 고려)
    left_col, right_col = st.columns([1, 1], gap="large")
    
    with left_col:
        st.subheader("👥 참여 인플루언서 목록")
        
        # 성과 관리용 컴팩트 스타일
        st.markdown("""
        <style>
        /* 성과 관리용 컴팩트 스타일 */
        .performance-list .stButton > button {
            height: 1.8rem !important;
            min-height: 1.8rem !important;
            width: 100% !important;
            font-size: 0.8rem !important;
            padding: 0.2rem 0.4rem !important;
            margin: 0.1rem 0 !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
        }
        
        .performance-list .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        .performance-list .stContainer {
            margin: 0.3rem 0 !important;
            padding: 0.5rem !important;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            background-color: #fafafa;
            transition: all 0.2s ease;
        }
        
        .performance-list .stContainer:hover {
            border-color: #007bff;
            background-color: #f8f9fa;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .performance-list .stMarkdown {
            margin: 0.1rem 0 !important;
            line-height: 1.3 !important;
        }
        
        .performance-list .stCaption {
            font-size: 0.75rem !important;
            margin: 0.05rem 0 !important;
            line-height: 1.2 !important;
            color: #666 !important;
        }
        
        /* 우측 패널 스타일 */
        .performance-right-panel {
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid #e9ecef;
        }
        
        /* 메트릭 카드 스타일 */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        /* 성과 입력 폼 스타일 */
        .performance-form {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* 스크롤바 스타일 */
        .performance-list {
            max-height: 70vh;
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        
        .performance-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .performance-list::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        
        .performance-list::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        
        .performance-list::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .performance-list {
                max-height: 50vh;
            }
            
            .performance-right-panel {
                margin-top: 1rem;
            }
            
            .performance-list .stContainer {
                margin: 0.2rem 0 !important;
                padding: 0.3rem !important;
            }
            
            .performance-list .stButton > button {
                height: 2rem !important;
                font-size: 0.9rem !important;
            }
        }
        
        @media (max-width: 480px) {
            .performance-list {
                max-height: 40vh;
            }
            
            .performance-list .stContainer {
                margin: 0.1rem 0 !important;
                padding: 0.2rem !important;
            }
            
            .performance-list .stCaption {
                font-size: 0.7rem !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 인플루언서 목록을 스크롤 가능한 컨테이너로 표시
        with st.container():
            st.markdown('<div class="performance-list">', unsafe_allow_html=True)
            
            for i, participation in enumerate(filtered_participations):
                with st.container():
                    # 인플루언서 기본 정보
                    st.markdown(f"**{participation.get('influencer_name') or participation['sns_id']}**")
                    st.caption(f"캠페인: {participation['campaign_name']} ({participation['campaign_type']})")
                    st.caption(f"플랫폼: {participation['platform']} | 샘플상태: {participation['sample_status']}")
                    st.caption(f"비용: {participation['cost_krw']:,}원 | 업로드: {'✅' if participation['content_uploaded'] else '❌'}")
                    
                    # 성과 지표 표시 (campaign_influencer_contents 테이블에서)
                    contents = db_manager.get_campaign_influencer_contents(participation['id'])
                    if contents:
                        # 좋아요, 댓글, 조회수 표시
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            total_likes = sum(content.get('likes', 0) for content in contents)
                            st.metric("❤️ 좋아요", f"{total_likes:,}")
                        with col2:
                            total_comments = sum(content.get('comments', 0) for content in contents)
                            st.metric("💬 댓글", f"{total_comments:,}")
                        with col3:
                            total_views = sum(content.get('views', 0) for content in contents)
                            st.metric("👁️ 조회수", f"{total_views:,}")
                    else:
                        st.info("성과 데이터가 없습니다.")
                    
                    # 액션 버튼들
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📝 성과 입력", key=f"perf_input_{participation['id']}_{i}", help="이 인플루언서의 성과를 입력합니다"):
                            st.session_state.inputting_performance = participation
                            st.rerun()
                    with col2:
                        if st.button("📊 상세보기", key=f"perf_detail_{participation['id']}_{i}", help="이 인플루언서의 성과를 상세히 봅니다"):
                            st.session_state.viewing_performance = participation
                            st.rerun()
                    
                    st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with right_col:
        st.markdown('<div class="performance-right-panel">', unsafe_allow_html=True)
        
        # 성과 입력 모달
        if 'inputting_performance' in st.session_state:
            render_performance_input_modal()
        
        # 성과 상세보기 모달
        elif 'viewing_performance' in st.session_state:
            render_performance_detail_modal()
        
        # 기본 상태 - 전체 성과 요약 표시
        else:
            # 전체 성과 요약 표시
            st.subheader("📊 전체 성과 요약")
            
            # 모든 참여자의 성과 집계
            total_likes = 0
            total_comments = 0
            total_views = 0
            total_cost = 0
            uploaded_count = 0
            
            for participation in filtered_participations:
                contents = db_manager.get_campaign_influencer_contents(participation['id'])
                if contents:
                    total_likes += sum(content.get('likes', 0) for content in contents)
                    total_comments += sum(content.get('comments', 0) for content in contents)
                    total_views += sum(content.get('views', 0) for content in contents)
                
                total_cost += participation.get('cost_krw', 0)
                if participation.get('content_uploaded'):
                    uploaded_count += 1
            
            # 요약 메트릭 표시
            col1, col2 = st.columns(2)
            with col1:
                st.metric("👥 총 참여자", f"{len(filtered_participations)}명")
                st.metric("💰 총 비용", f"{total_cost:,}원")
            with col2:
                st.metric("📤 업로드 완료", f"{uploaded_count}명")
                st.metric("📊 업로드율", f"{(uploaded_count/len(filtered_participations)*100):.1f}%" if filtered_participations else "0%")
            
            st.divider()
            
            # 성과 지표 요약
            if total_likes > 0 or total_comments > 0 or total_views > 0:
                st.subheader("📈 성과 지표 요약")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("❤️ 총 좋아요", f"{total_likes:,}")
                with col2:
                    st.metric("💬 총 댓글", f"{total_comments:,}")
                with col3:
                    st.metric("👁️ 총 조회수", f"{total_views:,}")
                
                # 평균 성과 계산
                if len(filtered_participations) > 0:
                    st.subheader("📊 평균 성과")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("평균 좋아요", f"{total_likes//len(filtered_participations):,}")
                    with col2:
                        st.metric("평균 댓글", f"{total_comments//len(filtered_participations):,}")
                    with col3:
                        st.metric("평균 조회수", f"{total_views//len(filtered_participations):,}")
            else:
                st.info("아직 성과 데이터가 없습니다. 인플루언서들의 성과를 입력해주세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_performance_crawling_modal():
    """성과 크롤링 모달 - 크롤링 기능이 제거되었습니다."""
    influencer = st.session_state.crawling_influencer
    
    st.subheader(f"🔍 {influencer.get('influencer_name') or influencer['sns_id']} 성과 크롤링")
    
    if st.button("❌ 닫기", key="close_crawling_modal"):
        del st.session_state.crawling_influencer
        st.rerun()
    
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")

def render_performance_input_modal():
    """성과 입력 모달 - 우측 레이아웃에 최적화"""
    influencer = st.session_state.inputting_performance
    
    # 인플루언서 정보 표시
    st.markdown(f"### 📝 {influencer.get('influencer_name') or influencer['sns_id']} 성과 입력")
    st.caption(f"캠페인: {influencer.get('campaign_name', 'N/A')} ({influencer.get('campaign_type', 'N/A')})")
    st.caption(f"플랫폼: {influencer.get('platform', 'N/A')} | 비용: {influencer.get('cost_krw', 0):,}원")
    
    if st.button("❌ 닫기", key="close_input_modal", help="성과 입력을 취소합니다"):
        del st.session_state.inputting_performance
        st.rerun()
    
    st.divider()
    
    # 컨텐츠 링크 표시 및 선택
    content_links = influencer.get('content_links', [])
    if content_links:
        st.markdown("**📎 컨텐츠 링크:**")
        selected_content_link = st.selectbox(
            "성과를 입력할 컨텐츠를 선택하세요",
            content_links,
            key="selected_content_link",
            help="인플루언서가 올린 컨텐츠별로 성과를 입력할 수 있습니다"
        )
    else:
        st.warning("컨텐츠 링크가 없습니다.")
        # 컨텐츠 링크가 없어도 성과 입력은 가능하도록 함
        selected_content_link = st.text_input(
            "컨텐츠 링크 (선택사항)",
            placeholder="https://...",
            key="manual_content_link",
            help="컨텐츠 링크를 직접 입력하거나 비워둘 수 있습니다"
        )
    
    # 성과 입력 폼 (컨텐츠 링크가 있든 없든 항상 표시)
    with st.form("performance_input_form"):
        st.markdown("**📊 성과 지표 입력**")
        
        # 지표 유형과 지표값을 같은 줄에 좌/우 배치
        col1, col2 = st.columns(2)
        with col1:
            metric_type = st.selectbox(
                "지표 유형",
                ["likes", "comments", "shares", "views", "clicks", "conversions"],
                format_func=lambda x: {
                    "likes": "👍 좋아요",
                    "comments": "💬 댓글",
                    "shares": "🔄 공유",
                    "views": "👁️ 조회수",
                    "clicks": "🖱️ 클릭수",
                    "conversions": "💰 전환수"
                }[x],
                key=f"metric_type_{influencer['id']}"
            )
        with col2:
            metric_value = st.number_input("지표 값", min_value=0, value=0, help="숫자만 입력하세요")
        
        # 정성평가는 별도로 길게 배치
        qualitative_evaluation = st.text_area(
            "정성평가",
            placeholder="컨텐츠의 품질, 반응, 브랜드 적합성 등에 대한 평가를 입력하세요...",
            key="qualitative_evaluation",
            help="컨텐츠의 품질에 대한 정성적 평가",
            height=100
        )
        
        # 저장 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.form_submit_button("💾 성과 저장", type="primary", use_container_width=True):
                # 성과 데이터 저장 (측정일은 현재 날짜로 자동 설정)
                from datetime import date
                
                # participation_id 가져오기
                participation_id = influencer.get('id')
                if not participation_id:
                    st.error("참여 정보를 찾을 수 없습니다.")
                else:
                    performance_metric = PerformanceMetric(
                        participation_id=participation_id,
                        content_link=selected_content_link,
                        metric_type=metric_type,
                        metric_value=metric_value,
                        measurement_date=date.today(),
                        qualitative_evaluation=qualitative_evaluation
                    )
                
                    result = db_manager.create_performance_metric(performance_metric)
                    if result["success"]:
                        st.success("✅ 성과가 저장되었습니다!")
                        st.rerun()
                    else:
                        st.error(f"❌ 저장 실패: {result['message']}")
    
    # 기존 성과 데이터 표시
    st.divider()
    st.markdown("**📈 기존 성과 데이터**")
    
    participation_id = influencer.get('id')
    if participation_id:
        contents = db_manager.get_campaign_influencer_contents(participation_id)
        if contents:
            for i, content in enumerate(contents):
                with st.expander(f"컨텐츠 {i+1}: {content.get('content_url', 'N/A')[:50]}...", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("좋아요", f"{content.get('likes', 0):,}")
                    with col2:
                        st.metric("댓글", f"{content.get('comments', 0):,}")
                    with col3:
                        st.metric("조회수", f"{content.get('views', 0):,}")
                    
                    if content.get('qualitative_note'):
                        st.caption(f"정성평가: {content['qualitative_note']}")
        else:
            st.info("아직 성과 데이터가 없습니다.")

def render_performance_detail_modal():
    """성과 상세보기 모달 - 우측 레이아웃에 최적화"""
    influencer = st.session_state.viewing_performance
    
    # 인플루언서 정보 표시
    st.markdown(f"### 📊 {influencer.get('influencer_name') or influencer['sns_id']} 성과 상세")
    st.caption(f"캠페인: {influencer.get('campaign_name', 'N/A')} ({influencer.get('campaign_type', 'N/A')})")
    st.caption(f"플랫폼: {influencer.get('platform', 'N/A')} | 비용: {influencer.get('cost_krw', 0):,}원")
    
    if st.button("❌ 닫기", key="close_detail_modal", help="상세보기를 닫습니다"):
        del st.session_state.viewing_performance
        st.rerun()
    
    st.divider()
    
    # participation_id 가져오기
    participation_id = influencer.get('id')
    if not participation_id:
        st.error("참여 정보를 찾을 수 없습니다.")
        return
    
    # 컨텐츠 성과 데이터 조회
    contents = db_manager.get_campaign_influencer_contents(participation_id)
    
    if contents:
        # 전체 성과 요약
        total_likes = sum(content.get('likes', 0) for content in contents)
        total_comments = sum(content.get('comments', 0) for content in contents)
        total_views = sum(content.get('views', 0) for content in contents)
        
        st.markdown("**📈 전체 성과 요약**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("❤️ 총 좋아요", f"{total_likes:,}")
        with col2:
            st.metric("💬 총 댓글", f"{total_comments:,}")
        with col3:
            st.metric("👁️ 총 조회수", f"{total_views:,}")
        
        # 평균 성과 계산
        if len(contents) > 0:
            st.markdown("**📊 평균 성과**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("평균 좋아요", f"{total_likes//len(contents):,}")
            with col2:
                st.metric("평균 댓글", f"{total_comments//len(contents):,}")
            with col3:
                st.metric("평균 조회수", f"{total_views//len(contents):,}")
        
        st.divider()
        
        # 컨텐츠별 상세 정보
        st.markdown("**📎 컨텐츠별 상세 성과**")
        for i, content in enumerate(contents):
            with st.expander(f"컨텐츠 {i+1}: {content.get('content_url', 'N/A')[:40]}...", expanded=False):
                # 성과 지표
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("좋아요", f"{content.get('likes', 0):,}")
                with col2:
                    st.metric("댓글", f"{content.get('comments', 0):,}")
                with col3:
                    st.metric("조회수", f"{content.get('views', 0):,}")
                
                # 컨텐츠 URL 표시
                if content.get('content_url'):
                    st.markdown(f"**🔗 컨텐츠 URL:**")
                    st.markdown(f"[{content['content_url']}]({content['content_url']})")
                
                # 정성평가 표시
                if content.get('qualitative_note'):
                    st.markdown("**📝 정성평가:**")
                    st.info(content['qualitative_note'])
                
                # 추가 정보가 있다면 표시
                if content.get('created_at'):
                    st.caption(f"📅 생성일: {content['created_at'][:10]}")
                
                # 수정 버튼
                if st.button(f"✏️ 성과 수정", key=f"edit_performance_{i}"):
                    st.session_state.inputting_performance = influencer
                    del st.session_state.viewing_performance
                    st.rerun()
    else:
        st.info("📊 성과 데이터가 없습니다.")
        
        # 컨텐츠 링크가 있는지 확인
        content_links = influencer.get('content_links', [])
        if content_links:
            st.markdown("**📎 등록된 컨텐츠 링크:**")
            for i, link in enumerate(content_links):
                st.markdown(f"{i+1}. [{link}]({link})")
            st.info("컨텐츠 링크는 있지만 성과 데이터가 없습니다. 성과를 입력해주세요.")
            
            # 성과 입력 버튼
            if st.button("📝 성과 입력하기", type="primary", use_container_width=True):
                st.session_state.inputting_performance = influencer
                del st.session_state.viewing_performance
                st.rerun()
        else:
            st.warning("컨텐츠 링크도 없습니다. 먼저 컨텐츠 링크를 추가해주세요.")

def render_performance_report_tab():
    """리포트 탭 - campaign_influencer_contents와 campaign_influencer_participations 테이블 기반 대시보드"""
    st.subheader("📋 성과 리포트")
    st.markdown("캠페인별 성과 데이터를 종합적으로 분석한 리포트를 제공합니다.")
    
    # 캠페인 목록 새로고침 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 데이터 새로고침", key="refresh_report_data", help="리포트 데이터를 새로 불러옵니다"):
            # 세션 상태를 초기화하여 데이터를 새로 불러오도록 함
            if 'campaigns_cache' in st.session_state:
                del st.session_state['campaigns_cache']
            if 'participations_cache' in st.session_state:
                del st.session_state['participations_cache']
            if 'contents_cache' in st.session_state:
                del st.session_state['contents_cache']
            st.success("리포트 데이터를 새로고침했습니다!")
            st.rerun()
    
    with col2:
        st.caption("리포트 데이터를 새로고침하려면 새로고침 버튼을 클릭하세요.")
    
    # 캠페인별로 참여 인플루언서 조회
    campaigns = db_manager.get_campaigns()
    
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    # 모든 캠페인의 참여 인플루언서와 성과 데이터를 가져와서 표시
    all_participations = []
    all_contents = []
    
    for campaign in campaigns:
        participations = db_manager.get_campaign_participations(campaign['id'])
        for participation in participations:
            participation['campaign_name'] = campaign['campaign_name']
            participation['campaign_type'] = campaign['campaign_type']
            all_participations.append(participation)
            
            # 각 참여자의 성과 데이터 조회
            contents = db_manager.get_campaign_influencer_contents(participation['id'])
            for content in contents:
                content['campaign_name'] = campaign['campaign_name']
                content['campaign_type'] = campaign['campaign_type']
                content['influencer_name'] = participation.get('connecta_influencers', {}).get('influencer_name', 'N/A')
                content['sns_id'] = participation.get('connecta_influencers', {}).get('sns_id', 'N/A')
                content['platform'] = participation.get('connecta_influencers', {}).get('platform', 'N/A')
                content['cost_krw'] = participation.get('cost_krw', 0)
                all_contents.append(content)
    
    if not all_participations:
        st.info("참여한 인플루언서가 없습니다.")
        return
    
    # 전체 요약 통계
    st.subheader("📊 전체 요약")
    
    # 기본 통계 계산
    total_participants = len(all_participations)
    total_cost = sum(p.get('cost_krw', 0) for p in all_participations)
    uploaded_count = sum(1 for p in all_participations if p.get('content_uploaded', False))
    
    # 성과 통계 계산
    total_likes = sum(c.get('likes', 0) for c in all_contents)
    total_comments = sum(c.get('comments', 0) for c in all_contents)
    total_views = sum(c.get('views', 0) for c in all_contents)
    total_shares = sum(c.get('shares', 0) for c in all_contents)
    total_clicks = sum(c.get('clicks', 0) for c in all_contents)
    total_conversions = sum(c.get('conversions', 0) for c in all_contents)
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 총 참여자", f"{total_participants}명")
        st.metric("💰 총 비용", f"{total_cost:,}원")
    with col2:
        st.metric("📤 업로드 완료", f"{uploaded_count}명")
        st.metric("📊 업로드율", f"{(uploaded_count/total_participants*100):.1f}%" if total_participants > 0 else "0%")
    with col3:
        st.metric("❤️ 총 좋아요", f"{total_likes:,}")
        st.metric("💬 총 댓글", f"{total_comments:,}")
    with col4:
        st.metric("👁️ 총 조회수", f"{total_views:,}")
        st.metric("🔄 총 공유", f"{total_shares:,}")
    
    st.divider()
    
    # 캠페인별 상세 분석
    st.subheader("📈 캠페인별 상세 분석")
    
    # 캠페인 선택
    campaign_names = list(set(p['campaign_name'] for p in all_participations))
    selected_campaign = st.selectbox("캠페인 선택", ["전체"] + campaign_names, key="report_campaign_select")
    
    # 선택된 캠페인에 따른 데이터 필터링
    if selected_campaign == "전체":
        filtered_participations = all_participations
        filtered_contents = all_contents
    else:
        filtered_participations = [p for p in all_participations if p['campaign_name'] == selected_campaign]
        filtered_contents = [c for c in all_contents if c['campaign_name'] == selected_campaign]
    
    if not filtered_participations:
        st.info("선택된 캠페인에 참여자가 없습니다.")
        return
    
    # 캠페인별 통계
    campaign_cost = sum(p.get('cost_krw', 0) for p in filtered_participations)
    campaign_uploaded = sum(1 for p in filtered_participations if p.get('content_uploaded', False))
    campaign_likes = sum(c.get('likes', 0) for c in filtered_contents)
    campaign_comments = sum(c.get('comments', 0) for c in filtered_contents)
    campaign_views = sum(c.get('views', 0) for c in filtered_contents)
    
    # ROI 계산 (간단한 지표)
    roi_likes = (campaign_likes / campaign_cost * 1000) if campaign_cost > 0 else 0  # 1000원당 좋아요 수
    roi_views = (campaign_views / campaign_cost * 1000) if campaign_cost > 0 else 0  # 1000원당 조회수
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("캠페인 비용", f"{campaign_cost:,}원")
        st.metric("업로드율", f"{(campaign_uploaded/len(filtered_participations)*100):.1f}%")
    with col2:
        st.metric("총 좋아요", f"{campaign_likes:,}")
        st.metric("총 댓글", f"{campaign_comments:,}")
    with col3:
        st.metric("총 조회수", f"{campaign_views:,}")
        st.metric("ROI (1000원당 좋아요)", f"{roi_likes:.1f}")
    
    st.divider()
    
    # 인플루언서별 성과 랭킹
    st.subheader("🏆 인플루언서별 성과 랭킹")
    
    # 인플루언서별 성과 집계
    influencer_performance = {}
    for content in filtered_contents:
        influencer_key = f"{content.get('influencer_name', 'N/A')} ({content.get('sns_id', 'N/A')})"
        if influencer_key not in influencer_performance:
            influencer_performance[influencer_key] = {
                'likes': 0,
                'comments': 0,
                'views': 0,
                'shares': 0,
                'clicks': 0,
                'conversions': 0,
                'cost': 0,
                'platform': content.get('platform', 'N/A')
            }
        
        influencer_performance[influencer_key]['likes'] += content.get('likes', 0)
        influencer_performance[influencer_key]['comments'] += content.get('comments', 0)
        influencer_performance[influencer_key]['views'] += content.get('views', 0)
        influencer_performance[influencer_key]['shares'] += content.get('shares', 0)
        influencer_performance[influencer_key]['clicks'] += content.get('clicks', 0)
        influencer_performance[influencer_key]['conversions'] += content.get('conversions', 0)
        influencer_performance[influencer_key]['cost'] += content.get('cost_krw', 0)
    
    # 정렬 기준 선택
    sort_by = st.selectbox("정렬 기준", ["좋아요", "댓글", "조회수", "공유", "클릭", "전환"], key="report_sort_by")
    
    # 정렬
    sort_key = {
        "좋아요": "likes",
        "댓글": "comments", 
        "조회수": "views",
        "공유": "shares",
        "클릭": "clicks",
        "전환": "conversions"
    }[sort_by]
    
    sorted_influencers = sorted(influencer_performance.items(), 
                              key=lambda x: x[1][sort_key], reverse=True)
    
    # 랭킹 표시
    for i, (influencer_name, performance) in enumerate(sorted_influencers[:10]):  # 상위 10명
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{i+1}위** {influencer_name}")
                st.caption(f"플랫폼: {performance['platform']}")
            
            with col2:
                st.metric("좋아요", f"{performance['likes']:,}")
            with col3:
                st.metric("댓글", f"{performance['comments']:,}")
            with col4:
                st.metric("조회수", f"{performance['views']:,}")
            with col5:
                st.metric("비용", f"{performance['cost']:,}원")
            
            st.divider()
    
    # 성과 트렌드 분석 (간단한 차트)
    if len(filtered_contents) > 0:
        st.subheader("📊 성과 트렌드")
        
        # 날짜별 성과 집계 (posted_at 기준)
        date_performance = {}
        for content in filtered_contents:
            if content.get('posted_at'):
                try:
                    # 날짜 파싱 (ISO 형식 가정)
                    date_str = content['posted_at'][:10]  # YYYY-MM-DD 부분만 추출
                    if date_str not in date_performance:
                        date_performance[date_str] = {'likes': 0, 'comments': 0, 'views': 0}
                    
                    date_performance[date_str]['likes'] += content.get('likes', 0)
                    date_performance[date_str]['comments'] += content.get('comments', 0)
                    date_performance[date_str]['views'] += content.get('views', 0)
                except:
                    continue
        
        if date_performance:
            # 날짜순 정렬
            sorted_dates = sorted(date_performance.items())
            
            # 간단한 차트 표시
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**일별 좋아요 트렌드**")
                for date, perf in sorted_dates:
                    st.write(f"{date}: {perf['likes']:,} 좋아요")
            
            with col2:
                st.write("**일별 조회수 트렌드**")
                for date, perf in sorted_dates:
                    st.write(f"{date}: {perf['views']:,} 조회수")
    
    # 샘플 상태별 분석
    st.subheader("📦 샘플 상태별 분석")
    
    sample_status_count = {}
    for participation in filtered_participations:
        status = participation.get('sample_status', '요청')
        if status not in sample_status_count:
            sample_status_count[status] = 0
        sample_status_count[status] += 1
    
    if sample_status_count:
        col1, col2, col3, col4 = st.columns(4)
        status_icons = {
            '요청': '📋',
            '발송준비': '📦',
            '발송완료': '🚚',
            '수령': '✅'
        }
        
        for i, (status, count) in enumerate(sample_status_count.items()):
            with [col1, col2, col3, col4][i % 4]:
                icon = status_icons.get(status, '📊')
                st.metric(f"{icon} {status}", f"{count}명")
    
    # 정성평가 요약
    qualitative_notes = [c.get('qualitative_note') for c in filtered_contents if c.get('qualitative_note')]
    if qualitative_notes:
        st.subheader("📝 정성평가 요약")
        st.write("**등록된 정성평가:**")
        for i, note in enumerate(qualitative_notes[:5]):  # 최대 5개만 표시
            st.write(f"{i+1}. {note}")
        
        if len(qualitative_notes) > 5:
            st.caption(f"... 외 {len(qualitative_notes) - 5}개 더")
