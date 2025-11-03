"""
네트워크 분석 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from .common_functions import get_enhanced_network_analysis_statistics

def filter_valid_data(data):
    """histogram에 사용할 데이터에서 NaN과 무효값 제거"""
    if not data:
        return []
    # NaN, None, inf 값 필터링
    filtered = [
        x for x in data 
        if x is not None and pd.notna(x) and np.isfinite(x)
    ]
    return filtered

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
                authenticity_data = filter_valid_data(network_stats['authenticity_distribution'])
                if authenticity_data:
                    fig = px.histogram(
                        x=authenticity_data,
                        nbins=20,
                        title="영향력 진정성 점수 분포",
                        labels={'x': '진정성 점수', 'y': '빈도'},
                        color_discrete_sequence=['#1f77b4']
                    )
                    if pd.notna(network_stats['avg_authenticity_score']) and np.isfinite(network_stats['avg_authenticity_score']):
                        fig.add_vline(x=network_stats['avg_authenticity_score'], 
                                     line_dash="dash", line_color="red",
                                     annotation_text=f"평균: {network_stats['avg_authenticity_score']:.1f}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("진정성 점수 데이터가 없습니다.")
            
            with col2:
                st.markdown("#### 📊 진정성 점수 박스플롯")
                authenticity_data = filter_valid_data(network_stats['authenticity_distribution'])
                if authenticity_data:
                    fig = px.box(
                        y=authenticity_data,
                        title="진정성 점수 분포 (박스플롯)",
                        labels={'y': '진정성 점수'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("진정성 점수 데이터가 없습니다.")
        
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
            ratio_data = filter_valid_data(network_stats['follower_following_ratio'])
            if ratio_data:
                fig = px.histogram(
                    x=ratio_data,
                    nbins=30,
                    title="팔로워/팔로잉 비율 분포",
                    labels={'x': '팔로워/팔로잉 비율', 'y': '빈도'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("팔로워/팔로잉 비율 데이터가 없습니다.")
        
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
        
        # 통계 해석 가이드
        st.markdown("---")
        st.markdown("#### 💡 네트워크 분석 통계 해석 가이드")
        
        with st.expander("🔍 상세 해석 가이드 보기", expanded=False):
            st.markdown("**📊 각 분석 항목 설명**")
            
            st.markdown("**🎯 영향력 진정성 점수**")
            st.markdown("인플루언서의 팔로워 네트워크가 얼마나 진정성 있는지 평가하는 점수입니다. 팔로워의 활동성, 상호작용 패턴, 계정 품질 등을 종합적으로 분석하여 산출됩니다.")
            
            st.markdown("**🌐 네트워크 유형**")
            st.markdown("인플루언서의 팔로워 네트워크 특성을 분류한 유형입니다. 예를 들어, '고품질 팔로워', '활성 팔로워', '봇 계정', '비활성 계정' 등으로 구분됩니다.")
            
            st.markdown("**👥 팔로워/팔로잉 비율**")
            st.markdown("인플루언서가 팔로우하는 계정 수 대비 자신을 팔로우하는 계정 수의 비율입니다. 높은 비율은 영향력 있는 인플루언서를 나타내며, 낮은 비율은 상호 팔로우가 많은 계정을 의미합니다.")
            
            st.markdown("**🔗 진정성 점수와 팔로워 수 상관관계**")
            st.markdown("팔로워 수가 많을수록 진정성 점수가 높아지는지, 아니면 반대인지를 분석합니다. 이를 통해 팔로워 수와 네트워크 품질 간의 관계를 파악할 수 있습니다.")
            
            st.markdown("**🏆 네트워크 품질 등급**")
            st.markdown("진정성 점수를 기반으로 인플루언서의 네트워크 품질을 등급별로 분류합니다. A등급(최고)부터 F등급(최저)까지 구분하여 네트워크의 전반적인 품질을 평가합니다.")
            
            st.markdown("**📈 분포 해석 방법**")
            st.markdown("""
            - **평균선 위치:** 빨간색 점선은 해당 항목의 평균값을 나타냅니다.
            - **분포 형태:** 좌편향(평균보다 낮은 값이 많음) 또는 우편향(평균보다 높은 값이 많음)을 확인할 수 있습니다.
            - **박스플롯:** 데이터의 분산, 이상치, 사분위수를 시각적으로 확인할 수 있습니다.
            - **상관관계:** 두 변수 간의 선형 관계를 파악하고 트렌드라인으로 추세를 확인할 수 있습니다.
            - **등급 분포:** 각 품질 등급에 속하는 인플루언서의 비율을 확인할 수 있습니다.
            """)
    
    except Exception as e:
        st.error(f"네트워크 분석 통계 조회 중 오류: {str(e)}")
