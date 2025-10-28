"""
기본 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
from collections import Counter
import io
import base64

# matplotlib와 wordcloud는 선택적 import
try:
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from .common_functions import (
    get_total_analyses_count,
    get_recent_analyses_count,
    get_average_overall_score,
    get_recommendation_distribution,
    get_category_distribution,
    get_analysis_rate,
    get_tags_for_wordcloud,
    get_category_tags,
    get_category_average_scores
)

def render_basic_statistics():
    """기본 통계"""
    st.markdown("### 📊 기본 통계")
    
    # 페이지 설명 추가
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border-left: 4px solid #007bff;">
        <h4 style="margin: 0 0 0.5rem 0; color: #495057;">📋 기본 통계 개요</h4>
        <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">
            AI 분석 결과의 핵심 지표들을 한눈에 확인할 수 있습니다. 
            <strong>총 분석 수</strong>, <strong>최근 7일 분석</strong>, <strong>평균 종합점수</strong>, <strong>분석률</strong>을 통해 
            전체적인 분석 현황을 파악하고, <strong>카테고리별 히스토그램</strong>을 통해 
            인플루언서들의 특성과 분포를 시각적으로 이해할 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 기본 통계 조회
        total_analyses = get_total_analyses_count()
        recent_analyses = get_recent_analyses_count()
        avg_score = get_average_overall_score()
        
        # 핵심 지표 섹션
        st.markdown("#### 📈 핵심 지표")
        st.markdown("AI 분석의 전반적인 현황을 나타내는 주요 지표들입니다.")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 분석 수", f"{total_analyses:,}")
        
        with col2:
            st.metric("최근 7일 분석", f"{recent_analyses:,}")
        
        with col3:
            st.metric("평균 종합점수", f"{avg_score:.1f}/10")
        
        with col4:
            # 분석률: tb_instagram_crawling 테이블 대비 ai_influencer_analyses 테이블의 비율
            analysis_rate = get_analysis_rate()
            st.metric("분석률", f"{analysis_rate:.1f}%")
        
        # 태그 분석 기능 일시 제외
        # st.markdown("#### 🏷️ 인플루언서 태그 분석")
        # st.markdown("AI 분석을 통해 도출된 인플루언서 태그들의 분포를 확인할 수 있습니다.")
        # 
        # tags_data = get_tags_for_wordcloud()
        # 
        # if tags_data:
        #     # 태그 빈도 계산
        #     tag_counts = Counter(tags_data)
        #     
        #     if tag_counts:
        #         # matplotlib가 사용 가능한 경우 워드클라우드 표시
        #         if MATPLOTLIB_AVAILABLE:
        #             st.markdown("**워드클라우드 시각화:**")
        #             try:
        #                 # 한글 폰트 설정 (시스템에 따라 조정 필요)
        #                 try:
        #                     wordcloud = WordCloud(
        #                         width=800, 
        #                         height=400, 
        #                         background_color='white',
        #                         font_path='C:/Windows/Fonts/malgun.ttf',  # Windows 한글 폰트
        #                         max_words=100,
        #                         colormap='viridis'
        #                     ).generate_from_frequencies(tag_counts)
        #                 except:
        #                     # 한글 폰트가 없는 경우 기본 폰트 사용
        #                     wordcloud = WordCloud(
        #                         width=800, 
        #                         height=400, 
        #                         background_color='white',
        #                         max_words=100,
        #                         colormap='viridis'
        #                     ).generate_from_frequencies(tag_counts)
        #                 
        #                 # 워드클라우드를 이미지로 변환
        #                 fig, ax = plt.subplots(figsize=(10, 5))
        #                 ax.imshow(wordcloud, interpolation='bilinear')
        #                 ax.axis('off')
        #                 ax.set_title('인플루언서 태그 워드클라우드', fontsize=16, pad=20)
        #                 
        #                 # Streamlit에 표시
        #                 st.pyplot(fig)
        #                 plt.close()
        #             except Exception as e:
        #                 st.warning(f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}")
        #                 st.info("대신 태그 통계를 표시합니다.")
        #         else:
        #             pass  # matplotlib가 없어도 계속 진행
        #         
        #         # 상위 태그 통계 표시 (항상 표시)
        #         st.markdown("**상위 태그 통계:**")
        #         top_tags = tag_counts.most_common(10)
        #         
        #         # 태그 통계를 막대 차트로 표시
        #         if len(top_tags) > 0:
        #             tags_df = px.data.tips()  # 임시 데이터프레임 생성
        #             # 실제 태그 데이터로 막대 차트 생성
        #             fig = px.bar(
        #                 x=[tag for tag, count in top_tags],
        #                 y=[count for tag, count in top_tags],
        #                 title="상위 태그 빈도",
        #                 labels={'x': '태그', 'y': '빈도'},
        #                 color=[count for tag, count in top_tags],
        #                 color_continuous_scale='viridis'
        #             )
        #             fig.update_layout(
        #                 xaxis_tickangle=45,
        #                 showlegend=False,
        #                 coloraxis_showscale=False
        #             )
        #             st.plotly_chart(fig, width='stretch')
        #         
        #         # 상세 태그 통계
        #         col1, col2 = st.columns(2)
        #         
        #         with col1:
        #             st.markdown("**상위 5개 태그:**")
        #             for i, (tag, count) in enumerate(top_tags[:5]):
        #                 st.metric(f"{i+1}. {tag}", f"{count}회")
        #         
        #         with col2:
        #             st.markdown("**6-10위 태그:**")
        #             for i, (tag, count) in enumerate(top_tags[5:10]):
        #                 st.metric(f"{i+6}. {tag}", f"{count}회")
        #         else:
        #             st.info("태그 데이터가 없습니다.")
        #     else:
        #         st.info("태그 데이터를 불러올 수 없습니다.")
        
        # 카테고리 분포 히스토그램
        st.markdown("#### 📂 카테고리별 분석 수 히스토그램")
        st.markdown("분석된 인플루언서들의 카테고리별 분포를 히스토그램으로 확인할 수 있습니다.")
        
        
        category_dist = get_category_distribution()
        category_avg_scores = get_category_average_scores()
        
        if category_dist:
            # Combo chart 생성 (막대 차트 + 라인 차트)
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            # 서브플롯 생성 (secondary y-axis 사용)
            fig = make_subplots(
                specs=[[{"secondary_y": True}]]
            )
            
            # 카테고리 순서 정렬 (분석 수 기준)
            categories = list(category_dist.keys())
            counts = [category_dist[cat] for cat in categories]
            scores = [category_avg_scores.get(cat, 0) for cat in categories]
            
            # 막대 차트 추가 (분석 수)
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=counts,
                    name="분석 수",
                    text=counts,
                    textposition='outside',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                secondary_y=False,
            )
            
            # 라인 차트 추가 (평균 점수)
            fig.add_trace(
                go.Scatter(
                    x=categories,
                    y=scores,
                    mode='lines+markers',
                    name="평균 점수",
                    line=dict(color='red', width=3),
                    marker=dict(size=8, color='red'),
                    text=[f"{score:.1f}" for score in scores],
                    textposition='top center'
                ),
                secondary_y=True,
            )
            
            # 레이아웃 설정
            fig.update_layout(
                title="카테고리별 분석 수 및 평균 점수",
                xaxis_tickangle=45,
                bargap=0.1,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Y축 레이블 설정
            fig.update_yaxes(title_text="분석 수", secondary_y=False)
            fig.update_yaxes(title_text="평균 점수 (/10)", secondary_y=True)
            
            st.plotly_chart(fig, width='stretch')
            
            # 카테고리별 태그 분석
            st.markdown("**카테고리별 태그 분석:**")
            
            # 카테고리 선택
            available_categories = list(category_dist.keys())
            selected_category = st.selectbox(
                "분석할 카테고리를 선택하세요:",
                available_categories,
                help="선택한 카테고리의 인플루언서들이 사용한 태그들을 분석합니다."
            )
            
            if selected_category:
                # 선택된 카테고리의 태그 데이터 가져오기
                category_tags = get_category_tags(selected_category)
                
                if category_tags:
                    # 태그 빈도 계산
                    tag_counts = Counter(category_tags)
                    
                    # 시각화 탭으로 분리
                    tab1, tab2, tab3 = st.tabs(["📊 태그 빈도 차트", "🏷️ 상위 태그", "📋 태그 상세"])
                    
                    with tab1:
                        # 태그 빈도 막대 차트
                        top_tags = tag_counts.most_common(20)  # 상위 20개만 표시
                        if top_tags:
                            fig = px.bar(
                                x=[tag for tag, count in top_tags],
                                y=[count for tag, count in top_tags],
                                title=f"'{selected_category}' 카테고리 태그 빈도 (상위 20개)",
                                labels={'x': '태그', 'y': '사용 횟수'},
                                color=[count for tag, count in top_tags],
                                color_continuous_scale='viridis'
                            )
                            fig.update_layout(
                                xaxis_tickangle=45,
                                showlegend=False,
                                coloraxis_showscale=False
                            )
                            fig.update_traces(text=[count for tag, count in top_tags], textposition='outside')
                            st.plotly_chart(fig, width='stretch')
                    
                    with tab2:
                        # 상위 태그 메트릭
                        st.markdown(f"**'{selected_category}' 카테고리 상위 태그:**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**상위 10개 태그:**")
                            for i, (tag, count) in enumerate(tag_counts.most_common(10), 1):
                                st.metric(f"{i}. {tag}", f"{count}회")
                        
                        with col2:
                            st.markdown("**11-20위 태그:**")
                            for i, (tag, count) in enumerate(tag_counts.most_common(20)[10:], 11):
                                st.metric(f"{i}. {tag}", f"{count}회")
                    
                    with tab3:
                        # 태그 상세 정보
                        st.markdown(f"**'{selected_category}' 카테고리 태그 상세 정보:**")
                        
                        # 통계 요약
                        total_tags = len(category_tags)
                        unique_tags = len(tag_counts)
                        avg_tags_per_influencer = total_tags / category_dist[selected_category] if category_dist[selected_category] > 0 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("총 태그 수", f"{total_tags:,}")
                        with col2:
                            st.metric("고유 태그 수", f"{unique_tags:,}")
                        with col3:
                            st.metric("인플루언서당 평균 태그", f"{avg_tags_per_influencer:.1f}")
                        
                        # 태그 데이터 테이블
                        st.markdown("**전체 태그 목록:**")
                        import pandas as pd
                        df = pd.DataFrame([
                            {
                                '태그': tag,
                                '사용 횟수': count,
                                '순위': i
                            }
                            for i, (tag, count) in enumerate(tag_counts.most_common(), 1)
                        ])
                        st.dataframe(df, width='stretch')
                else:
                    st.info(f"'{selected_category}' 카테고리의 태그 데이터를 찾을 수 없습니다.")
            
            # 카테고리 다양성 정보
            if len(category_dist) <= 2:
                st.warning("⚠️ 현재 분석된 카테고리가 제한적입니다. 더 다양한 카테고리의 인플루언서를 분석하면 더 풍부한 통계를 제공할 수 있습니다.")
        else:
            st.info("카테고리 분포 데이터가 없습니다.")
        
        # 통계 해석 가이드
        st.markdown("---")
        st.markdown("#### 💡 기본 통계 해석 가이드")
        
        with st.expander("🔍 상세 해석 가이드 보기", expanded=False):
            st.markdown("""
            - **분석률:** 크롤링된 인플루언서 중 AI 분석이 완료된 비율입니다.
            - **카테고리별 분석 수 및 평균 점수:** 분석된 인플루언서들의 분야별 분포와 각 카테고리의 평균 점수를 combo chart로 확인할 수 있습니다.
            - **평균 종합점수:** 모든 분석된 인플루언서의 평균 종합 평가 점수입니다.
            - **카테고리별 태그 분석:** 특정 카테고리를 선택하여 해당 카테고리 인플루언서들이 사용하는 태그들의 분포를 분석할 수 있습니다.
            """)
    
    except Exception as e:
        st.error(f"기본 통계 조회 중 오류: {str(e)}")
