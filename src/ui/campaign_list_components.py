"""
캠페인 조회 및 수정 관련 UI 컴포넌트
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.db.database import db_manager
from .common_functions import (
    format_campaign_type,
    format_campaign_status,
    validate_campaign_data
)

def render_campaign_list():
    """캠페인 목록 조회 및 관리"""
    st.markdown("### 📋 캠페인 목록")
    st.markdown("생성된 캠페인을 조회하고 관리합니다.")
    
    # 새로고침 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 새로고침", key="refresh_campaigns"):
            # 캐시 초기화
            if "campaigns_cache" in st.session_state:
                del st.session_state["campaigns_cache"]
            st.session_state.campaign_list_refresh_requested = True  # 캠페인 목록 새로고침 요청 플래그
            # 리렌더링 없이 상태 기반 UI 업데이트
    
    with col2:
        st.caption("캠페인 목록을 새로고침하려면 새로고침 버튼을 클릭하세요.")
    
    # 캠페인 목록 조회
    campaigns = db_manager.get_campaigns()
    
    if not campaigns:
        st.info("생성된 캠페인이 없습니다. 위에서 새 캠페인을 생성해보세요.")
        return
    
    # 캠페인 목록을 테이블로 표시
    campaign_data = []
    for campaign in campaigns:
        campaign_data.append({
            "ID": campaign.get('id', 'N/A'),
            "캠페인 이름": campaign.get('campaign_name', 'N/A'),
            "유형": format_campaign_type(campaign.get('campaign_type', '')),
            "상태": format_campaign_status(campaign.get('status', 'planned')),
            "시작일": campaign.get('start_date', 'N/A'),
            "종료일": campaign.get('end_date', '미정'),
            "예산": f"{campaign.get('budget', 0):,}원" if campaign.get('budget') else "미정",
            "목표 도달률": f"{campaign.get('target_reach', 0)}%" if campaign.get('target_reach') else "미정"
        })
    
    if campaign_data:
        df = pd.DataFrame(campaign_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 캠페인 선택 및 편집
        st.markdown("### ✏️ 캠페인 편집")
        campaign_options = {f"{c['campaign_name']} ({format_campaign_type(c['campaign_type'])})": c for c in campaigns}
        selected_campaign_name = st.selectbox(
            "편집할 캠페인을 선택하세요",
            list(campaign_options.keys()),
            key="campaign_edit_select"
        )
        
        if selected_campaign_name:
            selected_campaign = campaign_options[selected_campaign_name]
            render_campaign_edit_form(selected_campaign)
    else:
        st.info("표시할 캠페인이 없습니다.")

def render_campaign_edit_form(campaign):
    """캠페인 수정 폼"""
    st.markdown("---")
    st.markdown(f"**편집 대상:** {campaign.get('campaign_name', 'N/A')}")
    
    with st.form(f"edit_campaign_form_{campaign.get('id', 'unknown')}"):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("캠페인 이름", value=campaign.get('campaign_name', ''), key=f"edit_name_{campaign.get('id', 'unknown')}")
            current_type = campaign.get('campaign_type', 'seeding')
            type_options = ["seeding", "promotion", "sales"]
            try:
                type_index = type_options.index(current_type)
            except ValueError:
                type_index = 0  # 기본값으로 'seeding' 선택
            
            campaign_type = st.selectbox(
                "캠페인 유형",
                type_options,
                index=type_index,
                key=f"edit_type_{campaign.get('id', 'unknown')}",
                format_func=lambda x: {
                    "seeding": "🌱 시딩",
                    "promotion": "📢 홍보", 
                    "sales": "💰 판매"
                    }[x]
            )
            start_date_value = None
            if campaign.get('start_date'):
                try:
                    start_date_value = datetime.strptime(campaign['start_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    start_date_value = None
            
            start_date = st.date_input("시작날짜", value=start_date_value, key=f"edit_start_{campaign.get('id', 'unknown')}")
        
        with col2:
            campaign_description = st.text_area("캠페인 설명", value=campaign.get('campaign_description', ''), key=f"edit_desc_{campaign.get('id', 'unknown')}")
            campaign_instructions = st.text_area("캠페인 지침", value=campaign.get('campaign_instructions', ''), key=f"edit_instructions_{campaign.get('id', 'unknown')}")
            current_status = campaign.get('status', 'planned')
            status_options = ["planned", "active", "paused", "completed", "cancelled"]
            try:
                status_index = status_options.index(current_status)
            except ValueError:
                status_index = 0  # 기본값으로 'planned' 선택
            
            status = st.selectbox(
                "캠페인 상태",
                status_options,
                index=status_index,
                key=f"edit_status_{campaign.get('id', 'unknown')}",
                format_func=lambda x: {
                    "planned": "📋 계획",
                    "active": "🟢 진행중",
                    "paused": "⏸️ 일시정지",
                    "completed": "✅ 완료",
                    "cancelled": "❌ 취소"
                }[x]
            )
            end_date_value = None
            if campaign.get('end_date'):
                try:
                    end_date_value = datetime.strptime(campaign['end_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    end_date_value = None
            
            end_date = st.date_input(
                "종료날짜", 
                value=end_date_value,
                key=f"edit_end_{campaign.get('id', 'unknown')}"
            )
        
        # 예산 정보
        st.markdown("#### 💰 예산 정보")
        col3, col4 = st.columns(2)
        with col3:
            budget = st.number_input(
                "캠페인 예산 (원)", 
                min_value=0, 
                value=campaign.get('budget', 0) or 0,
                step=10000,
                key=f"edit_budget_{campaign.get('id', 'unknown')}"
            )
        with col4:
            target_reach = st.number_input(
                "목표 도달률", 
                min_value=0, 
                max_value=100, 
                value=campaign.get('target_reach', 0) or 0,
                step=1,
                key=f"edit_reach_{campaign.get('id', 'unknown')}"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 저장", type="primary"):
                if not campaign_name:
                    st.error("캠페인 이름을 입력해주세요.")
                else:
                    # 캠페인 데이터 유효성 검사
                    campaign_data = {
                        'campaign_name': campaign_name,
                        'campaign_type': campaign_type,
                        'start_date': start_date,
                        'end_date': end_date,
                        'budget': budget,
                        'target_reach': target_reach
                    }
                    
                    validation = validate_campaign_data(campaign_data)
                    if not validation["valid"]:
                        for error in validation["errors"]:
                            st.error(error)
                    else:
                        update_data = {
                            'campaign_name': campaign_name,
                            'campaign_type': campaign_type,
                            'campaign_description': campaign_description,
                            'campaign_instructions': campaign_instructions,
                            'start_date': start_date,
                            'end_date': end_date,
                            'status': status,
                            'budget': budget,
                            'target_reach': target_reach
                        }
                        
                        result = db_manager.update_campaign(campaign.get('id', ''), update_data)
                        if result["success"]:
                            st.success("캠페인이 업데이트되었습니다!")
                            # 캐시 초기화
                            if "campaigns_cache" in st.session_state:
                                del st.session_state["campaigns_cache"]
                            st.session_state.campaign_updated = True  # 캠페인 업데이트 완료 플래그
                            # 리렌더링 없이 상태 기반 UI 업데이트
                        else:
                            st.error(f"캠페인 업데이트 실패: {result['message']}")
        
        with col2:
            if st.form_submit_button("🗑️ 삭제", type="secondary"):
                result = db_manager.delete_campaign(campaign.get('id', ''))
                if result["success"]:
                    st.success("캠페인이 삭제되었습니다!")
                    # 캐시 초기화
                    if "campaigns_cache" in st.session_state:
                        del st.session_state["campaigns_cache"]
                    st.session_state.campaign_deleted = True  # 캠페인 삭제 완료 플래그
                    # 리렌더링 없이 상태 기반 UI 업데이트
                else:
                    st.error(f"캠페인 삭제 실패: {result['message']}")


