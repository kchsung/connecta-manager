"""
성과 관리 관련 공통 컴포넌트들
"""
import streamlit as st
from typing import Dict, Any
from ..db.database import db_manager
from ..db.models import PerformanceMetric  # 사용하지 않더라도 유지


def check_database_for_performance_data(participation_id: str) -> Dict[str, Any]:
    """데이터베이스에서 성과 데이터 확인 (campaign_influencer_contents 테이블 기반)"""
    try:
        result = db_manager.get_performance_data_by_participation(participation_id)

        if result and len(result) > 0:
            return {
                "success": True,
                "exists": True,
                "data": result,  # 모든 콘텐츠 데이터
                "message": f"✅ 성과 데이터를 찾았습니다: {len(result)}개 콘텐츠",
            }
        else:
            return {
                "success": True,
                "exists": False,
                "data": None,
                "message": "❌ 성과 데이터가 없습니다. 먼저 콘텐츠를 등록해주세요.",
            }
    except Exception as e:
        return {
            "success": False,
            "exists": False,
            "data": None,
            "message": f"❌ 성과 데이터 확인 중 오류가 발생했습니다: {str(e)}",
        }


def render_performance_crawl():
    """성과관리 크롤링 컴포넌트 - 크롤링 기능이 제거되었습니다."""
    st.subheader("📈 성과관리 크롤링")
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")


def render_performance_management():
    """성과 관리 메인 컴포넌트 - 탭별 컴포넌트를 import하여 사용"""
    st.subheader("📈 성과 관리")
    st.markdown("캠페인별 성과를 확인하고 인플루언서의 성과를 관리합니다.")

    # 탭별 컴포넌트 import
    from .performance_view_components import render_performance_view_tab
    from .performance_input_components import render_performance_input_tab
    from .performance_report_components import render_performance_report_tab

    tab1, tab2, tab3 = st.tabs(["📊 성과 조회", "✏️ 성과 입력", "📋 리포트"])

    with tab1:
        render_performance_view_tab()

    with tab2:
        render_performance_input_tab()

    with tab3:
        render_performance_report_tab()




