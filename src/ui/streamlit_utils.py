"""
Streamlit 버전 호환성을 위한 유틸리티 함수들
"""
import streamlit as st

def safe_tag(text, **kwargs):
    """
    Streamlit 버전에 관계없이 태그를 안전하게 표시하는 함수
    """
    try:
        # Streamlit 1.28+ 버전에서 사용 가능한 st.badge
        return st.badge(text, **kwargs)
    except AttributeError:
        try:
            # Streamlit 1.24+ 버전에서 사용 가능한 st.tag
            return st.tag(text, **kwargs)
        except AttributeError:
            # 구버전 호환성을 위한 st.markdown 사용
            return st.markdown(f"🏷️ `{text}`")

def safe_badge(text, **kwargs):
    """
    Streamlit 버전에 관계없이 배지를 안전하게 표시하는 함수
    """
    try:
        # Streamlit 1.28+ 버전에서 사용 가능한 st.badge
        return st.badge(text, **kwargs)
    except AttributeError:
        # 구버전 호환성을 위한 st.markdown 사용
        return st.markdown(f"🔖 `{text}`")

def display_tags(tags, max_display=10):
    """
    태그 리스트를 안전하게 표시하는 함수
    """
    if not tags:
        return
    
    st.markdown("**태그**:")
    
    # 태그를 한 줄에 표시 (호환성 문제 해결)
    display_tags = tags[:max_display]
    tag_text = " ".join([f"`{tag}`" for tag in display_tags])
    st.markdown(tag_text)
    
    if len(tags) > max_display:
        st.caption(f"외 {len(tags) - max_display}개 태그...")

def get_streamlit_version():
    """
    현재 Streamlit 버전을 반환하는 함수
    """
    try:
        import streamlit as st
        return st.__version__
    except:
        return "unknown"
