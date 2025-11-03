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
        
        # 좌측 하단: 인플루언서 기본 정보 (읽기 전용)
        st.markdown("---")
        st.markdown("#### 📋 인플루언서 기본 정보")
        st.caption("⚠️ 이 섹션은 읽기 전용입니다. 수정할 수 없습니다.")
        
        if st.session_state.selected_participation_id:
            selected_participation = next(
                (p for p in participations if p.get('id') == st.session_state.selected_participation_id), 
                None
            )
            if selected_participation:
                render_influencer_basic_info(selected_participation)
            else:
                st.info("선택된 인플루언서 정보를 찾을 수 없습니다.")
        else:
            st.info("위에서 편집할 인플루언서를 선택해주세요.")
    
    with col2:
        st.markdown("#### ✏️ 캠페인 정보 편집")
        st.caption("💡 이 섹션은 편집 가능합니다. 캠페인 참여 정보와 성과 정보를 수정할 수 있습니다.")
        
        if st.session_state.selected_participation_id:
            selected_participation = next(
                (p for p in participations if p.get('id') == st.session_state.selected_participation_id), 
                None
            )
            if selected_participation:
                render_participation_edit_section(selected_participation, selected_campaign)
            else:
                st.info("선택된 인플루언서 정보를 찾을 수 없습니다.")
        else:
            st.info("좌측에서 편집할 인플루언서를 선택해주세요.")

def render_influencer_cards(participations):
    """인플루언서 목록을 드롭다운 메뉴로 표시"""
    if not participations:
        st.info("참여 인플루언서가 없습니다.")
        return
    
    # 드롭다운 옵션 생성
    participation_options = {}
    default_index = 0
    
    for i, participation in enumerate(participations):
        participation_id = participation.get('id')
        influencer_name = participation.get('influencer_name', 'N/A')
        sns_id = participation.get('sns_id', 'N/A')
        platform = participation.get('platform', 'N/A').upper()
        status = "✅ 완료" if participation.get('content_uploaded', False) else "⏳ 대기"
        
        # 드롭다운에 표시할 텍스트
        option_text = f"👤 {influencer_name}  📱 {sns_id}  🌐 {platform}  {status}"
        participation_options[option_text] = participation_id
        
        # 현재 선택된 인플루언서의 인덱스 찾기
        if st.session_state.selected_participation_id == participation_id:
            default_index = i
    
    # "인플루언서를 선택하세요" 옵션 추가
    option_list = ["인플루언서를 선택하세요"] + list(participation_options.keys())
    
    # 기본 선택값 설정 (현재 선택된 인플루언서가 있으면 해당 인덱스, 없으면 0)
    if st.session_state.selected_participation_id:
        selected_option = next(
            (opt for opt in participation_options.keys() 
             if participation_options[opt] == st.session_state.selected_participation_id),
            option_list[0]
        )
        if selected_option in option_list:
            selected_index = option_list.index(selected_option)
        else:
            selected_index = 0
    else:
        selected_index = 0
    
    # 드롭다운 메뉴 표시
    selected_option_text = st.selectbox(
        "참여 인플루언서를 선택하세요",
        option_list,
        index=selected_index,
        key="participation_dropdown",
        help="편집할 인플루언서를 선택하세요"
    )
    
    # 선택된 옵션이 변경되면 세션 상태 업데이트
    if selected_option_text and selected_option_text != "인플루언서를 선택하세요":
        if selected_option_text in participation_options:
            st.session_state.selected_participation_id = participation_options[selected_option_text]
    else:
        st.session_state.selected_participation_id = None

def render_influencer_basic_info(participation):
    """인플루언서 기본 정보를 읽기 전용으로 표시 (좌측 하단)"""
    participation_id = participation.get('id', 'unknown')
    
    st.markdown(f"**선택된 인플루언서:** {participation.get('influencer_name', 'N/A')} ({participation.get('platform', 'N/A')})")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("플랫폼", value=participation.get('platform', ''), disabled=True, key=f"readonly_platform_{participation_id}")
        st.text_input("SNS ID", value=participation.get('sns_id', ''), disabled=True, key=f"readonly_sns_id_{participation_id}")
        st.text_input("인플루언서명", value=participation.get('influencer_name', ''), disabled=True, key=f"readonly_name_{participation_id}")
        
        # SNS URL을 클릭 가능한 링크로 표시
        sns_url = participation.get('sns_url', '')
        if sns_url and sns_url.strip():
            st.markdown(f"**SNS URL:** [{sns_url}]({sns_url})")
        else:
            st.text_input("SNS URL", value="등록되지 않음", disabled=True, key=f"readonly_url_{participation_id}")
            st.caption("⚠️ 이 인플루언서의 SNS URL이 데이터베이스에 등록되지 않았습니다.")
    
    with col2:
        st.number_input("팔로워 수", value=participation.get('followers_count', 0), disabled=True, key=f"readonly_followers_{participation_id}")
        st.text_input("연락방법", value=participation.get('contact_method', ''), disabled=True, key=f"readonly_contact_{participation_id}")
        st.text_input("전화번호", value=participation.get('phone_number', ''), disabled=True, key=f"readonly_phone_{participation_id}")
        st.text_input("이메일", value=participation.get('email', ''), disabled=True, key=f"readonly_email_{participation_id}")

