import streamlit as st
import sys
import os

# ── Page config: 모든 st.* 호출보다 우선 ─────────────────────────
st.set_page_config(
    page_title="Connecta Manager",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="auto",  # Streamlit Cloud 호환성을 위해 auto로 변경
)

# ── Streamlit 설정 (Windows 파일 감시 오류 해결) ──────────────────
import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_SERVER_RUN_ON_SAVE"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_LOGGER_LEVEL"] = "error"
os.environ["STREAMLIT_CLIENT_SHOW_ERROR_DETAILS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"

# Watchdog 모듈 완전 비활성화
try:
    import watchdog
    watchdog.observers.api.Observer = None
    watchdog.events.FileSystemEventHandler = None
except ImportError:
    pass

# ── 에러 처리 및 안정성 개선 ─────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
warnings.filterwarnings("ignore", category=FutureWarning, module="streamlit")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="streamlit")
warnings.filterwarnings("ignore", category=UserWarning, module="watchdog")
warnings.filterwarnings("ignore", category=FutureWarning, module="watchdog")

# Streamlit 로그 레벨 설정 (터미널 출력 최소화)
import logging
logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("watchdog").setLevel(logging.CRITICAL)
logging.getLogger("watchdog.observers").setLevel(logging.CRITICAL)
logging.getLogger("watchdog.observers.api").setLevel(logging.CRITICAL)
logging.getLogger("streamlit.watcher").setLevel(logging.CRITICAL)
logging.getLogger("streamlit.watcher.event_based_path_watcher").setLevel(logging.CRITICAL)

# Streamlit Cloud 호환성을 위한 경고 필터 추가
warnings.filterwarnings("ignore", message=".*use_container_width.*")
warnings.filterwarnings("ignore", message=".*Please replace.*use_container_width.*")

# Watchdog 관련 경고 필터 추가
warnings.filterwarnings("ignore", message=".*Paths don't have the same drive.*")
warnings.filterwarnings("ignore", message=".*ValueError.*commonpath.*")
warnings.filterwarnings("ignore", message=".*watchdog.*")
warnings.filterwarnings("ignore", message=".*event_based_path_watcher.*")
warnings.filterwarnings("ignore", message=".*handle_path_change_event.*")

# ── Path ─────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 분리된 컴포넌트들 import
from src.ui.project_components import (
    render_single_url_crawl, render_batch_url_crawl
)
from src.ui.campaign_components import render_campaign_management
from src.ui.performance_components import render_performance_management, render_performance_crawl
from src.ui.influencer_components import render_influencer_management
from src.ui.influencer_statistics_management_components import render_influencer_statistics_management
from src.ui.ai_analysis_components import render_ai_analysis_management
from src.ui.influencer_matching_components import render_influencer_matching


