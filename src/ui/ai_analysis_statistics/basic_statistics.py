"""
기본 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
from .common_functions import (
    get_total_analyses_count,
    get_recent_analyses_count,
    get_average_overall_score,
    get_recommendation_distribution,
    get_category_distribution
)

def render_basic_statistics():
    """기본 통계"""
    st.markdown("### 📊 기본 통계")
    
    try:
        # 기본 통계 조회
        total_analyses = get_total_analyses_count()
        recent_analyses = get_recent_analyses_count()
        avg_score = get_average_overall_score()
        
        # 통계 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 분석 수", f"{total_analyses:,}")
        
        with col2:
            st.metric("최근 7일 분석", f"{recent_analyses:,}")
        
        with col3:
            st.metric("평균 종합점수", f"{avg_score:.1f}/10")
        
        with col4:
            success_rate = (total_analyses - recent_analyses) / total_analyses * 100 if total_analyses > 0 else 0
            st.metric("분석 성공률", f"{success_rate:.1f}%")
        
        # 추천도 분포
        st.markdown("#### ⭐ 추천도 분포")
        recommendation_dist = get_recommendation_distribution()
        
        if recommendation_dist:
            fig = px.pie(
                values=list(recommendation_dist.values()),
                names=list(recommendation_dist.keys()),
                title="추천도 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("추천도 분포 데이터가 없습니다.")
        
        # 카테고리 분포
        st.markdown("#### 📂 카테고리 분포")
        category_dist = get_category_distribution()
        
        if category_dist:
            fig = px.bar(
                x=list(category_dist.keys()),
                y=list(category_dist.values()),
                title="카테고리별 분석 수"
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("카테고리 분포 데이터가 없습니다.")
    
    except Exception as e:
        st.error(f"기본 통계 조회 중 오류: {str(e)}")
