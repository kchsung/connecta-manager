"""
AI 분석 결과 관련 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import numpy as np
import time
from ..db.database import db_manager
from ..supabase.simple_client import simple_client
from ..constants.categories import (
    CATEGORY_OPTIONS,
    CATEGORY_DISPLAY_MAP_WITH_ALL,
)
from .streamlit_utils import display_tags


def _format_category(option: str) -> str:
    return CATEGORY_DISPLAY_MAP_WITH_ALL.get(option, option)

def render_ai_analysis_results():
    """AI 분석 결과 탭"""
    st.subheader("📊 인공지능 분석 결과")
    st.markdown("AI가 분석한 인플루언서 데이터를 조회하고 상세 정보를 확인할 수 있습니다.")
    
    try:
        # 검색 및 필터링 옵션
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 검색", placeholder="이름, 태그, ID로 검색")
        
        with col2:
            category_filter = st.selectbox(
                "📂 카테고리",
                ["전체"] + get_categories(),
                format_func=_format_category
            )
        
        with col3:
            recommendations = ["전체", "추천", "조건부", "비추천"]
            recommendation_filter = st.selectbox("⭐ 추천도", recommendations)
        
        # 페이지네이션 설정
        page_size = st.selectbox("📄 페이지 크기", [10, 25, 50, 100], index=1)
        
        # 검색 실행
        if st.button("🔍 검색", type="primary"):
            with st.spinner("분석 결과를 조회하는 중..."):
                # 전체 개수 조회
                total_count = get_ai_analysis_data_count(search_term, category_filter, recommendation_filter)
                
                if total_count == 0:
                    st.warning("검색 조건에 맞는 분석 결과가 없습니다.")
                    return
                
                st.success(f"총 {total_count:,}개의 분석 결과를 찾았습니다.")
                
                # 페이지네이션
                total_pages = (total_count + page_size - 1) // page_size
                page = st.number_input("페이지", min_value=1, max_value=total_pages, value=1)
                offset = (page - 1) * page_size
                
                # 데이터 조회
                analysis_data = get_ai_analysis_data(search_term, category_filter, recommendation_filter, page_size, offset)
                
                if not analysis_data:
                    st.warning("해당 페이지에 데이터가 없습니다.")
                    return
                
                # 결과 표시
                display_analysis_results(analysis_data, total_count, page, total_pages)
    
    except Exception as e:
        st.error(f"분석 결과 조회 중 오류: {str(e)}")

def get_ai_analysis_data(search_term="", category_filter="전체", recommendation_filter="전체", limit=1000, offset=0):
    """AI 분석 데이터 조회 (페이징 지원) - 재시도 로직 포함"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = simple_client.get_client()
            if not client:
                return []
            
            query = client.table("ai_influencer_analyses_new").select("*")
            
            # 검색 조건
            if search_term:
                # 이름, 태그, influencer_id에서 검색
                query = query.or_(f"name.ilike.%{search_term}%,tags.cs.{{{search_term}}},influencer_id.ilike.%{search_term}%")
            
            # 카테고리 필터
            if category_filter != "전체":
                query = query.eq("category", category_filter)
            
            # 추천도 필터
            if recommendation_filter != "전체":
                query = query.eq("recommendation", recommendation_filter)
            
            response = query.order("analyzed_at", desc=True).range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
            
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    st.error(f"분석 데이터 조회 실패(재시도 초과): {error_msg}")
                    return []
            elif "invalid input value for enum recommendation_ko" in error_msg:
                st.error("🚨 데이터베이스 enum 오류가 발생했습니다.")
                st.warning("🔧 해결 방법:")
                st.markdown("""
                **1단계: 안전한 진단**
                ```sql
                -- diagnose_enum_issue_safe.sql 실행
                ```
                
                **2단계: 최종 수정**
                ```sql
                -- fix_recommendation_enum_final.sql 실행
                ```
                
                **3단계: 확인**
                ```sql
                SELECT recommendation, COUNT(*) FROM ai_influencer_analyses GROUP BY recommendation;
                ```
                """)
                
                # 임시 해결책: recommendation 필터 없이 조회
                st.info("🔄 임시 해결책: 추천도 필터 없이 데이터를 조회합니다.")
                try:
                    query = client.table("ai_influencer_analyses_new").select("*")
                    if search_term:
                        query = query.or_(f"name.ilike.%{search_term}%,tags.cs.{{{search_term}}},influencer_id.ilike.%{search_term}%")
                    if category_filter != "전체":
                        query = query.eq("category", category_filter)
                    # recommendation 필터는 제외
                    response = query.order("analyzed_at", desc=True).range(offset, offset + limit - 1).execute()
                    return response.data if response.data else []
                except Exception as fallback_error:
                    st.error(f"임시 해결책도 실패했습니다: {str(fallback_error)}")
                    return []
            else:
                st.error(f"분석 데이터 조회 중 오류: {error_msg}")
                return []
    
    return []

