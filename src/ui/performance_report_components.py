"""
성과 리포트 탭 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
from ..db.database import db_manager
from .common_functions import format_campaign_type, get_date_range_options, calculate_date_range


def render_performance_report_tab():
    """리포트 탭 - 종합적인 성과 분석 및 리포트 생성"""
    st.subheader("📋 성과 리포트")
    st.markdown("캠페인별 성과를 종합적으로 분석하고 상세한 리포트를 생성합니다.")

    # 리포트 타입 선택
    report_type = st.selectbox(
        "리포트 타입 선택",
        ["📊 종합 대시보드", "📈 성과 지표 분석", "👥 인플루언서별 분석", "📅 날짜별 트렌드", "💰 ROI 분석"],
        key="report_type"
    )

    # 날짜 범위 선택
    st.markdown("#### 📅 분석 기간 선택")
    col1, col2 = st.columns(2)
    with col1:
        date_range_option = st.selectbox("날짜 범위", list(get_date_range_options().keys()), key="report_date_range")
    with col2:
        if date_range_option != "전체":
            start_date, end_date = calculate_date_range(get_date_range_options()[date_range_option])
            st.info(f"분석 기간: {start_date} ~ {end_date}")
        else:
            st.info("전체 기간 분석")

    # 캠페인 선택
    try:
        campaigns = db_manager.get_campaigns()
        if not campaigns:
            st.info("분석할 캠페인이 없습니다.")
            return
    except Exception as e:
        st.error(f"❌ 캠페인 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    selected_campaigns = st.multiselect(
        "분석할 캠페인 선택",
        [f"{c['campaign_name']} ({format_campaign_type(c['campaign_type'])})" for c in campaigns],
        key="report_campaigns",
        help="여러 캠페인을 선택하여 비교 분석할 수 있습니다",
    )

    if not selected_campaigns:
        st.info("분석할 캠페인을 선택해주세요.")
        return

    campaign_data = []
    for display_name in selected_campaigns:
        for campaign in campaigns:
            if f"{campaign['campaign_name']} ({format_campaign_type(campaign['campaign_type'])})" == display_name:
                campaign_data.append(campaign)
                break

    # 리포트 타입별 렌더링
    if report_type == "📊 종합 대시보드":
        render_comprehensive_dashboard(campaign_data)
    elif report_type == "📈 성과 지표 분석":
        render_performance_metrics_analysis(campaign_data)
    elif report_type == "👥 인플루언서별 분석":
        render_influencer_analysis(campaign_data)
    elif report_type == "📅 날짜별 트렌드":
        render_trend_analysis(campaign_data)
    elif report_type == "💰 ROI 분석":
        render_roi_analysis(campaign_data)

    # 리포트 내보내기 기능
    render_export_section(campaign_data, report_type)


def render_comprehensive_dashboard(campaign_data):
    """종합 대시보드 렌더링"""
    st.markdown("#### 📊 종합 대시보드")
    
    # 기본 참여 통계
    participation_counts = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            completed = len([p for p in participations if p.get("content_uploaded", False)])
            participation_counts.append(
                {
                    "캠페인": campaign["campaign_name"],
                    "유형": format_campaign_type(campaign["campaign_type"]),
                    "참여 인플루언서 수": len(participations),
                    "업로드 완료": completed,
                    "완료율": f"{(completed / len(participations) * 100):.1f}%" if participations else "0%",
                }
            )
    except Exception as e:
        st.error(f"❌ 참여 인플루언서 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if participation_counts:
        df_participations = pd.DataFrame(participation_counts)
        st.dataframe(df_participations, use_container_width=True, hide_index=True)

        colc1, colc2 = st.columns(2)
        with colc1:
            fig_participations = px.bar(
                df_participations, x="캠페인", y="참여 인플루언서 수", title="캠페인별 참여 인플루언서 수", color="유형"
            )
            st.plotly_chart(fig_participations, use_container_width=True)
        with colc2:
            fig_completion = px.bar(
                df_participations, x="캠페인", y="업로드 완료", title="캠페인별 업로드 완료 수", color="유형"
            )
            st.plotly_chart(fig_completion, use_container_width=True)

    # 플랫폼별 분석
    st.markdown("#### 📱 플랫폼별 분석")
    platform_data = {}
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            for participation in participations:
                platform = participation.get("platform", "N/A")
                if platform not in platform_data:
                    platform_data[platform] = {"참여 수": 0, "업로드 완료": 0}
                platform_data[platform]["참여 수"] += 1
                if participation.get("content_uploaded", False):
                    platform_data[platform]["업로드 완료"] += 1
    except Exception as e:
        st.error(f"❌ 플랫폼별 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if platform_data:
        platform_df = pd.DataFrame(
            [
                {
                    "플랫폼": platform,
                    "참여 수": data["참여 수"],
                    "업로드 완료": data["업로드 완료"],
                    "완료율": f"{(data['업로드 완료'] / data['참여 수'] * 100):.1f}%" if data["참여 수"] > 0 else "0%",
                }
                for platform, data in platform_data.items()
            ]
        )
        st.dataframe(platform_df, use_container_width=True, hide_index=True)

        colp1, colp2 = st.columns(2)
        with colp1:
            fig_platform = px.pie(platform_df, values="참여 수", names="플랫폼", title="플랫폼별 참여 비율")
            st.plotly_chart(fig_platform, use_container_width=True)
        with colp2:
            fig_platform_completion = px.bar(
                platform_df, x="플랫폼", y="업로드 완료", title="플랫폼별 업로드 완료 수"
            )
            st.plotly_chart(fig_platform_completion, use_container_width=True)

    # 요약 통계
    st.markdown("#### 📈 요약 통계")
    try:
        total_participations = sum(len(db_manager.get_all_campaign_participations(c["id"])) for c in campaign_data)
        total_completed = sum(
            len([p for p in db_manager.get_all_campaign_participations(c["id"]) if p.get("content_uploaded", False)])
            for c in campaign_data
        )
    except Exception as e:
        st.error(f"❌ 요약 통계 계산 중 오류가 발생했습니다: {str(e)}")
        return

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("총 참여 인플루언서", f"{total_participations}명")
    with s2:
        st.metric("업로드 완료", f"{total_completed}명")
    with s3:
        st.metric(
            "전체 완료율",
            f"{(total_completed / total_participations * 100):.1f}%" if total_participations > 0 else "0%",
        )
    with s4:
        st.metric("분석 캠페인 수", f"{len(campaign_data)}개")


def render_performance_metrics_analysis(campaign_data):
    """성과 지표 분석 렌더링"""
    st.markdown("#### 📈 성과 지표 분석")
    
    # 성과 지표 데이터 수집
    performance_data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            for participation in participations:
                contents = db_manager.get_campaign_influencer_contents(participation["id"])
                for content in contents:
                    likes = content.get("likes", 0)
                    comments = content.get("comments", 0)
                    shares = content.get("shares", 0)
                    views = content.get("views", 0)
                    
                    # 참여율 계산: (좋아요 + 댓글 + 공유) / 조회수 × 100
                    engagement_rate = 0
                    if views > 0:
                        engagement_rate = round((likes + comments + shares) / views * 100, 2)
                    
                    performance_data.append({
                        "캠페인": campaign["campaign_name"],
                        "인플루언서": participation.get("influencer_name", "N/A"),
                        "플랫폼": participation.get("platform", "N/A"),
                        "좋아요": likes,
                        "댓글": comments,
                        "조회수": views,
                        "참여율": engagement_rate,
                        "업로드일": content.get("posted_at", "N/A")
                    })
    except Exception as e:
        st.error(f"❌ 성과 지표 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if not performance_data:
        st.info("성과 지표 데이터가 없습니다.")
        return

    df_performance = pd.DataFrame(performance_data)
    
    # 성과 지표 요약
    col_title, col_help = st.columns([4, 1])
    with col_title:
        st.markdown("##### 📊 성과 지표 요약")
    with col_help:
        if st.button("❓", key="summary_help", help="성과 지표 요약 계산 방법"):
            st.session_state.show_summary_help = not st.session_state.get("show_summary_help", False)
    
    if st.session_state.get("show_summary_help", False):
        st.info("""
        **📊 성과 지표 요약 계산 방법:**
        
        - **좋아요**: 해당 캠페인의 모든 콘텐츠 좋아요 수의 합계
        - **댓글**: 해당 캠페인의 모든 콘텐츠 댓글 수의 합계
        - **조회수**: 해당 캠페인의 모든 콘텐츠 조회수(views)의 합계
        - **참여율**: (총 좋아요 + 총 댓글) / 총 조회수 × 100
        
        *참여율 = (좋아요 + 댓글) / 조회수 × 100*
        """)
    
    # 캠페인별 총합 계산
    summary_metrics = df_performance.groupby("캠페인").agg({
        "좋아요": "sum",
        "댓글": "sum", 
        "조회수": "sum"
    }).round(2)
    
    # 참여율을 총합 기반으로 재계산
    summary_metrics["참여율"] = 0
    for campaign in summary_metrics.index:
        total_likes = summary_metrics.loc[campaign, "좋아요"]
        total_comments = summary_metrics.loc[campaign, "댓글"]
        total_views = summary_metrics.loc[campaign, "조회수"]
        
        if total_views > 0:
            engagement_rate = round((total_likes + total_comments) / total_views * 100, 2)
            summary_metrics.loc[campaign, "참여율"] = engagement_rate
    
    # 참여율을 퍼센트 형식으로 표시
    summary_metrics_display = summary_metrics.copy()
    summary_metrics_display["참여율"] = summary_metrics_display["참여율"].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(summary_metrics_display, use_container_width=True)
    
    # 성과 지표 시각화
    col1, col2 = st.columns(2)
    with col1:
        fig_likes = px.bar(
            summary_metrics.reset_index(), 
            x="캠페인", 
            y="좋아요", 
            title="캠페인별 총 좋아요 수"
        )
        st.plotly_chart(fig_likes, use_container_width=True)
    
    with col2:
        fig_engagement = px.bar(
            summary_metrics.reset_index(), 
            x="캠페인", 
            y="참여율", 
            title="캠페인별 평균 참여율"
        )
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # 플랫폼별 성과 비교
    col_title, col_help = st.columns([4, 1])
    with col_title:
        st.markdown("##### 📱 플랫폼별 성과 비교")
    with col_help:
        if st.button("❓", key="platform_help", help="플랫폼별 성과 지표 계산 방법"):
            st.session_state.show_platform_help = not st.session_state.get("show_platform_help", False)
    
    if st.session_state.get("show_platform_help", False):
        st.info("""
        **📊 플랫폼별 성과 지표 계산 방법:**
        
        - **좋아요**: 해당 플랫폼의 모든 콘텐츠 좋아요 수의 합계
        - **댓글**: 해당 플랫폼의 모든 콘텐츠 댓글 수의 합계  
        - **조회수**: 해당 플랫폼의 모든 콘텐츠 조회수(views)의 합계
        - **참여율**: (총 좋아요 + 총 댓글) / 총 조회수 × 100
        
        *참여율 = (좋아요 + 댓글) / 조회수 × 100*
        """)
    
    # 플랫폼별 총합 계산
    platform_performance = df_performance.groupby("플랫폼").agg({
        "좋아요": "sum",
        "댓글": "sum",
        "조회수": "sum"
    }).round(2)
    
    # 참여율을 총합 기반으로 재계산
    platform_performance["참여율"] = 0
    for platform in platform_performance.index:
        total_likes = platform_performance.loc[platform, "좋아요"]
        total_comments = platform_performance.loc[platform, "댓글"]
        total_views = platform_performance.loc[platform, "조회수"]
        
        if total_views > 0:
            engagement_rate = round((total_likes + total_comments) / total_views * 100, 2)
            platform_performance.loc[platform, "참여율"] = engagement_rate
    
    # 참여율을 퍼센트 형식으로 표시
    platform_performance_display = platform_performance.copy()
    platform_performance_display["참여율"] = platform_performance_display["참여율"].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(platform_performance_display, use_container_width=True)
    
    # 플랫폼별 성과 시각화
    fig_platform_metrics = px.bar(
        platform_performance.reset_index(), 
        x="플랫폼", 
        y=["좋아요", "댓글", "조회수"],
        title="플랫폼별 총 성과 지표",
        barmode="group"
    )
    st.plotly_chart(fig_platform_metrics, use_container_width=True)


def render_influencer_analysis(campaign_data):
    """인플루언서별 분석 렌더링"""
    st.markdown("#### 👥 인플루언서별 분석")
    
    # 인플루언서별 성과 데이터 수집
    influencer_data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            for participation in participations:
                contents = db_manager.get_campaign_influencer_contents(participation["id"])
                total_likes = sum(content.get("likes", 0) for content in contents)
                total_comments = sum(content.get("comments", 0) for content in contents)
                total_views = sum(content.get("views", 0) for content in contents)
                total_shares = sum(content.get("shares", 0) for content in contents)
                
                # 참여율 계산: (총 좋아요 + 총 댓글) / 총 조회수 × 100
                avg_engagement = 0
                if total_views > 0:
                    avg_engagement = round((total_likes + total_comments) / total_views * 100, 2)
                
                influencer_data.append({
                    "캠페인": campaign["campaign_name"],
                    "인플루언서": participation.get("influencer_name", "N/A"),
                    "플랫폼": participation.get("platform", "N/A"),
                    "팔로워": participation.get("followers_count", 0),
                    "총 좋아요": total_likes,
                    "총 댓글": total_comments,
                    "총 조회수": total_views,
                    "평균 참여율": avg_engagement,
                    "콘텐츠 수": len(contents)
                })
    except Exception as e:
        st.error(f"❌ 인플루언서 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if not influencer_data:
        st.info("인플루언서 성과 데이터가 없습니다.")
        return

    df_influencers = pd.DataFrame(influencer_data)
    
    # 인플루언서 성과 랭킹
    st.markdown("##### 🏆 인플루언서 성과 랭킹")
    
    # 좋아요 기준 랭킹
    top_likes = df_influencers.nlargest(10, "총 좋아요")[["인플루언서", "캠페인", "플랫폼", "총 좋아요", "평균 참여율"]].copy()
    top_likes["평균 참여율"] = top_likes["평균 참여율"].apply(lambda x: f"{x:.2f}%")
    st.markdown("**좋아요 수 TOP 10**")
    st.dataframe(top_likes, use_container_width=True, hide_index=True)
    
    # 참여율 기준 랭킹
    top_engagement = df_influencers.nlargest(10, "평균 참여율")[["인플루언서", "캠페인", "플랫폼", "평균 참여율", "총 좋아요"]].copy()
    top_engagement["평균 참여율"] = top_engagement["평균 참여율"].apply(lambda x: f"{x:.2f}%")
    st.markdown("**참여율 TOP 10**")
    st.dataframe(top_engagement, use_container_width=True, hide_index=True)
    
    # 인플루언서별 성과 시각화
    col1, col2 = st.columns(2)
    with col1:
        fig_influencer_likes = px.bar(
            top_likes.head(5), 
            x="인플루언서", 
            y="총 좋아요", 
            title="TOP 5 인플루언서 좋아요 수",
            color="플랫폼"
        )
        st.plotly_chart(fig_influencer_likes, use_container_width=True)
    
    with col2:
        fig_influencer_engagement = px.bar(
            top_engagement.head(5), 
            x="인플루언서", 
            y="평균 참여율", 
            title="TOP 5 인플루언서 참여율",
            color="플랫폼"
        )
        st.plotly_chart(fig_influencer_engagement, use_container_width=True)
    
    # 팔로워 수 vs 성과 상관관계
    st.markdown("##### 📊 팔로워 수 vs 성과 상관관계")
    
    # 3개의 상관관계 차트를 2행으로 배치
    col1, col2 = st.columns(2)
    
    with col1:
        # 팔로워 수 vs 좋아요 상관관계
        fig_likes = px.scatter(
            df_influencers, 
            x="팔로워", 
            y="총 좋아요", 
            size="평균 참여율",
            color="플랫폼",
            hover_data=["인플루언서", "캠페인"],
            title="팔로워 수 vs 좋아요 수 상관관계"
        )
        st.plotly_chart(fig_likes, use_container_width=True)
    
    with col2:
        # 팔로워 수 vs 댓글 상관관계
        fig_comments = px.scatter(
            df_influencers, 
            x="팔로워", 
            y="총 댓글", 
            size="평균 참여율",
            color="플랫폼",
            hover_data=["인플루언서", "캠페인"],
            title="팔로워 수 vs 댓글 수 상관관계"
        )
        st.plotly_chart(fig_comments, use_container_width=True)
    
    # 팔로워 수 vs 조회수 상관관계 (전체 너비)
    fig_views = px.scatter(
        df_influencers, 
        x="팔로워", 
        y="총 조회수", 
        size="평균 참여율",
        color="플랫폼",
        hover_data=["인플루언서", "캠페인"],
        title="팔로워 수 vs 조회수 상관관계"
    )
    st.plotly_chart(fig_views, use_container_width=True)


def render_trend_analysis(campaign_data):
    """날짜별 트렌드 분석 렌더링"""
    st.markdown("#### 📅 날짜별 트렌드 분석")
    
    # 날짜별 성과 데이터 수집
    trend_data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            for participation in participations:
                contents = db_manager.get_campaign_influencer_contents(participation["id"])
                for content in contents:
                    upload_date = content.get("posted_at")
                    if upload_date:
                        likes = content.get("likes", 0)
                        comments = content.get("comments", 0)
                        shares = content.get("shares", 0)
                        views = content.get("views", 0)
                        
                        # 참여율 계산: (좋아요 + 댓글) / 조회수 × 100
                        engagement_rate = 0
                        if views > 0:
                            engagement_rate = round((likes + comments) / views * 100, 2)
                        
                        trend_data.append({
                            "날짜": pd.to_datetime(upload_date).date(),
                            "캠페인": campaign["campaign_name"],
                            "좋아요": likes,
                            "댓글": comments,
                            "조회수": views,
                            "참여율": engagement_rate
                        })
    except Exception as e:
        st.error(f"❌ 트렌드 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if not trend_data:
        st.info("날짜별 성과 데이터가 없습니다.")
        return

    df_trend = pd.DataFrame(trend_data)
    df_trend["날짜"] = pd.to_datetime(df_trend["날짜"])
    
    # 일별 성과 트렌드
    daily_trend = df_trend.groupby("날짜").agg({
        "좋아요": "sum",
        "댓글": "sum",
        "조회수": "sum",
        "참여율": "mean"
    }).reset_index()
    
    st.markdown("##### 📈 일별 성과 트렌드")
    
    # 일별 성과 데이터 테이블 표시
    daily_trend_display = daily_trend.copy()
    daily_trend_display["참여율"] = daily_trend_display["참여율"].apply(lambda x: f"{x:.2f}%")
    st.dataframe(daily_trend_display, use_container_width=True, hide_index=True)
    
    # 개별 지표별 트렌드 차트
    col1, col2 = st.columns(2)
    
    with col1:
        # 좋아요 트렌드
        fig_likes = px.line(
            daily_trend, 
            x="날짜", 
            y="좋아요", 
            title="일별 좋아요 수 트렌드",
            markers=True,
            line_shape='spline'
        )
        fig_likes.update_traces(line_color='red', marker_color='red')
        st.plotly_chart(fig_likes, use_container_width=True)
        
        # 댓글 트렌드
        fig_comments = px.line(
            daily_trend, 
            x="날짜", 
            y="댓글", 
            title="일별 댓글 수 트렌드",
            markers=True,
            line_shape='spline'
        )
        fig_comments.update_traces(line_color='blue', marker_color='blue')
        st.plotly_chart(fig_comments, use_container_width=True)
    
    with col2:
        # 조회수 트렌드
        fig_views = px.line(
            daily_trend, 
            x="날짜", 
            y="조회수", 
            title="일별 조회수 트렌드",
            markers=True,
            line_shape='spline'
        )
        fig_views.update_traces(line_color='green', marker_color='green')
        st.plotly_chart(fig_views, use_container_width=True)
        
        # 참여율 트렌드
        fig_engagement = px.line(
            daily_trend, 
            x="날짜", 
            y="참여율", 
            title="일별 참여율 트렌드",
            markers=True,
            line_shape='spline'
        )
        fig_engagement.update_traces(line_color='orange', marker_color='orange')
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # 통합 트렌드 차트 (좋아요, 댓글, 조회수)
    st.markdown("##### 📊 통합 성과 트렌드")
    fig_combined = px.line(
        daily_trend, 
        x="날짜", 
        y=["좋아요", "댓글", "조회수"],
        title="일별 성과 지표 통합 트렌드",
        markers=True,
        line_shape='spline'
    )
    fig_combined.update_layout(
        yaxis_title="수량",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_combined, use_container_width=True)
    
    # 캠페인별 트렌드 비교
    st.markdown("##### 📊 캠페인별 트렌드 비교")
    campaign_trend = df_trend.groupby(["날짜", "캠페인"])["좋아요"].sum().reset_index()
    
    fig_campaign_trend = px.line(
        campaign_trend, 
        x="날짜", 
        y="좋아요", 
        color="캠페인",
        title="캠페인별 좋아요 수 트렌드"
    )
    st.plotly_chart(fig_campaign_trend, use_container_width=True)


def render_roi_analysis(campaign_data):
    """ROI 분석 렌더링"""
    st.markdown("#### 💰 ROI 분석")
    st.info("💡 ROI 분석: 인플루언서 비용과 성과 지표를 연계한 종합적인 투자 대비 수익률 분석을 제공합니다.")
    
    # ROI 관련 데이터 수집
    roi_data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            total_likes = 0
            total_comments = 0
            total_views = 0
            total_cost = 0
            content_count = 0
            
            for participation in participations:
                # 비용 데이터 수집
                total_cost += float(participation.get("cost_krw", 0) or 0)
                
                contents = db_manager.get_campaign_influencer_contents(participation["id"])
                for content in contents:
                    total_likes += content.get("likes", 0)
                    total_comments += content.get("comments", 0)
                    total_views += content.get("views", 0)
                    content_count += 1
            
            # 참여율 계산: (총 좋아요 + 총 댓글) / 총 조회수 × 100
            avg_engagement = 0
            if total_views > 0:
                avg_engagement = round((total_likes + total_comments) / total_views * 100, 2)
            
            # ROI 지표 계산
            cost_per_like = round(total_cost / total_likes, 2) if total_likes > 0 else 0
            cost_per_view = round(total_cost / total_views, 2) if total_views > 0 else 0
            cost_per_influencer = round(total_cost / len(participations), 2) if participations else 0
            
            roi_data.append({
                "캠페인": campaign["campaign_name"],
                "참여 인플루언서": len(participations),
                "총 콘텐츠": content_count,
                "총 비용": f"{total_cost:,.0f}원",
                "총 좋아요": total_likes,
                "총 댓글": total_comments,
                "총 조회수": total_views,
                "평균 참여율": avg_engagement,
                "좋아요/인플루언서": round(total_likes / len(participations), 2) if participations else 0,
                "조회수/인플루언서": round(total_views / len(participations), 2) if participations else 0,
                "좋아요당 비용": f"{cost_per_like:,.0f}원",
                "조회수당 비용": f"{cost_per_view:,.2f}원",
                "인플루언서당 비용": f"{cost_per_influencer:,.0f}원"
            })
    except Exception as e:
        st.error(f"❌ ROI 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if not roi_data:
        st.info("ROI 분석 데이터가 없습니다.")
        return

    df_roi = pd.DataFrame(roi_data)
    
    # ROI 지표 요약
    col_title, col_help = st.columns([4, 1])
    with col_title:
        st.markdown("##### 📊 캠페인별 ROI 지표")
    with col_help:
        if st.button("❓", key="roi_help", help="ROI 지표 계산 방법"):
            st.session_state.show_roi_help = not st.session_state.get("show_roi_help", False)
    
    if st.session_state.get("show_roi_help", False):
        st.info("""
        **💰 ROI 지표 계산 방법:**
        
        - **참여 인플루언서**: 해당 캠페인에 참여한 인플루언서 수
        - **총 콘텐츠**: 해당 캠페인에서 생성된 총 콘텐츠 수
        - **총 비용**: 해당 캠페인의 모든 인플루언서 비용 합계 (원)
        - **총 좋아요/댓글/조회수**: 해당 캠페인의 모든 콘텐츠 성과 합계
        - **평균 참여율**: (총 좋아요 + 총 댓글) / 총 조회수 × 100
        - **좋아요/인플루언서**: 총 좋아요 수 ÷ 참여 인플루언서 수
        - **조회수/인플루언서**: 총 조회수 ÷ 참여 인플루언서 수
        - **좋아요당 비용**: 총 비용 ÷ 총 좋아요 수
        - **조회수당 비용**: 총 비용 ÷ 총 조회수
        - **인플루언서당 비용**: 총 비용 ÷ 참여 인플루언서 수
        """)
    
    # 참여율을 퍼센트 형식으로 표시
    df_roi_display = df_roi.copy()
    df_roi_display["평균 참여율"] = df_roi_display["평균 참여율"].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(df_roi_display, use_container_width=True, hide_index=True)
    
    # ROI 시각화
    col1, col2 = st.columns(2)
    with col1:
        fig_roi_likes = px.bar(
            df_roi, 
            x="캠페인", 
            y="좋아요/인플루언서", 
            title="인플루언서당 평균 좋아요 수"
        )
        st.plotly_chart(fig_roi_likes, use_container_width=True)
    
    with col2:
        fig_roi_views = px.bar(
            df_roi, 
            x="캠페인", 
            y="조회수/인플루언서", 
            title="인플루언서당 평균 조회수"
        )
        st.plotly_chart(fig_roi_views, use_container_width=True)
    
    # 비용 관련 시각화
    st.markdown("##### 💰 비용 효율성 분석")
    
    # 비용 데이터를 숫자로 변환 (시각화용)
    df_roi_viz = df_roi.copy()
    df_roi_viz["총_비용_숫자"] = df_roi_viz["총 비용"].str.replace("원", "").str.replace(",", "").astype(float)
    df_roi_viz["좋아요당_비용_숫자"] = df_roi_viz["좋아요당 비용"].str.replace("원", "").str.replace(",", "").astype(float)
    df_roi_viz["조회수당_비용_숫자"] = df_roi_viz["조회수당 비용"].str.replace("원", "").str.replace(",", "").astype(float)
    df_roi_viz["인플루언서당_비용_숫자"] = df_roi_viz["인플루언서당 비용"].str.replace("원", "").str.replace(",", "").astype(float)
    
    col3, col4 = st.columns(2)
    with col3:
        fig_cost_total = px.bar(
            df_roi_viz, 
            x="캠페인", 
            y="총_비용_숫자", 
            title="캠페인별 총 비용",
            labels={"총_비용_숫자": "총 비용 (원)"}
        )
        st.plotly_chart(fig_cost_total, use_container_width=True)
        
        fig_cost_per_like = px.bar(
            df_roi_viz, 
            x="캠페인", 
            y="좋아요당_비용_숫자", 
            title="좋아요당 비용",
            labels={"좋아요당_비용_숫자": "좋아요당 비용 (원)"}
        )
        st.plotly_chart(fig_cost_per_like, use_container_width=True)
    
    with col4:
        fig_cost_per_view = px.bar(
            df_roi_viz, 
            x="캠페인", 
            y="조회수당_비용_숫자", 
            title="조회수당 비용",
            labels={"조회수당_비용_숫자": "조회수당 비용 (원)"}
        )
        st.plotly_chart(fig_cost_per_view, use_container_width=True)
        
        fig_cost_per_influencer = px.bar(
            df_roi_viz, 
            x="캠페인", 
            y="인플루언서당_비용_숫자", 
            title="인플루언서당 비용",
            labels={"인플루언서당_비용_숫자": "인플루언서당 비용 (원)"}
        )
        st.plotly_chart(fig_cost_per_influencer, use_container_width=True)
    
    # 효율성 분석
    col_title, col_help = st.columns([4, 1])
    with col_title:
        st.markdown("##### ⚡ 캠페인 효율성 분석")
    with col_help:
        if st.button("❓", key="efficiency_help", help="효율성 점수 계산 방법"):
            st.session_state.show_efficiency_help = not st.session_state.get("show_efficiency_help", False)
    
    if st.session_state.get("show_efficiency_help", False):
        st.info("""
        **⚡ 비용 효율성 점수 계산 방법:**
        
        **비용 효율성 점수 = (비용 효율성 × 0.4) + (평균 참여율 × 0.6)**
        
        - **비용 효율성**: 1000원당 좋아요 수 (좋아요당 비용의 역수)
        - **평균 참여율**: (총 좋아요 + 총 댓글) / 총 조회수 × 100
        - **비용 효율성 가중치**: 40%
        - **참여율 가중치**: 60%
        
        *높은 점수일수록 비용 대비 성과가 우수한 캠페인입니다.*
        """)
    
    efficiency_data = df_roi_viz.copy()
    
    # 비용 효율성 점수 계산 (낮은 비용, 높은 성과 = 높은 점수)
    efficiency_data["비용_효율성_점수"] = 0
    for idx, row in efficiency_data.iterrows():
        # 좋아요당 비용이 낮을수록, 참여율이 높을수록 좋은 점수
        cost_efficiency = 0
        if row["좋아요당_비용_숫자"] > 0:
            # 좋아요당 비용의 역수 (낮은 비용일수록 높은 점수)
            cost_efficiency = 1000 / row["좋아요당_비용_숫자"]  # 1000원당 좋아요 수
        
        engagement_score = row["평균 참여율"]
        
        # 종합 효율성 점수 (비용 효율성 40%, 참여율 60%)
        efficiency_score = (cost_efficiency * 0.4 + engagement_score * 0.6)
        efficiency_data.loc[idx, "비용_효율성_점수"] = round(efficiency_score, 2)
    
    # 참여율을 퍼센트 형식으로 표시
    efficiency_display = efficiency_data[["캠페인", "비용_효율성_점수", "좋아요/인플루언서", "조회수/인플루언서", "평균 참여율", "좋아요당_비용_숫자"]].copy()
    efficiency_display["평균 참여율"] = efficiency_display["평균 참여율"].apply(lambda x: f"{x:.2f}%")
    efficiency_display["좋아요당_비용_숫자"] = efficiency_display["좋아요당_비용_숫자"].apply(lambda x: f"{x:,.0f}원")
    efficiency_display.columns = ["캠페인", "비용 효율성 점수", "좋아요/인플루언서", "조회수/인플루언서", "평균 참여율", "좋아요당 비용"]
    
    st.dataframe(efficiency_display, use_container_width=True, hide_index=True)
    
    fig_efficiency = px.bar(
        efficiency_data, 
        x="캠페인", 
        y="비용_효율성_점수", 
        title="캠페인 비용 효율성 점수 (높을수록 효율적)"
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)


def render_export_section(campaign_data, report_type):
    """리포트 내보내기 섹션 렌더링"""
    st.markdown("---")
    st.markdown("#### 📤 리포트 내보내기")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 CSV 다운로드", key="export_csv"):
            export_to_csv(campaign_data, report_type)
    
    with col2:
        if st.button("📈 Excel 다운로드", key="export_excel"):
            export_to_excel(campaign_data, report_type)
    
    with col3:
        if st.button("📋 요약 리포트", key="export_summary"):
            export_summary_report(campaign_data, report_type)


def export_to_csv(campaign_data, report_type):
    """CSV 형태로 리포트 내보내기"""
    try:
        # 리포트 타입에 따른 데이터 수집
        if report_type == "📊 종합 대시보드":
            data = get_comprehensive_data(campaign_data)
        elif report_type == "📈 성과 지표 분석":
            data = get_performance_metrics_data(campaign_data)
        elif report_type == "👥 인플루언서별 분석":
            data = get_influencer_analysis_data(campaign_data)
        else:
            data = get_basic_campaign_data(campaign_data)
        
        if data:
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="CSV 파일 다운로드",
                data=csv,
                file_name=f"campaign_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("내보낼 데이터가 없습니다.")
    except Exception as e:
        st.error(f"CSV 내보내기 중 오류가 발생했습니다: {str(e)}")


def export_to_excel(campaign_data, report_type):
    """Excel 형태로 리포트 내보내기"""
    try:
        # 여러 시트로 구성된 Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 기본 캠페인 데이터
            basic_data = get_basic_campaign_data(campaign_data)
            if basic_data:
                pd.DataFrame(basic_data).to_excel(writer, sheet_name='캠페인 요약', index=False)
            
            # 성과 지표 데이터
            performance_data = get_performance_metrics_data(campaign_data)
            if performance_data:
                pd.DataFrame(performance_data).to_excel(writer, sheet_name='성과 지표', index=False)
            
            # 인플루언서 분석 데이터
            influencer_data = get_influencer_analysis_data(campaign_data)
            if influencer_data:
                pd.DataFrame(influencer_data).to_excel(writer, sheet_name='인플루언서 분석', index=False)
        
        st.download_button(
            label="Excel 파일 다운로드",
            data=output.getvalue(),
            file_name=f"campaign_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Excel 내보내기 중 오류가 발생했습니다: {str(e)}")


def export_summary_report(campaign_data, report_type):
    """요약 리포트 생성"""
    try:
        summary = generate_summary_report(campaign_data, report_type)
        st.markdown("#### 📋 요약 리포트")
        st.markdown(summary)
        
        st.download_button(
            label="요약 리포트 다운로드 (TXT)",
            data=summary,
            file_name=f"campaign_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"요약 리포트 생성 중 오류가 발생했습니다: {str(e)}")


def get_basic_campaign_data(campaign_data):
    """기본 캠페인 데이터 수집"""
    data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            completed = len([p for p in participations if p.get("content_uploaded", False)])
            data.append({
                "캠페인명": campaign["campaign_name"],
                "캠페인 유형": format_campaign_type(campaign["campaign_type"]),
                "참여 인플루언서 수": len(participations),
                "업로드 완료": completed,
                "완료율": f"{(completed / len(participations) * 100):.1f}%" if participations else "0%",
                "시작일": campaign.get("start_date", "N/A"),
                "종료일": campaign.get("end_date", "N/A")
            })
    except Exception as e:
        st.error(f"기본 데이터 수집 중 오류: {str(e)}")
    return data


def get_performance_metrics_data(campaign_data):
    """성과 지표 데이터 수집"""
    data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            for participation in participations:
                contents = db_manager.get_campaign_influencer_contents(participation["id"])
                for content in contents:
                    likes = content.get("likes", 0)
                    comments = content.get("comments", 0)
                    shares = content.get("shares", 0)
                    views = content.get("views", 0)
                    
                    # 참여율 계산: (좋아요 + 댓글) / 조회수 × 100
                    engagement_rate = 0
                    if views > 0:
                        engagement_rate = round((likes + comments) / views * 100, 2)
                    
                    data.append({
                        "캠페인": campaign["campaign_name"],
                        "인플루언서": participation.get("influencer_name", "N/A"),
                        "플랫폼": participation.get("platform", "N/A"),
                        "좋아요": likes,
                        "댓글": comments,
                        "조회수": views,
                        "참여율": engagement_rate,
                        "업로드일": content.get("posted_at", "N/A")
                    })
    except Exception as e:
        st.error(f"성과 지표 데이터 수집 중 오류: {str(e)}")
    return data


def get_influencer_analysis_data(campaign_data):
    """인플루언서 분석 데이터 수집"""
    data = []
    try:
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            for participation in participations:
                contents = db_manager.get_campaign_influencer_contents(participation["id"])
                total_likes = sum(content.get("likes", 0) for content in contents)
                total_comments = sum(content.get("comments", 0) for content in contents)
                total_views = sum(content.get("views", 0) for content in contents)
                total_shares = sum(content.get("shares", 0) for content in contents)
                
                # 참여율 계산: (총 좋아요 + 총 댓글) / 총 조회수 × 100
                avg_engagement = 0
                if total_views > 0:
                    avg_engagement = round((total_likes + total_comments) / total_views * 100, 2)
                
                data.append({
                    "캠페인": campaign["campaign_name"],
                    "인플루언서": participation.get("influencer_name", "N/A"),
                    "플랫폼": participation.get("platform", "N/A"),
                    "팔로워": participation.get("followers_count", 0),
                    "총 좋아요": total_likes,
                    "총 댓글": total_comments,
                    "총 조회수": total_views,
                    "평균 참여율": avg_engagement,
                    "콘텐츠 수": len(contents)
                })
    except Exception as e:
        st.error(f"인플루언서 분석 데이터 수집 중 오류: {str(e)}")
    return data


def get_comprehensive_data(campaign_data):
    """종합 데이터 수집"""
    return get_basic_campaign_data(campaign_data)


def generate_summary_report(campaign_data, report_type):
    """요약 리포트 생성"""
    try:
        total_participations = sum(len(db_manager.get_all_campaign_participations(c["id"])) for c in campaign_data)
        total_completed = sum(
            len([p for p in db_manager.get_all_campaign_participations(c["id"]) if p.get("content_uploaded", False)])
            for c in campaign_data
        )
        
        summary = f"""
=== 캠페인 성과 리포트 요약 ===
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
리포트 타입: {report_type}

📊 기본 통계:
- 분석 캠페인 수: {len(campaign_data)}개
- 총 참여 인플루언서: {total_participations}명
- 업로드 완료: {total_completed}명
- 전체 완료율: {(total_completed / total_participations * 100):.1f}% (총 참여자 > 0인 경우)

📈 캠페인별 요약:
"""
        
        for campaign in campaign_data:
            participations = db_manager.get_all_campaign_participations(campaign["id"])
            completed = len([p for p in participations if p.get("content_uploaded", False)])
            summary += f"- {campaign['campaign_name']}: {len(participations)}명 참여, {completed}명 완료 ({(completed / len(participations) * 100):.1f}%)\n"
        
        summary += f"""
📋 상세 분석은 웹 인터페이스에서 확인하실 수 있습니다.
"""
        
        return summary
    except Exception as e:
        return f"요약 리포트 생성 중 오류가 발생했습니다: {str(e)}"
