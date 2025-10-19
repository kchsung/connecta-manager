"""
활동성/반응성 메트릭 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
from .common_functions import get_enhanced_activity_metrics_statistics

def render_activity_metrics_statistics():
    """활동성/반응성 메트릭 통계 - 고도화된 버전"""
    st.markdown("### 📈 활동성/반응성 메트릭 통계")
    
    try:
        # 활동성 메트릭 통계 조회
        activity_stats = get_enhanced_activity_metrics_statistics()
        
        if not activity_stats:
            st.warning("활동성 메트릭 데이터가 없습니다.")
            st.info("💡 AI 분석이 완료된 데이터가 있는지 확인해주세요.")
            
            # 디버깅 정보 표시
            with st.expander("🔍 디버깅 정보", expanded=False):
                st.write("**활동성/반응성 통계에서 분석하는 데이터:**")
                st.write("")
                st.write("**1. 직접 데이터 (우선순위):**")
                st.write("- `follow_network_analysis.avg_likes_last5` - 최근 5개 포스트 평균 좋아요")
                st.write("- `follow_network_analysis.recency_span_last5_days` - 최근 5개 포스트 활동 주기")
                st.write("- `follow_network_analysis.posting_pace_last5` - 최근 5개 포스트 게시 빈도")
                st.write("- `follow_network_analysis.est_engagement_rate_last5` - 최근 5개 포스트 추정 참여율")
                st.write("- `comment_authenticity_analysis.avg_comments_last5` - 최근 5개 포스트 평균 댓글")
                st.write("")
                st.write("**2. 추정 데이터 (대체 방법):**")
                st.write("- **참여율**: 팔로워/팔로잉 비율 기반 추정")
                st.write("- **좋아요**: 진정성 점수 기반 추정")
                st.write("- **댓글**: 진정성 비율 기반 추정")
                st.write("- **활동 주기**: 게시물 수 기반 추정")
                st.write("- **게시 빈도**: 네트워크 유형 기반 추정")
                st.write("")
                st.write("**가능한 원인:**")
                st.write("- AI 분석이 아직 완료되지 않음")
                st.write("- JSON 필드명이 다름")
                st.write("- 데이터 구조가 예상과 다름")
                st.write("- 실제 데이터가 없어 분석할 수 없음")
            return
        
        # 디버깅 정보 표시
        st.info(f"📊 활동성 메트릭 데이터 로드 완료: {len(activity_stats.get('engagement_rate_distribution', []))}개 항목")
        
        # 최근 5개 포스트 통계 - 참여율만 표시
        st.markdown("#### 📊 최근 5개 포스트 분석")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("평균 참여율", f"{activity_stats['avg_engagement_rate']:.2f}%")
        with col2:
            st.metric("참여율 표준편차", f"{activity_stats['std_engagement_rate']:.2f}%")
        
        # 활동 주기 분석
        st.markdown("#### ⏰ 활동 주기 분석")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("평균 활동 주기", f"{activity_stats['avg_recency_span']:.1f}일")
        with col2:
            st.metric("중앙값 활동 주기", f"{activity_stats['median_recency_span']:.1f}일")
        with col3:
            st.metric("최단 활동 주기", f"{activity_stats['min_recency_span']:.1f}일")
        with col4:
            st.metric("최장 활동 주기", f"{activity_stats['max_recency_span']:.1f}일")
        with col5:
            st.metric("활동 주기 표준편차", f"{activity_stats['std_recency_span']:.1f}일")
        
        # 좋아요와 댓글 상관관계 분석
        if activity_stats['likes_comments_correlation']:
            st.markdown("#### 🔗 좋아요와 댓글 상관관계")
            col1, col2 = st.columns(2)
            
            with col1:
                correlation_data = activity_stats['likes_comments_correlation']
                fig = px.scatter(
                    x=correlation_data['likes'],
                    y=correlation_data['comments'],
                    title="좋아요 vs 댓글 수",
                    labels={'x': '좋아요 수', 'y': '댓글 수'},
                    trendline="ols"
                )
                fig.update_layout(xaxis_type="log", yaxis_type="log")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 상관계수와 통계 정보
                correlation_coef = activity_stats.get('likes_comments_correlation_coef', 0)
                st.metric("상관계수", f"{correlation_coef:.3f}")
                
                # 참여율과 좋아요 상관관계
                if activity_stats.get('engagement_likes_correlation_coef'):
                    st.metric("참여율-좋아요 상관계수", f"{activity_stats['engagement_likes_correlation_coef']:.3f}")
        
        # 게시 빈도와 활동성 분석
        if activity_stats['posting_pace_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📅 게시 빈도 분포")
                fig = px.pie(
                    values=list(activity_stats['posting_pace_distribution'].values()),
                    names=list(activity_stats['posting_pace_distribution'].keys()),
                    title="게시 빈도 분포"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 게시 빈도별 평균 참여율")
                if activity_stats['posting_pace_engagement']:
                    pace_types = list(activity_stats['posting_pace_engagement'].keys())
                    engagement_rates = list(activity_stats['posting_pace_engagement'].values())
                    
                    fig = px.bar(
                        x=pace_types,
                        y=engagement_rates,
                        title="게시 빈도별 평균 참여율",
                        labels={'x': '게시 빈도', 'y': '평균 참여율 (%)'}
                    )
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
        
        # 참여율 분포 및 통계
        if activity_stats['engagement_rate_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 참여율 분포")
                fig = px.histogram(
                    x=activity_stats['engagement_rate_distribution'],
                    nbins=20,
                    title="참여율 분포",
                    labels={'x': '참여율 (%)', 'y': '빈도'},
                    color_discrete_sequence=['#2ecc71']
                )
                fig.add_vline(x=activity_stats['avg_engagement_rate'], 
                             line_dash="dash", line_color="red",
                             annotation_text=f"평균: {activity_stats['avg_engagement_rate']:.2f}%")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 참여율 박스플롯")
                fig = px.box(
                    y=activity_stats['engagement_rate_distribution'],
                    title="참여율 분포 (박스플롯)",
                    labels={'y': '참여율 (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 활동성 등급 분포
        if activity_stats['activity_grade_distribution']:
            st.markdown("#### 🏆 활동성 등급 분포")
            fig = px.bar(
                x=list(activity_stats['activity_grade_distribution'].keys()),
                y=list(activity_stats['activity_grade_distribution'].values()),
                title="활동성 등급 분포",
                labels={'x': '활동성 등급', 'y': '인플루언서 수'},
                color=list(activity_stats['activity_grade_distribution'].keys()),
                color_discrete_sequence=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 참여율 트렌드 분석 (시뮬레이션)
        if activity_stats['engagement_rate_distribution']:
            st.markdown("#### 📈 참여율 트렌드 분석")
            
            # 참여율 구간별 분포
            engagement_ranges = {
                "매우 높음 (5% 이상)": 0,
                "높음 (3-5%)": 0,
                "보통 (1-3%)": 0,
                "낮음 (0.5-1%)": 0,
                "매우 낮음 (0.5% 미만)": 0
            }
            
            for rate in activity_stats['engagement_rate_distribution']:
                if rate >= 5.0:
                    engagement_ranges["매우 높음 (5% 이상)"] += 1
                elif rate >= 3.0:
                    engagement_ranges["높음 (3-5%)"] += 1
                elif rate >= 1.0:
                    engagement_ranges["보통 (1-3%)"] += 1
                elif rate >= 0.5:
                    engagement_ranges["낮음 (0.5-1%)"] += 1
                else:
                    engagement_ranges["매우 낮음 (0.5% 미만)"] += 1
            
            fig = px.pie(
                values=list(engagement_ranges.values()),
                names=list(engagement_ranges.keys()),
                title="참여율 구간별 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"활동성 메트릭 통계 조회 중 오류: {str(e)}")