# ── CSS ──────────────────────────────────────────────────────
def load_css_file():
    css_file = os.path.join(os.path.dirname(__file__), 'css', 'main.css')
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def inject_layout_css():
    st.markdown("""
    <style>
    /* ===== 레이아웃 & 여백 조정 ===== */

    /* 본문 컨테이너: 상단여백 완전 제거 + 좌우 패딩 컴팩트 + 전체폭 */
    section.main > div.block-container {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding-top: 0 !important;           /* ⬅ 상단 여백 0 */
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    /* 첫 요소(타이틀/탭 등) 위 여백까지 0 */
    section.main > div.block-container > :first-child { margin-top: 0 !important; }

    /* 제목 기본 마진 완전 제거 */
    h1, h2, h3 { margin-top: 0 !important; margin-bottom: 0.5rem !important; }

    /* 탭 상단 여백 제거 */
    div[data-baseweb="tab-list"] { margin-top: 0 !important; }

    /* 가로 블록이 중앙 정렬되는 문제 방지 */
    div[data-testid="stHorizontalBlock"] { justify-content: flex-start !important; }

    /* ===== 사이드바 토글 정상작동 보장 =====
       - transform 강제 해제(기존 토글과 충돌 X)
       - 펼침(true)일 때만 폭 지정, 접힘(false)일 때는 프레임워크 기본 동작 유지
    */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 260px !important;
        max-width: 280px !important;
        width: 280px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        /* transform/translate는 프레임워크에 맡김 */
    }

    /* ===== 버튼/텍스트 미관 보정 ===== */

     /* 모든 버튼 한 줄 유지 (비밀번호 찾기 등) */
     div.stButton > button { white-space: nowrap !important; }
     
     /* 폼 버튼 크기 통일 */
     .stForm .stButton > button {
         min-height: 2.5rem !important;
         font-size: 0.95rem !important;
         font-weight: 600 !important;
     }


    /* 사이드바 헤드라인(로고 영역) 줄바꿈 방지 */
    .sidebar-title { white-space: nowrap; }

    /* 사이드바 메뉴 버튼 스타일링 */
    .stSidebar .stButton > button {
        width: 100% !important;
        margin-bottom: 0.25rem !important;
        text-align: left !important;
        padding: 0.75rem 1rem !important;
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stSidebar .stButton > button:hover {
        transform: translateX(2px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    /* 활성 메뉴 버튼 스타일 */
    .stSidebar .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* 비활성 메뉴 버튼 스타일 */
    .stSidebar .stButton > button[kind="secondary"] {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        color: #495057 !important;
    }

    /* ── 사이드바 전체 세로 간격 줄이기 */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]{
    gap: 2px !important;               /* 기본 16~24px → 6px 정도로 */
    }

    /* ── 각 요소 컨테이너의 아래 여백 축소 */
    [data-testid="stSidebar"] [data-testid="element-container"]{
    margin-bottom: 2px !important;     /* 필요하면 0~8px 사이로 조정 */
    padding-bottom: 0 !important;
    }

    /* ── 버튼 위아래 간격/패딩 미세조정 */
    [data-testid="stSidebar"] .stButton{ 
    margin: 2px 0 !important;          /* 버튼 블록 자체 여백 */
    }
    [data-testid="stSidebar"] .stButton > button{
    padding: 8px 12px !important;      /* 높이 줄이려면 6~8px 권장 */
    border-radius: .5rem !important;   /* 기존 모서리 유지 */
    }

    /* ── '메뉴' 같은 헤더의 아래 여백도 줄이기 */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4{
    margin-bottom: 2px !important;     /* 기본 16~32px → 8px */
    }


    /* Streamlit 헤더와 설정 메뉴 표시 보장 */
    .stApp > header {
        background-color: transparent;
        min-height: 3rem !important;
    }
    
    /* 헤더 툴바(설정 메뉴 포함) 표시 보장 */
    .stApp > header [data-testid="stToolbar"] {
        display: flex !important;
        visibility: visible !important;
    }
    
    /* 설정 메뉴 버튼(점 3개) 표시 보장 */
    .stApp > header [data-testid="stToolbar"] button {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* MainMenu 숨기지 않음 (설정 메뉴 보존) */
    #MainMenu {
        display: block !important;
    }

    /* 사이드바 폼 전체 간격 */
    .stSidebar .stForm, .stSidebar form {
      margin: 0 0 .5rem 0 !important;
      padding: 0 !important;
    }

    /* 라벨과 입력 사이 여백, 입력 높이 */
    .stSidebar .stForm label, .stSidebar form label {
      margin-bottom: .25rem !important;
    }
    .stSidebar .stForm input, .stSidebar .stForm textarea,
    .stSidebar form input, .stSidebar form textarea {
      min-height: 2.25rem !important;
    }

    /* 버튼은 항상 한 줄 + 풀폭 + 위아래 간격 */
    .stSidebar .stForm .stButton, .stSidebar form .stButton {
      margin: .25rem 0 !important;
    }
    .stSidebar .stForm .stButton > button,
    .stSidebar form .stButton > button {
      width: 100% !important;
      white-space: nowrap !important;
    }

    /* 탭 상단 여백 제거로 컴팩트 */
    .stSidebar [data-baseweb="tab-list"] { margin-top: 0 !important; }


    /* ====== AUTH 사이드바 전용 리셋/정돈 ====== */

    /* 사이드바의 .stForm 배경/박스는 제거해서 마진 충돌 방지 (main.css의 .stForm 오버라이드) */
    .stSidebar .stForm {
      background: transparent !important;
      box-shadow: none !important;
      border-radius: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
    }


    /* 사이드바 요소 기본 간격(너무 촘촘했던 2px → 8px로 일괄 정리) */
    [data-testid="stSidebar"] [data-testid="element-container"] {
      margin-bottom: 8px !important;
      padding-bottom: 0 !important;
    }

    /* 탭 컨테이너 위/아래 여백 */
    .stSidebar .stTabs {
      margin-top: 4px !important;
      margin-bottom: 6px !important;
    }
    .stSidebar [data-baseweb="tab-list"] { margin-top: 0 !important; }

    /* 입력/라벨 간격 & 입력 높이 통일 */
    .stSidebar label { margin-bottom: 6px !important; }
    .stSidebar input, .stSidebar textarea, .stSidebar select {
      min-height: 38px !important;
    }

    /* 버튼은 항상 세로 배치 + 풀폭 + 한 줄 */
    .stSidebar .stForm .stButton,
    .stSidebar form .stButton { margin: 6px 0 !important; }
    .stSidebar .stForm .stButton > button,
    .stSidebar form .stButton > button {
      width: 100% !important;
      white-space: nowrap !important;
    }



    </style>
    """, unsafe_allow_html=True)

