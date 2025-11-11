"""
인플루언서 분석 관리 관련 컴포넌트들
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager

def render_influencer_statistics_management():
    """인플루언서 분석 관리 메인 컴포넌트"""
    st.subheader("📊 인플루언서 분석")
    st.markdown("인플루언서 데이터 분석 및 통계 정보를 제공합니다.")
    
    # 분석 탭으로 분리
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 전체 통계", 
        "🏷️ 카테고리별 분석", 
        "📱 플랫폼별 분석", 
        "⭐ 평점 분석"
    ])
    
    with tab1:
        render_overall_statistics()
    
    with tab2:
        render_category_analysis()
    
    with tab3:
        render_platform_analysis()
    
    with tab4:
        render_rating_analysis()

def render_overall_statistics():
    """전체 통계 탭"""
    st.subheader("📈 전체 통계")
    
    try:
        # 인플루언서 데이터 가져오기
        influencers = db_manager.get_influencers()
        
        if not influencers:
            st.warning("등록된 인플루언서가 없습니다.")
            return
        
        # 기본 통계 계산
        total_influencers = len(influencers)
        active_influencers = len([inf for inf in influencers if inf.get('active', True)])
        inactive_influencers = total_influencers - active_influencers
        
        # 팔로워 수 통계
        followers_data = [inf.get('followers_count', 0) or 0 for inf in influencers if inf.get('followers_count')]
        total_followers = sum(followers_data)
        avg_followers = total_followers / len(followers_data) if followers_data else 0
        
        # 게시물 수 통계
        post_count_data = [inf.get('post_count', 0) or 0 for inf in influencers if inf.get('post_count') is not None]
        
        # 가격 통계
        price_data = [inf.get('price_krw', 0) or 0 for inf in influencers if inf.get('price_krw')]
        total_price = sum(price_data)
        avg_price = total_price / len(price_data) if price_data else 0
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "총 인플루언서 수", 
                f"{total_influencers:,}명",
                delta=f"활성: {active_influencers:,}명"
            )
        
        with col2:
            st.metric(
                "총 팔로워 수", 
                f"{total_followers:,}명",
                delta=f"평균: {avg_followers:,.0f}명"
            )
        
        with col3:
            st.metric(
                "평균 팔로워 수", 
                f"{avg_followers:,.0f}명",
                delta=f"총: {total_followers:,}명"
            )
        
        with col4:
            st.metric(
                "활성 비율", 
                f"{(active_influencers/total_influencers*100):.1f}%",
                delta=f"비활성: {inactive_influencers:,}명"
            )
        
        # 차트 섹션
        st.markdown("---")
        st.markdown("### 📊 시각화")
        
        # 팔로워 수 분포 차트
        if followers_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 팔로워 수 분포")
                # 팔로워 수 구간별 분포
                followers_df = pd.DataFrame({'팔로워수': followers_data})
                
                # 구간 설정
                bins = [0, 1000, 5000, 10000, 50000, 100000, 500000, float('inf')]
                labels = ['1K 미만', '1K-5K', '5K-10K', '10K-50K', '50K-100K', '100K-500K', '500K+']
                
                followers_df['구간'] = pd.cut(followers_df['팔로워수'], bins=bins, labels=labels, right=False)
                followers_dist = followers_df['구간'].value_counts().sort_index()
                
                fig = px.bar(
                    x=followers_dist.index, 
                    y=followers_dist.values,
                    title="팔로워 수 구간별 분포",
                    labels={'x': '팔로워 수 구간', 'y': '인플루언서 수'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 게시물 수 분포")
                if post_count_data:
                    # 게시물 수 구간별 분포
                    post_count_df = pd.DataFrame({'게시물수': post_count_data})
                    
                    # 게시물 수 구간 설정 (데이터 분포에 맞게 조정)
                    max_post = max(post_count_data) if post_count_data else 0
                    if max_post <= 100:
                        bins = [0, 10, 20, 30, 50, 100, float('inf')]
                        labels = ['10개 미만', '10-20개', '20-30개', '30-50개', '50-100개', '100개+']
                    elif max_post <= 500:
                        bins = [0, 50, 100, 200, 300, 500, float('inf')]
                        labels = ['50개 미만', '50-100개', '100-200개', '200-300개', '300-500개', '500개+']
                    elif max_post <= 1000:
                        bins = [0, 100, 200, 300, 500, 1000, float('inf')]
                        labels = ['100개 미만', '100-200개', '200-300개', '300-500개', '500-1000개', '1000개+']
                    else:
                        bins = [0, 100, 500, 1000, 2000, 5000, float('inf')]
                        labels = ['100개 미만', '100-500개', '500-1000개', '1000-2000개', '2000-5000개', '5000개+']
                    
                    post_count_df['구간'] = pd.cut(post_count_df['게시물수'], bins=bins, labels=labels, right=False)
                    post_count_dist = post_count_df['구간'].value_counts().sort_index()
                    
                    fig = px.bar(
                        x=post_count_dist.index, 
                        y=post_count_dist.values,
                        title="게시물 수 구간별 분포",
                        labels={'x': '게시물 수 구간', 'y': '인플루언서 수'}
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("게시물 수 데이터가 없습니다.")
        
        # 등록일별 추이
        st.markdown("#### 등록일별 인플루언서 추가 추이")
        registration_data = []
        for inf in influencers:
            if inf.get('created_at'):
                try:
                    # 날짜 파싱 (다양한 형식 지원)
                    created_at = inf['created_at']
                    if isinstance(created_at, str):
                        # ISO 형식 또는 다른 형식 처리
                        if 'T' in created_at:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            date_obj = datetime.strptime(created_at[:10], '%Y-%m-%d')
                    else:
                        date_obj = created_at
                    
                    registration_data.append({
                        'date': date_obj.date(),
                        'count': 1
                    })
                except:
                    continue
        
        if registration_data:
            reg_df = pd.DataFrame(registration_data)
            reg_df = reg_df.groupby('date').sum().reset_index()
            reg_df['cumulative'] = reg_df['count'].cumsum()
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 일별 추가 수
            fig.add_trace(
                go.Bar(x=reg_df['date'], y=reg_df['count'], name="일별 추가", opacity=0.7),
                secondary_y=False,
            )
            
            # 누적 수
            fig.add_trace(
                go.Scatter(x=reg_df['date'], y=reg_df['cumulative'], name="누적 수", mode='lines+markers'),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="날짜")
            fig.update_yaxes(title_text="일별 추가 수", secondary_y=False)
            fig.update_yaxes(title_text="누적 인플루언서 수", secondary_y=True)
            fig.update_layout(title_text="인플루언서 등록 추이")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("등록일 정보가 없습니다.")
        
    except Exception as e:
        st.error(f"분석 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")

def render_category_analysis():
    """카테고리별 분석 탭"""
    st.subheader("🏷️ 카테고리별 분석")
    
    try:
        influencers = db_manager.get_influencers()
        
        if not influencers:
            st.warning("등록된 인플루언서가 없습니다.")
            return
        
        # 카테고리별 통계
        category_stats = {}
        for inf in influencers:
            category = inf.get('content_category', '기타')
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_followers': 0,
                    'total_price': 0,
                    'active_count': 0,
                    'ratings': []
                }
            
            category_stats[category]['count'] += 1
            if inf.get('active', True):
                category_stats[category]['active_count'] += 1
            
            followers = inf.get('followers_count', 0) or 0
            category_stats[category]['total_followers'] += followers
            
            price = inf.get('price_krw', 0) or 0
            category_stats[category]['total_price'] += price
            
            if inf.get('manager_rating'):
                category_stats[category]['ratings'].append(inf['manager_rating'])
        
        # 데이터프레임 생성
        category_df = pd.DataFrame([
            {
                '카테고리': cat,
                '인플루언서 수': stats['count'],
                '활성 수': stats['active_count'],
                '총 팔로워 수': stats['total_followers'],
                '평균 팔로워 수': stats['total_followers'] / stats['count'] if stats['count'] > 0 else 0,
                '총 예산': stats['total_price'],
                '평균 예산': stats['total_price'] / stats['count'] if stats['count'] > 0 else 0,
                '평균 평점': sum(stats['ratings']) / len(stats['ratings']) if stats['ratings'] else 0
            }
            for cat, stats in category_stats.items()
        ])
        
        # 카테고리별 인플루언서 수 차트
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 카테고리별 인플루언서 수")
            fig = px.pie(
                category_df, 
                values='인플루언서 수', 
                names='카테고리',
                title="카테고리별 인플루언서 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 카테고리별 평균 팔로워 수")
            fig = px.bar(
                category_df, 
                x='카테고리', 
                y='평균 팔로워 수',
                title="카테고리별 평균 팔로워 수"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # 상세 분석 테이블
        st.markdown("#### 카테고리별 상세 분석")
        
        # 숫자 포맷팅
        display_df = category_df.copy()
        display_df['총 팔로워 수'] = display_df['총 팔로워 수'].apply(lambda x: f"{x:,.0f}")
        display_df['평균 팔로워 수'] = display_df['평균 팔로워 수'].apply(lambda x: f"{x:,.0f}")
        display_df['총 예산'] = display_df['총 예산'].apply(lambda x: f"{x:,.0f}원")
        display_df['평균 예산'] = display_df['평균 예산'].apply(lambda x: f"{x:,.0f}원")
        display_df['평균 평점'] = display_df['평균 평점'].apply(lambda x: f"{x:.1f}" if x > 0 else "N/A")
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"카테고리 분석 중 오류가 발생했습니다: {str(e)}")

def render_platform_analysis():
    """플랫폼별 분석 탭"""
    st.subheader("📱 플랫폼별 분석")
    
    try:
        influencers = db_manager.get_influencers()
        
        if not influencers:
            st.warning("등록된 인플루언서가 없습니다.")
            return
        
        # 플랫폼별 통계
        platform_stats = {}
        for inf in influencers:
            platform = inf.get('platform', 'unknown')
            if platform not in platform_stats:
                platform_stats[platform] = {
                    'count': 0,
                    'total_followers': 0,
                    'total_price': 0,
                    'active_count': 0,
                    'categories': {}
                }
            
            platform_stats[platform]['count'] += 1
            if inf.get('active', True):
                platform_stats[platform]['active_count'] += 1
            
            followers = inf.get('followers_count', 0) or 0
            platform_stats[platform]['total_followers'] += followers
            
            price = inf.get('price_krw', 0) or 0
            platform_stats[platform]['total_price'] += price
            
            category = inf.get('content_category', '기타')
            if category not in platform_stats[platform]['categories']:
                platform_stats[platform]['categories'][category] = 0
            platform_stats[platform]['categories'][category] += 1
        
        # 데이터프레임 생성
        platform_df = pd.DataFrame([
            {
                '플랫폼': platform,
                '인플루언서 수': stats['count'],
                '활성 수': stats['active_count'],
                '총 팔로워 수': stats['total_followers'],
                '평균 팔로워 수': stats['total_followers'] / stats['count'] if stats['count'] > 0 else 0,
                '총 예산': stats['total_price'],
                '평균 예산': stats['total_price'] / stats['count'] if stats['count'] > 0 else 0
            }
            for platform, stats in platform_stats.items()
        ])
        
        # 플랫폼 아이콘 매핑
        platform_icons = {
            "instagram": "📸 Instagram",
            "youtube": "📺 YouTube",
            "tiktok": "🎵 TikTok",
            "x": "🐦 X (Twitter)",
            "blog": "📝 블로그",
            "facebook": "👥 Facebook"
        }
        
        platform_df['플랫폼_표시'] = platform_df['플랫폼'].map(platform_icons).fillna(platform_df['플랫폼'])
        
        # 플랫폼별 인플루언서 수 차트
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 플랫폼별 인플루언서 수")
            fig = px.pie(
                platform_df, 
                values='인플루언서 수', 
                names='플랫폼_표시',
                title="플랫폼별 인플루언서 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 플랫폼별 평균 팔로워 수")
            fig = px.bar(
                platform_df, 
                x='플랫폼_표시', 
                y='평균 팔로워 수',
                title="플랫폼별 평균 팔로워 수"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 플랫폼별 카테고리 분포
        st.markdown("#### 플랫폼별 카테고리 분포")
        
        # 플랫폼-카테고리 매트릭스 생성
        platform_category_data = []
        for platform, stats in platform_stats.items():
            for category, count in stats['categories'].items():
                platform_category_data.append({
                    '플랫폼': platform_icons.get(platform, platform),
                    '카테고리': category,
                    '인플루언서 수': count
                })
        
        if platform_category_data:
            pc_df = pd.DataFrame(platform_category_data)
            fig = px.bar(
                pc_df,
                x='플랫폼',
                y='인플루언서 수',
                color='카테고리',
                title="플랫폼별 카테고리 분포",
                barmode='stack'
            )
            st.plotly_chart(fig, width='stretch')
        
        # 상세 분석 테이블
        st.markdown("#### 플랫폼별 상세 분석")
        
        # 숫자 포맷팅
        display_df = platform_df.copy()
        display_df['총 팔로워 수'] = display_df['총 팔로워 수'].apply(lambda x: f"{x:,.0f}")
        display_df['평균 팔로워 수'] = display_df['평균 팔로워 수'].apply(lambda x: f"{x:,.0f}")
        display_df['총 예산'] = display_df['총 예산'].apply(lambda x: f"{x:,.0f}원")
        display_df['평균 예산'] = display_df['평균 예산'].apply(lambda x: f"{x:,.0f}원")
        
        # 플랫폼 표시명으로 변경
        display_df = display_df.drop('플랫폼', axis=1)
        display_df = display_df.rename(columns={'플랫폼_표시': '플랫폼'})
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"플랫폼 분석 중 오류가 발생했습니다: {str(e)}")

def render_rating_analysis():
    """평점 분석 탭"""
    st.subheader("⭐ 평점 분석")
    
    try:
        influencers = db_manager.get_influencers()
        
        if not influencers:
            st.warning("등록된 인플루언서가 없습니다.")
            return
        
        # 평점 데이터 수집 (None 값 제외)
        manager_ratings = [inf.get('manager_rating') for inf in influencers if inf.get('manager_rating') is not None]
        content_ratings = [inf.get('content_rating') for inf in influencers if inf.get('content_rating') is not None]
        
        if not manager_ratings and not content_ratings:
            st.warning("평점 데이터가 없습니다.")
            return
        
        # 평점 분포 차트
        col1, col2 = st.columns(2)
        
        with col1:
            if manager_ratings:
                st.markdown("#### 매니저 평점 분포")
                rating_df = pd.DataFrame({'평점': manager_ratings})
                rating_dist = rating_df['평점'].value_counts().sort_index()
                
                fig = px.bar(
                    x=rating_dist.index,
                    y=rating_dist.values,
                    title="매니저 평점 분포",
                    labels={'x': '평점', 'y': '인플루언서 수'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("매니저 평점 데이터가 없습니다.")
        
        with col2:
            if content_ratings:
                st.markdown("#### 콘텐츠 평점 분포")
                rating_df = pd.DataFrame({'평점': content_ratings})
                rating_dist = rating_df['평점'].value_counts().sort_index()
                
                fig = px.bar(
                    x=rating_dist.index,
                    y=rating_dist.values,
                    title="콘텐츠 평점 분포",
                    labels={'x': '평점', 'y': '인플루언서 수'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("콘텐츠 평점 데이터가 없습니다.")
        
        # 평점 분석
        if manager_ratings or content_ratings:
            st.markdown("#### 평점 분석")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if manager_ratings:
                    st.markdown("**매니저 평점 분석**")
                    avg_manager = sum(manager_ratings) / len(manager_ratings)
                    st.metric("평균 평점", f"{avg_manager:.2f}/5")
                    st.metric("최고 평점", f"{max(manager_ratings)}/5")
                    st.metric("최저 평점", f"{min(manager_ratings)}/5")
                    st.metric("평점 개수", f"{len(manager_ratings)}개")
            
            with col2:
                if content_ratings:
                    st.markdown("**콘텐츠 평점 분석**")
                    avg_content = sum(content_ratings) / len(content_ratings)
                    st.metric("평균 평점", f"{avg_content:.2f}/5")
                    st.metric("최고 평점", f"{max(content_ratings)}/5")
                    st.metric("최저 평점", f"{min(content_ratings)}/5")
                    st.metric("평점 개수", f"{len(content_ratings)}개")
        
        # 평점별 인플루언서 목록
        if manager_ratings or content_ratings:
            st.markdown("#### 평점별 인플루언서 목록")
            
            # 평점이 있는 인플루언서 필터링 (None 값 제외)
            rated_influencers = [
                inf for inf in influencers 
                if inf.get('manager_rating') is not None or inf.get('content_rating') is not None
            ]
            
            if rated_influencers:
                # 평점별로 정렬 (None 값 처리)
                def get_avg_rating(inf):
                    manager_rating = inf.get('manager_rating') or 0
                    content_rating = inf.get('content_rating') or 0
                    if manager_rating and content_rating:
                        return (manager_rating + content_rating) / 2
                    elif manager_rating:
                        return manager_rating
                    elif content_rating:
                        return content_rating
                    else:
                        return 0
                
                rated_influencers.sort(key=get_avg_rating, reverse=True)
                
                # 표시용 데이터 준비
                display_data = []
                for inf in rated_influencers:
                    display_data.append({
                        'SNS ID': inf.get('sns_id', 'N/A'),
                        '이름': inf.get('influencer_name', 'N/A'),
                        '플랫폼': inf.get('platform', 'N/A'),
                        '매니저 평점': inf.get('manager_rating') if inf.get('manager_rating') is not None else 'N/A',
                        '콘텐츠 평점': inf.get('content_rating') if inf.get('content_rating') is not None else 'N/A',
                        '팔로워 수': f"{inf.get('followers_count', 0):,}" if inf.get('followers_count') else 'N/A',
                        '가격': f"{inf.get('price_krw', 0):,.0f}원" if inf.get('price_krw') else 'N/A'
                    })
                
                st.dataframe(
                    pd.DataFrame(display_data),
                    width='stretch',
                    hide_index=True
                )
        
    except Exception as e:
        st.error(f"평점 분석 중 오류가 발생했습니다: {str(e)}")

def render_ai_analysis():
    """AI 분석 탭 - 준비중"""
    st.subheader("🤖 AI 분석")
    
    # 준비중 메시지
    st.info("🚧 AI 분석 기능은 현재 개발 중입니다.")
    
    # AI 분석 기능 소개
    st.markdown("### 📋 분석 예정 범위")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 인플루언서 추천")
        st.markdown("""
        - **성과 기반 추천**: 과거 캠페인 성과를 바탕으로 한 인플루언서 추천
        - **카테고리 매칭**: 브랜드/제품 카테고리와 인플루언서 전문 분야 매칭
        - **예산 최적화**: 설정된 예산 내에서 최적의 ROI를 제공하는 인플루언서 추천
        - **팔로워 분석**: 타겟 오디언스와 인플루언서 팔로워의 일치도 분석
        """)
    
    with col2:
        st.markdown("#### 📊 성과 예측")
        st.markdown("""
        - **도달률 예측**: 인플루언서별 예상 도달률 및 노출 수 예측
        - **참여도 예측**: 예상 좋아요, 댓글, 공유 수 예측
        - **전환율 예측**: 클릭률 및 구매 전환율 예측
        - **ROI 예측**: 예상 투자 대비 수익률 계산
        """)
