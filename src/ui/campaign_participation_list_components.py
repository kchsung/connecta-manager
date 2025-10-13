"""
캠페인 참여 인플루언서 목록 및 편집 관련 UI 컴포넌트
"""
import streamlit as st
import pandas as pd
from src.db.database import db_manager
from .common_functions import format_campaign_type, format_sample_status

def render_participation_list():
    """참여 인플루언서 목록 및 편집 메인 컴포넌트"""
    st.markdown("### 📋 참여 인플루언서 목록 / 편집")
    st.markdown("캠페인에 참여하는 인플루언서 목록을 조회하고 편집합니다.")
    
    # 캠페인 선택
    campaigns = db_manager.get_campaigns()
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    campaign_options = {f"{c['campaign_name']} ({format_campaign_type(c['campaign_type'])})": c for c in campaigns}
    selected_campaign_name = st.selectbox(
        "관리할 캠페인을 선택하세요",
        list(campaign_options.keys()),
        key="list_participation_campaign_select"
    )
    
    if selected_campaign_name:
        selected_campaign = campaign_options[selected_campaign_name]
        st.markdown(f"**선택된 캠페인:** {selected_campaign.get('campaign_name', 'N/A')} ({format_campaign_type(selected_campaign.get('campaign_type', ''))})")
        
        # 참여 인플루언서 목록
        participations = db_manager.get_all_campaign_participations(selected_campaign.get('id', ''))
        
        if not participations:
            st.info("이 캠페인에 참여한 인플루언서가 없습니다.")
        else:
            # 좌우 분할 레이아웃
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📋 참여 인플루언서 목록")
                render_participation_list_table(participations)
            
            with col2:
                st.markdown("#### ✏️ 인플루언서 편집")
                render_participation_edit_section(participations)

def render_participation_list_table(participations):
    """참여 인플루언서 목록 테이블"""
    # 참여 인플루언서 목록을 테이블로 표시
    participation_data = []
    for participation in participations:
        participation_data.append({
            "인플루언서": participation.get('influencer_name', participation.get('sns_id', 'N/A')),
            "플랫폼": participation.get('platform', 'N/A'),
            "SNS ID": participation.get('sns_id', 'N/A'),
            "샘플 상태": format_sample_status(participation.get('sample_status', '요청')),
            "업로드 완료": "✅" if participation.get('content_uploaded', False) else "❌",
            "비용": f"{participation.get('cost_krw', 0):,.0f}원" if participation.get('cost_krw') else "0원",
            "참여일": participation.get('created_at', '')[:10] if participation.get('created_at') else "N/A"
        })
    
    if participation_data:
        df = pd.DataFrame(participation_data)
        # 높이를 조정하여 15개 행이 보이도록 설정 (대략 600px)
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)
    else:
        st.info("표시할 참여 인플루언서가 없습니다.")

def render_participation_edit_section(participations):
    """참여 인플루언서 편집 섹션"""
    if not participations:
        st.info("편집할 참여 인플루언서가 없습니다.")
        return
    
    # 편집할 참여 인플루언서 선택 (SNS ID 포함)
    participation_options = {}
    for p in participations:
        influencer_name = p.get('influencer_name', 'N/A')
        sns_id = p.get('sns_id', 'N/A')
        platform = p.get('platform', 'N/A')
        display_name = f"{influencer_name} (@{sns_id}) ({platform})"
        participation_options[display_name] = p
    
    selected_participation_name = st.selectbox(
        "편집할 참여 인플루언서를 선택하세요",
        list(participation_options.keys()),
        key="participation_edit_select"
    )
    
    if selected_participation_name:
        selected_participation = participation_options[selected_participation_name]
        render_participation_edit_form(selected_participation)

def render_participation_edit_form(participation):
    """참여 인플루언서 편집 폼"""
    influencer_name = participation.get('influencer_name', 'N/A')
    sns_id = participation.get('sns_id', 'N/A')
    platform = participation.get('platform', 'N/A')
    st.markdown(f"**편집 대상:** {influencer_name} (@{sns_id}) ({platform})")
    
    with st.form(f"edit_participation_form_{participation.get('id', 'unknown')}"):
        # 데이터베이스 스키마에 맞는 필드들
        col1, col2 = st.columns(2)
        
        with col1:
            manager_comment = st.text_area(
                "매니저 코멘트", 
                value=participation.get('manager_comment', ''),
                key=f"edit_manager_comment_{participation.get('id', 'unknown')}"
            )
            influencer_requests = st.text_area(
                "인플루언서 요청사항", 
                value=participation.get('influencer_requests', ''),
                key=f"edit_influencer_requests_{participation.get('id', 'unknown')}"
            )
            memo = st.text_area(
                "메모", 
                value=participation.get('memo', ''),
                key=f"edit_memo_{participation.get('id', 'unknown')}"
            )
        
        with col2:
            sample_status = st.selectbox(
                "샘플 상태",
                ["요청", "발송준비", "발송완료", "수령"],
                index=["요청", "발송준비", "발송완료", "수령"].index(participation.get('sample_status', '요청')),
                key=f"edit_sample_status_{participation.get('id', 'unknown')}",
                format_func=lambda x: {
                    "요청": "📋 요청",
                    "발송준비": "📦 발송준비",
                    "발송완료": "🚚 발송완료",
                    "수령": "✅ 수령"
                }[x]
            )
            influencer_feedback = st.text_area(
                "인플루언서 피드백", 
                value=participation.get('influencer_feedback', ''),
                key=f"edit_influencer_feedback_{participation.get('id', 'unknown')}"
            )
            content_uploaded = st.checkbox(
                "콘텐츠 업로드 완료", 
                value=participation.get('content_uploaded', False),
                key=f"edit_content_uploaded_{participation.get('id', 'unknown')}"
            )
            cost_krw = st.number_input(
                "비용 (원)", 
                min_value=0.0, 
                value=float(participation.get('cost_krw', 0) or 0),
                step=1000.0,
                key=f"edit_cost_krw_{participation.get('id', 'unknown')}"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 저장", type="primary"):
                update_data = {
                    'manager_comment': manager_comment,
                    'influencer_requests': influencer_requests,
                    'memo': memo,
                    'sample_status': sample_status,
                    'influencer_feedback': influencer_feedback,
                    'content_uploaded': content_uploaded,
                    'cost_krw': cost_krw
                }
                
                result = db_manager.update_campaign_participation(participation.get('id', ''), update_data)
                if result["success"]:
                    st.success("참여 정보가 업데이트되었습니다!")
                    # 캐시 초기화
                    if "participations_cache" in st.session_state:
                        del st.session_state["participations_cache"]
                    st.rerun()
                else:
                    st.error(f"참여 정보 업데이트 실패: {result['message']}")
        
        with col2:
            if st.form_submit_button("🗑️ 제거", type="secondary"):
                result = db_manager.delete_campaign_participation(participation.get('id', ''))
                if result["success"]:
                    st.success("인플루언서가 캠페인에서 제거되었습니다!")
                    # 캐시 초기화
                    if "participations_cache" in st.session_state:
                        del st.session_state["participations_cache"]
                    st.rerun()
                else:
                    st.error(f"인플루언서 제거 실패: {result['message']}")
