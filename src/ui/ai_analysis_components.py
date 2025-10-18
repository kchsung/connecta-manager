"""
인공지능 분석 관련 컴포넌트들
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
from ..db.database import db_manager
from ..supabase.simple_client import simple_client

def render_ai_analysis_management():
    """인공지능 분석 관리 메인 컴포넌트"""
    st.subheader("🤖 인공지능 분석")
    st.markdown("AI를 활용한 인플루언서 분석 및 평가를 제공합니다.")
    
    # AI 분석 탭으로 분리
    tab1, tab2, tab3 = st.tabs([
        "🚀 인공지능 분석 실행", 
        "📊 인공지능 분석 결과", 
        "📈 인공지능 분석 통계"
    ])
    
    with tab1:
        render_ai_analysis_execution()
    
    with tab2:
        render_ai_analysis_results()
    
    with tab3:
        render_ai_analysis_statistics()

def render_ai_analysis_execution():
    """AI 분석 실행 탭"""
    st.subheader("🚀 인공지능 분석 실행")
    st.markdown("크롤링이 완료된 인플루언서 데이터를 AI로 분석합니다.")
    
    # OpenAI API 키 확인
    openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. secrets.toml 또는 .env 파일에 OPENAI_API_KEY를 설정해주세요.")
        return
    
    # 분석 조건 표시
    st.info("""
    **분석 조건:**
    - tb_instagram_crawling 테이블의 status가 'COMPLETE'인 데이터만 분석
    - 1달 이내에 분석된 데이터는 재분석하지 않음
    - 새로운 데이터는 생성, 기존 데이터는 업데이트
    """)
    
    # 분석 실행 버튼
    if st.button("🤖 AI 분석 시작", type="primary", use_container_width=True):
        with st.spinner("AI 분석을 실행 중입니다..."):
            try:
                result = execute_ai_analysis()
                if result["success"]:
                    st.success(f"AI 분석이 완료되었습니다. {result['analyzed_count']}명의 인플루언서가 분석되었습니다.")
                    if result["skipped_count"] > 0:
                        st.info(f"{result['skipped_count']}명은 최근에 분석되어 건너뛰었습니다.")
                else:
                    st.error(f"AI 분석 중 오류가 발생했습니다: {result['error']}")
            except Exception as e:
                st.error(f"AI 분석 실행 중 오류가 발생했습니다: {str(e)}")
    
    # 디버깅용: 크롤링 데이터 미리보기
    if st.button("🔍 크롤링 데이터 미리보기", use_container_width=True):
        try:
            crawling_data = get_completed_crawling_data()
            if crawling_data:
                st.subheader("📊 크롤링 데이터 미리보기")
                st.write(f"총 {len(crawling_data)}개의 크롤링 데이터가 있습니다.")
                
                # 첫 번째 데이터 구조 확인
                if len(crawling_data) > 0:
                    first_data = crawling_data[0]
                    st.write("**첫 번째 데이터 구조:**")
                    st.json(first_data)
                    
                    # AI 입력 데이터 구성 예시
                    ai_input_example = {
                        "id": first_data.get("id", ""),
                        "description": first_data.get("description", ""),
                        "posts": first_data.get("posts", "")[:500] + "..." if len(first_data.get("posts", "")) > 500 else first_data.get("posts", "")
                    }
                    st.write("**AI 분석용 입력 데이터 예시:**")
                    st.json(ai_input_example)
                    
                    # posts 필드 확인
                    posts_content = first_data.get("posts", "")
                    if posts_content:
                        st.write("**posts 필드 내용 (처음 500자):**")
                        st.text(posts_content[:500])
                    else:
                        st.warning("posts 필드가 비어있습니다.")
            else:
                st.warning("크롤링 데이터가 없습니다.")
        except Exception as e:
            st.error(f"데이터 미리보기 중 오류: {str(e)}")

def execute_ai_analysis():
    """AI 분석 실행 함수"""
    try:
        # 1. 크롤링 완료된 데이터 조회
        crawling_data = get_completed_crawling_data()
        
        if not crawling_data:
            return {"success": False, "error": "분석할 크롤링 데이터가 없습니다."}
        
        total_count = len(crawling_data)
        analyzed_count = 0
        skipped_count = 0
        
        # 진행 상황 표시를 위한 프로그레스 바
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, data in enumerate(crawling_data):
            current_progress = (index + 1) / total_count
            progress_bar.progress(current_progress)
            status_text.text(f"진행 중: {index + 1}/{total_count} - {data.get('id', 'unknown')}")
            
            # 2. AI 분석용 JSON 데이터 구성 (id, description, posts)
            try:
                # posts는 TEXT 필드이므로 그대로 사용
                posts_content = data.get("posts", "")
                if not posts_content:
                    st.error(f"posts 데이터가 비어있음: {data.get('id', 'unknown')}")
                    return {"success": False, "error": f"posts 데이터가 비어있음: {data.get('id', 'unknown')}"}
                
                # AI 분석용 JSON 구성
                ai_input_data = {
                    "id": data.get("id", ""),
                    "description": data.get("description", ""),
                    "posts": posts_content
                }
                    
            except Exception as e:
                st.error(f"AI 입력 데이터 구성 중 오류: {data.get('id', 'unknown')} - 오류: {str(e)}")
                return {"success": False, "error": f"AI 입력 데이터 구성 중 오류: {str(e)}"}
            
            # 3. 최근 분석 여부 확인 (1달 이내) - id를 기준으로 확인
            if is_recently_analyzed_by_id(data["id"]):
                skipped_count += 1
                continue
            
            # 4. AI 분석 수행 (구성된 JSON 데이터 전달)
            analysis_result = perform_ai_analysis(ai_input_data)
            
            if not analysis_result:
                st.error(f"AI 분석 실패: {data.get('id', 'unknown')}")
                return {"success": False, "error": f"AI 분석 실패: {data.get('id', 'unknown')}"}
            
            # 5. 데이터 변환 (크롤링 ID 포함)
            transformed_result = transform_to_db_format(ai_input_data, analysis_result, data["id"])
            if not transformed_result:
                st.error(f"데이터 변환 실패: {data.get('id', 'unknown')}")
                return {"success": False, "error": f"데이터 변환 실패: {data.get('id', 'unknown')}"}
            
            # 6. 결과 저장
            try:
                save_ai_analysis_result(data, transformed_result, data["id"])
                analyzed_count += 1
            except Exception as e:
                st.error(f"결과 저장 실패: {data.get('id', 'unknown')} - 오류: {str(e)}")
                return {"success": False, "error": f"결과 저장 실패: {str(e)}"}
        
        # 완료 후 프로그레스 바와 상태 텍스트 정리
        progress_bar.progress(1.0)
        status_text.text("분석 완료!")
        
        return {
            "success": True,
            "analyzed_count": analyzed_count,
            "skipped_count": skipped_count
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_completed_crawling_data():
    """크롤링 완료된 데이터 조회"""
    try:
        # Supabase에서 크롤링 완료된 데이터 조회
        client = simple_client.get_client()
        if not client:
            return []
        
        response = client.table("tb_instagram_crawling").select("*").eq("status", "COMPLETE").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"크롤링 데이터 조회 중 오류: {str(e)}")
        return []

def is_recently_analyzed(influencer_id, platform):
    """최근 분석 여부 확인 (1달 이내) - 기존 함수 (호환성 유지)"""
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        
        client = simple_client.get_client()
        if not client:
            return False
        
        response = client.table("ai_influencer_analyses").select("analyzed_at").eq("influencer_id", influencer_id).eq("platform", platform).gte("analyzed_at", one_month_ago.isoformat()).execute()
        
        return len(response.data) > 0 if response.data else False
    except Exception as e:
        st.error(f"최근 분석 여부 확인 중 오류: {str(e)}")
        return False

def is_recently_analyzed_by_id(crawling_id):
    """크롤링 ID 기준으로 최근 분석 여부 확인 (1달 이내)"""
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        
        client = simple_client.get_client()
        if not client:
            return False
        
        # influencer_id와 platform 기준으로 확인 (influencer_id는 이제 VARCHAR 타입)
        response = client.table("ai_influencer_analyses").select("analyzed_at").eq("influencer_id", crawling_id).eq("platform", "instagram").gte("analyzed_at", one_month_ago.isoformat()).execute()
        
        return len(response.data) > 0 if response.data else False
    except Exception as e:
        st.error(f"최근 분석 여부 확인 중 오류: {str(e)}")
        return False

def perform_ai_analysis(data):
    """AI 분석 수행"""
    try:
        # OpenAI API 호출 (새로운 Responses API 사용)
        from openai import OpenAI
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            st.error("OpenAI API 키가 설정되지 않았습니다.")
            return None
        
        client = OpenAI(api_key=api_key)
        
        # 프롬프트 ID 설정 (실제 프롬프트 ID로 변경 필요)
        prompt_id = st.secrets.get("OPENAI_PROMPT_ID", "pmpt_68f36e44eab08196b4e75067a3074b7b0c099d8443a9dd49")
        prompt_version = st.secrets.get("OPENAI_PROMPT_VERSION", "4")
        
        # 데이터를 input으로 전달 (문자열로 변환)
        # OpenAI Responses API는 input이 문자열 또는 문자열 배열이어야 함
        input_data = json.dumps(data, ensure_ascii=False)  # JSON 문자열로 변환
        
        response = client.responses.create(
            prompt={
                "id": prompt_id,
                "version": prompt_version
            },
            input=input_data,
            reasoning={
                "summary": "auto"
            },
            store=True,
            include=[
                "reasoning.encrypted_content",
                "web_search_call.action.sources"
            ]
        )
        
        # 응답 파싱 및 ai_influencer_analyses 테이블 구조에 맞게 변환
        analysis_result = parse_ai_response(response)
        
        return analysis_result
        
    except Exception as e:
        st.error(f"AI 분석 수행 중 오류: {str(e)}")
        return None

def parse_ai_response(response):
    """AI 응답을 파싱하여 JSON 객체로 변환"""
    try:
        # 응답 객체의 속성들을 확인
        analysis_result = None
        
        # OpenAI Responses API의 실제 응답 구조에 맞게 수정
        # output_text가 실제 JSON 데이터를 포함하고 있음
        if hasattr(response, 'output_text') and response.output_text:
            analysis_result = response.output_text
        elif hasattr(response, 'output') and response.output:
            analysis_result = response.output
        elif hasattr(response, 'text') and response.text:
            analysis_result = response.text
        else:
            st.error("응답에서 분석 결과를 찾을 수 없습니다.")
            return None
        
        # JSON 파싱
        if isinstance(analysis_result, str):
            try:
                result = json.loads(analysis_result)
                return result
            except json.JSONDecodeError:
                # JSON이 아닌 경우 텍스트에서 JSON 추출
                if "```json" in analysis_result:
                    analysis_result = analysis_result.split("```json")[1].split("```")[0]
                elif "```" in analysis_result:
                    analysis_result = analysis_result.split("```")[1].split("```")[0]
                
                try:
                    result = json.loads(analysis_result)
                    return result
                except json.JSONDecodeError:
                    st.error("JSON 파싱에 실패했습니다.")
                    return None
        elif isinstance(analysis_result, dict):
            return analysis_result
        elif isinstance(analysis_result, list) and len(analysis_result) > 0:
            # 리스트 형태의 응답인 경우 첫 번째 요소에서 content 추출
            first_item = analysis_result[0]
            if hasattr(first_item, 'content') and first_item.content:
                content_list = first_item.content
                if isinstance(content_list, list) and len(content_list) > 0:
                    content_item = content_list[0]
                    if hasattr(content_item, 'text'):
                        try:
                            result = json.loads(content_item.text)
                            return result
                        except json.JSONDecodeError:
                            st.error("리스트 응답 텍스트에서 JSON 파싱에 실패했습니다.")
                            return None
        else:
            st.error("예상치 못한 응답 형식입니다.")
            return None
            
    except Exception as e:
        st.error(f"AI 응답 파싱 중 오류: {str(e)}")
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
        recommendation = ai_result.get("recommendation", "보통")
        notes = ai_result.get("notes", {})
        
        # 디버깅: AI 응답 구조 확인
        st.write("🔍 AI 응답 구조 확인:")
        st.write(f"- name: {name}")
        st.write(f"- category: {category}")
        st.write(f"- tags: {tags}")
        st.write(f"- recommendation: {recommendation}")
        st.write(f"- evaluation keys: {list(evaluation.keys()) if evaluation else 'None'}")
        st.write(f"- content_analysis keys: {list(content_analysis.keys()) if content_analysis else 'None'}")
        
        # 추천도 유효성 검증 및 변환
        valid_recommendations = ["매우 추천", "추천", "보통", "비추천", "매우 비추천", "조건부"]
        if recommendation not in valid_recommendations:
            # "조건부" 추천도는 "보통"으로 변환
            if recommendation == "조건부":
                recommendation = "보통"
            else:
                recommendation = "보통"
        
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
        
        return db_data
        
    except Exception as e:
        st.error(f"데이터 변환 중 오류: {str(e)}")
        return None

def save_ai_analysis_result(crawling_data, analysis_result, crawling_id):
    """AI 분석 결과 저장 (이미 변환된 데이터 구조 사용)"""
    try:
        client = simple_client.get_client()
        if not client:
            return
        
        # analysis_result는 이미 transform_to_db_format에서 변환된 데이터
        # influencer_id는 이미 crawling_id로 설정됨
        
        # 크롤링 ID를 notes에 추가 (추적용)
        if "notes" in analysis_result and isinstance(analysis_result["notes"], dict):
            analysis_result["notes"]["crawling_id"] = crawling_id
        
        # 기존 데이터 확인 (influencer_id 기준)
        existing_response = client.table("ai_influencer_analyses").select("id").eq("influencer_id", crawling_id).eq("platform", "instagram").execute()
        
        if existing_response.data:
            # 업데이트
            client.table("ai_influencer_analyses").update(analysis_result).eq("id", existing_response.data[0]["id"]).execute()
        else:
            # 새로 생성
            client.table("ai_influencer_analyses").insert(analysis_result).execute()
            
    except Exception as e:
        st.error(f"AI 분석 결과 저장 중 오류: {str(e)}")

def render_ai_analysis_results():
    """AI 분석 결과 탭"""
    st.subheader("📊 인공지능 분석 결과")
    st.markdown("AI 분석 결과를 조회하고 필터링할 수 있습니다.")
    
    # 검색 및 필터링
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 검색 (이름, 태그, influencer_id)", placeholder="인플루언서 이름, 태그, 또는 influencer_id를 입력하세요")
    
    with col2:
        category_filter = st.selectbox("📂 카테고리", ["전체"] + get_categories())
    
    with col3:
        recommendation_filter = st.selectbox("⭐ 추천도", ["전체", "매우 추천", "추천", "보통", "비추천", "매우 비추천"])
    
    # 분석 결과 조회
    try:
        analysis_data = get_ai_analysis_data(search_term, category_filter, recommendation_filter)
        
        if not analysis_data:
            st.warning("분석 결과가 없습니다.")
            return
        
        # 화면을 좌우로 분할
        left_col, right_col = st.columns([1, 2])
        
        with left_col:
            st.markdown("### 📋 검색 결과")
            st.markdown(f"총 {len(analysis_data)}개의 결과")
            
            # 좌측: 검색 리스트 (이름, 아이디, 플랫폼명만 표시)
            selected_analysis = None
            for i, analysis in enumerate(analysis_data):
                # 각 항목을 클릭 가능한 버튼으로 표시
                if st.button(
                    f"📊 {analysis['name']}\n"
                    f"🆔 {analysis['influencer_id']}\n"
                    f"📱 {analysis['platform']}",
                    key=f"select_{analysis['id']}",
                    use_container_width=True
                ):
                    selected_analysis = analysis
                    st.session_state.selected_analysis = analysis
        
        with right_col:
            st.markdown("### 📊 상세 정보")
            
            # 세션 상태에서 선택된 분석 결과 가져오기
            if 'selected_analysis' in st.session_state:
                selected_analysis = st.session_state.selected_analysis
            
            if selected_analysis:
                show_detailed_analysis_improved(selected_analysis)
            else:
                st.info("좌측에서 인플루언서를 선택하면 상세 정보가 표시됩니다.")
    
    except Exception as e:
        st.error(f"분석 결과 조회 중 오류: {str(e)}")

def get_ai_analysis_data(search_term="", category_filter="전체", recommendation_filter="전체"):
    """AI 분석 데이터 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return []
        
        query = client.table("ai_influencer_analyses").select("*")
        
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
        
        response = query.order("analyzed_at", desc=True).execute()
        return response.data if response.data else []
        
    except Exception as e:
        st.error(f"분석 데이터 조회 중 오류: {str(e)}")
        return []

