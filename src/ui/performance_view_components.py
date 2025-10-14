"""
성과 조회 탭 컴포넌트 - 수정가능한 리스트로 통합
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from ..db.database import db_manager
from .common_functions import format_campaign_type, format_participation_status


def render_performance_view_tab():
    """성과 조회 탭 - 수정가능한 성과 데이터 조회 및 입력 통합"""
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
        st.caption("캠페인 목록을 새로고침하거나 아래 테이블에서 성과 데이터를 직접 편집할 수 있습니다.")

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
    col1, col2, col3, col4, col5 = st.columns(5)
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
    with col5:
        sns_id_filter = st.text_input(
            "SNS ID 검색",
            key="sns_id_filter_performance",
            help="특정 SNS ID로 필터링합니다",
            placeholder="예: @username"
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

        # SNS ID 필터링 추가
        if sns_id_filter and sns_id_filter.strip():
            search_term = sns_id_filter.strip().lower()
            filtered_data = [
                p for p in filtered_data 
                if p and isinstance(p, dict) and p.get("sns_id", "").lower().find(search_term) != -1
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
    participation_mapping = {}  # 인덱스와 participation_id 매핑
    
    for idx, participation in enumerate(filtered_data):
        if not participation or "id" not in participation:
            continue

        participation_id = participation["id"]
        participation_mapping[idx] = participation_id
        
        try:
            content_data = db_manager.get_performance_data_by_participation(participation_id) or []
            total_views = sum(content.get("views", 0) for content in content_data if content)
            total_likes = sum(content.get("likes", 0) for content in content_data if content)
            total_comments = sum(content.get("comments", 0) for content in content_data if content)
            content_count = len(content_data)

            # 첫 번째 콘텐츠의 정보 가져오기
            first_content = content_data[0] if content_data else {}
            first_content_url = first_content.get("content_url", "") or ""
            content_url_display = (
                first_content_url[:30] + "..." if len(first_content_url) > 30 else first_content_url or "없음"
            )
            
            # 추가 필드들
            caption = first_content.get("caption", "") or ""
            caption_display = caption[:50] + "..." if len(caption) > 50 else caption or "없음"
            
            posted_at = first_content.get("posted_at", "")
            posted_at_display = posted_at[:10] if posted_at else "없음"
            
            is_rels = first_content.get("is_rels", 0)
            reels_display = "릴스" if is_rels == 1 else "일반"
            
            # 날짜 변환을 위한 원본 데이터 저장
            posted_at_date = None
            if posted_at:
                try:
                    from datetime import datetime
                    posted_at_date = datetime.fromisoformat(posted_at.replace("Z", "+00:00")).date()
                except:
                    posted_at_date = None
            
        except Exception:
            total_views = 0
            total_likes = 0
            total_comments = 0
            content_count = 0
            first_content_url = ""
            caption = ""
            posted_at_date = None
            reels_display = "일반"

        performance_data.append(
            {
                "인덱스": idx,
                "캠페인": participation.get("campaign_name", "N/A"),
                "캠페인 유형": format_campaign_type(participation.get("campaign_type", "")),
                "인플루언서": participation.get("influencer_name") or participation.get("sns_id", "N/A"),
                "플랫폼": participation.get("platform", "N/A"),
                "SNS ID": participation.get("sns_id", "N/A"),
                "팔로워 수": participation.get("followers_count", 0),
                "참여 상태": format_participation_status(participation.get("status", "assigned")),
                "샘플 상태": participation.get("sample_status", "요청"),
                "업로드 완료": "✅" if participation.get("content_uploaded", False) else "❌",
                "조회수": total_views,
                "좋아요": total_likes,
                "댓글": total_comments,
                "콘텐츠 URL": first_content_url,  # 원본 URL 저장
                "컨텐츠내용": caption,  # 원본 텍스트 저장
                "업로드일": posted_at_date,  # 날짜 객체로 저장
                "릴스여부": reels_display,
                "콘텐츠 수": content_count,
            }
        )

    if performance_data:
        df = pd.DataFrame(performance_data)
        
        # 숫자형 컬럼들을 명시적으로 정수형으로 변환
        numeric_columns = ['팔로워 수', '조회수', '좋아요', '댓글', '콘텐츠 수']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # 편집 가능한 컬럼 정의
        column_config = {
            "인덱스": st.column_config.NumberColumn("인덱스", disabled=True),
            "캠페인": st.column_config.TextColumn("캠페인", disabled=True),
            "캠페인 유형": st.column_config.TextColumn("캠페인 유형", disabled=True),
            "인플루언서": st.column_config.TextColumn("인플루언서", disabled=True),
            "플랫폼": st.column_config.TextColumn("플랫폼", disabled=True),
            "SNS ID": st.column_config.TextColumn("SNS ID", disabled=True),
            "팔로워 수": st.column_config.NumberColumn("팔로워 수", disabled=True, help="인플루언서의 팔로워 수"),
            "참여 상태": st.column_config.TextColumn("참여 상태", disabled=True),
            "샘플 상태": st.column_config.TextColumn("샘플 상태", disabled=True),
            "업로드 완료": st.column_config.TextColumn("업로드 완료", disabled=True),
            "조회수": st.column_config.NumberColumn("조회수", min_value=0, step=1),
            "좋아요": st.column_config.NumberColumn("좋아요", min_value=0, step=1),
            "댓글": st.column_config.NumberColumn("댓글", min_value=0, step=1),
            "콘텐츠 URL": st.column_config.TextColumn("콘텐츠 URL", help="콘텐츠의 URL"),
            "컨텐츠내용": st.column_config.TextColumn("컨텐츠내용", help="콘텐츠의 캡션 내용"),
            "업로드일": st.column_config.DateColumn("업로드일", help="콘텐츠 업로드 날짜"),
            "릴스여부": st.column_config.SelectboxColumn("릴스여부", options=["일반", "릴스"], help="릴스 여부"),
            "콘텐츠 수": st.column_config.NumberColumn("콘텐츠 수", disabled=True),
        }
        
        st.markdown("#### 📊 성과 데이터 (편집 가능)")
        st.caption("조회수, 좋아요, 댓글 수, 콘텐츠 URL, 컨텐츠내용, 업로드일, 릴스여부를 직접 편집할 수 있습니다. 변경 후 저장 버튼을 클릭하세요.")
        
        # 편집 가능한 데이터 테이블
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            key="performance_data_editor"
        )
        
        # 저장 버튼
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("💾 변경사항 저장", type="primary", key="save_performance_changes"):
                save_performance_changes(df, edited_df, participation_mapping)
        with col2:
            if st.button("🔄 새로고침", key="refresh_performance_data"):
                st.session_state.pop("campaigns_cache", None)
                st.session_state.pop("participations_cache", None)
                st.rerun()
        with col3:
            st.caption("변경사항을 저장하거나 데이터를 새로고침할 수 있습니다.")
            
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




def safe_int_conversion(value, default=0):
    """안전한 정수 변환 함수"""
    try:
        if pd.isna(value) or value is None:
            return default
        
        # 문자열인 경우
        if isinstance(value, str):
            value = value.strip()
            # "false", "true" 같은 문자열 처리
            if value.lower() in ['false', 'true', 'none', 'null', '']:
                return default
            # 숫자 문자열인지 확인
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default
        
        # 숫자형인 경우
        if isinstance(value, (int, float)):
            return int(value)
        
        # 기타 타입
        return default
    except (ValueError, TypeError, AttributeError):
        return default

def safe_rels_conversion(value):
    """안전한 릴스 여부 정수 변환 함수 (0: 일반, 1: 릴스)"""
    try:
        if pd.isna(value) or value is None:
            return 0
        if isinstance(value, str):
            return 1 if value.strip() == "릴스" else 0
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, (int, float)):
            return 1 if value else 0
        return 0
    except (ValueError, TypeError):
        return 0

def save_performance_changes(original_df, edited_df, participation_mapping):
    """성과 데이터 변경사항을 데이터베이스에 저장"""
    try:
        # 변경된 행 찾기
        changes_made = False
        success_count = 0
        error_count = 0
        
        for idx, row in edited_df.iterrows():
            original_row = original_df.iloc[idx]
            
            # 편집 가능한 필드들이 변경되었는지 확인
            if (row['조회수'] != original_row['조회수'] or 
                row['좋아요'] != original_row['좋아요'] or 
                row['댓글'] != original_row['댓글'] or
                row['콘텐츠 URL'] != original_row['콘텐츠 URL'] or
                row['컨텐츠내용'] != original_row['컨텐츠내용'] or
                row['업로드일'] != original_row['업로드일'] or
                row['릴스여부'] != original_row['릴스여부']):
                
                changes_made = True
                participation_id = participation_mapping.get(idx)
                
                if not participation_id:
                    st.error(f"인덱스 {idx}에 대한 참여 ID를 찾을 수 없습니다.")
                    error_count += 1
                    continue
                
                try:
                    # 해당 참여의 모든 콘텐츠 조회
                    content_data = db_manager.get_performance_data_by_participation(participation_id)
                    
                    if not content_data:
                        # 콘텐츠가 없으면 새로 생성
                        new_content_data = {
                            "participation_id": participation_id,
                            "content_url": str(row['콘텐츠 URL']) if pd.notna(row['콘텐츠 URL']) else "",
                            "posted_at": row['업로드일'].isoformat() if pd.notna(row['업로드일']) else datetime.now().isoformat(),
                            "views": safe_int_conversion(row['조회수']),
                            "likes": safe_int_conversion(row['좋아요']),
                            "comments": safe_int_conversion(row['댓글']),
                            "shares": 0,
                            "clicks": 0,
                            "conversions": 0,
                            "caption": str(row['컨텐츠내용']) if pd.notna(row['컨텐츠내용']) else "",
                            "qualitative_note": "",
                            "is_rels": safe_rels_conversion(row['릴스여부']),
                        }
                        result = db_manager.create_campaign_influencer_content(new_content_data)
                        if result.get('success'):
                            success_count += 1
                        else:
                            st.error(f"새 콘텐츠 생성 실패: {result.get('message', '알 수 없는 오류')}")
                            error_count += 1
                    else:
                        # 첫 번째 콘텐츠의 성과 데이터 업데이트
                        first_content = content_data[0]
                        update_data = {
                            "content_url": str(row['콘텐츠 URL']) if pd.notna(row['콘텐츠 URL']) else first_content.get("content_url", ""),
                            "posted_at": row['업로드일'].isoformat() if pd.notna(row['업로드일']) else first_content.get("posted_at", datetime.now().isoformat()),
                            "views": safe_int_conversion(row['조회수']),
                            "likes": safe_int_conversion(row['좋아요']),
                            "comments": safe_int_conversion(row['댓글']),
                            "shares": first_content.get("shares", 0),
                            "clicks": first_content.get("clicks", 0),
                            "conversions": first_content.get("conversions", 0),
                            "caption": str(row['컨텐츠내용']) if pd.notna(row['컨텐츠내용']) else first_content.get("caption", ""),
                            "qualitative_note": first_content.get("qualitative_note", ""),
                            "is_rels": safe_rels_conversion(row['릴스여부']),
                        }
                        result = db_manager.update_campaign_influencer_content(first_content['id'], update_data)
                        if result.get('success'):
                            success_count += 1
                        else:
                            st.error(f"콘텐츠 업데이트 실패: {result.get('message', '알 수 없는 오류')}")
                            error_count += 1
                            
                except Exception as e:
                    st.error(f"인덱스 {idx} 데이터 저장 중 오류: {str(e)}")
                    error_count += 1
        
        if changes_made:
            if success_count > 0:
                st.success(f"✅ {success_count}개의 성과 데이터가 성공적으로 저장되었습니다!")
            if error_count > 0:
                st.error(f"❌ {error_count}개의 데이터 저장에 실패했습니다.")
            
            # 캐시 클리어하여 최신 데이터 반영
            st.session_state.pop("campaigns_cache", None)
            st.session_state.pop("participations_cache", None)
            st.rerun()
        else:
            st.info("변경된 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"❌ 성과 데이터 저장 중 오류가 발생했습니다: {str(e)}")


