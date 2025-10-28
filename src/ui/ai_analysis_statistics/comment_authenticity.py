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
            st.plotly_chart(fig, width='stretch')
        
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
            st.plotly_chart(fig, width='stretch')
        
        # 통계 해석 가이드
        st.markdown("---")
        st.markdown("#### 💡 댓글 진정성 통계 해석 가이드")
        
        with st.expander("🔍 상세 해석 가이드 보기", expanded=False):
            st.markdown("**📊 각 분석 항목 설명**")
            
            st.markdown("**💬 댓글 진정성 등급**")
            st.markdown("인플루언서의 댓글들이 얼마나 진정성 있는지 평가한 등급입니다. 댓글의 내용 품질, 작성자 특성, 상호작용 패턴 등을 종합적으로 분석하여 '매우 높음', '높음', '보통', '낮음', '매우 낮음' 등으로 분류됩니다.")
            
            st.markdown("**📈 진정성 비율**")
            st.markdown("전체 댓글 중 진정성 있는 댓글의 비율을 나타냅니다. 높은 비율은 팔로워들이 진심으로 상호작용하고 있음을 의미하며, 낮은 비율은 봇이나 스팸 댓글이 많음을 나타냅니다.")
            
            st.markdown("**📉 저품질 비율**")
            st.markdown("전체 댓글 중 저품질 댓글(스팸, 봇, 무의미한 댓글)의 비율을 나타냅니다. 이 비율이 높을수록 인플루언서의 팔로워 품질이 낮거나 인위적인 상호작용이 많음을 의미합니다.")
            
            st.markdown("**🎯 진정성 평가 기준**")
            st.markdown("""
            - **댓글 내용 품질:** 의미 있는 내용, 관련성, 언어 품질
            - **작성자 특성:** 계정 신뢰도, 활동 패턴, 팔로워/팔로잉 비율
            - **상호작용 패턴:** 자연스러운 대화 흐름, 적절한 반응 시간
            - **스팸/봇 탐지:** 반복적인 패턴, 무의미한 내용, 자동화된 댓글
            """)
            
            st.markdown("**📊 분포 해석 방법**")
            st.markdown("""
            - **파이 차트:** 각 진정성 등급별 인플루언서 분포를 시각적으로 확인
            - **히스토그램:** 진정성 비율의 분포 형태를 확인하여 전체적인 품질 수준 파악
            - **통계 지표:** 평균과 중앙값을 비교하여 분포의 특성 이해
            - **비율 분석:** 진정성 비율과 저품질 비율을 함께 분석하여 종합적인 댓글 품질 평가
            """)
            
            st.markdown("**💡 활용 방안**")
            st.markdown("""
            - **인플루언서 선별:** 진정성 비율이 높은 인플루언서를 우선적으로 협업 대상으로 고려
            - **마케팅 전략:** 저품질 댓글이 많은 인플루언서는 신중하게 검토
            - **브랜드 안전성:** 진정성 있는 상호작용을 통해 브랜드 이미지 보호
            - **성과 예측:** 진정성 비율이 높은 인플루언서일수록 실제 마케팅 성과가 좋을 가능성 높음
            """)
    
    except Exception as e:
        st.error(f"댓글 진정성 통계 조회 중 오류: {str(e)}")
