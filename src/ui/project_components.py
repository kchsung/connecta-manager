"""
프로젝트 공통 컴포넌트들 (크롤링 관련 등)
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager

def check_database_for_influencer(platform: str, sns_id: str) -> Dict[str, Any]:
    """데이터베이스에서 인플루언서 정보 확인"""
    try:
        # SNS ID에서 @ 제거
        clean_sns_id = sns_id.replace('@', '') if sns_id else ''
        
        # 데이터베이스에서 인플루언서 정보 조회
        result = db_manager.get_influencer_info(platform, clean_sns_id)
        
        if result["success"] and result["exists"]:
            return {
                "success": True,
                "exists": True,
                "data": result["data"],
                "message": f"✅ 데이터베이스에서 인플루언서를 찾았습니다: {result['data']['influencer_name'] or clean_sns_id}"
            }
        else:
            return {
                "success": True,
                "exists": False,
                "data": None,
                "message": "❌ 데이터베이스에 해당 인플루언서가 없습니다."
            }
    except Exception as e:
        return {
            "success": False,
            "exists": False,
            "data": None,
            "message": f"❌ DB 확인 중 오류가 발생했습니다: {str(e)}"
        }

def perform_crawling(platform: str, url: str, sns_id: str, debug_mode: bool, save_to_db: bool) -> Dict[str, Any]:
    """크롤링 기능이 제거되었습니다."""
    return {
        "success": False,
        "message": "크롤링 기능이 제거되었습니다.",
        "data": None
    }

def render_single_url_crawl():
    """단일 URL 크롤링 컴포넌트 - 크롤링 기능이 제거되었습니다."""
    st.subheader("🔍 단일 URL 크롤링")
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")

def render_batch_url_crawl():
    """복수 URL 크롤링 컴포넌트 - 크롤링 기능이 제거되었습니다."""
    st.subheader("📊 복수 URL 크롤링")
    st.warning("⚠️ 크롤링 기능이 제거되었습니다.")
    st.info("이 기능은 더 이상 사용할 수 없습니다.")