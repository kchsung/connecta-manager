"""
캠페인 참여 인플루언서 목록 및 편집 관련 UI 컴포넌트
"""
import streamlit as st
import pandas as pd
from src.db.database import db_manager
from .common_functions import format_campaign_type, format_sample_status

@st.cache_data(ttl=300)  # 5분 캐시
def get_cached_campaigns():
    """캠페인 목록 캐싱"""
    return db_manager.get_campaigns()

@st.cache_data(ttl=60)  # 1분 캐시
def get_cached_participations(campaign_id: str):
    """참여 인플루언서 목록 캐싱"""
    return db_manager.get_all_campaign_participations(campaign_id)

def render_participation_list():
    """참여 인플루언서 목록 및 편집 메인 컴포넌트"""
    st.markdown("### 📋 참여 인플루언서 목록 / 편집")
    st.markdown("캠페인에 참여하는 인플루언서 목록을 조회하고 편집합니다.")
    
    # 캠페인 선택 (캐싱 적용)
    campaigns = get_cached_campaigns()
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    # 캠페인 선택과 검색 기능을 한 줄로 배치
    col1, col2 = st.columns([2, 1])
    
    with col1:
        campaign_options = {f"{c['campaign_name']} ({format_campaign_type(c['campaign_type'])})": c for c in campaigns}
        selected_campaign_name = st.selectbox(
            "관리할 캠페인을 선택하세요",
            list(campaign_options.keys()),
            key="list_participation_campaign_select"
        )
    
    with col2:
        # 인플루언서 검색 기능
        search_term = st.text_input(
            "🔍 인플루언서 검색",
            placeholder="이름 또는 SNS ID로 검색...",
            key="influencer_search_input",
            help="인플루언서 이름이나 SNS ID로 검색할 수 있습니다"
        )
    
    if selected_campaign_name:
        selected_campaign = campaign_options[selected_campaign_name]
        st.markdown(f"**선택된 캠페인:** {selected_campaign.get('campaign_name', 'N/A')} ({format_campaign_type(selected_campaign.get('campaign_type', ''))})")
        
        # 참여 인플루언서 목록 (캐싱 적용)
        participations = get_cached_participations(selected_campaign.get('id', ''))
        
        if not participations:
            st.info("이 캠페인에 참여한 인플루언서가 없습니다.")
        else:
            # 검색어가 있으면 필터링
            if search_term and search_term.strip():
                filtered_participations = []
                search_lower = search_term.strip().lower()
                
                for participation in participations:
                    influencer_name = participation.get('influencer_name', '').lower()
                    sns_id = participation.get('sns_id', '').lower()
                    
                    if search_lower in influencer_name or search_lower in sns_id:
                        filtered_participations.append(participation)
                
                participations = filtered_participations
                
                # 검색 결과 표시
                if participations:
                    st.success(f"🔍 '{search_term}' 검색 결과: {len(participations)}명의 인플루언서를 찾았습니다.")
                else:
                    st.warning(f"🔍 '{search_term}'에 대한 검색 결과가 없습니다.")
            
            # 좌우 분할 레이아웃으로 변경
            render_participation_list_with_cards(participations, selected_campaign)

def render_participation_list_with_cards(participations, selected_campaign):
    """좌우 분할 레이아웃으로 참여 인플루언서 목록 표시"""
    # 세션 상태 초기화
    if 'selected_participation_id' not in st.session_state:
        st.session_state.selected_participation_id = None
    
    # 좌우 분할 레이아웃
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 👥 참여 인플루언서 목록")
        render_influencer_cards(participations)
    
    with col2:
        st.markdown("#### ✏️ 상세 정보 편집")
        if st.session_state.selected_participation_id:
            selected_participation = next(
                (p for p in participations if p.get('id') == st.session_state.selected_participation_id), 
                None
            )
            if selected_participation:
                render_participation_detail_form(selected_participation, selected_campaign)
            else:
                st.info("선택된 인플루언서 정보를 찾을 수 없습니다.")
        else:
            st.info("좌측에서 편집할 인플루언서를 선택해주세요.")