def get_ai_analysis_data_count(search_term="", category_filter="전체", recommendation_filter="전체"):
    """AI 분석 데이터 총 개수 조회 - 재시도 로직 포함"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = simple_client.get_client()
            if not client:
                return 0
            
            query = client.table("ai_influencer_analyses").select("id", count="exact")
            
            # 검색 조건
            if search_term:
                # 이름, 태그, influencer_id에서 검색
                query = query.or_(f"name.ilike.%{search_term}%,tags.cs.{{{search_term}}},influencer_id.ilike.%{search_term}%")
            
            # 카테고리 필터
            if category_filter != "전체":
                query = query.eq("category", category_filter)
            
            # 추천도 필터
            if recommendation_filter != "전체":
                query = query.eq("recommendation", recommendation_filter)
            
            response = query.execute()
            return response.count if response.count else 0
            
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    st.error(f"분석 데이터 개수 조회 실패(재시도 초과): {error_msg}")
                    return 0
            elif "invalid input value for enum recommendation_ko" in error_msg:
                st.error("🚨 데이터베이스 enum 오류가 발생했습니다.")
                st.warning("🔧 해결 방법:")
                st.markdown("""
                **1단계: 안전한 진단**
                ```sql
                -- diagnose_enum_issue_safe.sql 실행
                ```
                
                **2단계: 최종 수정**
                ```sql
                -- fix_recommendation_enum_final.sql 실행
                ```
                
                **3단계: 확인**
                ```sql
                SELECT recommendation, COUNT(*) FROM ai_influencer_analyses GROUP BY recommendation;
                ```
                """)
                
                # 임시 해결책: recommendation 필터 없이 조회
                st.info("🔄 임시 해결책: 추천도 필터 없이 개수를 조회합니다.")
                try:
                    query = client.table("ai_influencer_analyses").select("id", count="exact")
                    if search_term:
                        query = query.or_(f"name.ilike.%{search_term}%,tags.cs.{{{search_term}}},influencer_id.ilike.%{search_term}%")
                    if category_filter != "전체":
                        query = query.eq("category", category_filter)
                    # recommendation 필터는 제외
                    response = query.execute()
                    return response.count if response.count else 0
                except Exception as fallback_error:
                    st.error(f"임시 해결책도 실패했습니다: {str(fallback_error)}")
                    return 0
            else:
                st.error(f"분석 데이터 개수 조회 중 오류: {error_msg}")
                return 0
    
    return 0

def get_categories() -> List[str]:
    """표준 카테고리 목록 반환"""
    return CATEGORY_OPTIONS

def display_analysis_results(analysis_data, total_count, current_page, total_pages):
    """분석 결과 표시"""
    st.markdown(f"### 📋 분석 결과 ({len(analysis_data)}개 표시 중, 전체 {total_count:,}개)")
    st.markdown(f"**페이지 {current_page}/{total_pages}**")
    
    # 결과 테이블
    for i, analysis in enumerate(analysis_data):
        # None 값 안전 처리
        name = analysis.get('name') or 'Unknown'
        alias = analysis.get('alias') or 'N/A'
        recommendation = analysis.get('recommendation') or 'N/A'
        with st.expander(f"📊 {name} ({alias}) - {recommendation}"):
            display_analysis_detail(analysis)

def display_analysis_detail(analysis):
    """개별 분석 결과 상세 표시"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📋 기본 정보")
        # None 값 안전 처리
        followers = analysis.get('followers') or 0
        followings = analysis.get('followings') or 0
        posts_count = analysis.get('posts_count') or 0
        analyzed_at = analysis.get('analyzed_at')
        
        basic_info = {
            "이름": analysis.get('name') or 'N/A',
            "별명": analysis.get('alias') or 'N/A',
            "플랫폼": analysis.get('platform') or 'N/A',
            "카테고리": analysis.get('category') or 'N/A',
            "팔로워": f"{followers:,}",
            "팔로잉": f"{followings:,}",
            "게시물 수": f"{posts_count:,}",
            "추천도": analysis.get('recommendation') or 'N/A',
            "분석일": analyzed_at[:10] if analyzed_at else 'N/A'
        }
        
        for key, value in basic_info.items():
            st.write(f"**{key}**: {value}")
        
        # 태그 표시 (호환성 문제 해결)
        tags = analysis.get('tags', [])
        if tags:
            display_tags(tags, max_display=10)
    
    with col2:
        st.markdown("#### 📊 평가 점수")
        evaluation = analysis.get('evaluation', {})
        if evaluation:
            score_metrics = {
                "참여도": evaluation.get('engagement') or 0,
                "활동성": evaluation.get('activity') or 0,
                "소통력": evaluation.get('communication') or 0,
                "성장성": evaluation.get('growth_potential') or 0,
                "종합점수": evaluation.get('overall_score') or 0
            }
            
            for metric, score in score_metrics.items():
                if isinstance(score, (int, float)) and score is not None:
                    st.metric(metric, f"{score:.1f}/10")
                else:
                    st.metric(metric, "N/A")
    
    # 요약 정보
    summary = analysis.get('summary')
    if summary and summary.strip():
        st.markdown("#### 📝 분석 요약")
        st.write(summary)
    
    # 상세 분석 섹션들
    st.markdown("#### 🔍 상세 분석")
    
    # 평가 섹션
    if evaluation:
        display_analysis_section(evaluation, "📊 평가")
    
    # 콘텐츠 분석 섹션
    content_analysis = analysis.get('content_analysis', {})
    if content_analysis:
        display_analysis_section(content_analysis, "📝 콘텐츠 분석")
    
    # 인사이트 섹션
    insights = analysis.get('insights', {})
    if insights:
        display_analysis_section(insights, "💡 인사이트")
    
    # 커머스 지향성 분석 섹션
    commerce_analysis = analysis.get('commerce_orientation_analysis', {})
    if commerce_analysis:
        display_analysis_section(commerce_analysis, "🛒 커머스 지향성 분석")
    
    # 네트워크 분석 섹션
    follow_network = analysis.get('follow_network_analysis', {})
    if follow_network:
        display_analysis_section(follow_network, "🌐 네트워크 분석")
    
    # 댓글 진정성 분석 섹션
    comment_analysis = analysis.get('comment_authenticity_analysis', {})
    if comment_analysis:
        display_analysis_section(comment_analysis, "💬 댓글 진정성 분석")

