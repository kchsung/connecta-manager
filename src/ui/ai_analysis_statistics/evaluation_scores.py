"""
평가 점수 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
from .common_functions import get_evaluation_scores_statistics

def render_evaluation_scores_statistics():
    """평가 점수 통계"""
    st.markdown("### 📈 평가 점수 통계")
    
    try:
        # 평가 점수 통계 조회
        score_stats = get_evaluation_scores_statistics()
        
        if not score_stats:
            st.warning("평가 점수 통계 데이터가 없습니다.")
            return
        
        # 점수별 평균 표시
        st.markdown("#### 📊 점수별 평균")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("참여도", f"{score_stats['avg_engagement']:.1f}/10")
        with col2:
            st.metric("활동성", f"{score_stats['avg_activity']:.1f}/10")
        with col3:
            st.metric("소통력", f"{score_stats['avg_communication']:.1f}/10")
        with col4:
            st.metric("성장성", f"{score_stats['avg_growth_potential']:.1f}/10")
        with col5:
            st.metric("종합점수", f"{score_stats['avg_overall']:.1f}/10")
        
        # 점수 분포 히스토그램
        st.markdown("#### 📊 점수 분포")
        
        # 종합점수 분포
        if score_stats['overall_score_distribution']:
            fig = px.histogram(
                x=score_stats['overall_score_distribution'],
                nbins=20,
                title="종합점수 분포",
                labels={'x': '종합점수', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 추론 신뢰도 분포
        if score_stats['inference_confidence_distribution']:
            fig = px.histogram(
                x=score_stats['inference_confidence_distribution'],
                nbins=20,
                title="추론 신뢰도 분포",
                labels={'x': '추론 신뢰도', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 상관관계 분석
        if score_stats['correlation_data'] is not None:
            st.markdown("#### 🔗 점수 간 상관관계")
            corr_data = score_stats['correlation_data']
            
            fig = px.imshow(
                corr_data,
                text_auto=True,
                aspect="auto",
                title="점수 간 상관관계 매트릭스"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"평가 점수 통계 조회 중 오류: {str(e)}")
