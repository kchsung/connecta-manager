"""
캠페인 관리 관련 컴포넌트들
"""
import streamlit as st
from .campaign_creation_components import render_campaign_creation
from .campaign_list_components import render_campaign_list
from .campaign_participation_add_components import render_participation_add
from .campaign_participation_list_components import render_participation_list

def render_campaign_management():
    """캠페인 관리 컴포넌트"""
    st.subheader("📋 캠페인 관리")
    st.markdown("시딩, 홍보, 판매 캠페인을 생성하고 참여 인플루언서를 관리합니다.")
    
    # 탭으로 캠페인 생성, 조회/수정, 참여 인플루언서 추가, 참여 인플루언서 목록/편집 구분
    tab1, tab2, tab3, tab4 = st.tabs(["🆕 캠페인 생성", "📋 캠페인 조회/수정", "➕ 참여 인플루언서 추가", "📋 참여 인플루언서 목록/편집"])
    
    with tab1:
        render_campaign_creation()
    
    with tab2:
        render_campaign_list()
    
    with tab3:
        render_participation_add()
    
    with tab4:
        render_participation_list()