def render_influencer_cards(participations):
    """인플루언서 목록을 카드 형태로 표시"""
    if not participations:
        st.info("참여 인플루언서가 없습니다.")
        return
    
    # 스크롤 가능한 컨테이너
    with st.container():
        for i, participation in enumerate(participations):
            # 카드 스타일 적용
            is_selected = st.session_state.selected_participation_id == participation.get('id')
            
            if is_selected:
                card_style = """
                <div style="
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 12px;
                    padding: 16px;
                    margin: 12px 0;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
                ">
                """
            else:
                card_style = """
                <div style="
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 16px;
                    margin: 12px 0;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                ">
                """
            
            # 카드 자체를 버튼으로 만들기
            influencer_name = participation.get('influencer_name', 'N/A')
            sns_id = participation.get('sns_id', 'N/A')
            platform = participation.get('platform', 'N/A').upper()
            status = "✅ 완료" if participation.get('content_uploaded', False) else "⏳ 대기"
            
            # 카드 내용을 버튼 텍스트로 구성
            button_text = f"👤 {influencer_name}  📱 {sns_id}  🌐 {platform}  {status}"
            
            # 카드 스타일을 버튼에 적용 (너비 일정하게)
            button_style = """
            <style>
            .stButton > button {
                width: 100% !important;
                min-width: 100% !important;
                max-width: 100% !important;
                height: 60px;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                background-color: #ffffff;
                color: #333333;
                font-weight: bold;
                font-size: 14px;
                text-align: left;
                padding: 16px;
                margin: 12px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .stButton > button:hover {
                background-color: #f5f5f5;
                border-color: #2196f3;
                box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
            }
            </style>
            """
            
            # 선택된 카드 스타일
            if is_selected:
                button_style = """
                <style>
                .stButton > button {
                    width: 100% !important;
                    min-width: 100% !important;
                    max-width: 100% !important;
                    height: 60px;
                    border-radius: 12px;
                    border: 2px solid #2196f3;
                    background-color: #e3f2fd;
                    color: #333333;
                    font-weight: bold;
                    font-size: 14px;
                    text-align: left;
                    padding: 16px;
                    margin: 12px 0;
                    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
                    transition: all 0.3s ease;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .stButton > button:hover {
                    background-color: #bbdefb;
                    border-color: #1976d2;
                    box-shadow: 0 6px 16px rgba(33, 150, 243, 0.4);
                }
                </style>
                """
            
            st.markdown(button_style, unsafe_allow_html=True)
            
            # 카드 전체를 클릭 가능한 버튼으로 만들기
            if st.button(button_text, key=f"card_button_{participation.get('id')}", help="이 인플루언서를 선택하여 편집"):
                st.session_state.selected_participation_id = participation.get('id')
                st.rerun()

