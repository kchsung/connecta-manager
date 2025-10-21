"""
캠페인 참여 인플루언서 추가 관련 UI 컴포넌트
"""
import streamlit as st
from src.db.database import db_manager
from src.db.models import CampaignInfluencerParticipation
from .common_functions import search_single_influencer, search_single_influencer_by_platform, safe_int_conversion

def render_participation_add():
    """참여 인플루언서 추가 메인 컴포넌트"""
    st.markdown("### ➕ 참여 인플루언서 추가")
    st.markdown("캠페인에 참여할 인플루언서를 검색하고 추가합니다.")
    
    # 캠페인 선택
    campaigns = db_manager.get_campaigns()
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    from .common_functions import format_campaign_type
    campaign_options = {f"{c['campaign_name']} ({format_campaign_type(c['campaign_type'])})": c for c in campaigns}
    selected_campaign_name = st.selectbox(
        "참여 인플루언서를 추가할 캠페인을 선택하세요",
        list(campaign_options.keys()),
        key="add_participation_campaign_select"
    )
    
    if selected_campaign_name:
        selected_campaign = campaign_options[selected_campaign_name]
        st.markdown(f"**선택된 캠페인:** {selected_campaign.get('campaign_name', 'N/A')} ({format_campaign_type(selected_campaign.get('campaign_type', ''))})")
        
        # 인플루언서 추가 워크플로우
        render_add_influencer_workflow(selected_campaign)

def render_add_influencer_workflow(selected_campaign):
    """인플루언서 추가 워크플로우"""
   
    # 좌우 분할 레이아웃
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("##### 🔍 인플루언서 검색")
        render_influencer_search_section()
    
    with col2:
        st.markdown("##### 📝 인플루언서 추가 정보")
        render_influencer_add_form(selected_campaign)

def render_influencer_search_section():
    """인플루언서 검색 섹션"""
    # 검색 섹션 - 폼 구조로 변경
    with st.form("add_influencer_search_form"):
        search_term = st.text_input("인플루언서 검색", placeholder="SNS ID 또는 이름을 입력하세요", key="add_influencer_search", help="등록자 검색")
        search_platform = st.selectbox("플랫폼", ["전체", "instagram", "youtube", "tiktok", "twitter"], key="add_influencer_platform")
        
        search_clicked = st.form_submit_button("🔍 검색", type="primary", key="search_influencer_for_add")
    
    if search_clicked:
        if not search_term:
            st.error("검색어를 입력해주세요.")
        else:
            # 인플루언서 검색 로직
            if search_platform == "전체":
                search_response = search_single_influencer(search_term)
            else:
                search_response = search_single_influencer_by_platform(search_term, search_platform)
            
            if search_response and search_response.get("success") and search_response.get("data"):
                search_data = search_response["data"]
                if isinstance(search_data, list) and len(search_data) > 0:
                    search_result = search_data[0]
                elif isinstance(search_data, dict):
                    search_result = search_data
                else:
                    search_result = None
                
                if search_result:
                    st.session_state.add_influencer_search_result = search_result
                    st.success(f"✅ 인플루언서를 찾았습니다: {search_result.get('influencer_name') or search_result['sns_id']} ({search_result.get('platform')})")
                else:
                    st.error(f"❌ '{search_term}'을(를) 찾을 수 없습니다.")
            else:
                st.error(f"❌ '{search_term}'을(를) 찾을 수 없습니다.")
    
    # 검색 결과 표시
    if 'add_influencer_search_result' in st.session_state:
        search_result = st.session_state.add_influencer_search_result
        render_influencer_search_card(search_result)

