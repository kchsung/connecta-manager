"""
평가 점수 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from .common_functions import get_evaluation_scores_statistics

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

def render_evaluation_scores_statistics():
    """평가 점수 통계"""
    st.markdown("### 📈 평가 점수 통계")
    
    try:
        # 평가 점수 통계 조회
        score_stats = get_evaluation_scores_statistics()
        
        if not score_stats:
            st.warning("평가 점수 통계 데이터가 없습니다.")
            return
        
        # 점수별 평균 표시
        st.markdown("#### 📊 점수별 평균")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("참여도", f"{score_stats['avg_engagement']:.1f}/10")
        with col2:
            st.metric("활동성", f"{score_stats['avg_activity']:.1f}/10")
        with col3:
            st.metric("소통력", f"{score_stats['avg_communication']:.1f}/10")
        with col4:
            st.metric("성장성", f"{score_stats['avg_growth_potential']:.1f}/10")
        with col5:
            st.metric("종합점수", f"{score_stats['avg_overall']:.1f}/10")
        
        # 점수 분포 히스토그램
        st.markdown("#### 📊 점수 분포")
        
        # 종합점수 분포
        if score_stats['overall_score_distribution']:
            overall_data = filter_valid_data(score_stats['overall_score_distribution'])
            if overall_data:
                fig = px.histogram(
                    x=overall_data,
                    nbins=20,
                    title="종합점수 분포",
                    labels={'x': '종합점수', 'y': '빈도'}
                )
                # 평균선 추가
                avg_overall = score_stats['avg_overall']
                if pd.notna(avg_overall) and np.isfinite(avg_overall):
                    fig.add_vline(
                        x=avg_overall, 
                        line_dash="dash", 
                        line_color="red",
                        annotation_text=f"평균: {avg_overall:.1f}",
                        annotation_position="top"
                    )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("종합점수 데이터가 없습니다.")
        
        # 추론 신뢰도 분포
        if score_stats['inference_confidence_distribution']:
            confidence_data = filter_valid_data(score_stats['inference_confidence_distribution'])
            if confidence_data:
                avg_confidence = sum(confidence_data) / len(confidence_data) if confidence_data else 0
                fig = px.histogram(
                    x=confidence_data,
                    nbins=20,
                    title="추론 신뢰도 분포",
                    labels={'x': '추론 신뢰도', 'y': '빈도'}
                )
                # 평균선 추가
                if pd.notna(avg_confidence) and np.isfinite(avg_confidence):
                    fig.add_vline(
                        x=avg_confidence, 
                        line_dash="dash", 
                        line_color="red",
                        annotation_text=f"평균: {avg_confidence:.1f}",
                        annotation_position="top"
                    )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("추론 신뢰도 데이터가 없습니다.")
        
        # 개별 점수 분포들
        st.markdown("#### 📊 개별 점수 분포")
        
        # 참여도 분포
        if score_stats['engagement_score_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                engagement_data = filter_valid_data(score_stats['engagement_score_distribution'])
                if engagement_data:
                    fig = px.histogram(
                        x=engagement_data,
                        nbins=20,
                        title="참여도 분포",
                        labels={'x': '참여도', 'y': '빈도'}
                    )
                    # 평균선 추가
                    if pd.notna(score_stats['avg_engagement']) and np.isfinite(score_stats['avg_engagement']):
                        fig.add_vline(
                            x=score_stats['avg_engagement'], 
                            line_dash="dash", 
                            line_color="red",
                            annotation_text=f"평균: {score_stats['avg_engagement']:.1f}",
                            annotation_position="top"
                        )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("참여도 데이터가 없습니다.")
            
            with col2:
                activity_data = filter_valid_data(score_stats['activity_score_distribution'])
                if activity_data:
                    fig = px.histogram(
                        x=activity_data,
                        nbins=20,
                        title="활동성 분포",
                        labels={'x': '활동성', 'y': '빈도'}
                    )
                    # 평균선 추가
                    if pd.notna(score_stats['avg_activity']) and np.isfinite(score_stats['avg_activity']):
                        fig.add_vline(
                            x=score_stats['avg_activity'], 
                            line_dash="dash", 
                            line_color="red",
                            annotation_text=f"평균: {score_stats['avg_activity']:.1f}",
                            annotation_position="top"
                        )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("활동성 데이터가 없습니다.")
        
        # 소통력과 성장성 분포
        if score_stats['communication_score_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                communication_data = filter_valid_data(score_stats['communication_score_distribution'])
                if communication_data:
                    fig = px.histogram(
                        x=communication_data,
                        nbins=20,
                        title="소통력 분포",
                        labels={'x': '소통력', 'y': '빈도'}
                    )
                    # 평균선 추가
                    if pd.notna(score_stats['avg_communication']) and np.isfinite(score_stats['avg_communication']):
                        fig.add_vline(
                            x=score_stats['avg_communication'], 
                            line_dash="dash", 
                            line_color="red",
                            annotation_text=f"평균: {score_stats['avg_communication']:.1f}",
                            annotation_position="top"
                        )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("소통력 데이터가 없습니다.")
            
            with col2:
                growth_data = filter_valid_data(score_stats['growth_potential_score_distribution'])
                if growth_data:
                    fig = px.histogram(
                        x=growth_data,
                        nbins=20,
                        title="성장성 분포",
                        labels={'x': '성장성', 'y': '빈도'}
                    )
                    # 평균선 추가
                    if pd.notna(score_stats['avg_growth_potential']) and np.isfinite(score_stats['avg_growth_potential']):
                        fig.add_vline(
                            x=score_stats['avg_growth_potential'], 
                            line_dash="dash", 
                            line_color="red",
                            annotation_text=f"평균: {score_stats['avg_growth_potential']:.1f}",
                            annotation_position="top"
                        )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("성장성 데이터가 없습니다.")
        
        # 상관관계 분석
        if score_stats['correlation_data'] is not None:
            st.markdown("#### 🔗 점수 간 상관관계")
            corr_data = score_stats['correlation_data']
            
            fig = px.imshow(
                corr_data,
                text_auto=True,
                aspect="auto",
                title="점수 간 상관관계 매트릭스"
            )
            st.plotly_chart(fig, width='stretch')
        
        # 통계 해석 가이드
        st.markdown("---")
        st.markdown("#### 💡 평가 점수 통계 해석 가이드")
        
        with st.expander("🔍 상세 해석 가이드 보기", expanded=False):
            st.markdown("**📊 각 평가 항목 설명**")
            
            st.markdown("**🎯 참여도 (Engagement)**")
            st.markdown("인플루언서의 콘텐츠에 대한 팔로워들의 참여 수준을 나타냅니다. 좋아요, 댓글, 공유 등의 상호작용을 종합적으로 평가합니다.")
            
            st.markdown("**⚡ 활동성 (Activity)**")
            st.markdown("인플루언서의 콘텐츠 업로드 빈도와 일관성을 평가합니다. 정기적인 포스팅과 지속적인 활동을 보여주는 정도를 측정합니다.")
            
            st.markdown("**💬 소통력 (Communication)**")
            st.markdown("팔로워들과의 소통 능력과 댓글 응답률을 평가합니다. 양방향 소통이 활발하고 의미 있는 상호작용을 하는 정도를 측정합니다.")
            
            st.markdown("**📈 성장성 (Growth Potential)**")
            st.markdown("인플루언서의 향후 성장 가능성을 평가합니다. 팔로워 증가율, 브랜드 협업 가능성, 콘텐츠 품질 향상 가능성 등을 종합적으로 판단합니다.")
            
            st.markdown("**🏆 종합점수 (Overall Score)**")
            st.markdown("위 4개 항목을 종합하여 산출한 전체적인 인플루언서 평가 점수입니다. 0-10점 척도로 측정되며, 높을수록 우수한 인플루언서로 평가됩니다.")
            
            st.markdown("**🔍 추론 신뢰도 (Inference Confidence)**")
            st.markdown("AI가 해당 인플루언서를 분석할 때의 신뢰도를 나타냅니다. 데이터의 충분성과 분석의 정확성을 반영하며, 높을수록 더 신뢰할 수 있는 분석 결과입니다.")
            
            st.markdown("**📈 분포 해석 방법**")
            st.markdown("""
            - **평균선 위치:** 빨간색 점선은 해당 항목의 평균값을 나타냅니다.
            - **분포 형태:** 좌편향(평균보다 낮은 값이 많음) 또는 우편향(평균보다 높은 값이 많음)을 확인할 수 있습니다.
            - **점수 비교:** 각 항목별로 평균에서 얼마나 높거나 낮은지 시각적으로 비교할 수 있습니다.
            - **상관관계:** 점수 간 상관관계 매트릭스로 항목들 간의 연관성을 파악할 수 있습니다.
            """)
    
    except Exception as e:
        st.error(f"평가 점수 통계 조회 중 오류: {str(e)}")
