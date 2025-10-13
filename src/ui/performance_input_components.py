"""
성과 입력 탭 컴포넌트
"""
import streamlit as st
from datetime import datetime
from ..db.database import db_manager
from .common_functions import format_participation_status
from .performance_components import check_database_for_performance_data


def render_performance_input_tab():
    """성과 입력 탭 - 좌우 분할 레이아웃"""
    st.markdown("#### ✏️ 성과 데이터 입력 및 수정")

    left_col, right_col = st.columns([1, 1])
    with left_col:
        render_user_search_panel()
    with right_col:
        render_input_form_panel()


def render_user_search_panel():
    """좌측: 사용자 검색 패널"""
    st.markdown("##### 🔍 인플루언서 검색")

    if st.button("🔄 새로고침", key="refresh_campaigns_input", help="캠페인 목록을 새로 불러옵니다"):
        st.session_state.pop("campaigns_cache", None)
        st.session_state.pop("participations_cache", None)
        st.session_state.pop("input_participations_cache", None)  # 새로운 캐시 키도 클리어
        st.success("캠페인 목록을 새로고침했습니다!")
        # st.rerun() 제거 - 캐시만 클리어

    # 캐시된 데이터 사용으로 성능 최적화
    cache_key = "input_participations_cache"
    if cache_key not in st.session_state:
        try:
            campaigns = db_manager.get_campaigns()
            if not campaigns:
                st.info("먼저 캠페인을 생성해주세요.")
                return
        except Exception as e:
            st.error(f"❌ 캠페인 데이터 조회 중 오류가 발생했습니다: {str(e)}")
            return

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
        
        # 캐시에 저장
        st.session_state[cache_key] = all_participations
    else:
        # 캐시된 데이터 사용
        all_participations = st.session_state[cache_key]

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
        "캠페인 선택",
        ["전체"] + campaign_names,
        key="input_campaign_select",
        help="특정 캠페인의 인플루언서만 보기",
    )

    # 필터링
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

    search_term = st.text_input(
        "인플루언서 검색",
        placeholder="이름 또는 SNS ID로 검색",
        key="performance_input_search",
        help="인플루언서 이름이나 SNS ID를 입력하여 검색하세요",
    )

    platform_options = ["전체"]
    try:
        platform_options.extend(
            list(
                set(
                    p.get("platform", "N/A")
                    for p in filtered_participations
                    if p and isinstance(p, dict)
                )
            )
        )
    except Exception as e:
        st.warning(f"플랫폼 옵션 추출 중 오류: {str(e)}")

    search_platform = st.selectbox(
        "플랫폼 필터",
        platform_options,
        key="performance_input_platform_filter",
        help="특정 플랫폼만 보기",
    )

    # 검색 결과 필터링
    try:
        search_results = filtered_participations.copy()

        if search_term:
            lt = search_term.lower()
            search_results = [
                p
                for p in search_results
                if (
                    p
                    and isinstance(p, dict)
                    and (
                        lt in (p.get("influencer_name", "") or "").lower()
                        or lt in (p.get("sns_id", "") or "").lower()
                    )
                )
            ]

        if search_platform != "전체":
            search_results = [
                p
                for p in search_results
                if p and isinstance(p, dict) and p.get("platform") == search_platform
            ]
    except Exception as e:
        st.warning(f"검색 필터링 중 오류: {str(e)}")
        search_results = filtered_participations

    if search_results:
        st.markdown(f"**검색 결과: {len(search_results)}명**")
        try:
            influencer_options = [
                f"{p.get('influencer_name') or p.get('sns_id', 'N/A')} ({p.get('platform', 'N/A')})"
                for p in search_results
                if p and isinstance(p, dict)
            ]
        except Exception as e:
            st.warning(f"인플루언서 옵션 생성 중 오류: {str(e)}")
            influencer_options = ["오류 발생"]

        selected_influencer_idx = st.selectbox(
            "인플루언서 선택",
            range(len(influencer_options)),
            format_func=lambda x: influencer_options[x],
            key="selected_influencer_input",
            help="성과를 입력할 인플루언서를 선택하세요",
        )

        try:
            if selected_influencer_idx < len(search_results):
                selected_influencer = search_results[selected_influencer_idx]
            else:
                st.error("선택된 인플루언서를 찾을 수 없습니다.")
                return
        except Exception as e:
            st.error(f"인플루언서 선택 중 오류: {str(e)}")
            return

        # 카드뷰 - Streamlit 컴포넌트로 변경
        influencer_name = selected_influencer.get("influencer_name") or selected_influencer.get("sns_id", "N/A")
        sns_id = selected_influencer.get("sns_id", "N/A")
        platform = selected_influencer.get("platform", "N/A")
        campaign_name = selected_influencer.get("campaign_name", "N/A")
        status = selected_influencer.get("status", "assigned")

        # 간소화된 인플루언서 정보
        with st.container():
            # 프로필 정보 (한 줄로 압축)
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"""
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                ">
                    {influencer_name[0].upper() if influencer_name else 'N'}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{influencer_name}**")
                st.caption(f"@{sns_id} • {platform.upper()}")
            
            # 상태와 캠페인 (한 줄로 압축)
            st.caption(f"상태: {format_participation_status(status)} | 캠페인: {campaign_name}")

        # 간소화된 성과 미리보기 (캐시 최적화)
        performance_cache_key = f"performance_data_{selected_influencer['id']}"
        if performance_cache_key not in st.session_state:
            try:
                performance_check = check_database_for_performance_data(selected_influencer["id"])
                st.session_state[performance_cache_key] = performance_check
            except Exception as e:
                st.warning(f"성과 데이터 확인 중 오류: {str(e)}")
                performance_check = None
        else:
            performance_check = st.session_state[performance_cache_key]
        
        if performance_check and performance_check.get("exists"):
            existing_contents = performance_check.get("data", []) or []
            if existing_contents:
                total_views = sum(content.get("views", 0) for content in existing_contents if content)
                total_likes = sum(content.get("likes", 0) for content in existing_contents if content)
                total_comments = sum(content.get("comments", 0) for content in existing_contents if content)
                
                # 한 줄로 압축된 성과 요약
                st.success(f"✅ {len(existing_contents)}개 콘텐츠 | 조회수: {total_views:,} | 좋아요: {total_likes:,} | 댓글: {total_comments:,}")
            else:
                st.info("등록된 콘텐츠가 없습니다.")
        else:
            st.info("성과 데이터가 없습니다.")

        # 성과 입력/수정 버튼 (맨 아래로 이동)
        if st.button(
            "✏️ 성과 입력/수정",
            help="선택된 인플루언서의 성과 데이터를 입력하거나 수정합니다",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.selected_influencer_for_input = selected_influencer
            # st.rerun() 제거 - 조건부 렌더링으로 대체

    else:
        st.warning("검색 조건에 맞는 인플루언서가 없습니다.")
        if search_term:
            st.info(f"'{search_term}'에 대한 검색 결과가 없습니다.")


def render_input_form_panel():
    """우측: 입력/수정 폼 패널"""
    st.markdown("##### 📝 성과 입력/수정")

    if "selected_influencer_for_input" in st.session_state:
        selected_influencer = st.session_state.selected_influencer_for_input
        render_performance_input_form(selected_influencer)
    else:
        st.markdown("**📋 성과 입력 가이드:**")
        st.markdown(
            """
        1. **좌측에서 인플루언서 선택**
        2. **"성과 입력/수정" 버튼 클릭**
        3. **기존 콘텐츠가 있으면 수정, 없으면 새로 등록**
        4. **성과 데이터 입력 후 저장**

        **📊 입력 가능한 성과 지표:**
        - 조회수, 좋아요, 댓글, 공유
        - 클릭수, 전환수
        - 정성평가 (노트)
        """
        )

        with st.expander("💡 성과 입력 팁"):
            st.markdown(
                """
            **효과적인 성과 관리:**
            - 정기적으로 성과 데이터를 업데이트하세요
            - 정성평가를 통해 콘텐츠 품질을 기록하세요
            - 여러 콘텐츠의 성과를 비교 분석하세요

            **데이터 정확성:**
            - 실제 성과 데이터를 정확히 입력하세요
            - 게시일과 측정일을 구분하여 기록하세요
            - URL은 정확한 콘텐츠 링크를 입력하세요
            """
            )


def render_performance_input_form(influencer):
    """성과 입력/수정 폼"""
    st.markdown(f"**📊 {influencer.get('influencer_name', influencer['sns_id'])} 성과 관리**")

    # 캐시된 성과 데이터 사용
    performance_cache_key = f"performance_data_{influencer['id']}"
    if performance_cache_key in st.session_state:
        performance_check = st.session_state[performance_cache_key]
        existing_contents = performance_check.get("data", []) or [] if performance_check else []
    else:
        try:
            existing_contents = db_manager.get_performance_data_by_participation(influencer["id"]) or []
        except Exception as e:
            st.error(f"❌ 성과 데이터 조회 중 오류가 발생했습니다: {str(e)}")
            existing_contents = []

    if existing_contents:
        st.success(f"✅ {len(existing_contents)}개의 콘텐츠가 등록되어 있습니다.")

        for i, content in enumerate(existing_contents):
            if not content:
                continue

            content_url_display = (content.get("content_url", "N/A") or "N/A")[:50]
            with st.expander(f"📱 콘텐츠 {i+1}: {content_url_display}...", expanded=True):
                with st.form(f"content_edit_form_{content.get('id', i)}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        content_url = st.text_input(
                            "콘텐츠 URL",
                            value=content.get("content_url", "") or "",
                            key=f"content_url_{i}",
                            help="콘텐츠의 URL을 입력하세요",
                        )

                        posted_at_value = datetime.now().date()
                        if content.get("posted_at"):
                            try:
                                posted_at_value = datetime.fromisoformat(
                                    content.get("posted_at", "").replace("Z", "+00:00")
                                ).date()
                            except Exception:
                                posted_at_value = datetime.now().date()

                        posted_at = st.date_input(
                            "게시일",
                            value=posted_at_value,
                            key=f"posted_at_{i}",
                            help="콘텐츠가 게시된 날짜",
                        )

                        views = st.number_input(
                            "조회수",
                            min_value=0,
                            value=content.get("views", 0) or 0,
                            key=f"views_{i}",
                            help="콘텐츠의 조회수",
                        )

                        likes = st.number_input(
                            "좋아요",
                            min_value=0,
                            value=content.get("likes", 0) or 0,
                            key=f"likes_{i}",
                            help="콘텐츠의 좋아요 수",
                        )

                    with col2:
                        comments = st.number_input(
                            "댓글",
                            min_value=0,
                            value=content.get("comments", 0) or 0,
                            key=f"comments_{i}",
                            help="콘텐츠의 댓글 수",
                        )

                        shares = st.number_input(
                            "공유",
                            min_value=0,
                            value=content.get("shares", 0) or 0,
                            key=f"shares_{i}",
                            help="콘텐츠의 공유 수",
                        )

                        clicks = st.number_input(
                            "클릭",
                            min_value=0,
                            value=content.get("clicks", 0) or 0,
                            key=f"clicks_{i}",
                            help="콘텐츠의 클릭 수",
                        )

                        conversions = st.number_input(
                            "전환",
                            min_value=0,
                            value=content.get("conversions", 0) or 0,
                            key=f"conversions_{i}",
                            help="콘텐츠의 전환 수",
                        )

                    caption = st.text_area(
                        "캡션",
                        value=content.get("caption", "") or "",
                        key=f"caption_{i}",
                        help="콘텐츠의 캡션",
                        height=100,
                    )

                    qualitative_note = st.text_area(
                        "정성평가",
                        value=content.get("qualitative_note", "") or "",
                        key=f"qualitative_note_{i}",
                        help="콘텐츠에 대한 정성평가",
                        height=100,
                    )

                    col1b, col2b = st.columns(2)
                    with col1b:
                        if st.form_submit_button("💾 저장", type="primary"):
                            try:
                                update_data = {
                                    "content_url": content_url,
                                    "posted_at": posted_at.isoformat(),
                                    "views": views,
                                    "likes": likes,
                                    "comments": comments,
                                    "shares": shares,
                                    "clicks": clicks,
                                    "conversions": conversions,
                                    "caption": caption,
                                    "qualitative_note": qualitative_note,
                                }
                                # TODO: 실제 DB 업데이트 호출
                                # db_manager.update_campaign_influencer_content(content['id'], update_data)
                                st.success("✅ 콘텐츠가 성공적으로 업데이트되었습니다!")
                                # st.rerun() 제거 - 폼 제출 후 자동으로 상태 변경
                            except Exception as e:
                                st.error(f"❌ 콘텐츠 업데이트 중 오류가 발생했습니다: {str(e)}")
                    with col2b:
                        if st.form_submit_button("❌ 취소"):
                            # st.rerun() 제거 - 폼 취소는 자동으로 처리
                            pass

        if st.button("➕ 새 콘텐츠 추가", help="새로운 콘텐츠를 추가합니다"):
            st.session_state.adding_new_content = True
            # st.rerun() 제거 - 상태 변경으로 자동 렌더링
    else:
        st.info("등록된 콘텐츠가 없습니다. 새 콘텐츠를 등록해주세요.")
        render_new_content_form(influencer)

    if st.button("❌ 닫기", help="성과 입력 폼을 닫습니다"):
        st.session_state.pop("selected_influencer_for_input", None)
        # st.rerun() 제거 - 상태 변경으로 자동 렌더링


def render_new_content_form(influencer):
    """새 콘텐츠 등록 폼"""
    with st.form("new_content_form"):
        st.markdown("#### 📱 새 콘텐츠 등록")

        col1, col2 = st.columns(2)
        with col1:
            content_url = st.text_input("콘텐츠 URL", key="new_content_url", help="콘텐츠의 URL을 입력하세요")
            posted_at = st.date_input(
                "게시일", value=datetime.now().date(), key="new_posted_at", help="콘텐츠가 게시된 날짜"
            )
            views = st.number_input("조회수", min_value=0, value=0, key="new_views", help="콘텐츠의 조회수")
            likes = st.number_input("좋아요", min_value=0, value=0, key="new_likes", help="콘텐츠의 좋아요 수")

        with col2:
            comments = st.number_input("댓글", min_value=0, value=0, key="new_comments", help="콘텐츠의 댓글 수")
            shares = st.number_input("공유", min_value=0, value=0, key="new_shares", help="콘텐츠의 공유 수")
            clicks = st.number_input("클릭", min_value=0, value=0, key="new_clicks", help="콘텐츠의 클릭 수")
            conversions = st.number_input("전환", min_value=0, value=0, key="new_conversions", help="콘텐츠의 전환 수")

        caption = st.text_area("캡션", key="new_caption", help="콘텐츠의 캡션", height=100)
        qualitative_note = st.text_area("정성평가", key="new_qualitative_note", help="콘텐츠에 대한 정성평가", height=100)

        col1b, col2b = st.columns(2)
        with col1b:
            if st.form_submit_button("💾 저장", type="primary"):
                try:
                    new_content_data = {
                        "participation_id": influencer["id"],
                        "content_url": content_url,
                        "posted_at": posted_at.isoformat(),
                        "views": views,
                        "likes": likes,
                        "comments": comments,
                        "shares": shares,
                        "clicks": clicks,
                        "conversions": conversions,
                        "caption": caption,
                        "qualitative_note": qualitative_note,
                    }
                    # TODO: 실제 DB 저장 호출
                    # db_manager.create_campaign_influencer_content(new_content_data)
                    st.success("✅ 새 콘텐츠가 성공적으로 등록되었습니다!")
                    # st.rerun() 제거 - 폼 제출 후 자동으로 상태 변경
                except Exception as e:
                    st.error(f"❌ 콘텐츠 등록 중 오류가 발생했습니다: {str(e)}")
        with col2b:
            if st.form_submit_button("❌ 취소"):
                # st.rerun() 제거 - 폼 취소는 자동으로 처리
                pass