def render_participation_edit_section(participation, selected_campaign):
    """캠페인 참여 정보 및 성과 정보 편집 섹션 (우측)"""
    participation_id = participation.get('id', 'unknown')
    
    # 캠페인 참여 정보 편집
    st.markdown("##### ✏️ 캠페인 참여 정보")
    
    with st.form(f"participation_edit_form_{participation_id}"):
        # 샘플 상태
        sample_status_options = ["요청", "발송준비", "발송완료", "수령"]
        current_sample_status = participation.get('sample_status', '요청')
        sample_status_index = sample_status_options.index(current_sample_status) if current_sample_status in sample_status_options else 0
        
        sample_status = st.selectbox(
            "샘플 상태",
            sample_status_options,
            index=sample_status_index,
            key=f"detail_sample_status_{participation_id}"
        )
        
        # 업로드 완료 여부
        content_uploaded = st.checkbox(
            "콘텐츠 업로드 완료",
            value=participation.get('content_uploaded', False),
            key=f"detail_content_uploaded_{participation_id}"
        )
        
        # 비용
        cost_krw = st.number_input(
            "비용 (원)",
            min_value=0,
            value=int(participation.get('cost_krw', 0)) if participation.get('cost_krw') else 0,
            step=1000,
            key=f"detail_cost_krw_{participation_id}"
        )
        
        # 텍스트 필드들
        manager_comment = st.text_area(
            "매니저 코멘트",
            value=participation.get('manager_comment', ''),
            key=f"detail_manager_comment_{participation_id}",
            max_chars=500
        )
        
        influencer_requests = st.text_area(
            "인플루언서 요청사항",
            value=participation.get('influencer_requests', ''),
            key=f"detail_influencer_requests_{participation_id}",
            max_chars=500
        )
        
        influencer_feedback = st.text_area(
            "인플루언서 피드백",
            value=participation.get('influencer_feedback', ''),
            key=f"detail_influencer_feedback_{participation_id}",
            max_chars=500
        )
        
        memo = st.text_area(
            "메모",
            value=participation.get('memo', ''),
            key=f"detail_memo_{participation_id}",
            max_chars=500
        )
        
        # 버튼들
        col1, col2 = st.columns(2)
        
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
    
    # 캠페인 성과 정보 입력 섹션
    st.markdown("---")
    st.markdown("##### 📊 캠페인 성과 정보")
    render_campaign_performance_section(participation)

def render_campaign_performance_section(participation):
    """캠페인 성과 정보 입력 섹션"""
    participation_id = participation.get('id')
    
    # 기존 콘텐츠 데이터 조회
    existing_contents = db_manager.get_campaign_influencer_contents(participation_id)
    
    # 콘텐츠 추가/편집 탭 (기존 콘텐츠 관리가 먼저 나오도록 변경)
    tab1, tab2 = st.tabs(["📋 기존 콘텐츠 관리", "📝 콘텐츠 추가"])
    
    with tab1:
        render_existing_contents(existing_contents)
    
    with tab2:
        render_add_content_form(participation_id)

def render_add_content_form(participation_id):
    """새 콘텐츠 추가 폼"""
    with st.form(f"add_content_form_{participation_id}"):
        st.markdown("**새 콘텐츠 성과 정보 입력**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_url = st.text_input(
                "콘텐츠 URL *",
                placeholder="https://instagram.com/p/...",
                help="콘텐츠의 URL을 입력하세요",
                key=f"new_content_url_{participation_id}"
            )
            
            posted_at = st.date_input(
                "게시일",
                value=None,
                help="콘텐츠가 게시된 날짜",
                key=f"new_posted_at_{participation_id}"
            )
            
            caption = st.text_area(
                "캡션",
                placeholder="콘텐츠의 캡션 내용",
                max_chars=1000,
                key=f"new_caption_{participation_id}"
            )
            
            qualitative_note = st.text_area(
                "정성평가",
                placeholder="콘텐츠에 대한 정성적 평가",
                max_chars=500,
                key=f"new_qualitative_note_{participation_id}"
            )
        
        with col2:
            likes = st.number_input(
                "좋아요 수",
                min_value=0,
                value=0,
                key=f"new_likes_{participation_id}"
            )
            
            comments = st.number_input(
                "댓글 수",
                min_value=0,
                value=0,
                key=f"new_comments_{participation_id}"
            )
            
            shares = st.number_input(
                "공유 수",
                min_value=0,
                value=0,
                key=f"new_shares_{participation_id}"
            )
            
            views = st.number_input(
                "조회 수",
                min_value=0,
                value=0,
                key=f"new_views_{participation_id}"
            )
            
            clicks = st.number_input(
                "클릭 수",
                min_value=0,
                value=0,
                key=f"new_clicks_{participation_id}"
            )
            
            conversions = st.number_input(
                "전환 수",
                min_value=0,
                value=0,
                key=f"new_conversions_{participation_id}"
            )
            
            is_rels = st.number_input(
                "REL 수",
                min_value=0,
                value=0,
                key=f"new_is_rels_{participation_id}"
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
    """참여 인플루언서 목록 테이블 (보기 전용)"""
    # 참여 인플루언서 목록을 보기 전용 테이블로 표시
    participation_data = []
    for participation in participations:
        participation_data.append({
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
        # 보기 전용 테이블 렌더링
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"총 {len(participations)}명의 참여 인플루언서가 표시됩니다.")
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
