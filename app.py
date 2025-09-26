import streamlit as st
import sys
import os

# ── Page config: 모든 st.* 호출보다 우선 ─────────────────────────
st.set_page_config(
    page_title="Connecta Manager",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Streamlit 설정 (Windows 파일 감시 오류 해결) ──────────────────
import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

# ── 에러 처리 및 안정성 개선 ─────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
warnings.filterwarnings("ignore", category=FutureWarning, module="streamlit")

# ── Path ─────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.auth_components import render_auth_sidebar, render_user_profile  # (미사용 시 삭제해도 됨)
# 크롤링 컴포넌트 import가 제거되었습니다.
from src.ui.project_components import (
    render_single_url_crawl, render_batch_url_crawl,
    render_campaign_management, render_performance_management, render_performance_crawl,
    render_influencer_management
)
from src.supabase.auth import supabase_auth


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

    /* 로그인 성공 배지: 한 줄, 넘치면 말줄임 */
    .login-ok {
        background: #e9f7ef;
        border: 1px solid #d4edda;
        color: #155724;
        padding: .6rem .75rem;
        border-radius: .5rem;
        font-size: .95rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .login-ok .email { font-weight: 600; }

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


    /* 필요 시 상단 헤더를 숨기지 않음(접힘 버튼 살리기) */
    /* #MainMenu만 숨기고, header/footer는 유지 */
    #MainMenu { display: none !important; }
    /* ===== 로그인/회원가입 사이드바 폼 정돈 ===== */

    /* 경고/안내 배지: 아래 여백 확보해 겹침 방지 */
    .login-alert, .login-ok {
      display: block !important;
      margin: 8px 0 12px !important;
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

    /* 로그인 성공 배지는 한 줄 유지 + 말줄임 */
    .login-ok { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    /* 경고 배지 별도 색상 */
    .login-warn {
      background: #fff3cd;
      border: 1px solid #ffeaa7;
      color: #856404;
      padding: .6rem .75rem;
      border-radius: .5rem;
      font-size: .95rem;
    }

    /* ====== AUTH 사이드바 전용 리셋/정돈 ====== */

    /* 사이드바의 .stForm 배경/박스는 제거해서 마진 충돌 방지 (main.css의 .stForm 오버라이드) */
    .stSidebar .stForm {
      background: transparent !important;
      box-shadow: none !important;
      border-radius: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
    }

    /* 경고/안내 배지 아래로 충분한 여백: 탭/폼과 겹침 방지 */
    .login-warn, .login-ok {
      display: block !important;
      margin: 10px 0 12px !important;
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

    /* 로그인/회원가입 묶음에 카드 느낌(시각적 그룹화 + 균일 마진) */
    .stSidebar .auth-card {
      padding: 12px !important;
      border: none !important;
      border-radius: 12px !important;
      background: #fff !important;
      box-shadow: none !important;
      margin: 6px 0 12px !important;
    }

    /* 카드 내부 요소 간격 살짝 축소 */
    .stSidebar .auth-card [data-testid="element-container"] {
      margin-bottom: 6px !important;
    }

    /* 경고 배지 룩 고정 */
    .login-warn {
      background: #fff8e1 !important;
      border: 1px solid #ffeaa7 !important;
      color: #7a5d00 !important;
      padding: .6rem .75rem !important;
      border-radius: .5rem !important;
      font-size: .95rem !important;
    }

    /* 성공 배지 룩 고정 */
    .login-ok {
      background: #e9f7ef !important;
      border: 1px solid #d4edda !important;
      color: #155724 !important;
      padding: .6rem .75rem !important;
      border-radius: .5rem !important;
      font-size: .95rem !important;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
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

        # 로그인 상태 표시
        if supabase_auth.is_authenticated():
            user = supabase_auth.get_current_user()
            # ✅ 커스텀 배지 (한 줄/말줄임)
            st.markdown(
                f"""<div class="login-ok">✅ 로그인됨:<br><span class="email">{user.email}</span></div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div class="login-warn login-alert">⚠️ 로그인이 필요합니다</div>""",
                unsafe_allow_html=True
            )
        
        # 로그인/로그아웃 버튼
        if supabase_auth.is_authenticated():
            if st.button("🚪 로그아웃", type="secondary", use_container_width=True, key="logout_btn"):
                result = supabase_auth.sign_out()
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])
        else:
            # 로그인/회원가입 탭 (카드 래핑)
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["로그인", "회원가입"])

            with tab1:
                with st.form("login_form", border=False):
                    email = st.text_input("이메일", placeholder="your@email.com", key="login_email")
                    password = st.text_input("비밀번호", type="password", key="login_password")

                    # 세로 배치 + 풀폭 (유지)
                    do_login = st.form_submit_button("로그인", type="primary", use_container_width=True)
                    do_reset = st.form_submit_button("비밀번호 찾기", use_container_width=True)

                    if do_login:
                        if not email or not password:
                            st.error("이메일과 비밀번호를 입력해주세요.")
                        else:
                            with st.spinner("로그인 중..."):
                                result = supabase_auth.sign_in(email, password)
                            if result["success"]:
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])

                    if do_reset:
                        if not email:
                            st.error("이메일을 입력해주세요.")
                        else:
                            with st.spinner("비밀번호 재설정 이메일 발송 중..."):
                                result = supabase_auth.reset_password(email)
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])

            with tab2:
                with st.form("signup_form", border=False):
                    email = st.text_input("이메일", placeholder="your@email.com", key="signup_email")
                    password = st.text_input("비밀번호", type="password", key="signup_password")
                    confirm = st.text_input("비밀번호 확인", type="password", key="signup_confirm")

                    do_signup = st.form_submit_button("회원가입", type="primary", use_container_width=True)

                    if do_signup:
                        if not email or not password or not confirm:
                            st.error("모든 필드를 입력해주세요.")
                        elif password != confirm:
                            st.error("비밀번호가 일치하지 않습니다.")
                        elif len(password) < 6:
                            st.error("비밀번호는 최소 6자 이상이어야 합니다.")
                        else:
                            with st.spinner("회원가입 중..."):
                                result = supabase_auth.sign_up(email, password)
                            if result["success"]:
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])
            st.markdown('</div>', unsafe_allow_html=True)  # auth-card 종료
        
        st.markdown("---")
    
        
        # 현재 선택된 페이지 초기화
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'campaign_management'
        
        # 크롤링 페이지가 선택된 경우 관리 페이지로 리다이렉트 (크롤링 기능 제거됨)
        if st.session_state.current_page in ['single_crawl', 'batch_crawl', 'performance_crawl']:
            st.session_state.current_page = 'campaign_management'
        
        # 관리 메뉴 그룹
        st.markdown("### 📋 관리 메뉴")
        
        management_menu_options = {
            'campaign_management': '📁 캠페인 관리',
            'performance_management': '📊 성과 관리',
            'influencer_management': '👥 인플루언서 관리'
        }
        
        for page_key, page_title in management_menu_options.items():
            if st.button(
                page_title, 
                key=f"menu_{page_key}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_key else "secondary"
            ):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # 추가 정보
        st.markdown("""
        <div style="text-align:center; margin-top: 1rem; color: #6c757d; font-size: 0.85rem;">
            <p style="margin: 0.25rem 0 0;">Main in Connect@</p>
        </div>
        """, unsafe_allow_html=True)


# ── Main content ─────────────────────────────────────────────
def render_main_content():
    # 로그인 체크 활성화
    if not supabase_auth.is_authenticated():
        st.markdown("""
        <div style="text-align:left; margin:0; padding:0;">
            <p style="font-size:1.05rem; color:#6c757d; margin:.5rem 0 0;">
                Connecta Manager를 사용하려면 먼저 로그인해주세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 현재 선택된 페이지에 따라 다른 컴포넌트 렌더링
    current_page = st.session_state.get('current_page', 'campaign_management')
    
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
    else:
        # 기본값으로 캠페인 관리 표시
        render_campaign_management()


# ── App ──────────────────────────────────────────────────────
def main():
    try:
        load_css()                # 프로젝트 CSS + 위 레이아웃 CSS

        # 인증 상태 초기화
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False

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
