"""
인공지능 분석 관련 컴포넌트들 - 메인 파일
"""
import streamlit as st
from .ai_analysis_execution import render_ai_analysis_execution
from .ai_analysis_results import render_ai_analysis_results
from .ai_analysis_statistics import render_ai_analysis_statistics
from .ai_analysis_statistics.correlation_analysis import render_correlation_analysis

def render_ai_analysis_management():
    """인공지능 분석 관리 메인 컴포넌트"""
    st.subheader("🤖 인공지능 분석")
    st.markdown("AI를 활용한 인플루언서 분석 및 평가를 제공합니다.")
    
    # 디버그 모드 확인
    debug_mode = False
    try:
        debug_mode = st.secrets.get("DEBUG_MODE", "false").lower() == "true"
    except (KeyError, AttributeError):
        debug_mode = False
    
    # AI 분석 탭으로 분리 (디버그 모드에 따라 실행 탭 포함/제외)
    if debug_mode:
        tab1, tab2, tab3, tab4 = st.tabs([
            "🚀 인공지능 분석 실행", 
            "📊 인공지능 분석 결과", 
            "📈 인공지능 분석 통계",
            "🔗 인공지능 성과 상관관계 분석"
        ])
        
        with tab1:
            render_ai_analysis_execution()
        
        with tab2:
            render_ai_analysis_results()
        
        with tab3:
            render_ai_analysis_statistics()
        
        with tab4:
            render_correlation_analysis()
    else:
        tab1, tab2, tab3 = st.tabs([
            "📊 인공지능 분석 결과", 
            "📈 인공지능 분석 통계",
            "🔗 인공지능 성과 상관관계 분석"
        ])
        
        with tab1:
            render_ai_analysis_results()
        
        with tab2:
            render_ai_analysis_statistics()
        
        with tab3:
            render_correlation_analysis()