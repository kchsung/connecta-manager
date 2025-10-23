"""
AI 분석 공통 함수들
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

def get_completed_crawling_data(client, limit=1000, offset=0):
    """크롤링 완료되고 AI 분석이 필요한 데이터 조회 (페이징) - 재시도 포함"""
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            if not client:
                return []
            # status가 COMPLETE이고 ai_analysis_status가 false인 데이터만 조회
            response = client.table("tb_instagram_crawling").select("*")\
                .eq("status", "COMPLETE")\
                .eq("ai_analysis_status", False)\
                .range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay); retry_delay *= 2; continue
                else:
                    st.error(f"크롤링 데이터 조회 실패(재시도 초과): {error_msg}")
                    return []
            else:
                st.error(f"크롤링 데이터 조회 오류: {error_msg}")
                return []
    return []

def get_completed_crawling_data_count(client):
    """크롤링 완료되고 AI 분석이 필요한 데이터 총 개수"""
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            if not client:
                return 0
            # status가 COMPLETE이고 ai_analysis_status가 false인 데이터 개수만 조회
            response = client.table("tb_instagram_crawling").select("id", count="exact")\
                .eq("status", "COMPLETE")\
                .eq("ai_analysis_status", False).execute()
            return response.count if response.count else 0
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay); retry_delay *= 2; continue
                else:
                    st.error(f"개수 조회 실패(재시도 초과): {error_msg}")
                    return 0
            else:
                st.error(f"개수 조회 오류: {error_msg}")
                return 0
    return 0

def is_recently_analyzed_by_id(client, crawling_id):
    """크롤링 ID 최근 분석 여부(30일) - AI 분석 상태 테이블 사용"""
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            if not client:
                return False
            one_month_ago = datetime.now() - timedelta(days=30)
            # ai_analysis_status 테이블에서 확인
            response = client.table("ai_analysis_status").select("is_analyzed", "analyzed_at")\
                .eq("id", crawling_id)\
                .eq("is_analyzed", True)\
                .gte("analyzed_at", one_month_ago.isoformat()).execute()
            return bool(response.data)
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay); retry_delay *= 2; continue
                else:
                    st.error(f"최근 분석 여부 확인 실패(재시도 초과): {error_msg}")
                    return False
            else:
                st.error(f"최근 분석 여부 확인 오류: {error_msg}")
                return False
    return False

def save_ai_analysis_result(client, crawling_data, analysis_result, crawling_id):
    """AI 분석 결과 저장 - client 주입 버전"""
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            if not client:
                raise Exception("Supabase 클라이언트 없음")

            # 추적용 crawling_id 주입
            if "notes" in analysis_result and isinstance(analysis_result["notes"], dict):
                analysis_result["notes"]["crawling_id"] = crawling_id

            existing_response = client.table("ai_influencer_analyses").select("id")\
                .eq("influencer_id", crawling_id).eq("platform", "instagram").execute()

            if existing_response.data:
                client.table("ai_influencer_analyses").update(analysis_result)\
                    .eq("id", existing_response.data[0]["id"]).execute()
            else:
                client.table("ai_influencer_analyses").insert(analysis_result).execute()
            
            # AI 분석 상태 업데이트 (트리거가 있지만 명시적으로도 업데이트)
            try:
                analyzed_at = analysis_result.get("analyzed_at", datetime.now().isoformat())
                client.table("ai_analysis_status").upsert({
                    "id": crawling_id,
                    "is_analyzed": True,
                    "analyzed_at": analyzed_at,
                    "updated_at": datetime.now().isoformat()
                }).execute()
                
                # tb_instagram_crawling 테이블의 AI 분석 상태도 업데이트
                client.table("tb_instagram_crawling").update({
                    "ai_analysis_status": True,
                    "ai_analyzed_at": analyzed_at,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", crawling_id).execute()
            except Exception as status_error:
                st.warning(f"AI 분석 상태 업데이트 중 오류 (분석 결과는 저장됨): {str(status_error)}")
            
            return

        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay); retry_delay *= 2; continue
                else:
                    st.error(f"AI 분석 결과 저장 실패(재시도 초과): {error_msg}")
                    raise
            else:
                st.error(f"AI 분석 결과 저장 오류: {error_msg}")
                raise

def perform_ai_analysis(data):
    """AI 분석 수행 - 5분 타임아웃, 재시도 없음"""
    from openai import OpenAI
    import time

    timeout_seconds = 300  # 5분 타임아웃

    # API 키 읽기 (환경변수 우선, 그 다음 secrets)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, AttributeError):
            api_key = None
    
    if not api_key or api_key == "your-openai-api-key-here":
        st.error("키가 설정되지 않았습니다.")
        return None

    client = OpenAI(api_key=api_key)

    # 모델 명시 필수 (secrets에서 오버라이드 가능)
    model = st.secrets.get("OPENAI_MODEL", "gpt-5-mini")
    prompt_id = st.secrets.get("OPENAI_PROMPT_ID", "pmpt_68f36e44eab08196b4e75067a3074b7b0c099d8443a9dd49")
    prompt_version = st.secrets.get("OPENAI_PROMPT_VERSION", "4")

    input_data = json.dumps(data, ensure_ascii=False)

    try:
        resp = client.responses.create(
            model=model,
            prompt={"id": prompt_id, "version": prompt_version},
            input=input_data,
            reasoning={"summary": "auto"},
            store=True,
            include=["reasoning.encrypted_content", "web_search_call.action.sources"],
            timeout=timeout_seconds,  # 5분 timeout
        )
        return parse_ai_response(resp)

    except Exception as e:
        st.error(f"AI 분석 수행 중 오류: {e}")
        return None

def parse_ai_response(response):
    """Responses API 표준 파서: output_text 우선, fallback로 content[*].text, 코드펜스 JSON 추출"""
    try:
        text = None

        if getattr(response, "output_text", None):
            text = response.output_text
        elif getattr(response, "output", None):
            chunks = []
            for block in (response.output or []):
                for c in getattr(block, "content", []) or []:
                    if hasattr(c, "text") and c.text:
                        chunks.append(c.text)
            text = "\n".join(chunks) if chunks else None

        if not text:
            st.error("응답에서 텍스트를 찾지 못했습니다.")
            return None

        import re, json as _json
        # ```json ... ``` 우선
        m = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, flags=re.S)
        if m:
            text = m.group(1)

        return _json.loads(text)

    except Exception as e:
        st.error(f"AI 응답 파싱 오류: {e}")
        return None

def transform_to_db_format(ai_input_data, ai_result, crawling_id):
    """AI 분석 결과를 ai_influencer_analyses 테이블 구조에 맞게 변환"""
    try:
        # 기본 데이터 추출 (AI 분석 결과에서 추출)
        # ai_input_data는 {"id": "", "description": "", "posts": ""} 형태
        influencer_id = crawling_id  # influencer_id는 이제 VARCHAR 타입이므로 crawling_id 사용
        platform = "instagram"  # tb_instagram_crawling은 모두 instagram 데이터
        
        # AI 분석 결과에서 기본 정보 추출 (AI가 분석한 결과 사용)
        name = ai_result.get("name", "")
        alias = ai_input_data.get("id", "")  # id를 alias로 사용
        followers = ai_result.get("followers", 0)
        followings = ai_result.get("followings", 0)
        posts_count = ai_result.get("posts_count", 0)
        
        # AI 분석 결과에서 데이터 추출
        category = ai_result.get("category", "기타")
        tags = ai_result.get("tags", [])
        follow_network_analysis = ai_result.get("follow_network_analysis", {})
        comment_authenticity_analysis = ai_result.get("comment_authenticity_analysis", {})
        content_analysis = ai_result.get("content_analysis", {})
        evaluation = ai_result.get("evaluation", {})
        insights = ai_result.get("insights", {})
        summary = ai_result.get("summary", "")
        recommendation = ai_result.get("recommendation", "조건부")
        notes = ai_result.get("notes", {})
        
        # 디버깅: AI 응답 구조 확인
        st.write("🔍 AI 응답 구조 확인:")
        st.write(f"- name: {name}")
        st.write(f"- category: {category}")
        st.write(f"- tags: {tags}")
        st.write(f"- recommendation: {recommendation}")
        st.write(f"- evaluation keys: {list(evaluation.keys()) if evaluation else 'None'}")
        st.write(f"- content_analysis keys: {list(content_analysis.keys()) if content_analysis else 'None'}")
        
        # 추천도 유효성 검증 및 변환 (현재 enum 값에 맞춤)
        valid_recommendations = ["추천", "조건부", "비추천"]
        if recommendation not in valid_recommendations:
            # 유효하지 않은 값은 "조건부"로 기본 설정
            recommendation = "조건부"
        
        # 점수 유효성 검증 (0-10 범위)
        def validate_score(score, default=0):
            try:
                score_val = float(score) if score is not None else default
                return max(0, min(10, score_val))
            except (ValueError, TypeError):
                return default
        
        # evaluation 점수들 검증
        if isinstance(evaluation, dict):
            evaluation["engagement"] = validate_score(evaluation.get("engagement", 0))
            evaluation["activity"] = validate_score(evaluation.get("activity", 0))
            evaluation["communication"] = validate_score(evaluation.get("communication", 0))
            evaluation["growth_potential"] = validate_score(evaluation.get("growth_potential", 0))
            evaluation["overall_score"] = validate_score(evaluation.get("overall_score", 0))
        
        # inference_confidence 검증 (0-1 범위)
        if isinstance(content_analysis, dict):
            confidence = content_analysis.get("inference_confidence", 0.5)
            try:
                confidence_val = float(confidence) if confidence is not None else 0.5
                content_analysis["inference_confidence"] = max(0, min(1, confidence_val))
            except (ValueError, TypeError):
                content_analysis["inference_confidence"] = 0.5
        
        # notes에 크롤링 ID 추가 (나중에 save_ai_analysis_result에서 설정됨)
        if not isinstance(notes, dict):
            notes = {}
        
        # 최종 데이터 구조 생성
        db_data = {
            "influencer_id": influencer_id,
            "platform": platform,
            "name": name,
            "alias": alias,
            "followers": followers,
            "followings": followings,
            "posts_count": posts_count,
            "category": category,
            "tags": tags,
            "follow_network_analysis": follow_network_analysis,
            "comment_authenticity_analysis": comment_authenticity_analysis,
            "content_analysis": content_analysis,
            "evaluation": evaluation,
            "insights": insights,
            "summary": summary,
            "recommendation": recommendation,
            "notes": notes,
            "source": "ai_auto",
            "analyzed_at": datetime.now().isoformat(),
            "analyzed_on": datetime.now().date().isoformat()
        }
        
        # 점수 관련 컬럼들은 모두 generated column이므로 직접 설정하지 않음
        # evaluation 점수들은 evaluation JSON 필드에 저장되고, 
        # DB에서 generated column으로 자동 계산됨
        # if isinstance(evaluation, dict):
        #     db_data["engagement_score"] = evaluation.get("engagement")
        #     db_data["activity_score"] = evaluation.get("activity")
        #     db_data["communication_score"] = evaluation.get("communication")
        #     db_data["growth_potential_score"] = evaluation.get("growth_potential")
        #     db_data["overall_score"] = evaluation.get("overall_score")

        # inference_confidence도 generated column이므로 직접 설정하지 않음
        # if isinstance(content_analysis, dict):
        #     db_data["inference_confidence"] = content_analysis.get("inference_confidence")
        
        return db_data
        
    except Exception as e:
        st.error(f"데이터 변환 중 오류: {str(e)}")
        return None