def get_categories():
    """카테고리 목록 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return []
        
        response = client.table("ai_influencer_analyses").select("category").execute()
        categories = list(set([item["category"] for item in response.data if item.get("category")]))
        return sorted(categories)
    except:
        return []

def display_analysis_section(data):
    """분석 섹션 데이터를 읽기 쉬운 형태로 표시"""
    if not data:
        st.info("분석 데이터가 없습니다.")
        return
    
    if isinstance(data, dict):
        for key, value in data.items():
            korean_key = get_korean_field_name(key)
            
            if isinstance(value, (dict, list)):
                # 중첩된 객체나 배열인 경우
                st.markdown(f"**{korean_key}:**")
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        korean_sub_key = get_korean_field_name(sub_key)
                        st.markdown(f"  - {korean_sub_key}: {sub_value}")
                else:  # list
                    for item in value:
                        st.markdown(f"  - {item}")
            else:
                # 단순 값인 경우
                st.markdown(f"**{korean_key}:** {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            st.markdown(f"{i}. {item}")
    else:
        st.markdown(str(data))

def get_korean_field_name(key):
    """영어 필드명을 한국어로 변환"""
    field_mapping = {
        # 팔로워 네트워크 분석
        "followers": "팔로워 수",
        "followings": "팔로잉 수", 
        "inference_reason": "추론 근거",
        "impact_on_brand_fit": "브랜드 적합성 영향",
        "network_type_inference": "네트워크 유형 추론",
        "influence_authenticity_score": "영향력 진정성 점수",
        "ratio_followers_to_followings": "팔로워/팔로잉 비율",
        
        # 댓글 진정성 분석
        "comment_authenticity": "댓글 진정성",
        "bot_detection": "봇 탐지",
        "engagement_quality": "참여 품질",
        "interaction_pattern": "상호작용 패턴",
        
        # 콘텐츠 분석
        "content_theme": "콘텐츠 테마",
        "posting_frequency": "게시 빈도",
        "content_quality": "콘텐츠 품질",
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
        "confidence_level": "신뢰도 수준"
    }
    
    return field_mapping.get(key, key)

def show_detailed_analysis_improved(analysis):
    """개선된 상세 분석 결과 표시 - 모든 AI 분석 정보를 표시"""
    
    # 기본 정보 섹션
    st.markdown("### 📋 기본 정보")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("이름", analysis.get('name', 'N/A'))
        st.metric("별명", analysis.get('alias', 'N/A'))
    
    with col2:
        st.metric("플랫폼", analysis.get('platform', 'N/A'))
        st.metric("카테고리", analysis.get('category', 'N/A'))
    
    with col3:
        st.metric("팔로워", f"{analysis.get('followers', 0):,}명")
        st.metric("팔로잉", f"{analysis.get('followings', 0):,}명")
    
    with col4:
        st.metric("게시물 수", f"{analysis.get('posts_count', 0):,}개")
        st.metric("추천도", analysis.get('recommendation', 'N/A'))
    
    # 태그 표시
    if analysis.get('tags'):
        st.markdown("**🏷️ 태그:**")
        tags = analysis['tags'] if isinstance(analysis['tags'], list) else []
        if tags:
            tag_cols = st.columns(min(len(tags), 5))
            for i, tag in enumerate(tags[:5]):
                with tag_cols[i]:
                    st.markdown(f"`{tag}`")
        else:
            st.markdown("태그 없음")
    
    # 요약 정보
    if analysis.get('summary'):
        st.markdown("### 📝 AI 분석 요약")
        st.info(analysis['summary'])
    
    # 평가 점수 섹션
    evaluation = analysis.get('evaluation', {})
    if evaluation:
        st.markdown("### ⭐ 평가 점수")
        score_cols = st.columns(5)
        
        with score_cols[0]:
            st.metric("참여도", f"{evaluation.get('engagement', 0)}/10")
        with score_cols[1]:
            st.metric("활동성", f"{evaluation.get('activity', 0)}/10")
        with score_cols[2]:
            st.metric("소통능력", f"{evaluation.get('communication', 0)}/10")
        with score_cols[3]:
            st.metric("성장잠재력", f"{evaluation.get('growth_potential', 0)}/10")
        with score_cols[4]:
            st.metric("종합점수", f"{evaluation.get('overall_score', 0)}/10")
    
    # 상세 분석 섹션들
    st.markdown("### 🔍 상세 분석")
    
    # 팔로워 네트워크 분석
    if analysis.get("follow_network_analysis"):
        with st.expander("👥 팔로워 네트워크 분석", expanded=False):
            display_analysis_section(analysis["follow_network_analysis"])
    
    # 댓글 진정성 분석
    if analysis.get("comment_authenticity_analysis"):
        with st.expander("💬 댓글 진정성 분석", expanded=False):
            display_analysis_section(analysis["comment_authenticity_analysis"])
    
    # 콘텐츠 분석
    if analysis.get("content_analysis"):
        with st.expander("📝 콘텐츠 분석", expanded=False):
            display_analysis_section(analysis["content_analysis"])
    
    # 인사이트
    if analysis.get("insights"):
        with st.expander("💡 인사이트", expanded=False):
            display_analysis_section(analysis["insights"])
    
    # 추가 노트
    if analysis.get("notes"):
        with st.expander("📋 추가 노트", expanded=False):
            display_analysis_section(analysis["notes"])
    

def show_detailed_analysis(analysis):
    """상세 분석 결과 표시 (기존 함수 - 호환성 유지)"""
    st.markdown("### 📊 상세 분석 결과")
    
    # 팔로워 네트워크 분석
    if analysis.get("follow_network_analysis"):
        st.markdown("**👥 팔로워 네트워크 분석:**")
        display_analysis_section(analysis["follow_network_analysis"])
    
    # 댓글 진정성 분석
    if analysis.get("comment_authenticity_analysis"):
        st.markdown("**💬 댓글 진정성 분석:**")
        display_analysis_section(analysis["comment_authenticity_analysis"])
    
    # 콘텐츠 분석
    if analysis.get("content_analysis"):
        st.markdown("**📝 콘텐츠 분석:**")
        display_analysis_section(analysis["content_analysis"])
    
    # 인사이트
    if analysis.get("insights"):
        st.markdown("**💡 인사이트:**")
        display_analysis_section(analysis["insights"])
    
    # 추가 노트
    if analysis.get("notes"):
        st.markdown("**📋 추가 노트:**")
        display_analysis_section(analysis["notes"])

def render_ai_analysis_statistics():
    """AI 분석 통계 탭 - 고도화된 버전"""
    st.subheader("📈 인공지능 분석 통계")
    st.markdown("AI 분석 결과의 모든 수치 정보를 종합적으로 분석합니다.")
    
    try:
        # 전체 통계 개요
        render_overview_statistics()
        
        # 탭으로 분리된 상세 통계
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 기본 계정 정보", 
            "🔍 네트워크 분석", 
            "📈 활동성/반응성", 
            "💬 댓글 진정성", 
            "🎯 평가 점수"
        ])
        
        with tab1:
            render_basic_account_statistics()
        
        with tab2:
            render_network_analysis_statistics()
        
        with tab3:
            render_activity_metrics_statistics()
        
        with tab4:
            render_comment_authenticity_statistics()
        
        with tab5:
            render_evaluation_scores_statistics()
    
    except Exception as e:
        st.error(f"통계 조회 중 오류: {str(e)}")

def render_overview_statistics():
    """전체 통계 개요"""
    st.markdown("### 📊 전체 통계 개요")
    
    # 기본 통계
    total_analyses = get_total_analyses_count()
    recent_analyses = get_recent_analyses_count()
    avg_score = get_average_overall_score()
    recommendation_dist = get_recommendation_distribution()
    most_common = max(recommendation_dist.items(), key=lambda x: x[1])[0] if recommendation_dist else "없음"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 분석 수", f"{total_analyses:,}건")
    
    with col2:
        st.metric("최근 7일 분석", f"{recent_analyses:,}건")
    
    with col3:
        st.metric("평균 종합점수", f"{avg_score:.1f}/10")
    
    with col4:
        st.metric("가장 많은 추천도", most_common)
    
    # 추천도 분포 차트
    if recommendation_dist:
        col1, col2 = st.columns([1, 1])
        with col1:
            fig = px.pie(
                values=list(recommendation_dist.values()),
                names=list(recommendation_dist.keys()),
                title="추천도 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            category_stats = get_category_statistics()
            if category_stats:
                fig = px.bar(
                    x=list(category_stats.keys()),
                    y=list(category_stats.values()),
                    title="카테고리별 분석 수"
                )
                st.plotly_chart(fig, use_container_width=True)

def render_basic_account_statistics():
    """기본 계정 정보 통계"""
    st.markdown("### 📊 기본 계정 정보 통계")
    
    try:
        # 기본 계정 정보 조회
        basic_stats = get_basic_account_statistics()
        
        if not basic_stats:
            st.warning("기본 계정 정보가 없습니다.")
            return
        
        # 팔로워 수 통계
        st.markdown("#### 👥 팔로워 수 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 팔로워", f"{basic_stats['avg_followers']:,.0f}명")
        with col2:
            st.metric("중앙값 팔로워", f"{basic_stats['median_followers']:,.0f}명")
        with col3:
            st.metric("최대 팔로워", f"{basic_stats['max_followers']:,.0f}명")
        with col4:
            st.metric("최소 팔로워", f"{basic_stats['min_followers']:,.0f}명")
        
        # 팔로워 분포 차트
        if basic_stats['followers_distribution']:
            fig = px.histogram(
                x=basic_stats['followers_distribution'],
                nbins=20,
                title="팔로워 수 분포",
                labels={"x": "팔로워 수", "y": "인플루언서 수"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 팔로잉 수 통계
        st.markdown("#### 👤 팔로잉 수 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 팔로잉", f"{basic_stats['avg_followings']:,.0f}명")
        with col2:
            st.metric("중앙값 팔로잉", f"{basic_stats['median_followings']:,.0f}명")
        with col3:
            st.metric("최대 팔로잉", f"{basic_stats['max_followings']:,.0f}명")
        with col4:
            st.metric("최소 팔로잉", f"{basic_stats['min_followings']:,.0f}명")
        
        # 게시물 수 통계
        st.markdown("#### 📝 게시물 수 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 게시물", f"{basic_stats['avg_posts']:,.0f}개")
        with col2:
            st.metric("중앙값 게시물", f"{basic_stats['median_posts']:,.0f}개")
        with col3:
            st.metric("최대 게시물", f"{basic_stats['max_posts']:,.0f}개")
        with col4:
            st.metric("최소 게시물", f"{basic_stats['min_posts']:,.0f}개")
        
        # 팔로워/팔로잉 비율 분석
        st.markdown("#### ⚖️ 팔로워/팔로잉 비율 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 비율", f"{basic_stats['avg_ratio']:.2f}")
        with col2:
            st.metric("중앙값 비율", f"{basic_stats['median_ratio']:.2f}")
        with col3:
            st.metric("최대 비율", f"{basic_stats['max_ratio']:.2f}")
        with col4:
            st.metric("최소 비율", f"{basic_stats['min_ratio']:.2f}")
        
        # 비율 분포 차트
        if basic_stats['ratio_distribution']:
            fig = px.histogram(
                x=basic_stats['ratio_distribution'],
                nbins=20,
                title="팔로워/팔로잉 비율 분포",
                labels={"x": "비율", "y": "인플루언서 수"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 수치 해석 가이드
        with st.expander("📖 수치 해석 가이드", expanded=False):
            st.markdown("""
            **팔로워 수 해석:**
            - 1만명 미만: 마이크로 인플루언서
            - 1만~10만명: 소규모 인플루언서  
            - 10만~100만명: 중간 규모 인플루언서
            - 100만명 이상: 대형 인플루언서
            
            **팔로워/팔로잉 비율 해석:**
            - 1.0~1.3: 상호 팔로우형 (품앗이형)
            - 0.5~1.0: 균형형
            - 0.5 미만: 영향력 집중형 (진정성 높음)
            """)
    
    except Exception as e:
        st.error(f"기본 계정 정보 통계 조회 중 오류: {str(e)}")

def render_network_analysis_statistics():
    """네트워크 분석 통계"""
    st.markdown("### 🔍 네트워크 분석 통계")
    
    try:
        # 네트워크 분석 통계 조회
        network_stats = get_network_analysis_statistics()
        
        if not network_stats:
            st.warning("네트워크 분석 데이터가 없습니다.")
            return
        
        # 영향력 진정성 점수 분석
        st.markdown("#### 🎯 영향력 진정성 점수 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 진정성 점수", f"{network_stats['avg_authenticity_score']:.1f}/100")
        with col2:
            st.metric("중앙값 진정성 점수", f"{network_stats['median_authenticity_score']:.1f}/100")
        with col3:
            st.metric("최고 진정성 점수", f"{network_stats['max_authenticity_score']:.1f}/100")
        with col4:
            st.metric("최저 진정성 점수", f"{network_stats['min_authenticity_score']:.1f}/100")
        
        # 진정성 점수 분포 차트
        if network_stats['authenticity_distribution']:
            fig = px.histogram(
                x=network_stats['authenticity_distribution'],
                nbins=20,
                title="영향력 진정성 점수 분포",
                labels={"x": "진정성 점수", "y": "인플루언서 수"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 네트워크 유형 분포
        if network_stats['network_type_distribution']:
            st.markdown("#### 🌐 네트워크 유형 분포")
            fig = px.pie(
                values=list(network_stats['network_type_distribution'].values()),
                names=list(network_stats['network_type_distribution'].keys()),
                title="네트워크 유형 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 수치 해석 가이드
        with st.expander("📖 네트워크 분석 해석 가이드", expanded=False):
            st.markdown("""
            **영향력 진정성 점수 해석:**
            - 80~100점: 정상 인플루언서형 (실제 팬층 중심)
            - 60~79점: 균형형 (일부 상호 팔로우 포함)
            - 40~59점: 품앗이형 (상호 팔로우 위주)
            - 40점 미만: 의심스러운 패턴
            
            **네트워크 유형:**
            - 정상 인플루언서형: 팔로워 대비 팔로잉 비율이 낮음
            - 품앗이형: 팔로워와 팔로잉 수가 비슷함
            - 균형형: 중간 정도의 팔로우 패턴
            """)
    
    except Exception as e:
        st.error(f"네트워크 분석 통계 조회 중 오류: {str(e)}")

def render_activity_metrics_statistics():
    """활동성/반응성 메트릭 통계"""
    st.markdown("### 📈 활동성/반응성 메트릭 통계")
    
    try:
        # 활동성 메트릭 통계 조회
        activity_stats = get_activity_metrics_statistics()
        
        if not activity_stats:
            st.warning("활동성 메트릭 데이터가 없습니다.")
            return
        
        # 최근 5개 포스트 통계
        st.markdown("#### 📊 최근 5개 포스트 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 좋아요", f"{activity_stats['avg_likes']:,.0f}")
        with col2:
            st.metric("중앙값 좋아요", f"{activity_stats['median_likes']:,.0f}")
        with col3:
            st.metric("평균 댓글", f"{activity_stats['avg_comments']:,.0f}")
        with col4:
            st.metric("평균 참여율", f"{activity_stats['avg_engagement_rate']:.2f}%")
        
        # 활동 주기 분석
        st.markdown("#### ⏰ 활동 주기 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 활동 주기", f"{activity_stats['avg_recency_span']:.1f}일")
        with col2:
            st.metric("중앙값 활동 주기", f"{activity_stats['median_recency_span']:.1f}일")
        with col3:
            st.metric("최단 활동 주기", f"{activity_stats['min_recency_span']:.1f}일")
        with col4:
            st.metric("최장 활동 주기", f"{activity_stats['max_recency_span']:.1f}일")
        
        # 게시 빈도 분석
        if activity_stats['posting_pace_distribution']:
            st.markdown("#### 📅 게시 빈도 분포")
            fig = px.pie(
                values=list(activity_stats['posting_pace_distribution'].values()),
                names=list(activity_stats['posting_pace_distribution'].keys()),
                title="게시 빈도 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 참여율 분포 차트
        if activity_stats['engagement_rate_distribution']:
            fig = px.histogram(
                x=activity_stats['engagement_rate_distribution'],
                nbins=20,
                title="참여율 분포",
                labels={"x": "참여율 (%)", "y": "인플루언서 수"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 수치 해석 가이드
        with st.expander("📖 활동성 메트릭 해석 가이드", expanded=False):
            st.markdown("""
            **참여율 해석:**
            - 6% 이상: 매우 활발한 참여
            - 3~6%: 우수한 참여
            - 1~3%: 일반적인 참여
            - 1% 미만: 낮은 참여
            
            **게시 빈도 해석:**
            - 매우 높음: 4개 이상 & 7일 이내
            - 높음: 3개 이상 & 14일 이내
            - 보통: 2개 이상 & 30일 이내
            - 낮음: 1개 & 30일 이내
            - 불명: 데이터 부족
            
            **활동 주기 해석:**
            - 7일 이내: 매우 활발한 활동
            - 7~14일: 활발한 활동
            - 14~30일: 보통 활동
            - 30일 이상: 낮은 활동
            """)
    
    except Exception as e:
        st.error(f"활동성 메트릭 통계 조회 중 오류: {str(e)}")

def render_comment_authenticity_statistics():
    """댓글 진정성 분석 통계"""
    st.markdown("### 💬 댓글 진정성 분석 통계")
    
    try:
        # 댓글 진정성 통계 조회
        comment_stats = get_comment_authenticity_statistics()
        
        if not comment_stats:
            st.warning("댓글 진정성 분석 데이터가 없습니다.")
            return
        
        # 댓글 진정성 비율 분석
        st.markdown("#### 🎯 댓글 진정성 비율 분석")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 진정성 비율", f"{comment_stats['avg_authentic_ratio']:.1f}%")
        with col2:
            st.metric("중앙값 진정성 비율", f"{comment_stats['median_authentic_ratio']:.1f}%")
        with col3:
            st.metric("평균 형식적 댓글 비율", f"{comment_stats['avg_low_authentic_ratio']:.1f}%")
        with col4:
            st.metric("중앙값 형식적 댓글 비율", f"{comment_stats['median_low_authentic_ratio']:.1f}%")
        
        # 진정성 비율 분포 차트
        if comment_stats['authentic_ratio_distribution']:
            fig = px.histogram(
                x=comment_stats['authentic_ratio_distribution'],
                nbins=20,
                title="댓글 진정성 비율 분포",
                labels={"x": "진정성 비율 (%)", "y": "인플루언서 수"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 진정성 등급 분포
        if comment_stats['authenticity_level_distribution']:
            st.markdown("#### 📊 진정성 등급 분포")
            fig = px.pie(
                values=list(comment_stats['authenticity_level_distribution'].values()),
                names=list(comment_stats['authenticity_level_distribution'].keys()),
                title="진정성 등급 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 수치 해석 가이드
        with st.expander("📖 댓글 진정성 해석 가이드", expanded=False):
            st.markdown("""
            **댓글 진정성 비율 해석:**
            - 70% 이상: 높은 진정성 (실제 팬층 중심)
            - 50~70%: 보통 진정성 (일부 형식적 댓글 포함)
            - 30~50%: 낮은 진정성 (많은 형식적 댓글)
            - 30% 미만: 매우 낮은 진정성 (의심스러운 패턴)
            
            **형식적 댓글 비율 해석:**
            - 30% 미만: 양호한 댓글 품질
            - 30~50%: 보통 댓글 품질
            - 50% 이상: 낮은 댓글 품질 (품앗이, 봇 의심)
            
            **진정성 등급:**
            - 높음: 실제 팬들의 진정한 반응이 많음
            - 중간: 일부 진정한 반응과 형식적 댓글 혼재
            - 낮음: 대부분 형식적이거나 의심스러운 댓글
            """)
    
    except Exception as e:
        st.error(f"댓글 진정성 통계 조회 중 오류: {str(e)}")

def render_evaluation_scores_statistics():
    """평가 점수 통계"""
    st.markdown("### 🎯 평가 점수 통계")
    
    try:
        # 평가 점수 통계 조회
        score_stats = get_evaluation_scores_statistics()
        
        if not score_stats:
            st.warning("평가 점수 데이터가 없습니다.")
            return
        
        # 각 점수별 통계
        st.markdown("#### 📊 점수별 통계")
        
        # 참여도 점수
        st.markdown("##### 💬 참여도 점수")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 참여도", f"{score_stats['avg_engagement']:.1f}/10")
        with col2:
            st.metric("중앙값 참여도", f"{score_stats['median_engagement']:.1f}/10")
        with col3:
            st.metric("최고 참여도", f"{score_stats['max_engagement']:.1f}/10")
        with col4:
            st.metric("최저 참여도", f"{score_stats['min_engagement']:.1f}/10")
        
        # 활동성 점수
        st.markdown("##### 🏃 활동성 점수")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 활동성", f"{score_stats['avg_activity']:.1f}/10")
        with col2:
            st.metric("중앙값 활동성", f"{score_stats['median_activity']:.1f}/10")
        with col3:
            st.metric("최고 활동성", f"{score_stats['max_activity']:.1f}/10")
        with col4:
            st.metric("최저 활동성", f"{score_stats['min_activity']:.1f}/10")
        
        # 소통능력 점수
        st.markdown("##### 💭 소통능력 점수")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 소통능력", f"{score_stats['avg_communication']:.1f}/10")
        with col2:
            st.metric("중앙값 소통능력", f"{score_stats['median_communication']:.1f}/10")
        with col3:
            st.metric("최고 소통능력", f"{score_stats['max_communication']:.1f}/10")
        with col4:
            st.metric("최저 소통능력", f"{score_stats['min_communication']:.1f}/10")
        
        # 성장잠재력 점수
        st.markdown("##### 🌱 성장잠재력 점수")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 성장잠재력", f"{score_stats['avg_growth_potential']:.1f}/10")
        with col2:
            st.metric("중앙값 성장잠재력", f"{score_stats['median_growth_potential']:.1f}/10")
        with col3:
            st.metric("최고 성장잠재력", f"{score_stats['max_growth_potential']:.1f}/10")
        with col4:
            st.metric("최저 성장잠재력", f"{score_stats['min_growth_potential']:.1f}/10")
        
        # 종합점수
        st.markdown("##### 🏆 종합점수")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("평균 종합점수", f"{score_stats['avg_overall']:.1f}/10")
        with col2:
            st.metric("중앙값 종합점수", f"{score_stats['median_overall']:.1f}/10")
        with col3:
            st.metric("최고 종합점수", f"{score_stats['max_overall']:.1f}/10")
        with col4:
            st.metric("최저 종합점수", f"{score_stats['min_overall']:.1f}/10")
        
        # 점수 분포 차트
        if score_stats['score_distributions']:
            col1, col2 = st.columns(2)
            
            with col1:
                # 종합점수 분포
                fig = px.histogram(
                    x=score_stats['score_distributions']['overall'],
                    nbins=10,
                    title="종합점수 분포",
                    labels={"x": "종합점수", "y": "인플루언서 수"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 추론 신뢰도 분포
                if score_stats['inference_confidence_distribution']:
                    fig = px.histogram(
                        x=score_stats['inference_confidence_distribution'],
                        nbins=10,
                        title="추론 신뢰도 분포",
                        labels={"x": "추론 신뢰도", "y": "인플루언서 수"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # 점수 상관관계 분석
        if score_stats['correlation_data']:
            st.markdown("#### 🔗 점수 상관관계 분석")
            fig = px.imshow(
                score_stats['correlation_data'],
                title="점수 간 상관관계",
                color_continuous_scale='RdBu_r'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 수치 해석 가이드
        with st.expander("📖 평가 점수 해석 가이드", expanded=False):
            st.markdown("""
            **점수 해석 기준:**
            - 9~10점: 매우 우수
            - 7~8점: 우수
            - 5~6점: 보통
            - 3~4점: 미흡
            - 0~2점: 매우 미흡
            
            **각 점수 의미:**
            - 참여도: 팔로워들의 반응 강도와 일관성
            - 활동성: 게시 빈도와 꾸준함
            - 소통능력: 팬과의 실질적인 상호작용 정도
            - 성장잠재력: 브랜드 협업 및 확장 가능성
            - 종합점수: 위 4개 점수의 평균
            
            **추론 신뢰도:**
            - 0.8~1.0: 매우 높은 신뢰도
            - 0.6~0.8: 높은 신뢰도
            - 0.4~0.6: 보통 신뢰도
            - 0.2~0.4: 낮은 신뢰도
            - 0.0~0.2: 매우 낮은 신뢰도
            """)
    
    except Exception as e:
        st.error(f"평가 점수 통계 조회 중 오류: {str(e)}")

def get_total_analyses_count():
    """총 분석 수 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return 0
        
        response = client.table("ai_influencer_analyses").select("id", count="exact").execute()
        return response.count if response.count else 0
    except:
        return 0

