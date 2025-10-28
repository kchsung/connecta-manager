"""
고급 시각화 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .common_functions import get_comprehensive_analysis_data

def render_advanced_visualizations():
    """고급 시각화"""
    st.markdown("### 🔥 고급 시각화")
    st.markdown("다양한 차원의 데이터를 종합적으로 분석하는 고급 시각화를 제공합니다.")
    
    try:
        # 종합 데이터 조회
        comprehensive_data = get_comprehensive_analysis_data()
        
        if not comprehensive_data:
            st.warning("종합 분석 데이터가 없습니다.")
            return
        
        # 1. 상관관계 히트맵
        st.markdown("#### 🔥 종합 상관관계 히트맵")
        if comprehensive_data.get('correlation_matrix') is not None:
            fig = px.imshow(
                comprehensive_data['correlation_matrix'],
                text_auto=True,
                aspect="auto",
                title="인플루언서 지표 간 상관관계 히트맵",
                color_continuous_scale="RdBu_r"
            )
            st.plotly_chart(fig, width='stretch')
        
        # 2. 2D 산점도 분석 (팔로워 수 vs 참여율)
        st.markdown("#### 📊 팔로워 수 vs 참여율 분석")
        if comprehensive_data.get('3d_scatter_data') is not None and not comprehensive_data['3d_scatter_data'].empty:
            scatter_data = comprehensive_data['3d_scatter_data']
            
            # NaN 값 필터링 및 유효한 데이터만 선택
            scatter_clean = scatter_data.dropna(subset=['followers', 'engagement_score', 'authenticity_score', 'overall_score'])
            
            # 추가 데이터 정제: 0보다 큰 값만 선택하고 NaN 제거
            scatter_clean = scatter_clean[
                (scatter_clean['followers'] > 0) & 
                (scatter_clean['engagement_score'] > 0) & 
                (scatter_clean['authenticity_score'] > 0) & 
                (scatter_clean['overall_score'] > 0)
            ].copy()
            
            # NaN 값이 있는 경우 기본값으로 대체
            scatter_clean['followers'] = scatter_clean['followers'].fillna(1000)
            scatter_clean['engagement_score'] = scatter_clean['engagement_score'].fillna(5.0)
            scatter_clean['authenticity_score'] = scatter_clean['authenticity_score'].fillna(5.0)
            scatter_clean['overall_score'] = scatter_clean['overall_score'].fillna(5.0)
            scatter_clean['category'] = scatter_clean['category'].fillna('기타')
            
            if not scatter_clean.empty:
                fig = px.scatter(
                    scatter_clean,
                    x='followers',
                    y='engagement_score',
                    color='category',
                    size='overall_score',
                    hover_data=['authenticity_score'],
                    title="팔로워 수 vs 참여 점수 (버블 크기: 종합점수, 색상: 카테고리)",
                    labels={
                        'followers': '팔로워 수',
                        'engagement_score': '참여 점수',
                        'authenticity_score': '진정성 점수',
                        'category': '카테고리',
                        'overall_score': '종합점수'
                    }
                )
                fig.update_layout(
                    xaxis_title="팔로워 수 (로그 스케일)",
                    yaxis_title="참여 점수",
                    xaxis_type="log"
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.warning("유효한 산점도 데이터가 없습니다.")
        
        # 3. 참여 점수 vs 진정성 점수 분석
        st.markdown("#### 💎 참여 점수 vs 진정성 점수 분석")
        if comprehensive_data.get('3d_scatter_data') is not None and not comprehensive_data['3d_scatter_data'].empty:
            scatter_data = comprehensive_data['3d_scatter_data']
            
            # NaN 값 필터링 및 유효한 데이터만 선택
            scatter_clean = scatter_data.dropna(subset=['engagement_score', 'authenticity_score', 'overall_score', 'followers'])
            
            # 추가 데이터 정제: 0보다 큰 값만 선택하고 NaN 제거
            scatter_clean = scatter_clean[
                (scatter_clean['engagement_score'] > 0) & 
                (scatter_clean['authenticity_score'] > 0) & 
                (scatter_clean['overall_score'] > 0) &
                (scatter_clean['followers'] > 0)
            ].copy()
            
            # NaN 값이 있는 경우 기본값으로 대체
            scatter_clean['followers'] = scatter_clean['followers'].fillna(1000)
            scatter_clean['engagement_score'] = scatter_clean['engagement_score'].fillna(5.0)
            scatter_clean['authenticity_score'] = scatter_clean['authenticity_score'].fillna(5.0)
            scatter_clean['overall_score'] = scatter_clean['overall_score'].fillna(5.0)
            scatter_clean['category'] = scatter_clean['category'].fillna('기타')
            
            if not scatter_clean.empty:
                fig = px.scatter(
                    scatter_clean,
                    x='engagement_score',
                    y='authenticity_score',
                    color='category',
                    size='followers',
                    hover_data=['overall_score'],
                    title="참여 점수 vs 진정성 점수 (버블 크기: 팔로워 수, 색상: 카테고리)",
                    labels={
                        'engagement_score': '참여 점수',
                        'authenticity_score': '진정성 점수',
                        'category': '카테고리',
                        'followers': '팔로워 수',
                        'overall_score': '종합점수'
                    }
                )
                fig.update_layout(
                    xaxis_title="참여 점수",
                    yaxis_title="진정성 점수"
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.warning("유효한 참여율-진정성 분석 데이터가 없습니다.")
        
        # 3. 다중 지표 분포 비교
        st.markdown("#### 📊 다중 지표 분포 비교")
        if comprehensive_data.get('multi_metric_distribution'):
            multi_data = comprehensive_data['multi_metric_distribution']
            
            # 데이터 정보 표시
            with st.expander("📋 데이터 정보", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("참여 점수 데이터 수", len(multi_data['engagement_scores']))
                    if multi_data['engagement_scores']:
                        st.write(f"범위: {min(multi_data['engagement_scores']):.2f} ~ {max(multi_data['engagement_scores']):.2f}")
                with col2:
                    st.metric("진정성 점수 데이터 수", len(multi_data['authenticity_scores']))
                    if multi_data['authenticity_scores']:
                        st.write(f"범위: {min(multi_data['authenticity_scores']):.2f} ~ {max(multi_data['authenticity_scores']):.2f}")
                with col3:
                    st.metric("종합점수 데이터 수", len(multi_data['overall_scores']))
                    if multi_data['overall_scores']:
                        st.write(f"범위: {min(multi_data['overall_scores']):.2f} ~ {max(multi_data['overall_scores']):.2f}")
                with col4:
                    st.metric("팔로워/팔로잉 비율 데이터 수", len(multi_data['follower_ratios']))
                    if multi_data['follower_ratios']:
                        st.write(f"범위: {min(multi_data['follower_ratios']):.2f} ~ {max(multi_data['follower_ratios']):.2f}")
            
            # 서브플롯 생성
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('참여 점수 분포', '진정성 점수 분포', '종합점수 분포', '팔로워/팔로잉 비율 분포'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 데이터 정제: NaN 값 제거
            import pandas as pd
            engagement_scores = [x for x in multi_data['engagement_scores'] if not pd.isna(x) and x > 0]
            authenticity_scores = [x for x in multi_data['authenticity_scores'] if not pd.isna(x) and x > 0]
            overall_scores = [x for x in multi_data['overall_scores'] if not pd.isna(x) and x > 0]
            follower_ratios = [x for x in multi_data['follower_ratios'] if not pd.isna(x) and x > 0]
            
            # 참여 점수 분포
            if engagement_scores:
                fig.add_trace(
                    go.Histogram(
                        x=engagement_scores, 
                        name='참여 점수', 
                        nbinsx=10,
                        marker_color='#3498db',
                        opacity=0.7
                    ),
                    row=1, col=1
                )
            
            # 진정성 점수 분포
            if authenticity_scores:
                fig.add_trace(
                    go.Histogram(
                        x=authenticity_scores, 
                        name='진정성 점수', 
                        nbinsx=10,
                        marker_color='#e74c3c',
                        opacity=0.7
                    ),
                    row=1, col=2
                )
            
            # 종합점수 분포
            if overall_scores:
                fig.add_trace(
                    go.Histogram(
                        x=overall_scores, 
                        name='종합점수', 
                        nbinsx=10,
                        marker_color='#2ecc71',
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            # 팔로워/팔로잉 비율 분포
            if follower_ratios:
                fig.add_trace(
                    go.Histogram(
                        x=follower_ratios, 
                        name='팔로워/팔로잉 비율', 
                        nbinsx=10,
                        marker_color='#f39c12',
                        opacity=0.7
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(height=600, showlegend=False, title_text="다중 지표 분포 비교")
            st.plotly_chart(fig, width='stretch')
        
        
        # 지표 설명 섹션
        st.markdown("---")
        st.markdown("### 📋 지표 설명")
        
        with st.expander("🔍 상관관계 히트맵 지표 설명", expanded=False):
            st.markdown("""
            **상관관계 히트맵**은 각 지표 간의 상관관계를 색상으로 표현합니다.
            
            - **빨간색 (양의 상관관계)**: 두 지표가 함께 증가하거나 감소하는 경향
            - **파란색 (음의 상관관계)**: 한 지표가 증가할 때 다른 지표가 감소하는 경향
            - **흰색 (상관관계 없음)**: 두 지표 간에 선형적 관계가 거의 없음
            
            **주요 지표들:**
            - **참여율**: (좋아요 + 댓글 + 공유) / 팔로워 수 × 100
            - **진정성 점수**: 댓글의 자연스러움과 다양성을 AI가 분석한 점수 (0-100)
            - **종합점수**: 참여율, 진정성, 팔로워 품질 등을 종합한 점수 (0-100)
            - **팔로워/팔로잉 비율**: 팔로워 수 / 팔로잉 수
            """)
        
        with st.expander("📊 2D 산점도 분석 설명", expanded=False):
            st.markdown("""
            **2D 산점도 분석**은 주요 지표들 간의 관계를 명확하게 시각화합니다.
            
            **팔로워 수 vs 참여율 분석:**
            - **X축 (팔로워 수)**: 인플루언서의 팔로워 규모 (로그 스케일)
            - **Y축 (참여율)**: 팔로워들의 참여도 (좋아요, 댓글, 공유 비율)
            - **버블 크기**: 종합점수 (클수록 더 높은 성과)
            - **색상**: 카테고리별 구분
            - **호버 데이터**: 진정성 점수 표시
            
            **참여율 vs 진정성 점수 분석:**
            - **X축 (참여율)**: 팔로워들의 참여도
            - **Y축 (진정성 점수)**: 콘텐츠와 댓글의 진정성 정도
            - **버블 크기**: 팔로워 수 (클수록 더 큰 규모)
            - **색상**: 카테고리별 구분
            - **호버 데이터**: 종합점수 표시
            
            **해석 방법:**
            - **우상단**: 높은 참여율과 진정성을 가진 인플루언서
            - **좌하단**: 낮은 참여율과 진정성을 가진 인플루언서
            - **중앙**: 평균적인 성과를 보이는 인플루언서
            - **대각선 패턴**: 참여율과 진정성이 비례하는 관계
            """)
        
        with st.expander("📊 다중 지표 분포 비교 설명", expanded=False):
            st.markdown("""
            **다중 지표 분포**는 각 지표의 데이터 분포를 히스토그램으로 보여줍니다.
            
            **참여율 분포:**
            - 일반적으로 1-5% 범위에서 정규분포 형태
            - 높은 참여율(5% 이상)은 우수한 인플루언서
            - 낮은 참여율(1% 미만)은 개선이 필요한 인플루언서
            
            **진정성 점수 분포:**
            - 0-100 점수 범위
            - 70점 이상: 높은 진정성
            - 50-70점: 보통 진정성
            - 50점 미만: 낮은 진정성
            
            **종합점수 분포:**
            - 모든 지표를 종합한 최종 평가 점수
            - 80점 이상: S급 인플루언서
            - 60-80점: A급 인플루언서
            - 40-60점: B급 인플루언서
            - 40점 미만: C급 인플루언서
            
            **팔로워/팔로잉 비율:**
            - 10:1 이상: 높은 영향력 (팔로워가 팔로잉보다 10배 이상)
            - 5:1 ~ 10:1: 보통 영향력
            - 5:1 미만: 낮은 영향력
            """)
        
    
    except Exception as e:
        st.error(f"고급 시각화 생성 중 오류: {str(e)}")
