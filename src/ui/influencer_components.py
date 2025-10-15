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
    tab_names = ["📝 인플루언서 등록", "📋 인플루언서 정보 수정", "👥 인플루언서 조회"]
    
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
        
        # 연락방법 선택
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
        
        contact_method = st.selectbox(
            "연락 방법",
            contact_method_options,
            key="create_contact_method"
        )
        
        # 연락방법 추가정보 필드 (언제나 표시)
        contacts_method_etc = st.text_input(
            "연락방법 추가정보",
            placeholder="연락방법에 대한 추가 상세 정보를 입력해주세요",
            key="create_contacts_method_etc",
            help="예: 특별한 연락 방법, 추가 연락처 정보 등"
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
                
                # 선택된 연락방법을 데이터베이스 값으로 변환
                selected_contact_method_db = contact_method_db_values[contact_method_options.index(contact_method)]
                
                influencer = Influencer(
                    platform=platform,
                    sns_id=sns_id,
                    influencer_name=final_influencer_name,
                    sns_url=sns_url,
                    contact_method=selected_contact_method_db,
                    contacts_method_etc=contacts_method_etc,
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
                    st.session_state.search_success = True  # 검색 성공 플래그
                    active_status = "활성" if search_result.get('active', True) else "비활성"
                    st.success(f"✅ 인플루언서를 찾았습니다: {search_result.get('influencer_name') or search_result['sns_id']} ({search_result.get('platform')}) [{active_status}]")
                    
                    # 검색 결과를 좌측에 표시
                    render_influencer_search_result(search_result)
                    
                    # 즉시 리렌더링하여 우측 수정 폼이 활성화되도록 함
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
    if 'selected_influencer' in st.session_state and st.session_state.get('search_success', False):
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
            
            # 연락방법 추가정보 필드 (언제나 표시)
            contacts_method_etc = st.text_input(
                "연락방법 추가정보",
                value=influencer.get('contacts_method_etc', ''),
                key=f"edit_contacts_method_etc_{influencer['id']}",
                help="연락방법에 대한 추가 상세 정보를 입력해주세요"
            )
        
        shipping_address = st.text_area(
            "배송 주소", 
            value=influencer.get('shipping_address', ''),
            key=f"edit_shipping_{influencer['id']}"
        )
        
        # DM 응답 정보
        st.markdown("#### 💬 DM 응답 정보")
        dm_reply = st.text_area(
            "DM 응답 내용", 
            value=influencer.get('dm_reply', ''),
            key=f"edit_dm_reply_{influencer['id']}",
            help="인플루언서의 DM 응답 내용을 기록하세요"
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
                        'contacts_method_etc': contacts_method_etc,
                        'preferred_mode': selected_preferred_mode_db,
                        'shipping_address': shipping_address,
                        'dm_reply': dm_reply,
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
                        if "manager_filtered_influencers" in st.session_state:
                            del st.session_state["manager_filtered_influencers"]
                        
                        
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
                    if "manager_filtered_influencers" in st.session_state:
                        del st.session_state["manager_filtered_influencers"]
                    
                    
                    st.rerun()
                else:
                    st.error(f"삭제 실패: {result['message']}")
        with col2:
            if st.button("❌ 취소"):
                del st.session_state[f"confirm_delete_{influencer['id']}"]
                st.rerun()

def render_manager_influencer_management():
    """담당자별 인플루언서 관리 탭"""
    st.subheader("👥 인플루언서 조회")
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
            # 검색 필터링 기능 추가
            search_term = st.text_input(
                "🔍 SNS ID 또는 이름으로 검색",
                placeholder="SNS ID 또는 이름 입력",
                key="manager_search_input",
                help="인플루언서의 SNS ID 또는 이름으로 검색할 수 있습니다"
            )
        
        with col3:
            if st.button("🔄 새로고침", key="manager_refresh"):
                # 캐시 초기화
                if "manager_filtered_influencers" in st.session_state:
                    del st.session_state["manager_filtered_influencers"]
                if "campaign_participation_cache" in st.session_state:
                    del st.session_state["campaign_participation_cache"]
                if "all_participation_influencer_ids" in st.session_state:
                    del st.session_state["all_participation_influencer_ids"]
                st.rerun()
        
        # 담당자 필터링 (먼저 적용)
        if selected_manager == "전체":
            filtered_influencers = all_influencers
        else:
            filtered_influencers = [
                inf for inf in all_influencers 
                if inf.get('created_by') and inf.get('created_by').strip() == selected_manager
            ]
        
        # 검색 필터링 적용
        if search_term and search_term.strip():
            search_term_clean = search_term.strip().lower()
            search_filtered_influencers = []
            
            for inf in filtered_influencers:
                sns_id = (inf.get('sns_id', '') or '').lower()
                influencer_name = (inf.get('influencer_name', '') or '').lower()
                
                # SNS ID나 이름에 검색어가 포함되어 있는지 확인
                if (search_term_clean in sns_id or 
                    search_term_clean in influencer_name or
                    search_term_clean.replace('@', '') in sns_id.replace('@', '')):
                    search_filtered_influencers.append(inf)
            
            filtered_influencers = search_filtered_influencers
        
        # 통합 필터링 섹션 (한 줄로 압축)
        st.markdown("---")
        st.markdown("### 🎯 고급 필터링")
        
        # 한 줄에 모든 필터링 옵션 배치
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
        
        with col1:
            # 캠페인 참여 필터 옵션 (가로 배치)
            campaign_filter_type = st.radio(
                "캠페인 참여",
                ["전체", "참여한 인플루언서", "참여하지 않은 인플루언서", "특정 캠페인"],
                key="campaign_filter_type",
                horizontal=True,
                format_func=lambda x: {
                    "전체": "🌐 전체",
                    "참여한 인플루언서": "✅ 참여",
                    "참여하지 않은 인플루언서": "❌ 미참여",
                    "특정 캠페인": "🎯 특정"
                }[x]
            )
        
        with col2:
            selected_campaign = None
            if campaign_filter_type == "특정 캠페인":
                # 캠페인 목록 조회
                try:
                    campaigns = db_manager.get_campaigns()
                    if campaigns:
                        campaign_options = ["캠페인 선택"] + [f"{camp['campaign_name']} (ID: {camp['id']})" for camp in campaigns]
                        selected_campaign_option = st.selectbox(
                            "캠페인 선택",
                            campaign_options,
                            key="campaign_filter_select"
                        )
                        
                        if selected_campaign_option != "캠페인 선택":
                            # 캠페인 ID 추출
                            campaign_id = selected_campaign_option.split("(ID: ")[1].split(")")[0]
                            selected_campaign = campaign_id
                    else:
                        st.warning("등록된 캠페인이 없습니다.")
                except Exception as e:
                    st.error(f"캠페인 목록 조회 중 오류: {e}")
            else:
                st.empty()  # 빈 공간 유지
        
        with col3:
            # 날짜 필터 방식
            date_filter_type = st.radio(
                "날짜 필터",
                ["전체", "기간 선택", "특정일"],
                key="date_filter_type",
                horizontal=True,
                format_func=lambda x: {
                    "전체": "🌐 전체",
                    "기간 선택": "📅 기간",
                    "특정일": "📆 특정일"
                }[x]
            )
        
        with col4:
            # 날짜 필터링 로직을 위한 변수 초기화
            date_filter = "전체"
            start_date = None
            end_date = None
            specific_date = None
            
            if date_filter_type == "기간 선택":
                start_date = st.date_input(
                    "시작일",
                    value=None,
                    key="date_filter_start"
                )
            elif date_filter_type == "특정일":
                specific_date = st.date_input(
                    "선택일",
                    value=None,
                    key="date_filter_specific"
                )
            else:
                st.empty()  # 빈 공간 유지
        
        with col5:
            if date_filter_type == "기간 선택":
                end_date = st.date_input(
                    "종료일", 
                    value=None,
                    key="date_filter_end"
                )
            else:
                st.empty()  # 빈 공간 유지
        
        # 캠페인 참여 필터링 적용
        if campaign_filter_type != "전체":
            try:
                # 캠페인 참여 정보 캐시 확인
                participation_cache_key = "all_participation_influencer_ids"
                if participation_cache_key not in st.session_state:
                    # 모든 캠페인에 참여한 인플루언서 ID 목록 조회
                    participated_influencer_ids = db_manager.get_all_participated_influencer_ids()
                    st.session_state[participation_cache_key] = participated_influencer_ids
                
                participated_influencer_ids = st.session_state[participation_cache_key]
                
                # 특정 캠페인의 참여자 ID 목록 (필요한 경우에만)
                specific_campaign_participant_ids = set()
                if campaign_filter_type == "특정 캠페인" and selected_campaign:
                    specific_participations = db_manager.get_all_campaign_participations(selected_campaign)
                    for participation in specific_participations:
                        influencer_id = participation.get('influencer_id')
                        if influencer_id:
                            specific_campaign_participant_ids.add(influencer_id)
                
                # 필터링 적용
                campaign_filtered_influencers = []
                for inf in filtered_influencers:
                    influencer_id = inf.get('id')
                    
                    include_influencer = False
                    
                    if campaign_filter_type == "참여한 인플루언서":
                        # campaign_influencer_participations 테이블의 influencer_id와 매칭
                        include_influencer = influencer_id in participated_influencer_ids
                    elif campaign_filter_type == "참여하지 않은 인플루언서":
                        # campaign_influencer_participations 테이블에 없는 influencer_id
                        include_influencer = influencer_id not in participated_influencer_ids
                    elif campaign_filter_type == "특정 캠페인" and selected_campaign:
                        # 특정 캠페인의 campaign_influencer_participations에 있는 influencer_id
                        include_influencer = influencer_id in specific_campaign_participant_ids
                    
                    if include_influencer:
                        campaign_filtered_influencers.append(inf)
                
                filtered_influencers = campaign_filtered_influencers
                
            except Exception as e:
                st.error(f"캠페인 참여 필터링 중 오류: {e}")
                import traceback
                st.code(traceback.format_exc())
        
        # 날짜 필터링 로직 처리
        if date_filter_type == "기간 선택":
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
            if specific_date:
                date_filter = "특정일"
        
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
        
        # 검색 필터 정보 추가
        search_info = ""
        if search_term and search_term.strip():
            search_info = f" (검색어: '{search_term.strip()}')"
        
        # 캠페인 참여 필터 정보 추가
        campaign_info = ""
        if campaign_filter_type == "참여한 인플루언서":
            campaign_info = " (캠페인 참여자)"
        elif campaign_filter_type == "참여하지 않은 인플루언서":
            campaign_info = " (캠페인 미참여자)"
        elif campaign_filter_type == "특정 캠페인" and selected_campaign:
            # 캠페인 이름 가져오기
            try:
                campaigns = db_manager.get_campaigns()
                campaign_name = "알 수 없는 캠페인"
                for camp in campaigns:
                    if camp['id'] == selected_campaign:
                        campaign_name = camp['campaign_name']
                        break
                campaign_info = f" ({campaign_name} 참여자)"
            except:
                campaign_info = f" (캠페인 ID: {selected_campaign} 참여자)"
        
        # 날짜 필터 정보 추가
        date_info = ""
        if date_filter == "기간" and start_date and end_date:
            date_info = f" (등록일: {start_date} ~ {end_date})"
        elif date_filter == "특정일" and specific_date:
            date_info = f" (등록일: {specific_date})"
        
        st.info(f"📊 {manager_text}의 인플루언서: {len(filtered_influencers)}명{search_info}{campaign_info}{date_info}")
        
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
    """필터링된 인플루언서 리스트 표시 - 편집 가능한 테이블뷰로 변경"""
    st.markdown("## 📋 인플루언서 목록 (편집 가능)")
    
    if not influencers:
        st.warning("표시할 인플루언서가 없습니다.")
        return
    
    # 테이블 데이터 준비 (편집 가능한 형태로)
    table_data = []
    for influencer in influencers:
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
        
        # Owner Comment
        owner_comment = influencer.get('owner_comment', '')
        
        # DM 응답 정보
        dm_reply = influencer.get('dm_reply', '')
        
        # 캠페인 참여 정보 조회 (캐시 사용)
        campaign_participation_info = ""
        try:
            # 캠페인 참여 정보 캐시 확인
            cache_key = "campaign_participation_cache"
            if cache_key not in st.session_state:
                # 캐시가 없으면 생성
                campaigns = db_manager.get_campaigns()
                participation_cache = {}
                
                for campaign in campaigns:
                    participations = db_manager.get_all_campaign_participations(campaign['id'])
                    for participation in participations:
                        influencer_id = participation.get('influencer_id')
                        if influencer_id:
                            if influencer_id not in participation_cache:
                                participation_cache[influencer_id] = []
                            participation_cache[influencer_id].append(campaign['campaign_name'])
                
                st.session_state[cache_key] = participation_cache
            
            # 캐시에서 참여 정보 조회
            participation_cache = st.session_state[cache_key]
            influencer_id = influencer.get('id')
            participated_campaigns = participation_cache.get(influencer_id, [])
            
            if participated_campaigns:
                campaign_participation_info = ", ".join(participated_campaigns[:3])  # 최대 3개만 표시
                if len(participated_campaigns) > 3:
                    campaign_participation_info += f" 외 {len(participated_campaigns) - 3}개"
            else:
                campaign_participation_info = "참여 없음"
        except:
            campaign_participation_info = "조회 실패"
        
        table_data.append({
            "ID": influencer.get('id'),  # 숨겨진 ID 필드
            "플랫폼": influencer.get('platform', 'instagram'),
            "이름": influencer.get('influencer_name', influencer.get('sns_id', '')),
            "SNS ID": influencer.get('sns_id', ''),
            "상태": influencer.get('active', True),
            "팔로워": influencer.get('followers_count', 0) or 0,
            "카테고리": influencer.get('content_category', '일반'),
            "가격": influencer.get('price_krw', 0) or 0,
            "매니저평점": influencer.get('manager_rating', 3) or 3,
            "콘텐츠평점": influencer.get('content_rating', 3) or 3,
            "담당자": influencer.get('created_by', ''),
            "등록일": formatted_date,
            "캠페인 참여": campaign_participation_info,
            "SNS URL": influencer.get('sns_url', ''),
            "Owner Comment": owner_comment,
            "DM 응답정보": dm_reply
        })
    
    # DataFrame으로 변환
    df = pd.DataFrame(table_data)
    
    # 컬럼 설정
    column_config = {
        "ID": st.column_config.NumberColumn("ID", disabled=True, help="인플루언서 고유 ID"),
        "플랫폼": st.column_config.SelectboxColumn(
            "플랫폼",
            help="SNS 플랫폼을 선택하세요",
            options=["instagram", "youtube", "tiktok", "twitter"],
            required=True,
        ),
        "이름": st.column_config.TextColumn(
            "이름",
            help="인플루언서 이름 또는 별칭",
            max_chars=100,
        ),
        "SNS ID": st.column_config.TextColumn(
            "SNS ID", 
            help="SNS 계정 ID",
            max_chars=50,
            required=True,
        ),
        "상태": st.column_config.CheckboxColumn(
            "활성 상태",
            help="인플루언서 활성/비활성 상태",
        ),
        "팔로워": st.column_config.NumberColumn(
            "팔로워 수",
            help="팔로워 수를 입력하세요",
            min_value=0,
            format="%d",
        ),
        "카테고리": st.column_config.SelectboxColumn(
            "카테고리",
            help="콘텐츠 카테고리",
            options=["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"],
        ),
        "가격": st.column_config.NumberColumn(
            "가격 (원)",
            help="협찬 가격을 입력하세요",
            min_value=0,
            format="%d원",
        ),
        "매니저평점": st.column_config.NumberColumn(
            "매니저 평점",
            help="1-5점 사이로 입력하세요",
            min_value=1,
            max_value=5,
            step=1,
        ),
        "콘텐츠평점": st.column_config.NumberColumn(
            "콘텐츠 평점",
            help="1-5점 사이로 입력하세요", 
            min_value=1,
            max_value=5,
            step=1,
        ),
        "담당자": st.column_config.TextColumn(
            "담당자",
            help="담당자 이름",
            max_chars=50,
        ),
        "등록일": st.column_config.TextColumn(
            "등록일",
            disabled=True,
            help="등록 날짜 (읽기 전용)",
        ),
        "캠페인 참여": st.column_config.TextColumn(
            "캠페인 참여",
            disabled=True,
            help="참여한 캠페인 목록 (읽기 전용)",
        ),
        "SNS URL": st.column_config.TextColumn(
            "SNS URL",
            help="SNS 프로필 URL",
            max_chars=200,
        ),
        "Owner Comment": st.column_config.TextColumn(
            "Owner Comment",
            help="담당자 코멘트 (상세 편집은 별도 버튼 사용)",
            max_chars=500,
        ),
        "DM 응답정보": st.column_config.TextColumn(
            "DM 응답정보",
            help="인플루언서의 DM 응답 내용",
            max_chars=500,
        ),
    }
    
    # 편집 가능한 테이블 표시
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        height=600,
        column_config=column_config,
        disabled=["ID", "등록일", "캠페인 참여"],  # 수정 불가능한 컬럼
        hide_index=True,
        key="influencer_editor"
    )
    
    # 편집된 데이터가 있는지 확인하고 저장
    st.markdown("---")
    st.markdown("### 💾 변경사항 저장")
    
    # 변경사항 감지 (더 정확한 방법)
    changes_made = False
    try:
        # DataFrame 비교를 위한 정확한 방법
        if not edited_df.equals(df):
            # 각 행과 열을 비교하여 실제 변경사항 확인
            for idx in range(len(df)):
                for col in df.columns:
                    if col not in ["ID", "등록일", "캠페인 참여"]:  # 비교에서 제외할 컬럼
                        original_val = str(df.iloc[idx][col])
                        edited_val = str(edited_df.iloc[idx][col])
                        if original_val != edited_val:
                            changes_made = True
                            break
                if changes_made:
                    break
    except Exception as e:
        # 비교 실패 시 기본적으로 변경사항이 있다고 가정
        changes_made = True
        st.warning(f"변경사항 감지 중 오류: {e}")
    
    if changes_made:
        # 변경된 항목 수 표시
        changed_items = 0
        for idx in range(len(df)):
            for col in df.columns:
                if col not in ["ID", "등록일", "캠페인 참여"]:
                    original_val = str(df.iloc[idx][col])
                    edited_val = str(edited_df.iloc[idx][col])
                    if original_val != edited_val:
                        changed_items += 1
        
        st.success(f"📝 테이블에서 {changed_items}개의 변경사항이 감지되었습니다!")
        
        # 변경사항 미리보기
        with st.expander("🔍 변경사항 미리보기", expanded=False):
            for idx in range(len(df)):
                row_changes = []
                for col in df.columns:
                    if col not in ["ID", "등록일", "캠페인 참여"]:
                        original_val = str(df.iloc[idx][col])
                        edited_val = str(edited_df.iloc[idx][col])
                        if original_val != edited_val:
                            row_changes.append(f"**{col}**: '{original_val}' → '{edited_val}'")
                
                if row_changes:
                    influencer_name = edited_df.iloc[idx]["이름"]
                    st.write(f"**{influencer_name}**:")
                    for change in row_changes:
                        st.write(f"  - {change}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("💾 변경사항 저장", type="primary", key="save_changes"):
                save_edited_influencers(df, edited_df)
        
        with col2:
            if st.button("🔄 변경사항 취소", key="cancel_changes"):
                st.rerun()
    else:
        st.info("변경된 내용이 없습니다. 테이블에서 데이터를 편집하면 저장 버튼이 나타납니다.")
    
    # 상세 편집 안내 메시지
    st.markdown("---")
    st.markdown("### 💡 편집 안내")
    st.info("📝 **간단한 정보**: 위 테이블에서 직접 편집 가능  \n📋 **상세 정보**: '인플루언서 정보 수정' 탭에서 개별 검색 후 편집 가능")
    
    # 총 개수 표시
    st.caption(f"총 {len(influencers)}명의 인플루언서가 표시됩니다. (편집 가능)")

def save_edited_influencers(original_df, edited_df):
    """편집된 인플루언서 데이터를 저장"""
    try:
        # 변경된 행들을 찾아서 업데이트
        updated_count = 0
        error_count = 0
        
        # DataFrame을 인덱스 기반으로 비교
        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]
            
            # 변경사항이 있는지 확인 (ID, 등록일, 캠페인 참여 제외)
            comparison_columns = [col for col in original_df.columns if col not in ["ID", "등록일", "캠페인 참여"]]
            has_changes = False
            
            for col in comparison_columns:
                if str(original_row[col]) != str(edited_row[col]):
                    has_changes = True
                    break
            
            if has_changes:
                influencer_id = edited_row["ID"]
                
                # 업데이트할 데이터 준비 (NumPy 타입을 Python 기본 타입으로 변환)
                update_data = {
                    'platform': str(edited_row["플랫폼"]),
                    'sns_id': str(edited_row["SNS ID"]),
                    'influencer_name': str(edited_row["이름"]) if edited_row["이름"] else str(edited_row["SNS ID"]),
                    'active': bool(edited_row["상태"]),
                    'followers_count': int(edited_row["팔로워"]) if edited_row["팔로워"] is not None else 0,
                    'content_category': str(edited_row["카테고리"]),
                    'price_krw': int(edited_row["가격"]) if edited_row["가격"] is not None else 0,
                    'manager_rating': int(edited_row["매니저평점"]) if edited_row["매니저평점"] is not None else None,
                    'content_rating': int(edited_row["콘텐츠평점"]) if edited_row["콘텐츠평점"] is not None else None,
                    'created_by': str(edited_row["담당자"]).strip() if edited_row["담당자"] and str(edited_row["담당자"]).strip() else None,
                    'sns_url': str(edited_row["SNS URL"]) if edited_row["SNS URL"] else None,
                    'owner_comment': str(edited_row["Owner Comment"]) if edited_row["Owner Comment"] else None,
                    'dm_reply': str(edited_row["DM 응답정보"]) if edited_row["DM 응답정보"] else None
                }
                
                # 데이터베이스 업데이트
                result = db_manager.update_influencer(influencer_id, update_data)
                if result["success"]:
                    updated_count += 1
                else:
                    error_count += 1
                    st.error(f"❌ ID {influencer_id} 업데이트 실패: {result['message']}")
        
        # 결과 표시
        if updated_count > 0:
            st.success(f"✅ {updated_count}명의 인플루언서 정보가 성공적으로 업데이트되었습니다!")
            
            # 업데이트된 인플루언서 목록 표시
            with st.expander("📋 업데이트된 인플루언서 목록", expanded=False):
                updated_influencers = []
                for idx in range(len(original_df)):
                    original_row = original_df.iloc[idx]
                    edited_row = edited_df.iloc[idx]
                    
                    # 변경사항이 있는지 확인
                    has_changes = False
                    for col in original_df.columns:
                        if col not in ["ID", "등록일", "캠페인 참여"]:
                            if str(original_row[col]) != str(edited_row[col]):
                                has_changes = True
                                break
                    
                    if has_changes:
                        updated_influencers.append(edited_row["이름"])
                
                for name in updated_influencers:
                    st.write(f"• {name}")
        
        if error_count > 0:
            st.error(f"❌ {error_count}명의 인플루언서 업데이트에 실패했습니다.")
        
        if updated_count > 0:
            # 캐시 초기화
            if "influencers_data" in st.session_state:
                del st.session_state["influencers_data"]
            if "manager_filtered_influencers" in st.session_state:
                del st.session_state["manager_filtered_influencers"]
            if "campaign_participation_cache" in st.session_state:
                del st.session_state["campaign_participation_cache"]
            if "all_participation_influencer_ids" in st.session_state:
                del st.session_state["all_participation_influencer_ids"]
            
            # 페이지 새로고침
            st.rerun()
            
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")
        import traceback
        st.code(traceback.format_exc())

def render_influencer_tab():
    """인플루언서 탭 - 기존 함수 유지 (호환성)"""
    render_influencer_management()
