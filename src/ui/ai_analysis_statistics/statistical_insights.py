"""
통계적 인사이트 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from .common_functions import get_statistical_insights_data

def render_statistical_insights():
    """통계적 인사이트"""
    st.markdown("### 🧠 통계적 인사이트")
    st.markdown("데이터에서 발견된 패턴과 인사이트를 제공합니다.")
    
    try:
        # 통계적 인사이트 데이터 조회
        insights_data = get_statistical_insights_data()
        
        if not insights_data:
            st.warning("통계적 인사이트 데이터가 없습니다.")
            return
        
        # 1. 이상치 탐지
        st.markdown("#### 🔍 이상치 탐지")
        if insights_data.get('outliers'):
            outliers = insights_data['outliers']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("참여율 이상치", f"{outliers['engagement_outliers']}개")
            with col2:
                st.metric("진정성 점수 이상치", f"{outliers['authenticity_outliers']}개")
            with col3:
                st.metric("종합점수 이상치", f"{outliers['overall_outliers']}개")
            
            # 이상치 시각화 - 기준 선택
            outlier_viz = insights_data.get('outlier_visualization')
            if outlier_viz is not None and not outlier_viz.empty:
                # NaN 값 필터링
                outlier_viz_clean = outlier_viz.dropna(subset=['followers', 'engagement_rate', 'authenticity_score', 'overall_score'])
                
                if not outlier_viz_clean.empty:
                    # 이상치 탐지 기준 선택
                    st.markdown("**이상치 탐지 기준 선택:**")
                    outlier_criteria = st.selectbox(
                        "이상치 탐지를 위한 기준을 선택하세요:",
                        ["참여율", "진정성 점수", "종합점수"],
                        key="outlier_criteria_selector"
                    )
                    
                    # 선택된 기준에 따라 데이터와 라벨 설정
                    if outlier_criteria == "참여율":
                        y_col = 'engagement_rate'
                        y_label = '참여율 (%)'
                        title_suffix = "참여율 기준"
                    elif outlier_criteria == "진정성 점수":
                        y_col = 'authenticity_score'
                        y_label = '진정성 점수'
                        title_suffix = "진정성 점수 기준"
                    else:  # 종합점수
                        y_col = 'overall_score'
                        y_label = '종합점수'
                        title_suffix = "종합점수 기준"
                    
                    # 이상치 여부를 선택된 기준으로 다시 계산
                    import pandas as pd
                    
                    def detect_outliers_single_series(series):
                        """단일 시리즈에 대한 이상치 탐지"""
                        # 0이 아닌 값들만 필터링
                        non_zero_series = series[series > 0]
                        if len(non_zero_series) < 4:  # 최소 4개 이상의 데이터가 필요
                            return pd.Series([False] * len(series), index=series.index)
                        
                        Q1 = non_zero_series.quantile(0.25)
                        Q3 = non_zero_series.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        return (series < lower_bound) | (series > upper_bound)
                    
                    outlier_viz_clean['is_outlier'] = detect_outliers_single_series(outlier_viz_clean[y_col])
                    
                    # 산점도 생성
                    fig = px.scatter(
                        outlier_viz_clean,
                        x='followers',
                        y=y_col,
                        color='is_outlier',
                        size='overall_score',
                        title=f"이상치 탐지 ({title_suffix})",
                        labels={
                            'followers': '팔로워 수',
                            y_col: y_label,
                            'is_outlier': '이상치 여부',
                            'overall_score': '종합점수'
                        },
                        color_discrete_map={True: '#e74c3c', False: '#2ecc71'}
                    )
                    fig.update_layout(xaxis_type="log")
                    
                    # 범례 제목 수정
                    fig.update_layout(
                        legend=dict(
                            title="이상치 여부"
                        )
                    )
                    
                    st.plotly_chart(fig, width='stretch')
                    
                    # 선택된 기준에 따른 이상치 통계 표시
                    outlier_count = outlier_viz_clean['is_outlier'].sum()
                    total_count = len(outlier_viz_clean)
                    outlier_percentage = (outlier_count / total_count) * 100 if total_count > 0 else 0
                    
                    st.info(f"📊 **{title_suffix}** 이상치: {outlier_count}개 / {total_count}개 ({outlier_percentage:.1f}%)")
                else:
                    st.info("📊 이상치 시각화를 위한 유효한 데이터가 없습니다.")
        
        # 2. 인사이트 요약
        st.markdown("#### 💡 핵심 인사이트")
        if insights_data.get('key_insights'):
            insights = insights_data['key_insights']
            
            for i, insight in enumerate(insights, 1):
                st.info(f"**인사이트 {i}**: {insight}")
        
        # 지표 설명 섹션
        st.markdown("---")
        st.markdown("### 📋 지표 설명")
        
        with st.expander("🔍 이상치 탐지 지표 설명", expanded=False):
            st.markdown("""
            **이상치 탐지**는 정상적인 범위를 벗어난 데이터 포인트를 찾아냅니다.
            
            **이상치 탐지 방법:**
            - **IQR 방법**: 1.5 × IQR 범위를 벗어나는 값들을 이상치로 판단
            - **Z-score 방법**: 평균에서 3 표준편차 이상 벗어나는 값들을 이상치로 판단
            
            **참여율 이상치:**
            - **높은 이상치**: 평균보다 현저히 높은 참여율 (예: 10% 이상)
            - **낮은 이상치**: 평균보다 현저히 낮은 참여율 (예: 0.1% 미만)
            - **의미**: 바이럴 콘텐츠나 봇 팔로워의 가능성
            
            **진정성 점수 이상치:**
            - **높은 이상치**: 매우 높은 진정성 점수 (예: 95점 이상)
            - **낮은 이상치**: 매우 낮은 진정성 점수 (예: 10점 미만)
            - **의미**: 특별히 진정한 콘텐츠나 가짜 댓글의 가능성
            
            **종합점수 이상치:**
            - **높은 이상치**: 전체적으로 우수한 성과를 보이는 인플루언서
            - **낮은 이상치**: 전반적으로 낮은 성과를 보이는 인플루언서
            - **의미**: 특별한 성과나 개선이 필요한 케이스
            """)
        
        with st.expander("💡 핵심 인사이트 지표 설명", expanded=False):
            st.markdown("""
            **핵심 인사이트**는 데이터 분석을 통해 발견된 중요한 패턴과 인사이트입니다.
            
            **인사이트 유형:**
            - **성과 관련**: 어떤 요인이 성과에 영향을 미치는지
            - **패턴 관련**: 데이터에서 발견된 특별한 패턴
            - **트렌드 관련**: 시간에 따른 변화 추이
            - **상관관계 관련**: 지표들 간의 관계
            
            **인사이트 해석 방법:**
            - **정량적 인사이트**: 숫자로 표현된 구체적인 발견
            - **정성적 인사이트**: 패턴이나 관계에 대한 설명
            - **실무적 인사이트**: 비즈니스에 적용할 수 있는 실용적 정보
            
            **활용 방법:**
            - 전략 수립의 근거로 활용
            - 의사결정에 참고
            - 새로운 가설 설정
            - 추가 분석 방향 제시
            
            **주의사항:**
            - 인사이트는 데이터 기반이지만 해석에 주의 필요
            - 인과관계와 상관관계를 구분해야 함
            - 지속적인 모니터링과 검증이 필요
            """)
    
    except Exception as e:
        st.error(f"통계적 인사이트 생성 중 오류: {str(e)}")
