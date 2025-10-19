"""
댓글 진정성 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
from .common_functions import get_comment_authenticity_statistics

def render_comment_authenticity_statistics():
    """댓글 진정성 통계"""
    st.markdown("### 💬 댓글 진정성 통계")
    
    try:
        # 댓글 진정성 통계 조회
        authenticity_stats = get_comment_authenticity_statistics()
        
        if not authenticity_stats:
            st.warning("댓글 진정성 통계 데이터가 없습니다.")
            return
        
        # 진정성 등급 분포
        st.markdown("#### 📊 진정성 등급 분포")
        if authenticity_stats['authenticity_level_distribution']:
            fig = px.pie(
                values=list(authenticity_stats['authenticity_level_distribution'].values()),
                names=list(authenticity_stats['authenticity_level_distribution'].keys()),
                title="댓글 진정성 등급 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 진정성 비율 통계
        st.markdown("#### 📈 진정성 비율 통계")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 진정성 비율", f"{authenticity_stats['avg_authentic_ratio']:.1f}%")
        with col2:
            st.metric("중앙값 진정성 비율", f"{authenticity_stats['median_authentic_ratio']:.1f}%")
        with col3:
            st.metric("평균 저품질 비율", f"{authenticity_stats['avg_low_authentic_ratio']:.1f}%")
        with col4:
            st.metric("중앙값 저품질 비율", f"{authenticity_stats['median_low_authentic_ratio']:.1f}%")
        
        # 진정성 비율 분포
        if authenticity_stats['authentic_ratio_distribution']:
            st.markdown("#### 📊 진정성 비율 분포")
            fig = px.histogram(
                x=authenticity_stats['authentic_ratio_distribution'],
                nbins=20,
                title="진정성 비율 분포",
                labels={'x': '진정성 비율 (%)', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"댓글 진정성 통계 조회 중 오류: {str(e)}")
