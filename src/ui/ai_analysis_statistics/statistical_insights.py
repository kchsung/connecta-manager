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
            
            # 이상치 시각화
            outlier_viz = insights_data.get('outlier_visualization')
            if outlier_viz is not None and not outlier_viz.empty:
                # NaN 값 필터링
                outlier_viz_clean = outlier_viz.dropna(subset=['followers', 'engagement_rate', 'overall_score'])
                
                if not outlier_viz_clean.empty:
                    fig = px.scatter(
                        outlier_viz_clean,
                        x='followers',
                        y='engagement_rate',
                        color='is_outlier',
                        size='overall_score',
                        title="이상치 탐지 (참여율 기준)",
                        labels={
                            'followers': '팔로워 수',
                            'engagement_rate': '참여율 (%)',
                            'is_outlier': '이상치 여부',
                            'overall_score': '종합점수'
                        }
                    )
                    fig.update_layout(xaxis_type="log")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 이상치 시각화를 위한 유효한 데이터가 없습니다.")
        
        # 2. 성과 예측 모델
        st.markdown("#### 🔮 성과 예측 모델")
        model_data = insights_data.get('prediction_model', {})
        
        if model_data:
            st.info(f"**모델 정확도**: {model_data.get('accuracy', 0):.2%}")
            st.info(f"**주요 예측 변수**: {', '.join(model_data.get('top_features', ['참여율', '진정성 점수', '팔로워 수']))}")
            
            # 예측 vs 실제 성과
            pred_data = model_data.get('prediction_vs_actual')
            if pred_data is not None and not pred_data.empty:
                fig = px.scatter(
                    pred_data,
                    x='actual',
                    y='predicted',
                    title="예측 vs 실제 성과",
                    labels={'actual': '실제 성과', 'predicted': '예측 성과'},
                    trendline="ols"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 예측 vs 실제 성과 차트 데이터가 없습니다.")
        else:
            st.warning("⚠️ 성과 예측 모델 데이터를 사용할 수 없습니다.")
        
        # 3. 클러스터링 분석
        st.markdown("#### 🎯 클러스터링 분석")
        cluster_data = insights_data.get('clustering', {})
        
        if cluster_data:
            st.info(f"**최적 클러스터 수**: {cluster_data.get('optimal_clusters', 3)}개")
            
            # 클러스터 시각화
            cluster_viz = cluster_data.get('cluster_visualization')
            if cluster_viz is not None and not cluster_viz.empty:
                # NaN 값 필터링
                cluster_viz_clean = cluster_viz.dropna(subset=['engagement_rate', 'authenticity_score', 'followers'])
                
                if not cluster_viz_clean.empty:
                    fig = px.scatter(
                        cluster_viz_clean,
                        x='engagement_rate',
                        y='authenticity_score',
                        color='cluster',
                        size='followers',
                        title="인플루언서 클러스터링 결과",
                        labels={
                            'engagement_rate': '참여율 (%)',
                            'authenticity_score': '진정성 점수',
                            'cluster': '클러스터',
                            'followers': '팔로워 수'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 클러스터 시각화를 위한 유효한 데이터가 없습니다.")
            else:
                st.info("📊 클러스터 시각화 데이터가 없습니다.")
            
            # 클러스터별 특성
            cluster_chars = cluster_data.get('cluster_characteristics')
            if cluster_chars:
                st.markdown("**클러스터별 특성:**")
                for cluster_id, characteristics in cluster_chars.items():
                    with st.expander(f"클러스터 {cluster_id}"):
                        for char, value in characteristics.items():
                            st.write(f"**{char}**: {value}")
            else:
                st.info("📊 클러스터별 특성 데이터가 없습니다.")
        else:
            st.warning("⚠️ 클러스터링 분석 데이터를 사용할 수 없습니다.")
        
        # 4. 트렌드 분석
        st.markdown("#### 📈 트렌드 분석")
        trend_data = insights_data.get('trend_analysis', {})
        
        if trend_data:
            
            # 트렌드 차트
            fig = go.Figure()
            
            for metric, values in trend_data['metrics'].items():
                fig.add_trace(go.Scatter(
                    x=trend_data['time_periods'],
                    y=values,
                    mode='lines+markers',
                    name=metric
                ))
            
            fig.update_layout(
                title="지표별 트렌드 분석",
                xaxis_title="기간",
                yaxis_title="평균 값"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 트렌드 요약
            if trend_data.get('trend_summary'):
                summary = trend_data['trend_summary']
                st.markdown("**트렌드 요약:**")
                for metric, trend in summary.items():
                    trend_icon = "📈" if trend == "상승" else "📉" if trend == "하락" else "➡️"
                    st.write(f"{trend_icon} **{metric}**: {trend}")
            else:
                st.info("📊 트렌드 요약 데이터가 없습니다.")
        else:
            st.warning("⚠️ 트렌드 분석 데이터를 사용할 수 없습니다.")
        
        # 5. 인사이트 요약
        st.markdown("#### 💡 핵심 인사이트")
        if insights_data.get('key_insights'):
            insights = insights_data['key_insights']
            
            for i, insight in enumerate(insights, 1):
                st.info(f"**인사이트 {i}**: {insight}")
    
    except Exception as e:
        st.error(f"통계적 인사이트 생성 중 오류: {str(e)}")
