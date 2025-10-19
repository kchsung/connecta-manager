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
            st.plotly_chart(fig, use_container_width=True)
        
        # 2. 3D 산점도 (팔로워 수, 참여율, 진정성 점수)
        st.markdown("#### 🌐 3D 산점도 분석")
        if comprehensive_data.get('3d_scatter_data') is not None and not comprehensive_data['3d_scatter_data'].empty:
            scatter_3d_data = comprehensive_data['3d_scatter_data']
            fig = px.scatter_3d(
                scatter_3d_data,
                x='followers',
                y='engagement_rate',
                z='authenticity_score',
                color='category',
                size='overall_score',
                title="팔로워 수 vs 참여율 vs 진정성 점수 (3D)",
                labels={
                    'followers': '팔로워 수',
                    'engagement_rate': '참여율 (%)',
                    'authenticity_score': '진정성 점수',
                    'category': '카테고리',
                    'overall_score': '종합점수'
                }
            )
            fig.update_layout(scene=dict(
                xaxis_title="팔로워 수 (로그)",
                yaxis_title="참여율 (%)",
                zaxis_title="진정성 점수"
            ))
            fig.update_layout(xaxis_type="log")
            st.plotly_chart(fig, use_container_width=True)
        
        # 3. 다중 지표 분포 비교
        st.markdown("#### 📊 다중 지표 분포 비교")
        if comprehensive_data.get('multi_metric_distribution'):
            multi_data = comprehensive_data['multi_metric_distribution']
            
            # 데이터 정보 표시
            with st.expander("📋 데이터 정보", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("참여율 데이터 수", len(multi_data['engagement_rates']))
                    if multi_data['engagement_rates']:
                        st.write(f"범위: {min(multi_data['engagement_rates']):.2f} ~ {max(multi_data['engagement_rates']):.2f}")
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
                subplot_titles=('참여율 분포', '진정성 점수 분포', '종합점수 분포', '팔로워/팔로잉 비율 분포'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 참여율 분포
            fig.add_trace(
                go.Histogram(
                    x=multi_data['engagement_rates'], 
                    name='참여율', 
                    nbinsx=10,
                    marker_color='#3498db',
                    opacity=0.7
                ),
                row=1, col=1
            )
            
            # 진정성 점수 분포
            fig.add_trace(
                go.Histogram(
                    x=multi_data['authenticity_scores'], 
                    name='진정성 점수', 
                    nbinsx=10,
                    marker_color='#e74c3c',
                    opacity=0.7
                ),
                row=1, col=2
            )
            
            # 종합점수 분포
            fig.add_trace(
                go.Histogram(
                    x=multi_data['overall_scores'], 
                    name='종합점수', 
                    nbinsx=10,
                    marker_color='#2ecc71',
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # 팔로워/팔로잉 비율 분포
            fig.add_trace(
                go.Histogram(
                    x=multi_data['follower_ratios'], 
                    name='팔로워/팔로잉 비율', 
                    nbinsx=10,
                    marker_color='#f39c12',
                    opacity=0.7
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=False, title_text="다중 지표 분포 비교")
            st.plotly_chart(fig, use_container_width=True)
        
        # 4. 카테고리별 성과 매트릭스
        st.markdown("#### 🎯 카테고리별 성과 매트릭스")
        if comprehensive_data.get('category_performance'):
            category_perf = comprehensive_data['category_performance']
            
            # 카테고리별 평균 지표
            categories = list(category_perf.keys())
            engagement_avg = [category_perf[cat]['avg_engagement'] for cat in categories]
            authenticity_avg = [category_perf[cat]['avg_authenticity'] for cat in categories]
            overall_avg = [category_perf[cat]['avg_overall'] for cat in categories]
            
            fig = go.Figure(data=[
                go.Bar(name='평균 참여율', x=categories, y=engagement_avg, yaxis='y'),
                go.Bar(name='평균 진정성', x=categories, y=authenticity_avg, yaxis='y2'),
                go.Bar(name='평균 종합점수', x=categories, y=overall_avg, yaxis='y3')
            ])
            
            fig.update_layout(
                title="카테고리별 성과 매트릭스",
                xaxis_title="카테고리",
                yaxis=dict(title="참여율 (%)", side="left"),
                yaxis2=dict(title="진정성 점수", side="right", overlaying="y"),
                yaxis3=dict(title="종합점수", side="right", overlaying="y", position=0.85),
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 5. 성과 등급별 분포
        st.markdown("#### 🏆 성과 등급별 분포")
        if comprehensive_data.get('performance_grades'):
            grade_data = comprehensive_data['performance_grades']
            
            fig = px.sunburst(
                values=list(grade_data.values()),
                names=list(grade_data.keys()),
                title="성과 등급별 분포 (Sunburst Chart)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"고급 시각화 생성 중 오류: {str(e)}")