def render_influencer_search_card(search_result):
    """인플루언서 검색 결과 카드"""
    st.markdown("---")
    st.markdown("**🔍 검색 결과**")
    
    # 카드 스타일 적용
    with st.container():
        st.markdown("""
        <div style="
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        ">
        """, unsafe_allow_html=True)
        
        # 인플루언서 정보를 컴팩트하게 표시
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**👤 {search_result.get('influencer_name', 'N/A')}**")
            st.markdown(f"**📱 {search_result.get('sns_id', 'N/A')}**")
            st.markdown(f"**🌐 {search_result.get('platform', 'N/A').upper()}**")
        
        with col2:
            followers = search_result.get('followers_count', 0)
            if followers:
                st.metric("팔로워", f"{followers:,}명")
            else:
                st.metric("팔로워", "N/A")
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_influencer_add_form(selected_campaign):
    """인플루언서 추가 폼"""
    if 'add_influencer_search_result' not in st.session_state:
        st.info("좌측에서 인플루언서를 검색해주세요.")
        return
    
    search_result = st.session_state.add_influencer_search_result
    st.markdown(f"**선택된 인플루언서:** {search_result.get('influencer_name') or search_result['sns_id']} ({search_result.get('platform')})")
    
    # campaign_id 안전하게 추출
    if isinstance(selected_campaign, dict):
        campaign_id = selected_campaign.get('id', '')
    else:
        campaign_id = str(selected_campaign)
    
    # 기존 참여 정보 조회
    existing_participation = None
    if 'add_influencer_search_result' in st.session_state:
        influencer_id = search_result['id']
        participation_result = db_manager.get_participation_by_campaign_and_influencer(campaign_id, influencer_id)
        if participation_result.get('success') and participation_result.get('data'):
            existing_participation = participation_result['data']
            st.info("📝 기존 참여 정보가 있습니다. 아래에서 수정할 수 있습니다.")
    
    with st.form("add_participation_form"):
        # 데이터베이스 스키마에 맞는 필드들 (기존 값으로 초기화)
        manager_comment = st.text_area(
            "매니저 코멘트", 
            value=existing_participation.get('manager_comment', '') if existing_participation else '',
            placeholder="매니저가 작성하는 코멘트", 
            key="add_manager_comment"
        )
        influencer_requests = st.text_area(
            "인플루언서 요청사항", 
            value=existing_participation.get('influencer_requests', '') if existing_participation else '',
            placeholder="인플루언서의 요청사항", 
            key="add_influencer_requests"
        )
        memo = st.text_area(
            "메모", 
            value=existing_participation.get('memo', '') if existing_participation else '',
            placeholder="기타 메모", 
            key="add_memo"
        )
        
        # 샘플 상태 선택 (기존 값으로 초기화)
        current_sample_status = existing_participation.get('sample_status', '요청') if existing_participation else '요청'
        sample_status_options = ["요청", "발송준비", "발송완료", "수령"]
        sample_status_index = sample_status_options.index(current_sample_status) if current_sample_status in sample_status_options else 0
        
        sample_status = st.selectbox(
            "샘플 상태",
            sample_status_options,
            index=sample_status_index,
            key="add_sample_status",
            format_func=lambda x: {
                "요청": "📋 요청",
                "발송준비": "📦 발송준비",
                "발송완료": "🚚 발송완료",
                "수령": "✅ 수령"
            }[x]
        )
        
        influencer_feedback = st.text_area(
            "인플루언서 피드백", 
            value=existing_participation.get('influencer_feedback', '') if existing_participation else '',
            placeholder="인플루언서의 피드백", 
            key="add_influencer_feedback"
        )
        content_uploaded = st.checkbox(
            "콘텐츠 업로드 완료", 
            value=existing_participation.get('content_uploaded', False) if existing_participation else False,
            key="add_content_uploaded"
        )
        cost_krw = st.number_input(
            "비용 (원)", 
            min_value=0, 
            value=safe_int_conversion(existing_participation.get('cost_krw', 0)) if existing_participation else 0, 
            step=1000, 
            key="add_cost_krw"
        )
        
        # 버튼 텍스트와 동작 결정
        if existing_participation:
            button_text = "💾 참여 정보 업데이트"
            button_type = "secondary"
        else:
            button_text = "➕ 인플루언서 추가"
            button_type = "primary"
        
        # 버튼들을 컬럼으로 배치
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.form_submit_button(button_text, type=button_type):
                # campaign_id 안전하게 추출 (이미 위에서 추출했지만 다시 확인)
                if isinstance(selected_campaign, dict):
                    campaign_id = selected_campaign.get('id', '')
                else:
                    campaign_id = str(selected_campaign)
                
                # influencer_id도 안전하게 추출
                influencer_id = search_result.get('id', '')
                
                # 데이터베이스 스키마에 맞는 필드로 참여 정보 생성
                participation_data = {
                    'campaign_id': campaign_id,
                    'influencer_id': influencer_id,
                    'manager_comment': manager_comment,
                    'influencer_requests': influencer_requests,
                    'memo': memo,
                    'sample_status': sample_status,
                    'influencer_feedback': influencer_feedback,
                    'content_uploaded': content_uploaded,
                    'cost_krw': cost_krw,
                    'content_links': existing_participation.get('content_links', []) if existing_participation else []  # 기존 링크 유지
                }
                
                
                if existing_participation:
                    # 기존 참여 정보 업데이트
                    result = db_manager.update_campaign_participation(existing_participation['id'], participation_data)
                    if result["success"]:
                        st.success("참여 정보가 업데이트되었습니다!")
                    else:
                        st.error(f"참여 정보 업데이트 실패: {result['message']}")
                else:
                    # 새 참여 정보 추가
                    result = db_manager.add_influencer_to_campaign(participation_data)
                    if result["success"]:
                        st.success("인플루언서가 캠페인에 추가되었습니다!")
                    else:
                        st.error(f"인플루언서 추가 실패: {result['message']}")
                
                # 성공 시 세션 상태 초기화 및 캐시 초기화
                if result.get("success"):
                    if 'add_influencer_search_result' in st.session_state:
                        del st.session_state['add_influencer_search_result']
                    if "participations_cache" in st.session_state:
                        del st.session_state["participations_cache"]
                    st.session_state.participation_added = True  # 참여 추가 완료 플래그
                    # 리렌더링 없이 상태 기반 UI 업데이트
        
        with col2:
            # 기존 참여 정보가 있을 때만 삭제 버튼 표시
            if existing_participation:
                if st.form_submit_button("🗑️ 참여 삭제", type="secondary"):
                    # 삭제 확인을 위한 세션 상태 설정
                    st.session_state[f"confirm_delete_participation_{existing_participation['id']}"] = True
                    # 리렌더링 없이 상태 기반 UI 업데이트
    
    # 삭제 확인 다이얼로그 (폼 외부에 위치)
    if existing_participation and st.session_state.get(f"confirm_delete_participation_{existing_participation['id']}", False):
        st.markdown("---")
        st.warning("⚠️ **정말로 이 인플루언서의 캠페인 참여를 삭제하시겠습니까?**")
        st.markdown(f"**삭제할 인플루언서:** {search_result.get('influencer_name') or search_result['sns_id']} ({search_result.get('platform')})")
        st.markdown(f"**캠페인:** {selected_campaign.get('campaign_name', 'N/A')}")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ 삭제 확인", type="primary", key=f"delete_confirm_{existing_participation['id']}"):
                # 실제 삭제 실행
                result = db_manager.remove_influencer_from_campaign(existing_participation['id'])
                if result["success"]:
                    st.success("인플루언서의 캠페인 참여가 삭제되었습니다!")
                    # 세션 상태 정리
                    del st.session_state[f"confirm_delete_participation_{existing_participation['id']}"]
                    if 'add_influencer_search_result' in st.session_state:
                        del st.session_state['add_influencer_search_result']
                    if "participations_cache" in st.session_state:
                        del st.session_state["participations_cache"]
                    st.session_state.participation_deleted = True  # 참여 삭제 완료 플래그
                    # 리렌더링 없이 상태 기반 UI 업데이트
                else:
                    st.error(f"삭제 실패: {result['message']}")
        
        with col2:
            if st.button("❌ 취소", key=f"delete_cancel_{existing_participation['id']}"):
                del st.session_state[f"confirm_delete_participation_{existing_participation['id']}"]
                # 리렌더링 없이 상태 기반 UI 업데이트
        
        with col3:
            st.empty()  # 빈 공간
