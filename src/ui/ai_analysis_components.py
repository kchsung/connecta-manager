"""
인공지능 분석 관련 컴포넌트들 - 메인 파일
"""
import streamlit as st
from .ai_analysis_execution import render_ai_analysis_execution
from .ai_analysis_results import render_ai_analysis_results
from .ai_analysis_statistics import render_ai_analysis_statistics

def render_ai_analysis_management():
    """인공지능 분석 관리 메인 컴포넌트"""
    st.subheader("🤖 인공지능 분석")
    st.markdown("AI를 활용한 인플루언서 분석 및 평가를 제공합니다.")
    
    # AI 분석 탭으로 분리
    tab1, tab2, tab3 = st.tabs([
        "🚀 인공지능 분석 실행", 
        "📊 인공지능 분석 결과", 
        "📈 인공지능 분석 통계"
    ])
    
    with tab1:
        render_ai_analysis_execution()
    
    with tab2:
        render_ai_analysis_results()
    
    with tab3:
        render_ai_analysis_statistics()