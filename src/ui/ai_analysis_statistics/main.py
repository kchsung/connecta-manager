"""
AI 분석 통계 메인 컴포넌트
"""
import streamlit as st
from .basic_statistics import render_basic_statistics
from .evaluation_scores import render_evaluation_scores_statistics
from .network_analysis import render_network_analysis_statistics
from .activity_metrics import render_activity_metrics_statistics
from .comment_authenticity import render_comment_authenticity_statistics
from .advanced_visualizations import render_advanced_visualizations
from .statistical_insights import render_statistical_insights

def render_ai_analysis_statistics():
    """AI 분석 통계 탭"""
    st.subheader("📈 인공지능 분석 통계")
    st.markdown("AI 분석 결과의 통계 정보와 트렌드를 확인할 수 있습니다.")
    
    # 통계 탭으로 분리
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 기본 통계", 
        "📈 평가 점수 통계", 
        "🌐 네트워크 분석 통계",
        "📈 활동성/반응성 통계",
        "💬 댓글 진정성 통계",
        "🔥 고급 시각화",
        "🧠 통계적 인사이트"
    ])
    
    with tab1:
        render_basic_statistics()
    
    with tab2:
        render_evaluation_scores_statistics()
    
    with tab3:
        render_network_analysis_statistics()
    
    with tab4:
        render_activity_metrics_statistics()
    
    with tab5:
        render_comment_authenticity_statistics()
    
    with tab6:
        render_advanced_visualizations()
    
    with tab7:
        render_statistical_insights()