def get_recent_analyses_count():
    """최근 7일 분석 수 조회"""
    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        client = simple_client.get_client()
        if not client:
            return 0
        
        response = client.table("ai_influencer_analyses").select("id", count="exact").gte("analyzed_at", seven_days_ago.isoformat()).execute()
        return response.count if response.count else 0
    except:
        return 0

def get_average_overall_score():
    """평균 종합점수 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return 0
        
        response = client.table("ai_influencer_analyses").select("overall_score").not_.is_("overall_score", "null").execute()
        scores = [item["overall_score"] for item in response.data if item.get("overall_score")]
        return sum(scores) / len(scores) if scores else 0
    except:
        return 0

def get_recommendation_distribution():
    """추천도 분포 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return {}
        
        response = client.table("ai_influencer_analyses").select("recommendation").execute()
        recommendations = [item["recommendation"] for item in response.data if item.get("recommendation")]
        
        distribution = {}
        for rec in recommendations:
            distribution[rec] = distribution.get(rec, 0) + 1
        
        return distribution
    except:
        return {}

def get_category_statistics():
    """카테고리별 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return {}
        
        response = client.table("ai_influencer_analyses").select("category").execute()
        categories = [item["category"] for item in response.data if item.get("category")]
        
        stats = {}
        for category in categories:
            stats[category] = stats.get(category, 0) + 1
        
        return stats
    except:
        return {}

def get_score_distribution():
    """점수 분포 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return []
        
        response = client.table("ai_influencer_analyses").select("overall_score").not_.is_("overall_score", "null").execute()
        return [item["overall_score"] for item in response.data if item.get("overall_score")]
    except:
        return []