def get_field_display_name(key):
    """필드 키를 한국어 표시명으로 변환"""
    field_mapping = {
        # 기본 정보
        "name": "이름",
        "alias": "별명",
        "platform": "플랫폼",
        "category": "카테고리",
        "followers": "팔로워 수",
        "followings": "팔로잉 수",
        "posts_count": "게시물 수",
        "tags": "태그",
        "recommendation": "추천도",
        "summary": "요약",
        
        # 평가 점수
        "engagement": "참여도",
        "activity": "활동성",
        "communication": "소통력",
        "growth_potential": "성장성",
        "overall_score": "종합점수",
        "brand_fit_comment": "브랜드 적합성 코멘트",
        
        # 콘텐츠 분석
        "dominant_topics": "주요 주제",
        "narrative_style": "내러티브 스타일",
        "visual_style": "비주얼 스타일",
        "audience_focus": "타겟 오디언스",
        "content_goal_inference": "콘텐츠 목표 추론",
        "inferred_tone": "추론된 톤",
        "inference_confidence": "추론 신뢰도",
        "content_type": "콘텐츠 유형",
        "engagement_rate": "참여율",
        
        # 인사이트
        "strengths": "강점",
        "weaknesses": "약점",
        "opportunities": "기회",
        "threats": "위협",
        "recommendations": "추천사항",
        
        # 기타
        "notes": "노트",
        "additional_info": "추가 정보",
        "analysis_date": "분석 날짜",
        "confidence_level": "신뢰도 수준",
        
        # 커머스 지향성
        "interpretation": "해석",
        "bragging_signals": "과시 신호",
        "selling_effort_signals": "판매 노력 신호",
        "creator_archetype": "크리에이터 유형",
        "primary_motivation": "주요 동기",
        "monetization_intent_level": "수익화 성향 점수",
        "bragging_orientation_level": "과시 지향 점수",
        "content_fit_for_selling_score": "커머스 적합도 점수"
    }
    
    return field_mapping.get(key, key)

def display_analysis_section(data, section_title):
    """분석 섹션 데이터를 읽기 쉬운 형태로 표시"""
    if not data:
        st.info("분석 데이터가 없습니다.")
        return
    
    st.markdown(f"**{section_title}**")
    
    for key, value in data.items():
        display_name = get_field_display_name(key)
        
        if isinstance(value, dict):
            st.markdown(f"**{display_name}**:")
            for sub_key, sub_value in value.items():
                sub_display_name = get_field_display_name(sub_key)
                # None 값 안전 처리
                safe_sub_value = sub_value if sub_value is not None else "없음"
                st.write(f"  - {sub_display_name}: {safe_sub_value}")
        elif isinstance(value, list):
            if value:
                # 리스트 내 None 값들도 안전하게 처리
                safe_values = [str(v) if v is not None else "없음" for v in value]
                st.markdown(f"**{display_name}**: {', '.join(safe_values)}")
            else:
                st.markdown(f"**{display_name}**: 없음")
        else:
            if value is not None and value != "":
                st.markdown(f"**{display_name}**: {value}")
            else:
                st.markdown(f"**{display_name}**: 없음")
