"""
인플루언서 관리 관련 컴포넌트들
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager
from ..db.models import Influencer
from .common_functions import (
    search_single_influencer, 
    search_single_influencer_by_platform
)
# 통계 기능은 별도 메뉴로 분리됨

def render_influencer_management():
    """인플루언서 관리 메인 컴포넌트"""
    st.subheader("👥 인플루언서 관리")
    st.markdown("인플루언서 등록과 수정, 조회 기능을 제공합니다.")
    
    # 탭 간 이동 처리 (담당자별 관리에서는 수정 기능이 없으므로 제거)
    
    # 등록, 조회, 담당자별 관리 탭으로 분리 (통계는 별도 메뉴로 분리)
    tab_names = ["📝 인플루언서 등록", "📋 인플루언서 정보 수정", "👥 담당자별 인플루언서 관리"]
    
    # 기본 탭 인덱스 설정
    default_tab = st.session_state.get("influencer_active_tab", 0)
    
    # 탭 생성
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_influencer_registration()
    
    with tabs[1]:
        render_influencer_inquiry()
    
    with tabs[2]:
        render_manager_influencer_management()

def render_influencer_registration():
    """인플루언서 등록 탭"""
    st.subheader("📝 인플루언서 등록")
    st.markdown("새로운 인플루언서를 검색하고 등록합니다.")
    
    # 두 컬럼으로 분할
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_influencer_search_for_registration()
    
    with col2:
        render_influencer_registration_form()

def render_influencer_search_for_registration():
    """인플루언서 검색 (중복체크) - 좌측 아래"""
    st.markdown("### 🔍 인플루언서 검색 (중복체크)")
    
    with st.form("search_influencer_for_registration"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            search_platform = st.selectbox(
                "플랫폼",
                ["전체", "instagram", "youtube", "tiktok", "twitter"],
                key="registration_search_platform",
                format_func=lambda x: {
                    "전체": "🌐 전체",
                    "instagram": "📸 Instagram",
                    "youtube": "📺 YouTube",
                    "tiktok": "🎵 TikTok",
                    "twitter": "🐦 Twitter"
                }[x]
            )
        
        with col2:
            search_term = st.text_input("SNS ID 또는 이름", placeholder="정확한 SNS ID 또는 이름 입력", key="registration_search_input", help="등록자 검색")
        
        search_clicked = st.form_submit_button("🔍 검색", type="primary")
    
    if search_clicked:
        if not search_term:
            st.error("검색어를 입력해주세요.")
        else:
            # 플랫폼별 단일 인플루언서 검색
            if search_platform == "전체":
                search_response = search_single_influencer(search_term)
            else:
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
                    # 검색 결과를 세션에 저장
                    st.session_state.registration_search_result = search_result
                    active_status = "활성" if search_result.get('active', True) else "비활성"
                    st.warning(f"⚠️ 이미 등록된 인플루언서입니다: {search_result.get('influencer_name') or search_result['sns_id']} ({search_result.get('platform')}) [{active_status}]")
                
                    # 검색된 인플루언서 정보 표시
                    with st.expander("📋 검색된 인플루언서 정보", expanded=True):
                        st.markdown(f"**SNS ID:** {search_result['sns_id']}")
                        st.markdown(f"**이름:** {search_result.get('influencer_name', 'N/A')}")
                        st.markdown(f"**플랫폼:** {search_result['platform']}")
                        st.markdown(f"**카테고리:** {search_result.get('content_category', 'N/A')}")
                        st.markdown(f"**팔로워 수:** {search_result.get('followers_count', 'N/A'):,}" if search_result.get('followers_count') else "**팔로워 수:** N/A")
                        st.markdown(f"**등록일:** {search_result.get('created_at', 'N/A')}")
                        if search_result.get('sns_url'):
                            st.markdown(f"**SNS URL:** [{search_result['sns_url']}]({search_result['sns_url']})")
                else:
                    # 검색 결과가 없으면 등록 가능
                    st.session_state.registration_search_result = None
                    st.success(f"✅ '{search_term}'은(는) 등록되지 않은 인플루언서입니다. 등록이 가능합니다.")
                    
                    # 등록 가능한 인플루언서 정보 표시
                    with st.expander("📝 등록 가능한 인플루언서", expanded=True):
                        st.info(f"**SNS ID:** {search_term}")
                        st.info(f"**플랫폼:** {search_platform if search_platform != '전체' else '선택 필요'}")
                        st.info("**상태:** 등록 가능 ✅")
            else:
                # 검색 결과가 없으면 등록 가능
                st.session_state.registration_search_result = None
                st.success(f"✅ '{search_term}'은(는) 등록되지 않은 인플루언서입니다. 등록이 가능합니다.")
                
                # 등록 가능한 인플루언서 정보 표시
                with st.expander("📝 등록 가능한 인플루언서", expanded=True):
                    st.info(f"**SNS ID:** {search_term}")
                    st.info(f"**플랫폼:** {search_platform if search_platform != '전체' else '선택 필요'}")
                    st.info("**상태:** 등록 가능 ✅")

def render_influencer_registration_form():
    """인플루언서 등록 폼 (우측)"""
    st.markdown("### 📝 인플루언서 등록")
    
    with st.form("create_influencer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            platform = st.selectbox(
                "플랫폼",
                ["instagram", "youtube", "tiktok", "twitter"],
                key="create_influencer_platform",
                format_func=lambda x: {
                    "instagram": "📸 Instagram",
                    "youtube": "📺 YouTube",
                    "tiktok": "🎵 TikTok",
                    "twitter": "🐦 Twitter"
                }[x]
            )
            sns_id = st.text_input("SNS ID", placeholder="@username 또는 username")
        
        with col2:
            influencer_name = st.text_input("별칭", placeholder="인플루언서의 별칭")
            sns_url = st.text_input("SNS URL", placeholder="https://...")
        
        # 팔로워 수 필드 추가
        followers_count = st.number_input(
            "팔로워 수", 
            min_value=0, 
            value=0,
            step=1000,
            help="인플루언서의 팔로워 수를 입력하세요"
        )
        
        # 등록자 필드 추가
        created_by = st.text_input(
            "등록자", 
            placeholder="등록자 이름 또는 ID를 입력하세요",
            help="홍길동"
        )
        
        # Owner Comment와 Content Category 추가
        owner_comment = st.text_area("Owner Comment", placeholder="인플루언서에 대한 담당자 코멘트")
        
        content_category = st.selectbox(
            "카테고리",
            ["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"],
            key="create_influencer_category",
            format_func=lambda x: {
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
        
        if st.form_submit_button("인플루언서 등록", type="primary"):
            if not sns_id:
                st.error("SNS ID를 입력해주세요.")
            elif not sns_url:
                st.error("SNS URL을 입력해주세요.")
            else:
                # 별칭이 비어있으면 SNS ID를 사용
                final_influencer_name = influencer_name.strip() if influencer_name else sns_id
                
                influencer = Influencer(
                    platform=platform,
                    sns_id=sns_id,
                    influencer_name=final_influencer_name,
                    sns_url=sns_url,
                    owner_comment=owner_comment,
                    content_category=content_category,
                    followers_count=followers_count,
                    created_by=created_by if created_by.strip() else None
                )
                
                result = db_manager.create_influencer(influencer)
                if result["success"]:
                    st.success("인플루언서가 등록되었습니다!")
                    # 캐시 초기화
                    if "influencers_data" in st.session_state:
                        del st.session_state["influencers_data"]
                    # 검색 결과 초기화
                    if "registration_search_result" in st.session_state:
                        del st.session_state["registration_search_result"]
                    st.rerun()
                else:
                    st.error(f"인플루언서 등록 실패: {result['message']}")

def render_influencer_inquiry():
    """인플루언서 정보 관리 탭"""
    st.subheader("📋 인플루언서 정보 관리")
    st.markdown("등록된 인플루언서를 검색하고 상세 정보를 조회/수정합니다.")
    
    # 두 컬럼으로 분할
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_influencer_search_for_inquiry()
    
    with col2:
        render_influencer_detail_view()

def render_influencer_search_for_inquiry():
    """인플루언서 검색 (조회용) - 좌측"""
    st.markdown("### 🔍 인플루언서 검색")
    
    with st.form("search_influencer_for_inquiry"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            search_platform = st.selectbox(
                "플랫폼",
                ["전체", "instagram", "youtube", "tiktok", "twitter"],
                key="inquiry_search_platform",
                format_func=lambda x: {
                    "전체": "🌐 전체",
                    "instagram": "📸 Instagram",
                    "youtube": "📺 YouTube",
                    "tiktok": "🎵 TikTok",
                    "twitter": "🐦 Twitter"
                }[x]
            )
        
        with col2:
            search_term = st.text_input("SNS ID 또는 이름", placeholder="정확한 SNS ID 또는 이름 입력", key="inquiry_search_input", help="등록자 검색")
        
        search_clicked = st.form_submit_button("🔍 검색", type="primary")
    
    if search_clicked:
        if not search_term:
            st.error("검색어를 입력해주세요.")
        else:
            # 플랫폼별 단일 인플루언서 검색
            if search_platform == "전체":
                search_response = search_single_influencer(search_term)
            else:
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
                    
                    # 검색 결과를 좌측에 표시
                    render_influencer_search_result(search_result)
                    st.rerun()
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

def render_influencer_search_result(influencer):
    """검색된 인플루언서 결과를 좌측에 표시"""
    st.markdown("### 📋 검색된 인플루언서 정보")
    
    # 기본 정보 표시
    col1, col2 = st.columns(2)
    with col1:
        # 플랫폼 아이콘화
        platform_icons = {
            "instagram": "📸 Instagram",
            "youtube": "📺 YouTube", 
            "tiktok": "🎵 TikTok",
            "twitter": "🐦 Twitter"
        }
        platform_display = platform_icons.get(influencer['platform'], f"🌐 {influencer['platform']}")
        st.metric("플랫폼", platform_display)
    with col2:
        st.metric("SNS ID", influencer['sns_id'])
    
    # 상세 정보 표시
    st.markdown("#### 📊 기본 정보")
    st.markdown(f"**이름:** {influencer.get('influencer_name', 'N/A')}")
    st.markdown(f"**카테고리:** {influencer.get('content_category', 'N/A')}")
    st.markdown(f"**팔로워 수:** {influencer.get('followers_count', 'N/A'):,}" if influencer.get('followers_count') else "**팔로워 수:** N/A")
    st.markdown(f"**게시물 수:** {influencer.get('post_count', 'N/A'):,}" if influencer.get('post_count') else "**게시물 수:** N/A")
    
    # SNS URL 표시
    sns_url = influencer.get('sns_url', 'N/A')
    if sns_url and sns_url != 'N/A':
        st.markdown(f"**🔗 SNS URL:** [{sns_url}]({sns_url})")
    else:
        st.markdown(f"**🔗 SNS URL:** {sns_url}")
    
    # Owner Comment 표시
    owner_comment = influencer.get('owner_comment', 'N/A')
    st.markdown("**💬 Owner Comment:**")
    try:
        safe_owner_comment = str(owner_comment) if owner_comment else 'N/A'
        st.text_area("Owner Comment", value=safe_owner_comment, height=80, disabled=True, key=f"search_result_owner_comment_{influencer['id']}", label_visibility="collapsed")
    except Exception as e:
        st.text_area("Owner Comment", value="[텍스트 표시 오류]", height=80, disabled=True, key=f"search_result_owner_comment_{influencer['id']}", label_visibility="collapsed")
    
    # 추가 정보 표시
    st.markdown("#### 📈 성과 정보")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("매니저 평점", f"{influencer.get('manager_rating', 'N/A')}/5" if influencer.get('manager_rating') else "N/A")
    with col2:
        st.metric("콘텐츠 평점", f"{influencer.get('content_rating', 'N/A')}/5" if influencer.get('content_rating') else "N/A")
    
    # 가격 정보
    price_krw = influencer.get('price_krw')
    if price_krw:
        st.markdown(f"**💰 가격:** {price_krw:,}원")
    else:
        st.markdown("**💰 가격:** N/A")
    
    # 상태 정보
    active_status = "활성" if influencer.get('active', True) else "비활성"
    status_color = "🟢" if influencer.get('active', True) else "🔴"
    st.markdown(f"**{status_color} 상태:** {active_status}")
    
    # 등록/수정 일시
    st.markdown("#### 📅 일시 정보")
    created_at = influencer.get('created_at', 'N/A')
    updated_at = influencer.get('updated_at', 'N/A')
    created_by = influencer.get('created_by', 'N/A')
    st.markdown(f"**등록일:** {created_at}")
    st.markdown(f"**등록자:** {created_by}")
    st.markdown(f"**수정일:** {updated_at}")

def render_influencer_detail_view():
    """인플루언서 정보 수정 폼 (우측)"""
    st.subheader("✏️ 인플루언서 정보 수정")
    
    # 선택된 인플루언서가 있는지 확인
    if 'selected_influencer' in st.session_state:
        influencer = st.session_state.selected_influencer
        render_influencer_edit_form(influencer)
    else:
        st.info("좌측에서 인플루언서를 검색하여 선택해주세요.")
        st.markdown("---")
        st.markdown("### 💡 사용 방법")
        st.markdown("1. 좌측에서 인플루언서를 검색하세요")
        st.markdown("2. 검색 결과가 좌측에 표시됩니다")
        st.markdown("3. 우측에 수정 폼이 나타납니다")
        st.markdown("4. 필요한 정보를 수정하고 저장하세요")

def render_influencer_edit_form(influencer):
    """인플루언서 정보 수정 폼"""
    st.markdown(f"**수정 대상:** {influencer.get('influencer_name') or influencer['sns_id']} ({influencer.get('platform')})")
    st.markdown("---")
    
    # 편집 폼
    with st.form(f"edit_influencer_form_{influencer['id']}"):
        # 기본 정보 섹션
        st.markdown("#### 📝 기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            platform_options = ["instagram", "youtube", "tiktok", "twitter"]
            current_platform = influencer.get('platform', 'instagram')
            try:
                platform_index = platform_options.index(current_platform)
            except ValueError:
                # 매칭되지 않으면 기본값 사용
                platform_index = 0
            
            platform = st.selectbox(
                "플랫폼",
                platform_options,
                index=platform_index,
                key=f"edit_platform_{influencer['id']}",
                format_func=lambda x: {
                    "instagram": "📸 Instagram",
                    "youtube": "📺 YouTube",
                    "tiktok": "🎵 TikTok",
                    "twitter": "🐦 Twitter"
                }[x]
            )
            sns_id = st.text_input("SNS ID", value=influencer.get('sns_id', ''), key=f"edit_sns_id_{influencer['id']}")
        
        with col2:
            influencer_name = st.text_input("별칭", value=influencer.get('influencer_name', ''), key=f"edit_name_{influencer['id']}")
            sns_url = st.text_input("SNS URL", value=influencer.get('sns_url', ''), key=f"edit_url_{influencer['id']}")
        
        # 카테고리와 Owner Comment
        category_options = ["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"]
        current_category = influencer.get('content_category', '일반')
        try:
            category_index = category_options.index(current_category)
        except ValueError:
            # 매칭되지 않으면 기본값 사용
            category_index = 0
        
        content_category = st.selectbox(
            "카테고리",
            category_options,
            index=category_index,
            key=f"edit_category_{influencer['id']}",
            format_func=lambda x: {
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
        
        owner_comment = st.text_area(
            "Owner Comment", 
            value=influencer.get('owner_comment', ''), 
            key=f"edit_owner_comment_{influencer['id']}"
        )
        
        # 통계 정보 섹션
        st.markdown("#### 📊 통계 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            followers_count = st.number_input(
                "팔로워 수", 
                min_value=0, 
                value=influencer.get('followers_count', 0) or 0,
                key=f"edit_followers_{influencer['id']}"
            )
            post_count = st.number_input(
                "게시물 수", 
                min_value=0, 
                value=influencer.get('post_count', 0) or 0,
                key=f"edit_posts_{influencer['id']}"
            )
            # 등록자 필드 추가
            created_by = st.text_input(
                "등록자", 
                value=influencer.get('created_by', ''),
                key=f"edit_created_by_{influencer['id']}",
                help="이 인플루언서를 등록한 담당자 정보"
            )
        
        with col2:
            price_krw = st.number_input(
                "가격 (원)", 
                min_value=0, 
                value=influencer.get('price_krw', 0) or 0,
                key=f"edit_price_{influencer['id']}"
            )
            active = st.checkbox(
                "활성 상태", 
                value=influencer.get('active', True),
                key=f"edit_active_{influencer['id']}"
            )
        
        # 평점 정보
        st.markdown("#### ⭐ 평점 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            manager_rating = st.slider(
                "매니저 평점", 
                min_value=1, 
                max_value=5, 
                value=influencer.get('manager_rating', 3) or 3,
                key=f"edit_manager_rating_{influencer['id']}"
            )
        
        with col2:
            content_rating = st.slider(
                "콘텐츠 평점", 
                min_value=1, 
                max_value=5, 
                value=influencer.get('content_rating', 3) or 3,
                key=f"edit_content_rating_{influencer['id']}"
            )
        
        # 연락처 정보
        st.markdown("#### 📞 연락처 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            phone_number = st.text_input(
                "전화번호", 
                value=influencer.get('phone_number', ''),
                key=f"edit_phone_{influencer['id']}"
            )
            # 데이터베이스 enum 값과 매핑
            contact_method_mapping = {
                'dm': 'DM',
                'email': '이메일', 
                'phone': '전화',
                'kakao': '카카오톡',
                'form': '폼',
                'other': '기타'
            }
            contact_method_options = list(contact_method_mapping.values())
            contact_method_db_values = list(contact_method_mapping.keys())
            
            current_contact_method = influencer.get('contact_method', 'dm')
            try:
                contact_method_index = contact_method_db_values.index(current_contact_method)
            except ValueError:
                # 매칭되지 않으면 기본값 사용
                contact_method_index = 0
            
            contact_method = st.selectbox(
                "연락 방법",
                contact_method_options,
                index=contact_method_index,
                key=f"edit_contact_method_{influencer['id']}"
            )
        
        with col2:
            # 데이터베이스 enum 값과 매핑
            preferred_mode_mapping = {
                'seeding': '협찬',
                'promotion': '홍보',
                'sales': '판매'
            }
            preferred_mode_options = list(preferred_mode_mapping.values())
            preferred_mode_db_values = list(preferred_mode_mapping.keys())
            
            current_preferred_mode = influencer.get('preferred_mode', 'seeding')
            try:
                preferred_mode_index = preferred_mode_db_values.index(current_preferred_mode)
            except ValueError:
                # 매칭되지 않으면 기본값 사용
                preferred_mode_index = 0
            
            preferred_mode = st.selectbox(
                "선호 모드",
                preferred_mode_options,
                index=preferred_mode_index,
                key=f"edit_preferred_mode_{influencer['id']}"
            )
        
        shipping_address = st.text_area(
            "배송 주소", 
            value=influencer.get('shipping_address', ''),
            key=f"edit_shipping_{influencer['id']}"
        )
        
        # 태그 정보
        tags = st.text_input(
            "태그 (쉼표로 구분)", 
            value=influencer.get('tags', ''),
            key=f"edit_tags_{influencer['id']}"
        )
        
        # 버튼
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 저장", type="primary"):
                # 데이터 수집 및 검증
                if not sns_id:
                    st.error("SNS ID를 입력해주세요.")
                elif not sns_url:
                    st.error("SNS URL을 입력해주세요.")
                else:
                    # 선택된 값들을 데이터베이스 값으로 변환
                    selected_contact_method_db = contact_method_db_values[contact_method_options.index(contact_method)]
                    selected_preferred_mode_db = preferred_mode_db_values[preferred_mode_options.index(preferred_mode)]
                    
                    # 업데이트할 데이터 준비
                    update_data = {
                        'platform': platform,
                        'sns_id': sns_id,
                        'influencer_name': influencer_name or sns_id,
                        'sns_url': sns_url,
                        'content_category': content_category,
                        'owner_comment': owner_comment,
                        'followers_count': followers_count,
                        'post_count': post_count,
                        'price_krw': price_krw,
                        'active': active,
                        'manager_rating': manager_rating,
                        'content_rating': content_rating,
                        'phone_number': phone_number,
                        'contact_method': selected_contact_method_db,
                        'preferred_mode': selected_preferred_mode_db,
                        'shipping_address': shipping_address,
                        'tags': tags,
                        'created_by': created_by if created_by.strip() else None
                    }
                    
                    # 데이터베이스 업데이트
                    result = db_manager.update_influencer(influencer['id'], update_data)
                    if result["success"]:
                        st.success("인플루언서 정보가 업데이트되었습니다!")
                        # 세션 상태 업데이트
                        st.session_state.selected_influencer.update(update_data)
                        # 캐시 초기화
                        if "influencers_data" in st.session_state:
                            del st.session_state["influencers_data"]
                        st.rerun()
                    else:
                        st.error(f"업데이트 실패: {result['message']}")
        
        with col2:
            if st.form_submit_button("🗑️ 삭제", type="secondary"):
                # 삭제 확인
                st.session_state[f"confirm_delete_{influencer['id']}"] = True
                st.rerun()
        
        with col3:
            if st.form_submit_button("🔄 새로고침"):
                # 세션 상태 초기화
                if 'selected_influencer' in st.session_state:
                    del st.session_state.selected_influencer
                st.rerun()
    
    # 삭제 확인 다이얼로그
    if st.session_state.get(f"confirm_delete_{influencer['id']}", False):
        st.warning("⚠️ 정말로 이 인플루언서를 삭제하시겠습니까?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 삭제 확인", type="primary"):
                result = db_manager.delete_influencer(influencer['id'])
                if result["success"]:
                    st.success("인플루언서가 삭제되었습니다!")
                    # 세션 상태 정리
                    del st.session_state.selected_influencer
                    del st.session_state[f"confirm_delete_{influencer['id']}"]
                    # 캐시 초기화
                    if "influencers_data" in st.session_state:
                        del st.session_state["influencers_data"]
                    st.rerun()
                else:
                    st.error(f"삭제 실패: {result['message']}")
        with col2:
            if st.button("❌ 취소"):
                del st.session_state[f"confirm_delete_{influencer['id']}"]
                st.rerun()

def render_manager_influencer_management():
    """담당자별 인플루언서 관리 탭"""
    st.subheader("👥 담당자별 인플루언서 관리")
    st.markdown("담당자별로 인플루언서를 필터링하고 조회합니다.")
    
    # 모든 인플루언서에서 담당자 목록 가져오기
    try:
        all_influencers = db_manager.get_influencers()
        
        # 담당자 목록 추출 (중복 제거)
        managers = set()
        for influencer in all_influencers:
            created_by = influencer.get('created_by')
            if created_by and created_by.strip():
                managers.add(created_by.strip())
        
        managers = sorted(list(managers))
        
        if not managers:
            st.warning("등록된 담당자가 없습니다.")
            return
        
        # 필터링 조건
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            selected_manager = st.selectbox(
                "담당자 선택",
                ["전체"] + managers,
                key="manager_filter_select",
                format_func=lambda x: f"👤 {x}" if x != "전체" else "🌐 전체 담당자"
            )
        
        with col2:
            # 등록날짜 필터링 조건 추가 - 달력 기반
            st.markdown("**📅 등록날짜 필터**")
            
            # 날짜 범위 선택 방식
            date_filter_type = st.radio(
                "날짜 필터 방식",
                ["전체", "기간 선택", "특정일"],
                key="date_filter_type",
                horizontal=True,
                format_func=lambda x: {
                    "전체": "🌐 전체",
                    "기간 선택": "📅 기간",
                    "특정일": "📆 특정일"
                }[x]
            )
            
            # 날짜 필터링 로직을 위한 변수 초기화
            date_filter = "전체"
            start_date = None
            end_date = None
            specific_date = None
            
            if date_filter_type == "기간 선택":
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date = st.date_input(
                        "시작일",
                        value=None,
                        key="date_filter_start"
                    )
                with col_end:
                    end_date = st.date_input(
                        "종료일", 
                        value=None,
                        key="date_filter_end"
                    )
                
                if start_date and end_date:
                    if start_date <= end_date:
                        date_filter = "기간"
                    else:
                        st.error("시작일은 종료일보다 이전이어야 합니다.")
                        date_filter = "전체"
                elif start_date or end_date:
                    st.warning("시작일과 종료일을 모두 선택해주세요.")
                    date_filter = "전체"
                    
            elif date_filter_type == "특정일":
                specific_date = st.date_input(
                    "선택일",
                    value=None,
                    key="date_filter_specific"
                )
                if specific_date:
                    date_filter = "특정일"
        
        with col3:
            if st.button("🔄 새로고침", key="manager_refresh"):
                # 캐시 초기화
                if "manager_filtered_influencers" in st.session_state:
                    del st.session_state["manager_filtered_influencers"]
                st.rerun()
        
        # 담당자 필터링
        if selected_manager == "전체":
            filtered_influencers = all_influencers
        else:
            filtered_influencers = [
                inf for inf in all_influencers 
                if inf.get('created_by') and inf.get('created_by').strip() == selected_manager
            ]
        
        # 등록날짜 필터링 - 달력 기반
        if date_filter != "전체":
            from datetime import datetime, timedelta
            import pandas as pd
            
            # 날짜 필터링 적용
            date_filtered_influencers = []
            for inf in filtered_influencers:
                created_at = inf.get('created_at')
                if created_at:
                    try:
                        # 날짜 파싱
                        if isinstance(created_at, str):
                            # ISO 형식 날짜 파싱
                            if 'T' in created_at:
                                inf_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                inf_date = datetime.strptime(created_at, '%Y-%m-%d')
                        else:
                            inf_date = created_at
                        
                        # 날짜를 date 객체로 변환 (시간 정보 제거)
                        inf_date_only = inf_date.date()
                        
                        # 필터링 조건에 따라 비교
                        include_influencer = False
                        
                        if date_filter == "기간" and start_date and end_date:
                            # 기간 선택: 시작일과 종료일 사이
                            include_influencer = start_date <= inf_date_only <= end_date
                            
                        elif date_filter == "특정일" and specific_date:
                            # 특정일: 정확히 해당 날짜
                            include_influencer = inf_date_only == specific_date
                        
                        if include_influencer:
                            date_filtered_influencers.append(inf)
                            
                    except Exception as e:
                        # 날짜 파싱 실패시 포함하지 않음
                        continue
            
            filtered_influencers = date_filtered_influencers
        
        # 결과 표시
        if selected_manager == "전체":
            manager_text = "전체 담당자"
        else:
            manager_text = f"{selected_manager} 담당자"
        
        # 날짜 필터 정보 추가
        date_info = ""
        if date_filter == "기간" and start_date and end_date:
            date_info = f" (등록일: {start_date} ~ {end_date})"
        elif date_filter == "특정일" and specific_date:
            date_info = f" (등록일: {specific_date})"
        
        st.info(f"📊 {manager_text}의 인플루언서: {len(filtered_influencers)}명{date_info}")
        
        # 최근 등록순으로 정렬 (created_at 기준)
        filtered_influencers.sort(
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        # 필터링된 인플루언서 리스트 표시
        if filtered_influencers:
            render_filtered_influencer_list(filtered_influencers, selected_manager)
        else:
            st.warning(f"'{selected_manager}' 담당자로 등록된 인플루언서가 없습니다.")
            
    except Exception as e:
        st.error(f"담당자별 인플루언서 조회 중 오류가 발생했습니다: {e}")
        import traceback
        st.code(traceback.format_exc())

def render_filtered_influencer_list(influencers, selected_manager):
    """필터링된 인플루언서 리스트 표시 - 테이블뷰로 변경"""
    st.markdown("## 📋 인플루언서 목록")
    
    if not influencers:
        st.warning("표시할 인플루언서가 없습니다.")
        return
    
    # 테이블 데이터 준비
    table_data = []
    for influencer in influencers:
        # 플랫폼 아이콘
        platform_icons = {
            "instagram": "📸",
            "youtube": "📺", 
            "tiktok": "🎵",
            "twitter": "🐦"
        }
        platform_icon = platform_icons.get(influencer.get('platform', ''), "🌐")
        
        # 상태 아이콘
        status_icon = "🟢" if influencer.get('active', True) else "🔴"
        status_text = "활성" if influencer.get('active', True) else "비활성"
        
        # 날짜 포맷팅
        created_at = influencer.get('created_at', 'N/A')
        formatted_date = "N/A"
        if created_at != 'N/A':
            try:
                if isinstance(created_at, str):
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                else:
                    formatted_date = str(created_at)[:10]
            except:
                formatted_date = str(created_at)
        
        # 팔로워 수 포맷팅
        followers_count = influencer.get('followers_count', 0) or 0
        followers_display = f"{followers_count:,}" if followers_count > 0 else "N/A"
        
        # 가격 포맷팅
        price_krw = influencer.get('price_krw', 0) or 0
        price_display = f"{price_krw:,}원" if price_krw > 0 else "N/A"
        
        # 평점 정보
        manager_rating = influencer.get('manager_rating')
        content_rating = influencer.get('content_rating')
        manager_rating_display = f"{manager_rating}/5" if manager_rating else "N/A"
        content_rating_display = f"{content_rating}/5" if content_rating else "N/A"
        
        table_data.append({
            "플랫폼": f"{platform_icon} {influencer.get('platform', 'N/A')}",
            "이름": influencer.get('influencer_name', influencer.get('sns_id', 'N/A')),
            "SNS ID": influencer.get('sns_id', 'N/A'),
            "상태": f"{status_icon} {status_text}",
            "팔로워": followers_display,
            "카테고리": influencer.get('content_category', 'N/A'),
            "가격": price_display,
            "매니저평점": manager_rating_display,
            "콘텐츠평점": content_rating_display,
            "담당자": influencer.get('created_by', 'N/A'),
            "등록일": formatted_date,
            "SNS URL": influencer.get('sns_url', 'N/A'),
            "Owner Comment": influencer.get('owner_comment', 'N/A')[:50] + "..." if influencer.get('owner_comment') and len(str(influencer.get('owner_comment'))) > 50 else influencer.get('owner_comment', 'N/A')
        })
    
    # DataFrame으로 변환
    df = pd.DataFrame(table_data)
    
    # 테이블 표시 (스크롤 가능)
    st.dataframe(
        df,
        use_container_width=True,
        height=600,  # 고정 높이로 스크롤 가능하게 설정
        hide_index=True
    )
    
    # 총 개수 표시
    st.caption(f"총 {len(influencers)}명의 인플루언서가 표시됩니다.")

def render_influencer_tab():
    """인플루언서 탭 - 기존 함수 유지 (호환성)"""
    render_influencer_management()
