"""
네트워크 분석 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
from .common_functions import get_enhanced_network_analysis_statistics

def render_network_analysis_statistics():
    """네트워크 분석 통계 - 고도화된 버전"""
    st.markdown("### 🌐 네트워크 분석 통계")
    
    try:
        # 네트워크 분석 통계 조회
        network_stats = get_enhanced_network_analysis_statistics()
        
        if not network_stats:
            st.warning("네트워크 분석 통계 데이터가 없습니다.")
            return
        
        # 영향력 진정성 점수 통계
        st.markdown("#### 📊 영향력 진정성 점수")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("평균 점수", f"{network_stats['avg_authenticity_score']:.1f}")
        with col2:
            st.metric("중앙값", f"{network_stats['median_authenticity_score']:.1f}")
        with col3:
            st.metric("최고점", f"{network_stats['max_authenticity_score']:.1f}")
        with col4:
            st.metric("최저점", f"{network_stats['min_authenticity_score']:.1f}")
        with col5:
            st.metric("표준편차", f"{network_stats['std_authenticity_score']:.1f}")
        
        # 진정성 점수 분포 및 통계
        if network_stats['authenticity_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 진정성 점수 분포")
                fig = px.histogram(
                    x=network_stats['authenticity_distribution'],
                    nbins=20,
                    title="영향력 진정성 점수 분포",
                    labels={'x': '진정성 점수', 'y': '빈도'},
                    color_discrete_sequence=['#1f77b4']
                )
                fig.add_vline(x=network_stats['avg_authenticity_score'], 
                             line_dash="dash", line_color="red",
                             annotation_text=f"평균: {network_stats['avg_authenticity_score']:.1f}")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 진정성 점수 박스플롯")
                fig = px.box(
                    y=network_stats['authenticity_distribution'],
                    title="진정성 점수 분포 (박스플롯)",
                    labels={'y': '진정성 점수'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 네트워크 유형별 상세 분석
        if network_stats['network_type_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🌐 네트워크 유형 분포")
                fig = px.pie(
                    values=list(network_stats['network_type_distribution'].values()),
                    names=list(network_stats['network_type_distribution'].keys()),
                    title="네트워크 유형 분포"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 네트워크 유형별 진정성 점수")
                if network_stats['network_type_authenticity']:
                    network_types = list(network_stats['network_type_authenticity'].keys())
                    authenticity_scores = list(network_stats['network_type_authenticity'].values())
                    
                    fig = px.bar(
                        x=network_types,
                        y=authenticity_scores,
                        title="네트워크 유형별 평균 진정성 점수",
                        labels={'x': '네트워크 유형', 'y': '평균 진정성 점수'}
                    )
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
        
        # 팔로워/팔로잉 비율 분석
        if network_stats['follower_following_ratio']:
            st.markdown("#### 👥 팔로워/팔로잉 비율 분석")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("평균 팔로워/팔로잉 비율", f"{network_stats['avg_follower_following_ratio']:.2f}")
            with col2:
                st.metric("중앙값 팔로워/팔로잉 비율", f"{network_stats['median_follower_following_ratio']:.2f}")
            with col3:
                st.metric("최대 팔로워/팔로잉 비율", f"{network_stats['max_follower_following_ratio']:.2f}")
            
            # 팔로워/팔로잉 비율 분포
            fig = px.histogram(
                x=network_stats['follower_following_ratio'],
                nbins=30,
                title="팔로워/팔로잉 비율 분포",
                labels={'x': '팔로워/팔로잉 비율', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 진정성 점수와 팔로워 수 상관관계
        if network_stats['authenticity_follower_correlation']:
            st.markdown("#### 🔗 진정성 점수와 팔로워 수 상관관계")
            correlation_data = network_stats['authenticity_follower_correlation']
            
            fig = px.scatter(
                x=correlation_data['followers'],
                y=correlation_data['authenticity_scores'],
                title="진정성 점수 vs 팔로워 수",
                labels={'x': '팔로워 수', 'y': '진정성 점수'},
                trendline="ols"
            )
            fig.update_layout(xaxis_type="log")  # 로그 스케일로 표시
            st.plotly_chart(fig, use_container_width=True)
            
            # 상관계수 표시
            correlation_coef = network_stats.get('authenticity_follower_correlation_coef', 0)
            st.info(f"상관계수: {correlation_coef:.3f}")
        
        # 네트워크 품질 등급 분포
        if network_stats['network_quality_grades']:
            st.markdown("#### 🏆 네트워크 품질 등급 분포")
            fig = px.bar(
                x=list(network_stats['network_quality_grades'].keys()),
                y=list(network_stats['network_quality_grades'].values()),
                title="네트워크 품질 등급 분포",
                labels={'x': '품질 등급', 'y': '인플루언서 수'},
                color=list(network_stats['network_quality_grades'].keys()),
                color_discrete_sequence=['#00cc88', '#88cc00', '#ffaa00', '#ff8800', '#ff4444']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"네트워크 분석 통계 조회 중 오류: {str(e)}")
