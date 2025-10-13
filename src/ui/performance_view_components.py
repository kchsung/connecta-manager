"""
성과 조회 탭 컴포넌트
"""
import streamlit as st
import pandas as pd
from ..db.database import db_manager
from .common_functions import format_campaign_type, format_participation_status


def render_performance_view_tab():
    """성과 조회 탭 - 성과 데이터 조회 및 확인 전용"""
    # 모달 표시 확인
    if "viewing_performance" in st.session_state:
        render_performance_detail_modal()
        return

    # 캠페인 목록 새로고침
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(
            "🔄 캠페인 목록 새로고침",
            key="refresh_campaigns_performance",
            help="캠페인 목록을 새로 불러옵니다",
        ):
            st.session_state.pop("campaigns_cache", None)
            st.session_state.pop("participations_cache", None)
            st.success("캠페인 목록을 새로고침했습니다!")
            st.rerun()
    with col2:
        st.caption("캠페인 목록을 새로고침하려면 새로고침 버튼을 클릭하세요.")

    # 캠페인 조회
    try:
        campaigns = db_manager.get_campaigns()
        if not campaigns:
            st.info("먼저 캠페인을 생성해주세요.")
            return
    except Exception as e:
        st.error(f"❌ 캠페인 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    # 모든 캠페인의 참여 인플루언서 모으기
    all_participations = []
    try:
        for campaign in campaigns:
            if not campaign or "id" not in campaign:
                continue

            participations = db_manager.get_all_campaign_participations(campaign["id"])
            if not participations:
                continue

            for participation in participations:
                if not participation:
                    continue

                safe_participation = dict(participation) if isinstance(participation, dict) else {}
                safe_participation["campaign_name"] = campaign.get("campaign_name", "N/A")
                safe_participation["campaign_type"] = campaign.get("campaign_type", "")
                all_participations.append(safe_participation)
    except Exception as e:
        st.error(f"❌ 참여 인플루언서 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if not all_participations:
        st.info("참여한 인플루언서가 없습니다.")
        return

    # 캠페인 선택
    try:
        campaign_names = list(
            set(
                p.get("campaign_name", "N/A")
                for p in all_participations
                if p and isinstance(p, dict)
            )
        )
    except Exception as e:
        st.warning(f"캠페인 이름 추출 중 오류: {str(e)}")
        campaign_names = ["전체"]

    selected_campaign = st.selectbox(
        "캠페인을 선택하세요",
        ["전체"] + campaign_names,
        key="performance_campaign_select",
        help="특정 캠페인의 성과만 보고 싶다면 선택하세요",
    )

    # 선택된 캠페인 필터
    try:
        if selected_campaign == "전체":
            filtered_participations = all_participations
        else:
            filtered_participations = [
                p
                for p in all_participations
                if p and isinstance(p, dict) and p.get("campaign_name") == selected_campaign
            ]
    except Exception as e:
        st.warning(f"데이터 필터링 중 오류: {str(e)}")
        filtered_participations = all_participations

    # 필터 UI
    st.subheader("🔍 필터링 옵션")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        upload_filter = st.selectbox(
            "업로드 여부",
            ["전체", "업로드 완료", "업로드 미완료"],
            key="upload_filter_performance",
            help="업로드 상태에 따라 필터링합니다",
        )
    with col2:
        status_filter = st.selectbox(
            "참여 상태",
            ["전체", "assigned", "in_progress", "completed", "cancelled"],
            key="status_filter_performance",
            help="참여 상태에 따라 필터링합니다",
            format_func=lambda x: {
                "전체": "🌐 전체",
                "assigned": "📋 배정",
                "in_progress": "🟢 진행중",
                "completed": "✅ 완료",
                "cancelled": "❌ 취소",
            }.get(x, x),
        )
    with col3:
        platform_filter = st.selectbox(
            "플랫폼",
            ["전체", "instagram", "youtube", "tiktok", "twitter"],
            key="platform_filter_performance",
            help="플랫폼에 따라 필터링합니다",
            format_func=lambda x: {
                "전체": "🌐 전체",
                "instagram": "📸 Instagram",
                "youtube": "📺 YouTube",
                "tiktok": "🎵 TikTok",
                "twitter": "🐦 Twitter",
            }.get(x, x),
        )
    with col4:
        sample_filter = st.selectbox(
            "샘플 상태",
            ["전체", "요청", "발송준비", "발송완료", "수령"],
            key="sample_filter_performance",
            help="샘플 상태에 따라 필터링합니다",
            format_func=lambda x: {
                "전체": "🌐 전체",
                "요청": "📋 요청",
                "발송준비": "📦 발송준비",
                "발송완료": "🚚 발송완료",
                "수령": "✅ 수령",
            }.get(x, x),
        )

    # 필터 적용
    try:
        filtered_data = filtered_participations.copy()

        if upload_filter == "업로드 완료":
            filtered_data = [
                p for p in filtered_data if p and isinstance(p, dict) and p.get("content_uploaded", False)
            ]
        elif upload_filter == "업로드 미완료":
            filtered_data = [
                p for p in filtered_data if p and isinstance(p, dict) and not p.get("content_uploaded", False)
            ]

        if status_filter != "전체":
            filtered_data = [
                p for p in filtered_data if p and isinstance(p, dict) and p.get("status") == status_filter
            ]

        if platform_filter != "전체":
            filtered_data = [
                p for p in filtered_data if p and isinstance(p, dict) and p.get("platform") == platform_filter
            ]

        if sample_filter != "전체":
            filtered_data = [
                p for p in filtered_data if p and isinstance(p, dict) and p.get("sample_status") == sample_filter
            ]
    except Exception as e:
        st.warning(f"필터 적용 중 오류: {str(e)}")
        filtered_data = filtered_participations

    # 결과 표시
    st.subheader(f"📊 성과 관리 결과 ({len(filtered_data)}명)")

    if not filtered_data:
        st.info("선택한 조건에 맞는 참여 인플루언서가 없습니다.")
        return

    # 성과 데이터 테이블 (campaign_influencer_contents 집계 포함)
    performance_data = []
    for participation in filtered_data:
        if not participation or "id" not in participation:
            continue

        participation_id = participation["id"]
        try:
            content_data = db_manager.get_performance_data_by_participation(participation_id) or []
            total_views = sum(content.get("views", 0) for content in content_data if content)
            total_likes = sum(content.get("likes", 0) for content in content_data if content)
            total_comments = sum(content.get("comments", 0) for content in content_data if content)
            content_count = len(content_data)

            first_content_url = ""
            if content_data and content_data[0]:
                first_content_url = content_data[0].get("content_url", "") or ""
            content_url_display = (
                first_content_url[:30] + "..." if len(first_content_url) > 30 else first_content_url or "없음"
            )
        except Exception:
            total_views = 0
            total_likes = 0
            total_comments = 0
            content_count = 0
            content_url_display = "없음"

        performance_data.append(
            {
                "캠페인": participation.get("campaign_name", "N/A"),
                "캠페인 유형": format_campaign_type(participation.get("campaign_type", "")),
                "인플루언서": participation.get("influencer_name") or participation.get("sns_id", "N/A"),
                "플랫폼": participation.get("platform", "N/A"),
                "SNS ID": participation.get("sns_id", "N/A"),
                "참여 상태": format_participation_status(participation.get("status", "assigned")),
                "샘플 상태": participation.get("sample_status", "요청"),
                "업로드 완료": "✅" if participation.get("content_uploaded", False) else "❌",
                "조회수": f"{total_views:,}",
                "좋아요": f"{total_likes:,}",
                "댓글": f"{total_comments:,}",
                "콘텐츠 URL": content_url_display,
                "콘텐츠 수": f"{content_count}개",
            }
        )

    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("표시할 성과 데이터가 없습니다.")


def render_performance_detail_modal():
    """성과 상세보기 모달 - campaign_influencer_contents 테이블 기반"""
    influencer = st.session_state.viewing_performance
    st.markdown(
        f"**성과 상세보기:** {influencer.get('influencer_name') or influencer['sns_id']} ({influencer['platform']})"
    )

    try:
        performance_data = db_manager.get_performance_data_by_participation(influencer["id"])
        if not performance_data:
            st.info("이 인플루언서의 성과 데이터가 없습니다.")
            return
    except Exception as e:
        st.error(f"❌ 성과 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    st.markdown("#### 📊 콘텐츠별 성과 데이터")

    total_views = sum(content.get("views", 0) for content in performance_data)
    total_likes = sum(content.get("likes", 0) for content in performance_data)
    total_comments = sum(content.get("comments", 0) for content in performance_data)
    total_shares = sum(content.get("shares", 0) for content in performance_data)
    total_clicks = sum(content.get("clicks", 0) for content in performance_data)
    total_conversions = sum(content.get("conversions", 0) for content in performance_data)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("총 조회수", f"{total_views:,}")
        st.metric("총 좋아요", f"{total_likes:,}")
    with c2:
        st.metric("총 댓글", f"{total_comments:,}")
        st.metric("총 공유", f"{total_shares:,}")
    with c3:
        st.metric("총 클릭", f"{total_clicks:,}")
        st.metric("총 전환", f"{total_conversions:,}")

    st.markdown("#### 📱 콘텐츠별 상세 성과")
    for i, content in enumerate(performance_data):
        with st.expander(f"📱 콘텐츠 {i+1}: {content.get('content_url', 'N/A')[:50]}...", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("조회수", f"{content.get('views', 0):,}")
                st.metric("좋아요", f"{content.get('likes', 0):,}")
            with col2:
                st.metric("댓글", f"{content.get('comments', 0):,}")
                st.metric("공유", f"{content.get('shares', 0):,}")
            with col3:
                st.metric("클릭", f"{content.get('clicks', 0):,}")
                st.metric("전환", f"{content.get('conversions', 0):,}")

            st.markdown("**콘텐츠 정보:**")
            st.text(f"URL: {content.get('content_url', 'N/A')}")
            st.text(f"게시일: {content.get('posted_at', 'N/A')[:10] if content.get('posted_at') else 'N/A'}")
            st.text(f"캡션: {content.get('caption', 'N/A')[:200]}..." if content.get("caption") else "캡션: N/A")

            if content.get("qualitative_note"):
                st.markdown("**정성평가:**")
                st.text_area("", value=content["qualitative_note"], height=100, disabled=True)

    if len(performance_data) > 1:
        st.markdown("#### 📈 성과 히스토리")
        history_data = []
        for i, content in enumerate(performance_data):
            history_data.append(
                {
                    "콘텐츠": f"콘텐츠 {i+1}",
                    "게시일": content.get("posted_at", "N/A")[:10] if content.get("posted_at") else "N/A",
                    "조회수": content.get("views", 0),
                    "좋아요": content.get("likes", 0),
                    "댓글": content.get("comments", 0),
                    "공유": content.get("shares", 0),
                    "클릭": content.get("clicks", 0),
                    "전환": content.get("conversions", 0),
                }
            )
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True, hide_index=True)

    if st.button("❌ 닫기", key=f"close_performance_detail_{influencer['id']}"):
        st.session_state.pop("viewing_performance", None)
        st.rerun()


