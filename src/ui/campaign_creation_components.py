"""
캠페인 생성 관련 UI 컴포넌트
"""
import streamlit as st
from datetime import datetime
from src.db.database import db_manager
from src.db.models import Campaign
from .common_functions import validate_campaign_data

def render_campaign_creation():
    """캠페인 생성 메인 컴포넌트"""
    st.markdown("### 🆕 새 캠페인 생성")
    st.markdown("새로운 캠페인을 생성합니다.")
    
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
            campaign_instructions = st.text_area("캠페인 지침", placeholder="인플루언서에게 전달할 구체적인 지침을 입력하세요")
            status = st.selectbox(
                "캠페인 상태",
                ["planned", "active", "paused", "completed", "cancelled"],
                key="create_campaign_status",
                format_func=lambda x: {
                    "planned": "📋 계획",
                    "active": "🟢 진행중",
                    "paused": "⏸️ 일시정지",
                    "completed": "✅ 완료",
                    "cancelled": "❌ 취소"
                }[x]
            )
            end_date = st.date_input("캠페인 종료날짜", value=None)
        
        # 예산 정보
        st.markdown("#### 💰 예산 정보")
        col3, col4 = st.columns(2)
        with col3:
            budget = st.number_input("캠페인 예산 (원)", min_value=0, value=0, step=10000)
        with col4:
            target_reach = st.number_input("목표 도달률", min_value=0, max_value=100, value=0, step=1)
        
        if st.form_submit_button("캠페인 생성", type="primary"):
            if not campaign_name:
                st.error("캠페인 이름을 입력해주세요.")
            else:
                # 캠페인 데이터 유효성 검사
                campaign_data = {
                    'campaign_name': campaign_name,
                    'campaign_description': campaign_description,
                    'campaign_instructions': campaign_instructions,
                    'campaign_type': campaign_type,
                    'start_date': start_date,
                    'end_date': end_date,
                    'status': status,
                    'budget': budget,
                    'target_reach': target_reach
                }
                
                validation = validate_campaign_data(campaign_data)
                if not validation["valid"]:
                    for error in validation["errors"]:
                        st.error(error)
                else:
                    campaign = Campaign(
                        campaign_name=campaign_name,
                        campaign_type=campaign_type,
                        campaign_description=campaign_description,
                        campaign_instructions=campaign_instructions,
                        start_date=start_date,
                        end_date=end_date,
                        status=status,
                        budget=budget,
                        target_reach=target_reach
                    )
                    
                    result = db_manager.create_campaign(campaign)
                    if result["success"]:
                        st.success("캠페인이 생성되었습니다!")
                        # 캐시 초기화
                        if "campaigns_cache" in st.session_state:
                            del st.session_state["campaigns_cache"]
                        st.rerun()
                    else:
                        st.error(f"캠페인 생성 실패: {result['message']}")