def load_css():
    load_css_file()     # 프로젝트 CSS
    inject_layout_css() # 레이아웃/사이드바/버튼/배지 CSS


# ── Sidebar ──────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # 로고 및 제목
        st.markdown("""
        <div style="text-align:center; margin-bottom: 1.5rem;" class="sidebar-title">
            <div style="margin-bottom: .5rem;">
                <img src="https://zttosbzbwkgqkpsdgpcx.supabase.co/storage/v1/object/public/connecta/connecta_logo.svg"
                     alt="Connecta Logo"
                     style="height: 60px; width: auto; max-width: 120px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));">
            </div>
        </div>
        """, unsafe_allow_html=True)

        
        
        st.markdown("---")
    
        
        # 현재 선택된 페이지 초기화
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'influencer_management'
        
        # 크롤링 페이지가 선택된 경우 관리 페이지로 리다이렉트 (크롤링 기능 제거됨)
        if st.session_state.current_page in ['single_crawl', 'batch_crawl', 'performance_crawl']:
            st.session_state.current_page = 'influencer_management'
        
        # 관리 메뉴 그룹
        st.markdown("### 📋 관리 메뉴")
        
        management_menu_options = {
            'influencer_management': '👥 인플루언서 관리',
            'influencer_analysis': '📊 인플루언서 분석',
            'ai_analysis': '🤖 인공지능 분석',
            'campaign_management': '📁 캠페인 관리',
            'influencer_matching': '🎯 인플루언서 매칭',
            'performance_management': '📊 성과 관리'
        }
        
        for page_key, page_title in management_menu_options.items():
            if st.button(
                page_title, 
                key=f"menu_{page_key}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_key else "secondary"
            ):
                st.session_state.current_page = page_key
                st.session_state.page_changed = True  # 페이지 변경 플래그
                st.rerun()  # 즉시 리렌더링하여 버튼 상태 업데이트
        
        st.markdown("---")
        
        # 추가 정보
        st.markdown("""
        <div style="text-align:center; margin-top: 1rem; color: #6c757d; font-size: 0.85rem;">
            <p style="margin: 0.25rem 0 0;">Main in Connect@</p>
        </div>
        """, unsafe_allow_html=True)


# ── Main content ─────────────────────────────────────────────
def render_main_content():

    # 현재 선택된 페이지에 따라 다른 컴포넌트 렌더링
    current_page = st.session_state.get('current_page', 'influencer_management')
    
    if current_page == 'single_crawl':
        render_single_url_crawl()
    elif current_page == 'batch_crawl':
        render_batch_url_crawl()
    elif current_page == 'performance_crawl':
        render_performance_crawl()
    elif current_page == 'campaign_management':
        render_campaign_management()
    elif current_page == 'performance_management':
        render_performance_management()
    elif current_page == 'influencer_management':
        render_influencer_management()
    elif current_page == 'influencer_analysis':
        render_influencer_statistics_management()
    elif current_page == 'ai_analysis':
        render_ai_analysis_management()
    elif current_page == 'influencer_matching':
        render_influencer_matching()
    else:
        # 기본값으로 인플루언서 관리 표시
        render_influencer_management()


# ── App ──────────────────────────────────────────────────────
def main():
    try:
        load_css()                # 프로젝트 CSS + 위 레이아웃 CSS

        
        # 모든 모드에서 메인 컨텐츠 렌더링

        render_sidebar()          # 실제 st.sidebar 렌더
        render_main_content()     # 본문

        st.markdown("""
        <div style="text-align:center; margin-top: 2rem; padding: 1.25rem; color:#6c757d; border-top:1px solid #e9ecef;">
            <p style="margin:0;">hello@thegpc.kr</p>
            <p style="font-size:.9rem; margin:.35rem 0 0;">THEGPC INC.</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"애플리케이션 오류가 발생했습니다: {str(e)}")
        st.info("페이지를 새로고침하거나 다시 시도해주세요.")

if __name__ == "__main__":
    main()
