"""
인플루언서 검색 및 목록 관련 컴포넌트들
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager
from .common_functions import (
    search_single_influencer, 
    search_single_influencer_by_platform
)

def render_influencer_search_and_filter():
    """인플루언서 검색 및 필터링 (좌측) - 기존 함수 (호환성 유지)"""
    st.subheader("🔍 인플루언서 검색")
    with st.form("search_influencer_form"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            search_platform = st.selectbox(
                "플랫폼",
                ["전체", "instagram", "youtube", "tiktok", "x", "blog", "facebook"],
                key="search_platform_select",
                format_func=lambda x: {
                    "전체": "🌐 전체",
                    "instagram": "📸 Instagram",
                    "youtube": "📺 YouTube",
                    "tiktok": "🎵 TikTok",
                    "x": "🐦 X (Twitter)",
                    "blog": "📝 블로그",
                    "facebook": "👥 Facebook"
                }.get(x, x)
            )
        
        with col2:
            search_term = st.text_input("SNS ID 또는 이름", placeholder="정확한 SNS ID 또는 이름 입력", key="influencer_search_input", help="등록자 검색")
        
        search_clicked = st.form_submit_button("🔍 검색", type="primary")
    
    if search_clicked:
        if not search_term:
            st.error("검색어를 입력해주세요.")
        else:
            # 플랫폼별 단일 인플루언서 검색
            if search_platform == "전체":
                # 전체 플랫폼에서 검색
                search_response = search_single_influencer(search_term)
            else:
                # 특정 플랫폼에서 검색
                search_response = search_single_influencer_by_platform(search_term, search_platform)
            
            if search_response and search_response.get("success") and search_response.get("data"):
                search_data = search_response["data"]
                # search_data가 리스트인 경우 첫 번째 요소를 사용
                if isinstance(search_data, list) and len(search_data) > 0:
                    search_result = search_data[0]
                elif isinstance(search_data, dict):
                    search_result = search_data
                else:
                    search_result = None
                
                if search_result:
                    # 기존 선택된 인플루언서가 있다면 관련 세션 상태 정리
                    if 'selected_influencer' in st.session_state:
                        old_influencer = st.session_state.selected_influencer
                        old_form_key = f"edit_influencer_form_{old_influencer['id']}"
                        
                        # 기존 폼 초기화 플래그 제거
                        if f"{old_form_key}_initialized" in st.session_state:
                            del st.session_state[f"{old_form_key}_initialized"]
                        
                        # 기존 편집 관련 세션 상태 정리
                        for key in list(st.session_state.keys()):
                            if key.startswith(f"edit_") and key.endswith(f"_{old_influencer['id']}"):
                                del st.session_state[key]
                    
                    # 새로운 인플루언서 선택
                    st.session_state.selected_influencer = search_result
                    active_status = "활성" if search_result.get('active', True) else "비활성"
                    st.success(f"✅ 인플루언서를 찾았습니다: {search_result.get('influencer_name') or search_result['sns_id']} ({search_result.get('platform')}) [{active_status}]")
                    st.session_state.search_result_updated = True  # 검색 결과 업데이트 플래그
                    # 리렌더링 없이 상태 기반 UI 업데이트
                else:
                    st.error(f"❌ '{search_term}'을(를) 찾을 수 없습니다.")
            else:
                # 더 자세한 오류 메시지와 도움말 제공
                platform_text = f" ({search_platform})" if search_platform != "전체" else ""
                st.error(f"❌ '{search_term}'{platform_text}를 찾을 수 없습니다.")
                
                # 도움말 및 디버깅 정보 제공
                with st.expander("💡 검색 도움말", expanded=False):
                    st.markdown("""
                    **검색 팁:**
                    - SNS ID를 정확히 입력해주세요 (예: `username` 또는 `@username`)
                    - 플랫폼을 선택하면 해당 플랫폼에서만 검색합니다
                    - "전체"를 선택하면 모든 플랫폼에서 검색합니다
                    - 대소문자는 구분하지 않습니다
                    - 인플루언서 이름으로도 검색할 수 있습니다
                    - 부분 검색도 지원됩니다
                    
                    **문제가 계속되면:**
                    1. 인플루언서가 먼저 등록되어 있는지 확인하세요
                    2. 플랫폼이 올바른지 확인하세요
                    3. SNS ID에 오타가 없는지 확인하세요
                    """)
                
                # 모든 인플루언서 목록 표시
                with st.expander("🔍 모든 인플루언서 목록", expanded=True):
                    try:
                        all_influencers = db_manager.get_influencers()
                        st.write(f"**총 {len(all_influencers)}명의 인플루언서가 등록되어 있습니다:**")
                        
                        # 검색어와 정확히 일치하는 인플루언서 찾기
                        exact_matches = []
                        partial_matches = []
                        clean_search_term = search_term.replace('@', '').strip().lower()
                        
                        for inf in all_influencers:
                            sns_id = inf.get('sns_id', '').lower()
                            name = (inf.get('influencer_name', '') or '').lower()
                            clean_sns_id = sns_id.replace('@', '').strip()
                            
                            # 정확한 매칭
                            if (search_term.lower() == sns_id or 
                                search_term.lower() == name or
                                clean_search_term == clean_sns_id or
                                clean_search_term == name):
                                exact_matches.append(inf)
                            
                            # 부분 매칭
                            elif (clean_search_term in clean_sns_id or 
                                  clean_search_term in name or
                                  search_term.lower() in sns_id or
                                  search_term.lower() in name):
                                partial_matches.append(inf)
                        
                        # 정확한 매칭 결과
                        if exact_matches:
                            st.success(f"**✅ 정확한 매칭 ({len(exact_matches)}명):**")
                            for inf in exact_matches:
                                active_status = "활성" if inf.get('active', True) else "비활성"
                                st.write(f"- {inf.get('sns_id')} ({inf.get('platform')}) - {inf.get('influencer_name') or '이름 없음'} [{active_status}]")
                        
                        # 부분 매칭 결과
                        if partial_matches:
                            st.info(f"**🔍 부분 매칭 ({len(partial_matches)}명):**")
                            for inf in partial_matches[:5]:  # 최대 5명만 표시
                                active_status = "활성" if inf.get('active', True) else "비활성"
                                st.write(f"- {inf.get('sns_id')} ({inf.get('platform')}) - {inf.get('influencer_name') or '이름 없음'} [{active_status}]")
                            if len(partial_matches) > 5:
                                st.write(f"... 외 {len(partial_matches) - 5}명 더")
                        
                        # 매칭이 없으면 전체 목록 표시
                        if not exact_matches and not partial_matches:
                            st.warning("**❌ 검색어와 일치하는 인플루언서가 없습니다.**")
                            
                            # 플랫폼별로 그룹화
                            platform_groups = {}
                            for inf in all_influencers:
                                platform = inf.get('platform', 'unknown')
                                if platform not in platform_groups:
                                    platform_groups[platform] = []
                                platform_groups[platform].append(inf)
                            
                            st.write("**전체 인플루언서 목록:**")
                            for platform, influencers in platform_groups.items():
                                st.write(f"**{platform.upper()} ({len(influencers)}명):**")
                                for inf in influencers[:10]:  # 각 플랫폼당 최대 10명 표시
                                    active_status = "활성" if inf.get('active', True) else "비활성"
                                    st.write(f"- {inf.get('sns_id')} ({inf.get('influencer_name') or '이름 없음'}) [{active_status}]")
                                if len(influencers) > 10:
                                    st.write(f"... 외 {len(influencers) - 10}명 더")
                                st.write("")
                            
                    except Exception as e:
                        st.error(f"인플루언서 목록 조회 중 오류: {e}")
                        import traceback
                        st.code(traceback.format_exc())
    
    # 필터링 기능
    st.markdown("### 🎯 필터링")
    
    # 플랫폼 필터
    platform_filter = st.selectbox(
        "플랫폼",
        ["전체", "instagram", "youtube", "tiktok", "x", "blog", "facebook"],
        key="influencer_platform_filter",
        format_func=lambda x: {
            "전체": "🌐 전체",
            "instagram": "📸 Instagram",
            "youtube": "📺 YouTube",
            "tiktok": "🎵 TikTok",
            "x": "🐦 X (Twitter)",
            "blog": "📝 블로그",
            "facebook": "👥 Facebook"
        }[x]
    )
    
    # 콘텐츠 카테고리 필터
    content_category_filter = st.selectbox(
        "콘텐츠 카테고리",
        ["전체", "일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"],
        key="influencer_content_category_filter",
        format_func=lambda x: {
            "전체": "📂 전체",
            "일반": "📝 일반",
            "뷰티": "💄 뷰티",
            "패션": "👗 패션",
            "푸드": "🍽️ 푸드",
            "여행": "✈️ 여행",
            "라이프스타일": "🏠 라이프스타일",
            "테크": "💻 테크",
            "게임": "🎮 게임",
            "스포츠": "⚽ 스포츠",
            "애견": "🐕 애견",
            "기타": "🔧 기타"
        }[x]
    )
    
    # 팔로워 수 필터
    col1, col2 = st.columns(2)
    with col1:
        min_followers = st.number_input("최소 팔로워 수", min_value=0, value=0, key="min_followers")
    with col2:
        max_followers = st.number_input("최대 팔로워 수", min_value=0, value=10000000, key="max_followers")
    
    # 필터 적용 버튼
    if st.button("🔄 필터 적용", help="선택한 필터 조건으로 인플루언서를 조회합니다", key="apply_filter"):
        # 필터 조건을 세션에 저장
        st.session_state.filter_conditions = {
            "platform": platform_filter if platform_filter != "전체" else None,
            "content_category": content_category_filter if content_category_filter != "전체" else None,
            "min_followers": min_followers,
            "max_followers": max_followers
        }
        # 페이지 초기화
        st.session_state.influencer_current_page = 0
        # 필터링된 데이터 캐시 초기화
        for key in list(st.session_state.keys()):
            if key.startswith("filtered_influencers_"):
                del st.session_state[key]
        st.success("필터가 적용되었습니다!")
        st.session_state.filter_applied = True  # 필터 적용 완료 플래그
        # 리렌더링 없이 상태 기반 UI 업데이트
    
    # 인플루언서 목록 표시 (페이징)
    render_influencer_list_with_pagination()

def render_influencer_list_with_pagination():
    """페이징이 적용된 인플루언서 목록 표시"""
    st.markdown("### 📊 인플루언서 목록")
    
    # 필터 조건 확인
    filter_conditions = st.session_state.get('filter_conditions', {})
    
    if not filter_conditions:
        st.info("필터 조건을 설정하고 '필터 적용' 버튼을 클릭해주세요.")
        return
    
    # 필터링된 인플루언서 조회
    cache_key = f"filtered_influencers_{hash(str(filter_conditions))}"
    
    if cache_key not in st.session_state:
        with st.spinner("필터링된 인플루언서를 불러오는 중..."):
            all_influencers = db_manager.get_influencers()
            
            # 필터링 적용
            filtered_influencers = all_influencers.copy()
            
            # 플랫폼 필터
            if filter_conditions.get("platform"):
                filtered_influencers = [inf for inf in filtered_influencers if inf['platform'] == filter_conditions["platform"]]
            
            # 콘텐츠 카테고리 필터 (LIKE 검색)
            if filter_conditions.get("content_category"):
                content_category = filter_conditions["content_category"]
                filtered_influencers = [
                    inf for inf in filtered_influencers 
                    if inf.get('content_category') and content_category.lower() in inf.get('content_category', '').lower()
                ]
            
            # 팔로워 수 필터
            min_followers = filter_conditions.get("min_followers", 0)
            max_followers = filter_conditions.get("max_followers", 10000000)
            filtered_influencers = [
                inf for inf in filtered_influencers 
                if min_followers <= inf.get('followers_count', 0) <= max_followers
            ]
            
            st.session_state[cache_key] = filtered_influencers
    
    filtered_influencers = st.session_state[cache_key]
    
    # 페이징 설정
    items_per_page = 10
    total_pages = (len(filtered_influencers) - 1) // items_per_page + 1
    current_page = st.session_state.get('influencer_current_page', 0)
    
    # 페이지 선택
    if total_pages > 1:
        page_options = list(range(total_pages))
        selected_page = st.selectbox(
            f"페이지 선택 (총 {total_pages}페이지, {len(filtered_influencers)}명)",
            page_options,
            index=current_page,
            key="page_selector"
        )
        
        if selected_page != current_page:
            st.session_state.influencer_current_page = selected_page
            st.session_state.page_changed = True  # 페이지 변경 플래그
            # 리렌더링 없이 상태 기반 UI 업데이트
    
    # 현재 페이지의 인플루언서 표시
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_influencers))
    page_influencers = filtered_influencers[start_idx:end_idx]
    
    st.caption(f"페이지 {current_page + 1}/{total_pages} (총 {len(filtered_influencers)}명)")
    
    if page_influencers:
        # 인플루언서 목록 표시
        for i, influencer in enumerate(page_influencers):
            with st.container():
                # 인플루언서 정보를 잘 조합해서 표시
                render_influencer_list_item(influencer, i)
                st.divider()
    else:
        st.info("해당 조건에 맞는 인플루언서가 없습니다.")

def render_influencer_list_item(influencer, index):
    """인플루언서 리스트 아이템 표시"""
    # 인플루언서 정보 조합 표시 (이미지 제거로 2컬럼으로 변경)
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # SNS ID와 팔로워 수
        st.markdown(f"**SNS ID:** `{influencer['sns_id']}`")
        st.caption(f"👥 팔로워: {influencer.get('followers_count', 0):,}명")
        
        # SNS URL - 링크로 표시
        if influencer.get('sns_url'):
            sns_url = influencer['sns_url']
            st.caption(f"🔗 URL: [{sns_url}]({sns_url})")
        
        # Owner Comment (있는 경우) - 안전한 텍스트 표시
        if influencer.get('owner_comment'):
            try:
                safe_comment = str(influencer['owner_comment'])
                st.caption(f"💬 코멘트: {safe_comment}")
            except:
                st.caption("💬 코멘트: [텍스트 표시 오류]")
        
        # 프로필 텍스트 (간단히) - 안전한 텍스트 표시
        if influencer.get('profile_text'):
            try:
                safe_profile_text = str(influencer['profile_text'])
                profile_text = safe_profile_text[:100] + "..." if len(safe_profile_text) > 100 else safe_profile_text
                st.caption(f"📝 프로필: {profile_text}")
            except:
                st.caption("📝 프로필: [텍스트 표시 오류]")
    
    with col2:
        # 현재 선택된 인플루언서인지 확인
        is_selected = (st.session_state.get('selected_influencer', {}).get('id') == influencer['id'])
        
        # 선택 버튼 (editor 아이콘) - 선택된 경우 primary 타입으로 표시
        button_type = "primary" if is_selected else "secondary"
        if st.button("📝", key=f"select_{influencer['id']}_{index}", help="상세보기", type=button_type):
            # 기존 선택된 인플루언서가 있다면 관련 세션 상태 정리
            if 'selected_influencer' in st.session_state:
                old_influencer = st.session_state.selected_influencer
                old_form_key = f"edit_influencer_form_{old_influencer['id']}"
                
                # 기존 폼 초기화 플래그 제거
                if f"{old_form_key}_initialized" in st.session_state:
                    del st.session_state[f"{old_form_key}_initialized"]
                
                # 기존 편집 관련 세션 상태 정리
                for key in list(st.session_state.keys()):
                    if key.startswith(f"edit_") and key.endswith(f"_{old_influencer['id']}"):
                        del st.session_state[key]
            
            # 새로운 인플루언서 선택
            st.session_state.selected_influencer = influencer
            st.session_state.influencer_selected = True  # 인플루언서 선택 플래그
            # 리렌더링 없이 상태 기반 UI 업데이트
        
        # 편집 버튼
        if st.button("✏️", key=f"edit_{influencer['id']}_{index}", help="편집"):
            st.session_state.editing_influencer = influencer
            st.session_state.editing_mode_activated = True  # 편집 모드 활성화 플래그
            # 리렌더링 없이 상태 기반 UI 업데이트
        
        # 삭제 버튼
        if st.button("🗑️", key=f"delete_inf_{influencer['id']}_{index}", help="삭제"):
            result = db_manager.delete_influencer(influencer['id'])
            if result["success"]:
                st.success("인플루언서가 삭제되었습니다!")
                # 선택된 인플루언서가 삭제된 경우 선택 해제
                if is_selected:
                    del st.session_state.selected_influencer
                    
                    # 폼 초기화 플래그 제거
                    form_key = f"edit_influencer_form_{influencer['id']}"
                    if f"{form_key}_initialized" in st.session_state:
                        del st.session_state[f"{form_key}_initialized"]
                    
                    # 모든 편집 관련 세션 상태 정리
                    for key in list(st.session_state.keys()):
                        if key.startswith(f"edit_") and key.endswith(f"_{influencer['id']}"):
                            del st.session_state[key]
                
                # 캐시 초기화
                for key in list(st.session_state.keys()):
                    if key.startswith("filtered_influencers_"):
                        del st.session_state[key]
                st.session_state.influencer_deleted_from_search = True  # 검색에서 인플루언서 삭제 완료 플래그
                # 리렌더링 없이 상태 기반 UI 업데이트
            else:
                st.error(f"삭제 실패: {result['message']}")