def get_basic_account_statistics():
    """기본 계정 정보 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        response = client.table("ai_influencer_analyses").select("followers, followings, posts_count").execute()
        
        if not response.data:
            return None
        
        # 데이터 추출
        followers = [item["followers"] for item in response.data if item.get("followers") is not None]
        followings = [item["followings"] for item in response.data if item.get("followings") is not None]
        posts = [item["posts_count"] for item in response.data if item.get("posts_count") is not None]
        
        # 팔로워/팔로잉 비율 계산
        ratios = []
        for i in range(min(len(followers), len(followings))):
            if followings[i] and followings[i] > 0:
                ratios.append(followers[i] / followings[i])
        
        return {
            "avg_followers": sum(followers) / len(followers) if followers else 0,
            "median_followers": sorted(followers)[len(followers)//2] if followers else 0,
            "max_followers": max(followers) if followers else 0,
            "min_followers": min(followers) if followers else 0,
            "followers_distribution": followers,
            
            "avg_followings": sum(followings) / len(followings) if followings else 0,
            "median_followings": sorted(followings)[len(followings)//2] if followings else 0,
            "max_followings": max(followings) if followings else 0,
            "min_followings": min(followings) if followings else 0,
            
            "avg_posts": sum(posts) / len(posts) if posts else 0,
            "median_posts": sorted(posts)[len(posts)//2] if posts else 0,
            "max_posts": max(posts) if posts else 0,
            "min_posts": min(posts) if posts else 0,
            
            "avg_ratio": sum(ratios) / len(ratios) if ratios else 0,
            "median_ratio": sorted(ratios)[len(ratios)//2] if ratios else 0,
            "max_ratio": max(ratios) if ratios else 0,
            "min_ratio": min(ratios) if ratios else 0,
            "ratio_distribution": ratios
        }
    except Exception as e:
        st.error(f"기본 계정 정보 통계 조회 중 오류: {str(e)}")
        return None

def get_network_analysis_statistics():
    """네트워크 분석 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        response = client.table("ai_influencer_analyses").select("follow_network_analysis").execute()
        
        if not response.data:
            return None
        
        authenticity_scores = []
        network_types = []
        
        for item in response.data:
            network_analysis = item.get("follow_network_analysis", {})
            if isinstance(network_analysis, dict):
                # 영향력 진정성 점수 추출
                score = network_analysis.get("influence_authenticity_score")
                if score is not None:
                    try:
                        authenticity_scores.append(float(score))
                    except (ValueError, TypeError):
                        pass
                
                # 네트워크 유형 추출
                network_type = network_analysis.get("network_type_inference")
                if network_type:
                    network_types.append(network_type)
        
        # 네트워크 유형 분포 계산
        network_type_dist = {}
        for nt in network_types:
            network_type_dist[nt] = network_type_dist.get(nt, 0) + 1
        
        return {
            "avg_authenticity_score": sum(authenticity_scores) / len(authenticity_scores) if authenticity_scores else 0,
            "median_authenticity_score": sorted(authenticity_scores)[len(authenticity_scores)//2] if authenticity_scores else 0,
            "max_authenticity_score": max(authenticity_scores) if authenticity_scores else 0,
            "min_authenticity_score": min(authenticity_scores) if authenticity_scores else 0,
            "authenticity_distribution": authenticity_scores,
            "network_type_distribution": network_type_dist
        }
    except Exception as e:
        st.error(f"네트워크 분석 통계 조회 중 오류: {str(e)}")
        return None

def get_activity_metrics_statistics():
    """활동성 메트릭 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        response = client.table("ai_influencer_analyses").select("follow_network_analysis, comment_authenticity_analysis").execute()
        
        if not response.data:
            return None
        
        likes = []
        comments = []
        engagement_rates = []
        recency_spans = []
        posting_paces = []
        
        for item in response.data:
            network_analysis = item.get("follow_network_analysis", {})
            comment_analysis = item.get("comment_authenticity_analysis", {})
            
            if isinstance(network_analysis, dict):
                # 최근 5개 포스트 메트릭 추출
                avg_likes = network_analysis.get("avg_likes_last5")
                if avg_likes is not None:
                    try:
                        likes.append(float(avg_likes))
                    except (ValueError, TypeError):
                        pass
                
                # 활동 주기 추출
                recency_span = network_analysis.get("recency_span_last5_days")
                if recency_span is not None:
                    try:
                        recency_spans.append(float(recency_span))
                    except (ValueError, TypeError):
                        pass
                
                # 게시 빈도 추출
                posting_pace = network_analysis.get("posting_pace_last5")
                if posting_pace:
                    posting_paces.append(posting_pace)
                
                # 참여율 추출
                engagement_rate = network_analysis.get("est_engagement_rate_last5")
                if engagement_rate is not None:
                    try:
                        engagement_rates.append(float(engagement_rate))
                    except (ValueError, TypeError):
                        pass
            
            if isinstance(comment_analysis, dict):
                # 평균 댓글 수 추출
                avg_comments = comment_analysis.get("comments_avg_last5")
                if avg_comments is not None:
                    try:
                        comments.append(float(avg_comments))
                    except (ValueError, TypeError):
                        pass
        
        # 게시 빈도 분포 계산
        posting_pace_dist = {}
        for pp in posting_paces:
            posting_pace_dist[pp] = posting_pace_dist.get(pp, 0) + 1
        
        return {
            "avg_likes": sum(likes) / len(likes) if likes else 0,
            "median_likes": sorted(likes)[len(likes)//2] if likes else 0,
            "avg_comments": sum(comments) / len(comments) if comments else 0,
            "avg_engagement_rate": sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0,
            "avg_recency_span": sum(recency_spans) / len(recency_spans) if recency_spans else 0,
            "median_recency_span": sorted(recency_spans)[len(recency_spans)//2] if recency_spans else 0,
            "min_recency_span": min(recency_spans) if recency_spans else 0,
            "max_recency_span": max(recency_spans) if recency_spans else 0,
            "posting_pace_distribution": posting_pace_dist,
            "engagement_rate_distribution": engagement_rates
        }
    except Exception as e:
        st.error(f"활동성 메트릭 통계 조회 중 오류: {str(e)}")
        return None

def get_comment_authenticity_statistics():
    """댓글 진정성 분석 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        response = client.table("ai_influencer_analyses").select("comment_authenticity_analysis").execute()
        
        if not response.data:
            return None
        
        authentic_ratios = []
        low_authentic_ratios = []
        authenticity_levels = []
        
        for item in response.data:
            comment_analysis = item.get("comment_authenticity_analysis", {})
            if isinstance(comment_analysis, dict):
                # 진정성 비율 추출
                authentic_ratio = comment_analysis.get("authentic_comments_ratio")
                if authentic_ratio is not None:
                    try:
                        authentic_ratios.append(float(authentic_ratio))
                    except (ValueError, TypeError):
                        pass
                
                # 형식적 댓글 비율 추출
                low_authentic_ratio = comment_analysis.get("low_authentic_comments_ratio")
                if low_authentic_ratio is not None:
                    try:
                        low_authentic_ratios.append(float(low_authentic_ratio))
                    except (ValueError, TypeError):
                        pass
                
                # 진정성 등급 추출
                authenticity_level = comment_analysis.get("authenticity_level")
                if authenticity_level:
                    authenticity_levels.append(authenticity_level)
        
        # 진정성 등급 분포 계산
        authenticity_level_dist = {}
        for al in authenticity_levels:
            authenticity_level_dist[al] = authenticity_level_dist.get(al, 0) + 1
        
        return {
            "avg_authentic_ratio": sum(authentic_ratios) / len(authentic_ratios) if authentic_ratios else 0,
            "median_authentic_ratio": sorted(authentic_ratios)[len(authentic_ratios)//2] if authentic_ratios else 0,
            "avg_low_authentic_ratio": sum(low_authentic_ratios) / len(low_authentic_ratios) if low_authentic_ratios else 0,
            "median_low_authentic_ratio": sorted(low_authentic_ratios)[len(low_authentic_ratios)//2] if low_authentic_ratios else 0,
            "authentic_ratio_distribution": authentic_ratios,
            "authenticity_level_distribution": authenticity_level_dist
        }
    except Exception as e:
        st.error(f"댓글 진정성 통계 조회 중 오류: {str(e)}")
        return None

def get_evaluation_scores_statistics():
    """평가 점수 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        response = client.table("ai_influencer_analyses").select("engagement_score, activity_score, communication_score, growth_potential_score, overall_score, inference_confidence").execute()
        
        if not response.data:
            return None
        
        # 각 점수별 데이터 추출
        engagement_scores = [item["engagement_score"] for item in response.data if item.get("engagement_score") is not None]
        activity_scores = [item["activity_score"] for item in response.data if item.get("activity_score") is not None]
        communication_scores = [item["communication_score"] for item in response.data if item.get("communication_score") is not None]
        growth_potential_scores = [item["growth_potential_score"] for item in response.data if item.get("growth_potential_score") is not None]
        overall_scores = [item["overall_score"] for item in response.data if item.get("overall_score") is not None]
        inference_confidences = [item["inference_confidence"] for item in response.data if item.get("inference_confidence") is not None]
        
        # 상관관계 데이터 준비
        import pandas as pd
        correlation_data = None
        if len(engagement_scores) > 1:
            df = pd.DataFrame({
                'engagement': engagement_scores[:len(engagement_scores)],
                'activity': activity_scores[:len(engagement_scores)],
                'communication': communication_scores[:len(engagement_scores)],
                'growth_potential': growth_potential_scores[:len(engagement_scores)],
                'overall': overall_scores[:len(engagement_scores)]
            })
            correlation_data = df.corr().values.tolist()
        
        return {
            "avg_engagement": sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0,
            "median_engagement": sorted(engagement_scores)[len(engagement_scores)//2] if engagement_scores else 0,
            "max_engagement": max(engagement_scores) if engagement_scores else 0,
            "min_engagement": min(engagement_scores) if engagement_scores else 0,
            
            "avg_activity": sum(activity_scores) / len(activity_scores) if activity_scores else 0,
            "median_activity": sorted(activity_scores)[len(activity_scores)//2] if activity_scores else 0,
            "max_activity": max(activity_scores) if activity_scores else 0,
            "min_activity": min(activity_scores) if activity_scores else 0,
            
            "avg_communication": sum(communication_scores) / len(communication_scores) if communication_scores else 0,
            "median_communication": sorted(communication_scores)[len(communication_scores)//2] if communication_scores else 0,
            "max_communication": max(communication_scores) if communication_scores else 0,
            "min_communication": min(communication_scores) if communication_scores else 0,
            
            "avg_growth_potential": sum(growth_potential_scores) / len(growth_potential_scores) if growth_potential_scores else 0,
            "median_growth_potential": sorted(growth_potential_scores)[len(growth_potential_scores)//2] if growth_potential_scores else 0,
            "max_growth_potential": max(growth_potential_scores) if growth_potential_scores else 0,
            "min_growth_potential": min(growth_potential_scores) if growth_potential_scores else 0,
            
            "avg_overall": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
            "median_overall": sorted(overall_scores)[len(overall_scores)//2] if overall_scores else 0,
            "max_overall": max(overall_scores) if overall_scores else 0,
            "min_overall": min(overall_scores) if overall_scores else 0,
            
            "score_distributions": {
                "engagement": engagement_scores,
                "activity": activity_scores,
                "communication": communication_scores,
                "growth_potential": growth_potential_scores,
                "overall": overall_scores
            },
            "inference_confidence_distribution": inference_confidences,
            "correlation_data": correlation_data
        }
    except Exception as e:
        st.error(f"평가 점수 통계 조회 중 오류: {str(e)}")
        return None
