"""
개발 모드 토글 스크립트
이 스크립트를 실행하여 개발 모드를 쉽게 활성화/비활성화할 수 있습니다.
"""

import streamlit as st
import os

def toggle_dev_mode():
    """개발 모드 토글"""
    st.title("🔧 개발 모드 설정")
    
    # 현재 개발 모드 상태 확인
    current_dev_mode = (
        os.getenv("DEV_MODE", "false").lower() == "true" or
        st.session_state.get("dev_mode", False) or
        st.secrets.get("dev_mode", False)
    )
    
    st.write(f"**현재 개발 모드 상태:** {'🟢 활성화' if current_dev_mode else '🔴 비활성화'}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟢 개발 모드 활성화", type="primary"):
            st.session_state.dev_mode = True
            st.success("개발 모드가 활성화되었습니다!")
            st.info("이제 로그인 없이 애플리케이션을 테스트할 수 있습니다.")
            st.rerun()
    
    with col2:
        if st.button("🔴 개발 모드 비활성화"):
            st.session_state.dev_mode = False
            st.success("개발 모드가 비활성화되었습니다!")
            st.info("이제 로그인이 필요합니다.")
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📋 개발 모드 설정 방법")
    st.markdown("""
    **방법 1: 이 페이지에서 토글**
    - 위의 버튼을 사용하여 개발 모드를 활성화/비활성화
    
    **방법 2: 환경 변수 설정**
    ```bash
    set DEV_MODE=true  # Windows
    export DEV_MODE=true  # Linux/Mac
    ```
    
    **방법 3: Streamlit secrets 설정**
    `.streamlit/secrets.toml` 파일에 추가:
    ```toml
    dev_mode = true
    ```
    """)
    
    st.markdown("### ⚠️ 주의사항")
    st.warning("""
    - 개발 모드는 **테스트 목적으로만** 사용하세요
    - 프로덕션 환경에서는 **반드시 비활성화**하세요
    - 개발 모드에서는 인증 없이 데이터베이스에 접근할 수 있습니다
    """)

if __name__ == "__main__":
    toggle_dev_mode()