def render_participation_detail_form(participation, selected_campaign):
    """선택된 인플루언서의 상세 정보 편집 폼"""
    st.markdown(f"**선택된 인플루언서:** {participation.get('influencer_name', 'N/A')} ({participation.get('platform', 'N/A')})")
    
    # connecta_influencers 테이블 정보 (읽기 전용)
    st.markdown("##### 📋 인플루언서 기본 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("플랫폼", value=participation.get('platform', ''), disabled=True, key="readonly_platform")
        st.text_input("SNS ID", value=participation.get('sns_id', ''), disabled=True, key="readonly_sns_id")
        st.text_input("인플루언서명", value=participation.get('influencer_name', ''), disabled=True, key="readonly_name")
        
        # SNS URL을 클릭 가능한 링크로 표시
        sns_url = participation.get('sns_url', '')
        
        # 디버깅 정보 표시 (개발용)
        if st.checkbox("🔍 디버깅 정보 표시", key="debug_info"):
            st.markdown("**Participation 데이터 구조:**")
            st.json(participation)
            st.markdown(f"**SNS URL 값:** `{repr(sns_url)}`")
            st.markdown(f"**SNS URL 타입:** `{type(sns_url)}`")
            st.markdown(f"**SNS URL 길이:** `{len(sns_url) if sns_url else 0}`")
            
            # 캐시 초기화 버튼
            if st.button("🔄 캐시 초기화 및 새로고침", key="clear_cache"):
                # 모든 캐시 초기화
                if "participations_cache" in st.session_state:
                    del st.session_state["participations_cache"]
                st.cache_data.clear()
                st.rerun()
        
        if sns_url and sns_url.strip():
            st.markdown(f"**SNS URL:** [{sns_url}]({sns_url})")
        else:
            st.text_input("SNS URL", value="등록되지 않음", disabled=True, key="readonly_url")
            st.caption("⚠️ 이 인플루언서의 SNS URL이 데이터베이스에 등록되지 않았습니다.")
    
    with col2:
        st.number_input("팔로워 수", value=participation.get('followers_count', 0), disabled=True, key="readonly_followers")
        st.text_input("연락방법", value=participation.get('contact_method', ''), disabled=True, key="readonly_contact")
        st.text_input("전화번호", value=participation.get('phone_number', ''), disabled=True, key="readonly_phone")
        st.text_input("이메일", value=participation.get('email', ''), disabled=True, key="readonly_email")
    
    
    # campaign_influencer_participations 테이블 정보 (편집 가능)
    st.markdown("##### ✏️ 캠페인 참여 정보")
    
    with st.form("participation_edit_form"):
        # 샘플 상태
        sample_status_options = ["요청", "발송준비", "발송완료", "수령"]
        current_sample_status = participation.get('sample_status', '요청')
        sample_status_index = sample_status_options.index(current_sample_status) if current_sample_status in sample_status_options else 0
        
        sample_status = st.selectbox(
            "샘플 상태",
            sample_status_options,
            index=sample_status_index,
            key="detail_sample_status"
        )
        
        # 업로드 완료 여부
        content_uploaded = st.checkbox(
            "콘텐츠 업로드 완료",
            value=participation.get('content_uploaded', False),
            key="detail_content_uploaded"
        )
        
        # 비용
        cost_krw = st.number_input(
            "비용 (원)",
            min_value=0,
            value=int(participation.get('cost_krw', 0)) if participation.get('cost_krw') else 0,
            step=1000,
            key="detail_cost_krw"
        )
        
        # 텍스트 필드들
        manager_comment = st.text_area(
            "매니저 코멘트",
            value=participation.get('manager_comment', ''),
            key="detail_manager_comment",
            max_chars=500
        )
        
        influencer_requests = st.text_area(
            "인플루언서 요청사항",
            value=participation.get('influencer_requests', ''),
            key="detail_influencer_requests",
            max_chars=500
        )
        
        influencer_feedback = st.text_area(
            "인플루언서 피드백",
            value=participation.get('influencer_feedback', ''),
            key="detail_influencer_feedback",
            max_chars=500
        )
        
        memo = st.text_area(
            "메모",
            value=participation.get('memo', ''),
            key="detail_memo",
            max_chars=500
        )
        
        # 버튼들
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 저장", type="primary"):
                save_participation_detail(participation, {
                    'sample_status': sample_status,
                    'content_uploaded': content_uploaded,
                    'cost_krw': cost_krw,
                    'manager_comment': manager_comment,
                    'influencer_requests': influencer_requests,
                    'influencer_feedback': influencer_feedback,
                    'memo': memo
                })
        
        with col2:
            if st.form_submit_button("🔄 새로고침"):
                st.rerun()
        
        with col3:
            if st.form_submit_button("❌ 선택 해제"):
                st.session_state.selected_participation_id = None
                st.rerun()
    
    # 캠페인 성과 정보 입력 섹션
    st.markdown("---")
    st.markdown("##### 📊 캠페인 성과 정보")
    render_campaign_performance_section(participation)

def render_campaign_performance_section(participation):
    """캠페인 성과 정보 입력 섹션"""
    participation_id = participation.get('id')
    
    # 기존 콘텐츠 데이터 조회
    existing_contents = db_manager.get_campaign_influencer_contents(participation_id)
    
    # 콘텐츠 추가/편집 탭
    tab1, tab2 = st.tabs(["📝 콘텐츠 추가", "📋 기존 콘텐츠 관리"])
    
    with tab1:
        render_add_content_form(participation_id)
    
    with tab2:
        render_existing_contents(existing_contents)

def render_add_content_form(participation_id):
    """새 콘텐츠 추가 폼"""
    with st.form("add_content_form"):
        st.markdown("**새 콘텐츠 성과 정보 입력**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_url = st.text_input(
                "콘텐츠 URL *",
                placeholder="https://instagram.com/p/...",
                help="콘텐츠의 URL을 입력하세요",
                key="new_content_url"
            )
            
            posted_at = st.date_input(
                "게시일",
                value=None,
                help="콘텐츠가 게시된 날짜",
                key="new_posted_at"
            )
            
            caption = st.text_area(
                "캡션",
                placeholder="콘텐츠의 캡션 내용",
                max_chars=1000,
                key="new_caption"
            )
            
            qualitative_note = st.text_area(
                "정성평가",
                placeholder="콘텐츠에 대한 정성적 평가",
                max_chars=500,
                key="new_qualitative_note"
            )
        
        with col2:
            likes = st.number_input(
                "좋아요 수",
                min_value=0,
                value=0,
                key="new_likes"
            )
            
            comments = st.number_input(
                "댓글 수",
                min_value=0,
                value=0,
                key="new_comments"
            )
            
            shares = st.number_input(
                "공유 수",
                min_value=0,
                value=0,
                key="new_shares"
            )
            
            views = st.number_input(
                "조회 수",
                min_value=0,
                value=0,
                key="new_views"
            )
            
            clicks = st.number_input(
                "클릭 수",
                min_value=0,
                value=0,
                key="new_clicks"
            )
            
            conversions = st.number_input(
                "전환 수",
                min_value=0,
                value=0,
                key="new_conversions"
            )
            
            is_rels = st.number_input(
                "REL 수",
                min_value=0,
                value=0,
                key="new_is_rels"
            )
        
        if st.form_submit_button("➕ 콘텐츠 추가", type="primary"):
            if not content_url:
                st.error("콘텐츠 URL은 필수 입력 항목입니다.")
            else:
                # 콘텐츠 데이터 준비
                content_data = {
                    'participation_id': participation_id,
                    'content_url': content_url,
                    'posted_at': posted_at.isoformat() if posted_at else None,
                    'caption': caption if caption else None,
                    'qualitative_note': qualitative_note if qualitative_note else None,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'views': views,
                    'clicks': clicks,
                    'conversions': conversions,
                    'is_rels': is_rels
                }
                
                # 데이터베이스에 저장
                result = db_manager.create_campaign_influencer_content(content_data)
                
                if result.get("success"):
                    st.success("✅ 콘텐츠가 성공적으로 추가되었습니다!")
                    st.rerun()
                else:
                    st.error(f"❌ 콘텐츠 추가 실패: {result.get('message', '알 수 없는 오류')}")

def render_existing_contents(existing_contents):
    """기존 콘텐츠 관리"""
    if not existing_contents:
        st.info("등록된 콘텐츠가 없습니다.")
        return
    
    st.markdown(f"**등록된 콘텐츠 ({len(existing_contents)}개)**")
    
    for i, content in enumerate(existing_contents):
        with st.expander(f"콘텐츠 {i+1}: {content.get('content_url', 'N/A')[:50]}..."):
            render_content_edit_form(content)

def render_content_edit_form(content):
    """콘텐츠 편집 폼"""
    content_id = content.get('id')
    
    with st.form(f"edit_content_form_{content_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            content_url = st.text_input(
                "콘텐츠 URL",
                value=content.get('content_url', ''),
                key=f"edit_url_{content_id}"
            )
            
            posted_at_str = content.get('posted_at', '')
            posted_at = None
            if posted_at_str:
                try:
                    from datetime import datetime
                    posted_at = datetime.fromisoformat(posted_at_str.replace('Z', '+00:00')).date()
                except:
                    pass
            
            posted_at = st.date_input(
                "게시일",
                value=posted_at,
                key=f"edit_posted_at_{content_id}"
            )
            
            caption = st.text_area(
                "캡션",
                value=content.get('caption', ''),
                max_chars=1000,
                key=f"edit_caption_{content_id}"
            )
            
            qualitative_note = st.text_area(
                "정성평가",
                value=content.get('qualitative_note', ''),
                max_chars=500,
                key=f"edit_qualitative_note_{content_id}"
            )
        
        with col2:
            likes = st.number_input(
                "좋아요 수",
                min_value=0,
                value=content.get('likes', 0),
                key=f"edit_likes_{content_id}"
            )
            
            comments = st.number_input(
                "댓글 수",
                min_value=0,
                value=content.get('comments', 0),
                key=f"edit_comments_{content_id}"
            )
            
            shares = st.number_input(
                "공유 수",
                min_value=0,
                value=content.get('shares', 0),
                key=f"edit_shares_{content_id}"
            )
            
            views = st.number_input(
                "조회 수",
                min_value=0,
                value=content.get('views', 0),
                key=f"edit_views_{content_id}"
            )
            
            clicks = st.number_input(
                "클릭 수",
                min_value=0,
                value=content.get('clicks', 0),
                key=f"edit_clicks_{content_id}"
            )
            
            conversions = st.number_input(
                "전환 수",
                min_value=0,
                value=content.get('conversions', 0),
                key=f"edit_conversions_{content_id}"
            )
            
            is_rels = st.number_input(
                "REL 수",
                min_value=0,
                value=content.get('is_rels', 0),
                key=f"edit_is_rels_{content_id}"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 저장", type="primary"):
                # 업데이트 데이터 준비
                update_data = {
                    'content_url': content_url,
                    'posted_at': posted_at.isoformat() if posted_at else None,
                    'caption': caption if caption else None,
                    'qualitative_note': qualitative_note if qualitative_note else None,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'views': views,
                    'clicks': clicks,
                    'conversions': conversions,
                    'is_rels': is_rels
                }
                
                # 데이터베이스 업데이트
                result = db_manager.update_campaign_influencer_content(content_id, update_data)
                
                if result.get("success"):
                    st.success("✅ 콘텐츠가 성공적으로 업데이트되었습니다!")
                    st.rerun()
                else:
                    st.error(f"❌ 업데이트 실패: {result.get('message', '알 수 없는 오류')}")
        
        with col2:
            if st.form_submit_button("🗑️ 삭제", type="secondary"):
                # 삭제 확인
                st.session_state[f"confirm_delete_content_{content_id}"] = True
        
        with col3:
            st.empty()  # 빈 공간
    
    # 삭제 확인 다이얼로그
    if st.session_state.get(f"confirm_delete_content_{content_id}", False):
        st.warning("⚠️ **정말로 이 콘텐츠를 삭제하시겠습니까?**")
        st.markdown(f"**삭제할 콘텐츠:** {content.get('content_url', 'N/A')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ 삭제 확인", type="primary", key=f"delete_confirm_{content_id}"):
                result = db_manager.delete_campaign_influencer_content(content_id)
                if result.get("success"):
                    st.success("✅ 콘텐츠가 삭제되었습니다!")
                    del st.session_state[f"confirm_delete_content_{content_id}"]
                    st.rerun()
                else:
                    st.error(f"❌ 삭제 실패: {result.get('message', '알 수 없는 오류')}")
        
        with col2:
            if st.button("❌ 취소", key=f"delete_cancel_{content_id}"):
                del st.session_state[f"confirm_delete_content_{content_id}"]
                st.rerun()

def save_participation_detail(participation, update_data):
    """참여 인플루언서 상세 정보 저장"""
    try:
        participation_id = participation.get('id')
        if not participation_id:
            st.error("참여 정보 ID를 찾을 수 없습니다.")
            return
        
        # 데이터베이스 업데이트
        result = db_manager.update_campaign_participation(participation_id, update_data)
        
        if result["success"]:
            st.success("✅ 참여 인플루언서 정보가 업데이트되었습니다!")
            # 캐시 초기화
            if "participations_cache" in st.session_state:
                del st.session_state["participations_cache"]
        else:
            st.error(f"❌ 업데이트 실패: {result['message']}")
            
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")
        import traceback
        st.code(traceback.format_exc())

def render_participation_list_table(participations):
    """참여 인플루언서 목록 테이블 (편집 가능)"""
    # 참여 인플루언서 목록을 편집 가능한 테이블로 표시
    participation_data = []
    for participation in participations:
        participation_data.append({
            "ID": participation.get('id'),  # 숨겨진 ID 필드
            "인플루언서": participation.get('influencer_name', participation.get('sns_id', '')),
            "플랫폼": participation.get('platform', 'instagram'),
            "SNS ID": participation.get('sns_id', ''),
            "샘플 상태": participation.get('sample_status', '요청'),
            "업로드 완료": participation.get('content_uploaded', False),
            "비용": participation.get('cost_krw', 0) or 0,
            "매니저코멘트": participation.get('manager_comment', ''),
            "인플루언서요청사항": participation.get('influencer_requests', ''),
            "인플루언서피드백": participation.get('influencer_feedback', ''),
            "메모": participation.get('memo', ''),
            "참여일": participation.get('created_at', '')[:10] if participation.get('created_at') else "N/A"
        })
    
    if participation_data:
        df = pd.DataFrame(participation_data)
        
        # 컬럼 설정
        column_config = {
            "ID": st.column_config.NumberColumn("ID", disabled=True, help="참여 인플루언서 고유 ID"),
            "인플루언서": st.column_config.TextColumn(
                "인플루언서",
                help="인플루언서 이름 (읽기 전용)",
                disabled=True,
            ),
            "플랫폼": st.column_config.TextColumn(
                "플랫폼",
                help="SNS 플랫폼 (읽기 전용)",
                disabled=True,
            ),
            "SNS ID": st.column_config.TextColumn(
                "SNS ID", 
                help="SNS 계정 ID (읽기 전용)",
                disabled=True,
            ),
            "샘플 상태": st.column_config.SelectboxColumn(
                "샘플 상태",
                help="샘플 발송 상태",
                options=["요청", "발송준비", "발송완료", "수령"],
            ),
            "업로드 완료": st.column_config.CheckboxColumn(
                "업로드 완료",
                help="콘텐츠 업로드 완료 여부",
            ),
            "비용": st.column_config.NumberColumn(
                "비용 (원)",
                help="협찬 비용",
                min_value=0,
                step=1,
                format="%d원",
            ),
            "매니저코멘트": st.column_config.TextColumn(
                "매니저코멘트",
                help="매니저 코멘트",
                max_chars=500,
            ),
            "인플루언서요청사항": st.column_config.TextColumn(
                "인플루언서요청사항",
                help="인플루언서 요청사항",
                max_chars=500,
            ),
            "인플루언서피드백": st.column_config.TextColumn(
                "인플루언서피드백",
                help="인플루언서 피드백",
                max_chars=500,
            ),
            "메모": st.column_config.TextColumn(
                "메모",
                help="기타 메모",
                max_chars=500,
            ),
            "참여일": st.column_config.TextColumn(
                "참여일",
                disabled=True,
                help="참여 등록일 (읽기 전용)",
            ),
        }
        
        # 편집 가능한 테이블 표시
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            height=600,
            column_config=column_config,
            disabled=["ID", "인플루언서", "플랫폼", "SNS ID", "참여일"],  # 수정 불가능한 컬럼
            hide_index=True,
            key="participation_editor"
        )
        
        # 저장 버튼 (변경사항 감지 없이 항상 표시)
        st.markdown("---")
        st.markdown("### 💾 변경사항 저장")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("💾 변경사항 저장", type="primary", key="save_participation_changes"):
                save_edited_participations(df, edited_df)
        
        with col2:
            if st.button("🔄 새로고침", key="refresh_participation_data"):
                st.session_state.participation_data_refresh_requested = True  # 참여 데이터 새로고침 요청 플래그
                st.rerun()
        
        st.info("💡 테이블에서 데이터를 편집한 후 '변경사항 저장' 버튼을 클릭하여 저장하세요.")
        
        # 총 개수 표시 및 편집 안내
        st.caption(f"총 {len(participations)}명의 참여 인플루언서가 표시됩니다.")
        st.info("💡 **편집 가능한 필드**: 샘플 상태, 업로드 완료, 비용, 매니저코멘트, 인플루언서요청사항, 인플루언서피드백, 메모  \n📖 **읽기 전용 필드**: 인플루언서, 플랫폼, SNS ID, 참여일")
    else:
        st.info("표시할 참여 인플루언서가 없습니다.")

def save_edited_participations(original_df, edited_df):
    """편집된 참여 인플루언서 데이터를 저장"""
    try:
        # 변경된 행들을 찾아서 업데이트
        updated_count = 0
        error_count = 0
        total_changes = 0
        
        # DataFrame을 인덱스 기반으로 비교
        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]
            
            # 변경사항이 있는지 확인 (읽기 전용 컬럼 제외)
            readonly_columns = ["ID", "인플루언서", "플랫폼", "SNS ID", "참여일"]
            comparison_columns = [col for col in original_df.columns if col not in readonly_columns]
            has_changes = False
            
            for col in comparison_columns:
                if str(original_row[col]) != str(edited_row[col]):
                    has_changes = True
                    total_changes += 1
                    break
            
            if has_changes:
                participation_id = edited_row["ID"]
                
                # 업데이트할 데이터 준비 (NumPy 타입을 Python 기본 타입으로 변환)
                # 참고: influencer_name, platform, sns_id는 connecta_influencers 테이블에 있으므로 업데이트 불가
                update_data = {
                    'sample_status': str(edited_row["샘플 상태"]),
                    'content_uploaded': bool(edited_row["업로드 완료"]),
                    'cost_krw': int(edited_row["비용"]) if edited_row["비용"] is not None else 0,
                    'manager_comment': str(edited_row["매니저코멘트"]) if edited_row["매니저코멘트"] else None,
                    'influencer_requests': str(edited_row["인플루언서요청사항"]) if edited_row["인플루언서요청사항"] else None,
                    'influencer_feedback': str(edited_row["인플루언서피드백"]) if edited_row["인플루언서피드백"] else None,
                    'memo': str(edited_row["메모"]) if edited_row["메모"] else None
                }
                
                # 데이터베이스 업데이트
                result = db_manager.update_campaign_participation(participation_id, update_data)
                if result["success"]:
                    updated_count += 1
                else:
                    error_count += 1
                    st.error(f"❌ ID {participation_id} 업데이트 실패: {result['message']}")
        
        # 결과 표시
        if total_changes == 0:
            st.info("💡 변경된 내용이 없습니다. 테이블에서 정보를 편집한 후 다시 저장해주세요.")
        elif updated_count > 0:
            st.success(f"✅ {updated_count}명의 참여 인플루언서 정보가 업데이트되었습니다!")
        
        if error_count > 0:
            st.error(f"❌ {error_count}명의 참여 인플루언서 업데이트에 실패했습니다.")
        
        if updated_count > 0:
            # 캐시 초기화
            if "participations_cache" in st.session_state:
                del st.session_state["participations_cache"]
            
            # 페이지 새로고침
            st.session_state.participation_bulk_update_completed = True  # 참여 대량 업데이트 완료 플래그
            
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")
        import traceback
        st.code(traceback.format_exc())
